"""
sop_version_update - update an sop version
"""

from db_functions import update_into_db
from activities.activity_handler_class import ActivityHandler
from class_errors import ClientBadRequest


class SopVersionUpdate(ActivityHandler):
    """
    Update an sop version

    :param sop_version_id: ID of the sop version 
    :param description: description of the version
    :param approved_date: date when the version was approved
    :type approved_date: optional
    :param effective_date: date when the version goes into effect
    :type effective_date: optional
    :param review_due_date: due date to review the version
    :type review_due_date: optional
    :param review_effective_date: effective date of the review
    :type review_effective_date: optional
    :param revision_description: description of the revision
    :type revision_description: optional
    :param revision_reason: reason for the revision
    :type revision_reason: optional

    :returns: An object containing the new activity's id, as well as the affected rows of the sop_versions table

    :raises: 400 missing_required_fields
    """

    required_args = {
        'sop_version_id',
        'sop_id'
    }

    possible_fields = {
        'sop_name',
        'description',
        'department',
        'approved_date',
        'effective_date',
        'review_due_date',
        'review_effective_date',
        'review_approval_date',
        'revision_description',
        'revision_reason',
    }

    not_null_fields = {
        'sop_name',
        'description'
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """
        Do the activity

        :param cls: this class
        :param args: arguments passed to the activity handler from the client
        :type args: dict
        :param current_user: current user object
        """

        # get a list of fields to be updated from the args
        update_fields = list(set(args.keys()) & cls.possible_fields)

        if not update_fields:
            raise ClientBadRequest(
                {
                    'code': 'missing_required_fields',
                    'description': 'Sop version update must contain one of {}'.format(
                        ', '.join(cls.possible_fields))
                }, 400)

        # check if the update fields which cannot be null are null
        for field in [field for field in update_fields if field in cls.not_null_fields]:
            if not args[field]:
                raise ClientBadRequest(
                    {
                        'code': 'null_fields',
                        'description': 'Sop version update cannot have null fields for the following: {}'.format(
                            ', '.join(cls.not_null_fields))
                    }, 400)

        cls.check_required_args(args)

        # copy the fields to be updated into a new sop_version_updates object
        sop_version_updates = {field:args[field] for field in update_fields}


        affected_rows = {
            'sops': 0,
            'sop_versions': 0
        }

        if 'sop_name' in sop_version_updates:
            # sop_name is an sops table update
            sop_update_result = update_into_db('sops', args['sop_id'], {
                    'name': sop_version_updates['sop_name']
                })
            del sop_version_updates['sop_name']
            affected_rows['sops'] = sop_update_result['affected_rows']

        if 'department' in sop_version_updates:
            # sop_name is an sops table update
            sop_update_result = update_into_db('sop_versions_departments', args['sop_version_id'], {
                    'department_id': sop_version_updates['department']
                })
            del sop_version_updates['department']
            affected_rows['sops'] = sop_update_result['affected_rows']
        
        if sop_version_updates:      
            sop_versions_update_result = update_into_db('sop_versions', args['sop_version_id'], sop_version_updates)
            affected_rows['sop_versions'] = sop_versions_update_result['affected_rows']
        activity_result = cls.insert_activity_into_db(args) 
        return {
            'activity_id': activity_result['id'],
            'affected_rows': affected_rows['sop_versions']
        }
