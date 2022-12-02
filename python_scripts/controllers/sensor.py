from flask import request, Blueprint, jsonify
from sqlalchemy import desc
from auth0_authentication import requires_auth
from models.equipment import Equipment
from serializer.sensor import SensorSchema
from models.sensor import SensorData
from controllers import BaseController
from app import db
from class_errors import ClientBadRequest


sensor_schema = SensorSchema()


class SensorCollection(BaseController):
    
    @requires_auth
    def post(self, current_user, organization_id):
        data = self.serialize(sensor_schema, request.get_json())
        equipment = Equipment.query.get(data.get('sensor_id'))
        if equipment and equipment.default_unit_type:   
            sensor_reading = SensorData().get_converted_unit_type_value(
                data.get('unit_type'),
                default_unit_type=equipment.default_unit_type,
                value=float(data.get("sensor_reading"))
            )
            sensor_data = SensorData(
                organization_id = organization_id,
                created_by = current_user.get("user_id"),
                sensor_reading = sensor_reading,
                sensor_id = data.get('sensor_id'),
                sensor_type = data.get('sensor_type'),
                reading_timestamp = data.get('reading_timestamp'),
                data = {'unit_type': data.get('unit_type')},
            )
            db.session.add(sensor_data)
            db.session.commit()
            return jsonify({"message":"success", "sensor_data_id":sensor_data.id}), 200
        raise ClientBadRequest({"message": f"No record found for sensor_id #{data.get('sensor_id')}"}, 404)

    @requires_auth
    def get(self, current_user, organization_id):
        sensor_id = request.args.get('sensor_id', type=int)
        page = request.args.get('page', type=int)
        per_page = request.args.get("per_page", type=int)
        if sensor_id:            
            base_query = SensorData.query.filter(SensorData.organization_id==organization_id, SensorData.sensor_id == sensor_id).order_by(desc('id'))
        else:
            base_query = SensorData.query.filter(SensorData.organization_id==organization_id).order_by(desc('id'))
        if page and per_page:
            pagination = True
            query = base_query.paginate(page, per_page, False)
            queryset = query.items
        else:
            pagination = False
            query = None
            queryset = base_query.all()
        data = SensorData().deserialize_sensor_queryset(queryset)
        return self.get_success_response(data, query, pagination)


class SensorResource(BaseController):
    
    @requires_auth
    def get(self, current_user, organization_id, sensor_id):
        obj = SensorData.query.get(sensor_id)
        data = SensorData().deserialize_sensor_object(obj)
        return self.get_success_response(data)


# Make blueprint for sensor API
sensor_bp = Blueprint('sensor_bp', __name__)

# Define url_patterns related to sensor API here
sensors = SensorCollection.as_view('sensors')
sensor_bp.add_url_rule('/sensors', view_func=sensors, methods=['POST','GET'])

sensor = SensorResource.as_view('sensor')
sensor_bp.add_url_rule('/sensors/<sensor_id>', view_func=sensor, methods=['GET'])

