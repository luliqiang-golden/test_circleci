'''This module contains serializer schema used for rooms API'''

from marshmallow import Schema, fields, pre_dump

def partition(items, container_name):
    seen = []
    
    return [ 
        {
            'zone': i['zone'],
            container_name: [item for item in items if item['zone'] == i['zone']],
        }
        for i in reversed(items) if i['zone'] not in seen and not seen.append(i['zone'])
    ]

class RoomsSchema(Schema):
    class Meta:
        fields = (
            'id',
            'name'
        )

class RoomsPerSectionSchemaGetResponse(Schema):

    rooms = fields.Nested(RoomsSchema, many=True)
    class Meta:
        fields = (
            'zone',
            'rooms'
        )

    @pre_dump(pass_many=True)
    def partition_rooms(self, data, many):
        return partition(data, 'rooms')