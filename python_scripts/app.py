import sentry_sdk
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from api_encoder import CustomJSONEncoder

from settings import Settings
from sentry_sdk.integrations.flask import FlaskIntegration

if  Settings.get_setting('FLASK_ENV', None) != 'development':
    sentry_sdk.init(
        dsn="https://f427cdc1f2754a259d70c8269765ee12@o349937.ingest.sentry.io/5932985",
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0
    )


app = Flask(__name__)  # pylint: disable=C0103
CORS(app)

app.json_encoder = CustomJSONEncoder
app.config['RESTFUL_JSON'] = {'cls': app.json_encoder}

DB_HOST = Settings.get_setting("DB_HOST", 'localhost')
DB_HOST_APP_ENGINE = Settings.get_setting("DB_HOST_APP_ENGINE", DB_HOST) # 172.17.0.1
DB_USERNAME = Settings.get_setting("DB_USERNAME", 'postgres')
DB = Settings.get_setting("DB")
DB_PASSWORD = Settings.get_setting("DB_PASSWORD", 'password')

sql_url = "postgresql://{0}:{1}@{2}/{3}".format(DB_USERNAME, DB_PASSWORD, DB_HOST_APP_ENGINE, DB)

app.config['SQLALCHEMY_DATABASE_URI'] = sql_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from controllers.batches_controller import batches_bp, harvest_whole_plant_bp, harvest_multiple_bp, merge_harvest_multiple_bp, weight_adjustment_bp, room_batches_bp
from reporting import reporting_bp
from controllers.currency import currency_bp
from controllers.lots import lots_bp
from controllers.order_items import order_items_bp
from controllers.sensor import sensor_bp
from controllers.lot_items import lot_item_bp
from controllers.consumable_lots import consumable_lots_bp
from controllers.skus import skus_bp
from controllers.role import role_bp
from controllers.role_permission import role_permission_bp
from controllers.user_role import user_role_bp
from controllers.user_role_history import user_role_history_bp
from controllers.role_permission_history import role_permission_history_bp
from controllers.permission import permission_bp
from controllers.activities.create_activity_log import create_activity_log_bp
from controllers.activities_history import activities_history_bp
from controllers.activities_mapping import activities_mapping_bp, activities_mapping_weight_adjustment_bp
from controllers.activities.revert_destructions import revert_destructions_bp
from controllers.destruction_inventory import destruction_inventory_bp
from controllers.activities.backdate_activity import backdate_activity_bp
from controllers.rooms import rooms_bp
from controllers.external_order_items import external_order_items_bp
from controllers.activities.bulk_activities import bulk_activities_bp
from controllers.notifications import activities_notifications_bp


app.register_blueprint(batches_bp, url_prefix='/v1/organizations/<organization_id>/batches')
app.register_blueprint(harvest_whole_plant_bp, url_prefix='/v1/organizations/<organization_id>/batches')
app.register_blueprint(harvest_multiple_bp, url_prefix='/v1/organizations/<organization_id>/batches')
app.register_blueprint(merge_harvest_multiple_bp, url_prefix='/v1/organizations/<organization_id>/batches')
app.register_blueprint(weight_adjustment_bp, url_prefix='/v1/organizations/<organization_id>/batches')
app.register_blueprint(
   reporting_bp, url_prefix="/v1/organizations/<organization_id>/reporting")
app.register_blueprint(currency_bp,  url_prefix='/v1')
app.register_blueprint(lots_bp, url_prefix="/v1/organizations/<organization_id>")
app.register_blueprint(order_items_bp, url_prefix="/v1/organizations/<organization_id>")
app.register_blueprint(sensor_bp, url_prefix="/v1/organizations/<organization_id>")
app.register_blueprint(lot_item_bp, url_prefix="/v1/organizations/<organization_id>")
app.register_blueprint(consumable_lots_bp, url_prefix="/v1/organizations/<organization_id>")
app.register_blueprint(skus_bp, url_prefix="/v1/organizations/<organization_id>")
app.register_blueprint(role_bp, url_prefix="/v1/organizations/<organization_id>")
app.register_blueprint(role_permission_bp, url_prefix="/v1/organizations/<organization_id>")
app.register_blueprint(user_role_bp, url_prefix="/v1/organizations/<organization_id>")
app.register_blueprint(user_role_history_bp, url_prefix="/v1/organizations/<organization_id>")
app.register_blueprint(role_permission_history_bp, url_prefix="/v1/organizations/<organization_id>")
app.register_blueprint(permission_bp, url_prefix="/v1/organizations/<organization_id>")
app.register_blueprint(create_activity_log_bp, url_prefix="/v1/organizations/<organization_id>/activity")
app.register_blueprint(activities_history_bp, url_prefix="/v1/organizations/<organization_id>/")
app.register_blueprint(activities_mapping_bp, url_prefix="/v1/organizations/<organization_id>/")
app.register_blueprint(activities_mapping_weight_adjustment_bp, url_prefix="/v1/organizations/<organization_id>/")
app.register_blueprint(revert_destructions_bp, url_prefix="/v1/organizations/<organization_id>/")
app.register_blueprint(destruction_inventory_bp, url_prefix="/v1/organizations/<organization_id>/")
app.register_blueprint(backdate_activity_bp, url_prefix="/v1/organizations/<organization_id>/")
app.register_blueprint(rooms_bp, url_prefix="/v1/organizations/<organization_id>/")
app.register_blueprint(room_batches_bp, url_prefix="/v1/organizations/<organization_id>/")
app.register_blueprint(external_order_items_bp, url_prefix="/v1/organizations/<organization_id>/")
app.register_blueprint(bulk_activities_bp, url_prefix="/v1/organizations/<organization_id>/")
app.register_blueprint(activities_notifications_bp, url_prefix="/v1/organizations/<organization_id>/")
