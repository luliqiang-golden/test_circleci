import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))


from abc import ABC,abstractmethod
from class_errors import EngineError
import db_functions
import json 

class Stats: 
    
    __instance = None

    def __init__(self, org_id):
        """
            Constructor method
        """
        param = {"org_id": org_id}

        query = """
            select  name, 
                    data->>'type' as type, 
                    data->>'parent' as parent, 
                    data->>'stages' as stages, 
                    data->>'subtype' as subtype, 
                    data->>'friendlyName' as friendly_name,
		            data->>'metricMass' as metric_mass,
		            data->>'activity' as activity
            from taxonomy_options
            where taxonomy_id = (select id from taxonomies where name = 'stats' and organization_id = %(org_id)s) 
            order by id;
        """
        self.org_id = org_id

        self.__statsObjectList = db_functions.select_from_db(query, param)

    
    # this class is singleton
    @staticmethod
    def get_instance(org) -> 'Stats':
        if (not Stats.__instance):
            Stats.__instance = Stats(org)

        return Stats.__instance


    def get_stats_object_by_name(self, name):
        stats = list(filter(lambda stats: stats["name"] == name, self.__statsObjectList))

        if (stats):
            return stats[0]

    def get_stats_object_list_by_type(self, statsType):
        stats = list(filter(lambda stats: stats["type"] == statsType, self.__statsObjectList))

        if (stats):
            return stats


    @staticmethod
    def serialize_stats(stats):
        return Stats.__get_serialized_stats(stats)


    def deserialize_stats(self, unit, quantity):
        
        parent = self.get_stats_object_by_name(unit).get('parent')
        
        if parent:
            return {
                parent: {
                    unit: quantity
                }
            }
        else:
            return {
                    unit: quantity
                }


    @staticmethod
    def __get_serialized_stats(stats, mesurement = None): 
        for key in stats.keys():
            stats_value = stats[key]
            if (type(stats_value) is dict):
                stats_value = Stats.__get_serialized_stats(stats_value, key)
                if (stats_value):
                    return stats_value
                
         
            if (stats_value):
                metric_mass = None
                type_stats = None
                # if g-extracts then it will get metric_mass = g and type = extracts 
                if (mesurement):
                    [metric_mass, type_stats] = mesurement.split('-')
                else:
                    #  if it's g-wet - mc=g and t=wet
                    if ("-" in key):
                        [metric_mass, type_stats] = key.split('-')
                    else:
                        metric_mass = key


                    # [metricMass, type_stats] = key.split('-')
                #  if plants, for instance, then mc=plants and t=undefined, so i need to invert it to mc=undefined and t=plants
                if ( not type_stats):
                    type_stats = metric_mass
                    metric_mass = None
            
                return { "unit": key, "qty": stats_value, "metric_mass": metric_mass, "type": type_stats }
          
        return None


if __name__ == "__main__":
    obj = [ {"id": 1, "stats": {
                'plants': 0,
                'g-dry': {'dry': 0, 'cured': 0},
                'g-wet': 0,
                'g-extracts': {'bubbleHash': 0, 'hash': 10, 'biomass': 0}}},

         {"id": 2, "stats": {
                'plants': 0,
                'g-dry': {'dry': 10, 'cured': 0},
                'g-wet': 0,
                'g-extracts': {'bubbleHash': 0, 'hash': 10, 'biomass': 0}}},
         {"id": 2, "stats": {
                'plants': 0,
                'g-dry': {'dry': 0, 'cured': 50},
                'g-wet': 0,
                'g-extracts': {'bubbleHash': 0, 'hash': 10, 'biomass': 0}}},
         
         {"id": 3, "stats": {
                'plants': 0,
                'g-dry': {'dry': 0, 'cured': 0},
                'g-wet': 0,
                'g-extracts': {'bubbleHash': 0, 'hash': 10, 'biomass': 0}}},

        {"id": 3, "stats": {
                'plants': 0,
                'g-dry': {'dry': 0, 'cured': 0},
                'g-wet': 10,
                'g-extracts': {'bubbleHash': 0, 'hash': 10, 'biomass': 0}}},
         {"id": 3, "stats": {
                'plants': 0,
                'g-dry': {'dry': 0, 'cured': 0},
                'g-wet': 40,
                'g-extracts': {'bubbleHash': 0, 'hash': 10, 'biomass': 0}}}



      ]
    stats = Stats(1)




      