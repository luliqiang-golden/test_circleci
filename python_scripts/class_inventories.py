"""Endpoints for inventories"""

from flask import jsonify, request
from flask_restful import Resource
from resource_functions import post_update_existing_resource, delete_resource
from resource_functions import get_collection, post_new_resource, get_resource
from db_functions import select_from_db
from auth0_authentication import requires_auth
from abc import ABC, abstractmethod
from enum import Enum



class InventoryType(Enum):
    ALL = 'all'
    BATCH = "batch"
    MOTHER = "mother"
    MOTHER_BATCH = "mother batch"
    RECEIVED_INVENTORY = "received inventory"
    LOT = "lot"
    LOT_ITEM = "lot item"
    SAMPLE = "sample"
    DESTRUCTION_INVENTORY = "destruction inventory"

class ArchiveType(Enum):
    ARCHIVED = "archived"
    NOT_ARCHIVED = "not_archived"
    BOTH = "both"
    

class AbstractInventory(ABC):    
    @abstractmethod
    def _get_query(self, inventory_type: InventoryType, archive_type: ArchiveType) -> str:
        pass

    @abstractmethod
    def execute(self, current_user: object, 
                      organization_id: int = None, 
                      inventory_type: InventoryType = InventoryType.ALL, 
                      archive_type: ArchiveType = ArchiveType.BOTH):
        pass


class AbstractFactoryInventory(ABC):    
    @abstractmethod
    def create_inventory(self) -> AbstractInventory:
        pass


class ConcreteFactoryInventoryBase(AbstractFactoryInventory):    
    def create_inventory(self) -> AbstractInventory:
        return InventoryBase()


class ConcreteFactoryBatch(AbstractFactoryInventory):    
    def create_inventory(self) -> AbstractInventory:
        return InventoryBatch()


class ConcreteFactoryMother(AbstractFactoryInventory):    
    def create_inventory(self) -> AbstractInventory:
        return InventoryMother()


class ConcreteFactorySample(AbstractFactoryInventory):
    def create_inventory(self) -> AbstractInventory:
        return InventorySample()


class ConcreteFactoryLotItem(AbstractFactoryInventory):
    def create_inventory(self) -> AbstractInventory:
        return InventoryLotItem()


class InventoryBase(AbstractInventory):

    def _get_query_base(self, inventory_type: InventoryType) -> str:

        query_base = """
            select *, (f_serialize_stats(inv.stats)).qty, (f_serialize_stats(inv.stats)).unit from inventories as inv where type = '{0}'

        """.format(inventory_type.value)

        return query_base


    def _get_query_not_archived(self, query):
        
        query = query + """
            and (((f_serialize_stats(inv.stats)).qty > 0) or inv.is_parent = true)
        """

        return query


    def _get_query_archived(self, query):
        query = query + """
            and ((f_serialize_stats(inv.stats)).qty = 0)
        """

        return query



    def _get_query(self, inventory_type: InventoryType, archive_type: ArchiveType) -> str:

        query = self._get_query_base(inventory_type)

        if (archive_type == ArchiveType.ARCHIVED):
            query = self._get_query_archived(query)

        elif (archive_type == ArchiveType.NOT_ARCHIVED):
            query = self._get_query_not_archived(query)

        return query


    def execute(self, current_user: object, 
                      organization_id: int = None, 
                      inventory_type: InventoryType = InventoryType.ALL, 
                      archive_type: ArchiveType = ArchiveType.BOTH):


        query = self._get_query(inventory_type, archive_type)

        result = get_collection(
            current_user=current_user,
            organization_id=organization_id,
            resource='inventories',
            query=query)

        if result:
            return result


class InventoryBatch(InventoryBase):
    def _get_query_not_archived(self, query):
        
        query = super()._get_query_not_archived(query) + """
            or (inv.attributes->>'processor_status' = 'sent_to_processor')
        """

        return query


    def _get_query_archived(self, query):
        query = super()._get_query_archived(query) + """
            and (inv.attributes->>'processor_status' != 'sent_to_processor' or  inv.attributes->>'processor_status' isnull)
        """

        return query


class InventoryMother(InventoryBase):
    def _get_query_base(self, inventory_type: InventoryType) -> str:
        return """
            select act.data ->> 'to_inventory_id' AS mother_batch_id,
                inv.*,
                (f_serialize_stats(inv.stats)).qty, (f_serialize_stats(inv.stats)).unit
            from inventories inv
                left join activities act on inv.id = ((act.data ->> 'from_inventory_id')::numeric) and 
                                            inv.organization_id = act.organization_id and 
                                            act.name = 'transfer_mother_plants_to_mother_batch'
            where inv.type = 'mother'
        """

    def _get_query_not_archived(self, query):
        query = super()._get_query_not_archived(query) + """
            or (inv.attributes->'status' = '"added_to_batch"')
        """

        return query

    def _get_query_archived(self, query):
        query = super()._get_query_archived(query) + """
            and (inv.attributes->'status' != '"added_to_batch"')
        """

        return query


class InventorySample(InventoryBase):
    def _get_query_not_archived(self, query):
        query = super()._get_query_not_archived(query) + """
            or ((inv.attributes ->> 'test_status' = 'sample-sent-to-lab') and inv.type = 'sample')
        """

        return query

    def _get_query_archived(self, query):
        query = super()._get_query_archived(query) + """
            and ((inv.attributes->>'test_status' <> 'sample-sent-to-lab') and inv.type = 'sample')
        """

        return query

class InventoryLotItem(InventoryBase):
    def _get_query_base(self, inventory_type: InventoryType) -> str:
        return """
           SELECT s.name AS sku_name,
                inv.*,
                (f_serialize_stats(inv.stats)).qty, (f_serialize_stats(inv.stats)).unit
            FROM inventories inv
            LEFT JOIN skus s ON ((inv.data ->> 'sku_id')::bigint) = s.id
            WHERE inv.type = 'lot item'
        """

class Inventories(Resource):

    # Read all client records
    @requires_auth
    def get(self, current_user, organization_id=None):

        query = """
            select inv.*, (f_serialize_stats(inv.stats)).qty, (f_serialize_stats(inv.stats)).unit from inventories as inv
        """

        result = get_collection(
            current_user=current_user,
            organization_id=organization_id,
            query=query,
            resource='Inventories')

        return result
 
    # Insert new client record, along with meta
    @requires_auth
    def post(self, current_user, organization_id=None):
        return post_new_resource(
            current_user=current_user,
            organization_id=organization_id,
            resource='Inventories')


class InventoriesByType(Resource):

    @requires_auth
    def get(self, current_user, organization_id=None, inventory_type=InventoryType.ALL, archive_type=ArchiveType.BOTH):
        result = None
        inventory_type = InventoryType(inventory_type)
        archive_type = ArchiveType(archive_type)
        if (InventoryType(inventory_type) == InventoryType.BATCH):
            result = self.get_inventory(ConcreteFactoryBatch(), current_user, organization_id, inventory_type, archive_type)

        elif (InventoryType(inventory_type) == InventoryType.MOTHER):
            result = self.get_inventory(ConcreteFactoryMother(), current_user, organization_id, inventory_type, archive_type)

        elif (InventoryType(inventory_type) == InventoryType.SAMPLE):
            result = self.get_inventory(ConcreteFactorySample(), current_user, organization_id, inventory_type, archive_type)
        
        elif (InventoryType(inventory_type) == InventoryType.LOT_ITEM):
            result = self.get_inventory(ConcreteFactoryLotItem(), current_user, organization_id, inventory_type, archive_type)

        else:
            result = self.get_inventory(ConcreteFactoryInventoryBase(), current_user, organization_id, inventory_type, archive_type)


        return result



    def get_inventory(self, factory_inventory: AbstractFactoryInventory, 
                            current_user, 
                            organization_id=None, 
                            inventory_type: InventoryType = InventoryType.ALL, 
                            archive_type: ArchiveType = ArchiveType.BOTH):

        inventory = factory_inventory.create_inventory() 
        return inventory.execute(current_user=current_user, organization_id=organization_id, inventory_type=inventory_type, archive_type=archive_type)

class DestructionsHistory(Resource):
    '''
        Class to retrieve all the destruction data based on destruction inventory
    '''
    @requires_auth
    def get(self, current_user, organization_id=None):
        
        query = """
            SELECT inv.*, ROW_TO_JSON(act_1.*) AS queue_for_destruction, ROW_TO_JSON(act_2.*) AS complete_destruction
            FROM inventories AS inv
            INNER JOIN activities AS act_1 ON act_1.name = 'queue_for_destruction' AND CAST(act_1.data->>'to_inventory_id' AS numeric) = inv.id
            INNER JOIN activities AS act_2 ON act_2.name = 'complete_destruction' AND CAST(act_2.data->>'from_inventory_id' AS numeric) = inv.id AND act_2.deleted = false
            WHERE inv.type = 'destruction inventory' AND inv.attributes->>'status' = 'destroyed'
        """

        result = get_collection(
            current_user=current_user,
            organization_id=organization_id,
            resource='inventories',
            query=query
        )

        if result:
            return result
        

class Inventory(Resource):

    # Read single client record by id
    @requires_auth
    def get(self, current_user, inventory_id, organization_id=None):
        return get_resource(
            current_user=current_user,
            resource_id=inventory_id,
            organization_id=organization_id,
            resource='Inventories',
            select='SELECT t.*, (f_serialize_stats(t.stats)).qty, (f_serialize_stats(t.stats)).unit')

    # Updates existing client record, along with meta
    @requires_auth
    def patch(self, current_user, inventory_id, organization_id=None):
        return post_update_existing_resource(
            current_user=current_user,
            resource_id=inventory_id,
            organization_id=organization_id,
            resource='Inventories')

    # Delete client record by id
    @requires_auth
    def delete(self, current_user, inventory_id, organization_id=None):
        return delete_resource(
            current_user=current_user,
            resource='Inventories',
            resource_id=inventory_id,
            organization_id=organization_id)

class BatchRecord(Resource):
    @requires_auth
    def get(self, current_user, inventory_id, organization_id=None):
        query = """
		SELECT inv.*,
        (
	        SELECT coalesce(ARRAY_TO_JSON(ARRAY_AGG(ROW_TO_JSON(equip))), '[]')
            FROM (
      	        SELECT e.*
		        FROM equipment AS e WHERE e.room = CAST(inv.attributes->>'room' AS varchar)
            ) equip   
        ) AS equipments,
		(
			SELECT COALESCE(ARRAY_TO_JSON(ARRAY_AGG(ROW_TO_JSON(deviation_report))), '[]')
			FROM (
				SELECT *
				FROM (
					SELECT DISTINCT d.*, act_dr.id as activity_id
					FROM deviation_reports AS d
					INNER JOIN activities AS act_dr ON d.id = CAST(act_dr.data->>'deviation_report_id' AS numeric)
					WHERE CAST(act_dr.data->>'inventory_id' AS numeric) = inv.id
					AND act_dr.name = 'deviation_report_add_link'
				) deviation_reports_list			
				order by deviation_reports_list.activity_id
			) deviation_report
		) AS deviation_reports,
		(
			SELECT COALESCE(ARRAY_TO_JSON(ARRAY_AGG(ROW_TO_JSON(capa))), '[]')
			FROM (
				SELECT capa_row.*,
				(
					SELECT COALESCE(ARRAY_TO_JSON(ARRAY_AGG(ROW_TO_JSON(capa_link))), '[]')
					FROM (
						SELECT
							act_capa_link.*
						FROM activities AS act_capa_link
						WHERE CAST(act_capa_link.data->>'capa_id' AS numeric) = capa_row.id
						AND act_capa_link.name = 'capa_add_link'
					) capa_link
				) AS capa_links,
				(
					SELECT COALESCE(ARRAY_TO_JSON(ARRAY_AGG(ROW_TO_JSON(capa_action))), '[]')
					FROM (
						SELECT
							act_capa_action.*
						FROM activities AS act_capa_action
						WHERE CAST(act_capa_action.data->>'capa_id' AS numeric) = capa_row.id
						AND act_capa_action.name = 'capa_add_action'
					) capa_action
				) AS capa_actions,
				(
					SELECT COALESCE(ARRAY_TO_JSON(ARRAY_AGG(ROW_TO_JSON(capa_note))), '[]')
					FROM (
						SELECT
							act_capa_note.*
						FROM activities AS act_capa_note
						WHERE CAST(act_capa_note.data->>'capa_id' AS numeric) = capa_row.id
						AND act_capa_note.name = 'capa_add_note'
					) capa_note
				) AS capa_notes,
				(
					SELECT COALESCE(ARRAY_TO_JSON(ARRAY_AGG(ROW_TO_JSON(capa_initiate))), '[]')
					FROM (
						SELECT
							act_capa_initiate.*
						FROM activities AS act_capa_initiate
						WHERE CAST(act_capa_initiate.data->>'capa_id' AS numeric) = capa_row.id
						AND act_capa_initiate.name = 'capa_initiate'
						ORDER BY act_capa_initiate.id DESC
					) capa_initiate
				) AS capa_initiates
				FROM (
					SELECT DISTINCT capa.*				
					FROM capas AS capa
					INNER JOIN activities AS act_capa ON capa.id = CAST(act_capa.data->>'capa_id' AS numeric)
					WHERE CAST(act_capa.data->>'inventory_id' AS numeric) = inv.id
				) AS capa_row
			) capa
		) AS capas,
		(
			SELECT COALESCE(ARRAY_TO_JSON(ARRAY_AGG(ROW_TO_JSON(sop))), '[]')
			FROM (
				SELECT *
				FROM (
				SELECT DISTINCT sop.*, act_sop.id as activity_id
				FROM vw_sops AS sop
				INNER JOIN activities AS act_sop
					ON sop.version_number = CAST(act_sop.data->>'sop_version_number' AS numeric)
					AND sop.id = CAST(act_sop.data->>'sop_id' AS numeric)
				WHERE CAST(act_sop.data->>'inventory_id' AS numeric) = inv.id
				AND act_sop.name = 'sop_add_link'
				) sops_list
                ORDER BY sops_list.activity_id
			) sop
		) AS sops,
		(
			SELECT COALESCE(ARRAY_TO_JSON(ARRAY_AGG(ROW_TO_JSON(supply))), '[]')
			FROM (
				SELECT
					cc.subtype,
					cc.type,
                    act_cc.timestamp,
					act_cc.data
				FROM consumable_classes AS cc
				INNER JOIN activities AS act_cc
					ON cc.id = CAST(act_cc.data->>'consumable_class_id' AS numeric)
				WHERE CAST(act_cc.data->>'inventory_id' AS numeric) = inv.id
				AND act_cc.name = 'plants_add_pesticide' OR act_cc.name = 'plants_add_ipm'
                ORDER BY act_cc.timestamp ASC
			) supply
		) AS supplies,
		(
			SELECT COALESCE(ARRAY_TO_JSON(ARRAY_AGG(ROW_TO_JSON(room))), '[]')
			FROM (
				SELECT
					act_room.*
				FROM activities AS act_room
				WHERE cast(act_room.data->>'inventory_id' AS numeric) = inv.id
				AND act_room.name = 'update_room'
                ORDER BY act_room.timestamp DESC
			) room
		) AS rooms,
        (
			SELECT COALESCE(ARRAY_TO_JSON(ARRAY_AGG(ROW_TO_JSON(lab_test_result))), '[]')
			FROM (
				SELECT
					act_lab.*
				FROM activities AS act_lab
				WHERE CAST(act_lab.data->>'related_inventory_id' AS numeric) = inv.id
				AND act_lab.name = 'sample_lab_result_received'
                ORDER BY act_lab.timestamp ASC
			) lab_test_result
		) AS lab_test_results,
        (
	        SELECT COALESCE(ARRAY_TO_JSON(ARRAY_AGG(ROW_TO_JSON(act))), '[]')
            FROM (
                SELECT act.id, act.name, act.timestamp, act.data, usr.name AS created_by
				FROM f_activities_from_inventory(inv.id) AS act 
				INNER JOIN users usr ON usr.id = act.created_by
                ORDER BY act.timestamp ASC
            ) act
        ) AS activities
        FROM inventories AS inv
        WHERE inv.type = 'batch' AND inv.id = {0}
        GROUP BY inv.id
        """.format(inventory_id)

        return select_from_db(query=query, code="batch_record_generating_error")[0]