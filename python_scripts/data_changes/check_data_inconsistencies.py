import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

from db_functions import select_from_db


class CheckDataInconsistencies():

    def get_inventories(self, initial_month, final_month, year):
        params = {"id": id}

        query = '''
            select id, latest_unit, latest_quantity, type from f_inventories_latest_stats_stage('{2}-{1}-31') where id in (

            SELECT id
            FROM inventories  
            WHERE type <> 'destruction inventory' and
            organization_id = 2 AND
            TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN '{2}-{0}-01' AND '{2}-{1}-31'
            )
        '''.format(initial_month, final_month, year)

        # query = "select * from inventories where id = 2417"

        result = select_from_db(query, params)
        if (result):
           return result
    
    def __get_activities(self, id):

        params = {"id": id}

        query = '''
             select act.*
                from inventories as inv
                inner join f_activities_from_inventory(inv.id) as act on inv.id = act.inventory_id
                    
            where inv.id = %(id)s and inv.organization_id = 2  
            and act.name in ('propagate_cuttings', 
            'transfer_mother_plants_to_mother_batch', 
            'split_batch',
            'germinate_seeds',
            'create_sample', 
            'queue_for_destruction',
            'sample_sent_to_lab',
            'batch_record_dry_weight',
            'transfer_inventory',
            'batch_record_crude_oil_weight',
            'batch_record_harvest_weight',
            'batch_record_cured_weight',
            'receive_inventory',
            'inventory_adjustment', 'merge_batch')
             and not (act.name = 'inventory_adjustment' and act.data->>'activity_name'='shipment_shipped')
             and to_char(act.timestamp,'YYYY-MM-DD') <= '2020-12-31'
            order by timestamp, id 
        '''

        result = select_from_db(query, params)

        if (result):
           return result

    def execute_checking(self, inventories):
        if (inventories):
            for inventory in inventories:
                id = inventory["id"]
                inv_stats = {}
                inv_stats["unit"] = inventory["latest_unit"]
                inv_stats["qty"] = inventory["latest_quantity"]
                stats = {}
                activities = self.__get_activities(id)

                if (inventory["type"] == "received inventory"):
                    rec_act = list(filter(lambda act: act["name"] == "receive_inventory", activities))
                    if (len(rec_act) == 0):
                        print("[ERROR] INV HAS NO RECEIVE_IVENTORY ACT - id: ", id )

                if (not activities or len(activities) == 0):
                    print("[ERROR] INV HAS NO ACTIVITIES - id: ", id )
                elif any(act['is_next_id_greater'] == False for act in activities):
                    print("[WARNING] INV INCORRECT TIMESTAMP / ID ORDER - id: ", id)
                else:
                    for activity in activities:
                        act = activity["data"]
                        unit = ""
                        qty = 0
                        if (act.get("to_inventory_id")):
                            if (int(act["to_inventory_id"]) == id):
                                unit = act["to_qty_unit"]
                                qty = act["to_qty"]

                                if (not stats.get(unit)):
                                    stats[unit] = qty
                                else:
                                    stats[unit] = stats[unit] + qty

                        if (act.get("from_inventory_id")):
                            if (int(act["from_inventory_id"]) == id):
                                if (act.get("from_qty_unit")):
                                    unit = act["from_qty_unit"]
                                    qty = act["from_qty"]

                                    if (stats.get(unit)):
                                        stats[unit] = stats[unit] - qty

                        if (activity["name"] == "inventory_adjustment"):
                            adj_unit = act["unit"]
                            adj_qty = float(act["quantity"])

                            if (stats):
                                if (stats.get(adj_unit) and float(stats.get(adj_unit)) < 0 or adj_qty < 0):
                                    print("[ERROR] NEGATIVE VALUE - id: ", id, " act.id: ", activity["id"])
                                if (stats.get(adj_unit) and float(stats.get(adj_unit)) != adj_qty):
                                    print("[ERROR] CALCULATION INVENTORY ADJUSTMENT - id: ", id, " act.id: ", activity["id"])
                if (inv_stats != {}  and (stats.get(inv_stats["unit"]) != inv_stats["qty"])):
                    print("[ERROR] COMPARING STATS WITH INVENTORY ADJUSMENT - id: ", id )

if __name__ == "__main__":   
    print('executing ')
    checkData = CheckDataInconsistencies()

    inv_ids = checkData.get_inventories('01','09', '2021')

    checkData.execute_checking(inv_ids)
    


    

    
    

    
    