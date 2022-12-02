from flask_restful import Resource
from flask import jsonify, request
import psycopg2
import psycopg2.extras
from psycopg2 import sql
from resource_functions import get_resource, prep_sorts, prep_filters
from db_functions import DATABASE, rehydrate_resource, comparison_formatter
from auth0_authentication import requires_auth
from class_errors import DatabaseError


class CapaLinks(Resource):

    """
    could not just use get_collection since we need to hit the inventories table to get subtype for 
    inventory links
    """
    @requires_auth
    def get(self, current_user, organization_id=None):

        filters = []
        filters += prep_filters()

        sorts = prep_sorts()

        per_page = request.args.get('per_page', 20, type=int)

        page = request.args.get('page', 1, type=int)

        results, count = self.select_capa_links_from_db(
            'capa_links',
            organization_id,
            page=page,
            per_page=per_page,
            filters=filters,
            sorts=sorts,
        )

        return jsonify(
            page=page, per_page=per_page, total=count['count'], data=results)

    def select_capa_links_from_db(self,
                                  resource: str,
                                  organization_id: int,
                                  meta=True,
                                  page=1,
                                  per_page=20,
                                  filters=None,
                                  sorts=None):
        """
        Select a collection of resources from the database
        meta -- set False to not query for resource_meta. Used when resource doesn't have a meta table
        """
        if per_page and per_page < 1:
            raise DatabaseError(
                {
                    "code": "per_page_error",
                    "message": "There must be at least 1 query per page"
                }, 400)

        if page < 1:
            raise DatabaseError({
                "code": "page_error",
                "message": "There must be at least 1 page"
            }, 400)

        filters = filters or []

        sorts = sorts or [('id', 'DESC')]

        plural = resource.lower()

        applied_filters, escaped_values = self.build_collection_filters(filters)

        order_by = self.build_collection_sorts(sorts)

        if plural != 'organizations' and organization_id is not None:
            applied_filters.append(
                sql.SQL("{}.organization_id = %(organization_id)s").format(
                    sql.Identifier('capa_links')
                )
            )
            escaped_values['organization_id'] = organization_id

        where = sql.SQL('')
        if applied_filters:
            where = sql.SQL('WHERE ') + sql.Composed(applied_filters).join(' AND ')

        if per_page:
            offset = (page - 1) * per_page
            pagination = sql.SQL("LIMIT {} OFFSET {}").format(
                sql.Placeholder('per_page'), sql.Placeholder('offset'))
            escaped_values['per_page'] = per_page
            escaped_values['offset'] = offset
        else:
            pagination = sql.SQL('')

        query_count = sql.Composed([
            sql.SQL('SELECT COUNT(id) as count'),
            sql.SQL('FROM {}'.format(plural)), where
        ])

        query_count = query_count.join('\n')


        # TODO: try to rewrite this so its easier to read...
        query = sql.Composed([
            sql.SQL('SELECT {}.*, {}.{} as subtype').format(
                sql.Identifier('capa_links'),
                sql.Identifier('inventories'),
                sql.Identifier('type')
            ),
            sql.SQL('FROM {}').format(sql.Identifier(plural)),
            sql.SQL('LEFT JOIN {}').format(sql.Identifier('inventories')),
            sql.SQL('ON {}.{} = {}.{}').format(
                sql.Identifier('capa_links'),
                sql.Identifier('link_id'),
                sql.Identifier('inventories'),
                sql.Identifier('id')
            ),
            sql.SQL('AND {}.{} = {}').format(
                sql.Identifier('capa_links'),
                sql.Identifier('link_type'),
                sql.Literal('inventory')
            ),
            where,
            order_by,
            pagination,
        ])
        query = query.join('\n')

        cursor = DATABASE.dedicated_connection().cursor()
        try:
            print('THIS IS THE QUERY', cursor.mogrify(query, escaped_values))
            cursor.execute(query, escaped_values)
            results = cursor.fetchall()

            cursor.execute(query_count, escaped_values)
            count = cursor.fetchone()

        except (psycopg2.Error, psycopg2.Warning,
                psycopg2.ProgrammingError) as error:
            DATABASE.dedicated_connection().rollback()
            print('SQL: {!r}, errno is {}'.format(error, error.args[0]))
            raise DatabaseError(
                {
                    "code": "select_collection_error",
                    "message": "There was an error querying the database"
                }, 500)

        cursor.close()

        results = [rehydrate_resource(row) for row in results]

        print('results', results, count)
        return results, count

    def build_collection_sorts(self, sorts):

        directions = {'DESC': ' DESC', 'ASC': ' ASC'}
        sort_parts = []
        for column, direction in sorts:
            column = sql.SQL('{}.{}').format(
                sql.Identifier('capa_links'),
                sql.Identifier(column)
            )
            sort_parts.append(
                sql.Composed([column, sql.SQL(directions[direction])]))

        order_by = sql.Composed(
            [sql.SQL('ORDER BY '),
             sql.Composed(sort_parts).join(', ')])

        return order_by

    def build_collection_filters(self, filters):
        """
        Take a list of filter tuples (key, '=', value)
        and return list of SQL filters, dict of values to escape, and count of meta tables to join
        """

        applied_filters = []
        escaped_values = {}

        for filt in filters:
            filter_columns = filt[0].split('|')
            try:
                filter_values = filt[2].split('|')
            except AttributeError:  # in case of numbers
                filter_values = [filt[2]]

            filter_parts = []

            for column in filter_columns:
                column = sql.SQL('{}.{}').format(
                    sql.Identifier('capa_links'),
                    sql.Identifier(column)
                )

                for value in filter_values:
                    escaped_value_key = "escaped_value_{}".format(
                        len(escaped_values))
                    comparison, formatted_value = comparison_formatter(
                        filt[1], value)
                    filter_template = sql.SQL("{0} {1} {2}").format(
                        column, sql.SQL(comparison),
                        sql.Placeholder(escaped_value_key))

                    filter_parts.append(filter_template)
                    escaped_values[escaped_value_key] = formatted_value

            filter_whole = sql.SQL("({})").format(
                sql.Composed(filter_parts).join(' OR '))
            applied_filters.append(filter_whole)

        return applied_filters, escaped_values


class CapaLink(Resource):

    @requires_auth
    def get(self, current_user, capa_link_id, organization_id=None):
        return get_resource(
            current_user=current_user,
            resource_id=capa_link_id,
            organization_id=organization_id,
            resource='capa_links')
