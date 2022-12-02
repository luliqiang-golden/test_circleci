"""adds permission to the system

Revision ID: 89515362c3ef
Revises: fca9e519fa05
Create Date: 2022-05-05 12:26:56.224287

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '89515362c3ef'
down_revision = 'fca9e519fa05'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
        """
        CREATE TABLE public."role" (
	id bigserial NOT NULL,
	organization_id int4 NOT NULL,
	created_by int4 NOT NULL,
	"timestamp" timestamptz NOT NULL DEFAULT now(),
	"name" varchar NOT NULL,
	"role_description" varchar NULL,
	UNIQUE(organization_id, "name"),
	CONSTRAINT roles_pkey PRIMARY KEY (id)
);

CREATE TYPE resource_types AS ENUM ('group', 'subgroup', 'action', 'tab');

CREATE TABLE public."permission" (
	id bigserial NOT NULL,
	"timestamp" timestamptz NOT NULL DEFAULT now(),
	"name" varchar NOT NULL,
	"resource_type" resource_types NOT NULL,
	component_friendly_name varchar NOT NULL,
	"parent_id" bigint NULL,
	UNIQUE("name"),
	CONSTRAINT permissions_pkey PRIMARY KEY (id)
);




CREATE TABLE public."user_role" (
	id bigserial NOT NULL,
	user_id bigint NOT NULL,
	role_id bigint NOT NULL,
	CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
	CONSTRAINT fk_role FOREIGN KEY (role_id) REFERENCES role(id) ON DELETE CASCADE
);

CREATE TABLE public.role_permission (
	id bigserial NOT NULL,
	role_id bigint NOT NULL,
	permission_id bigint NOT NULL,
	CONSTRAINT fk_role FOREIGN KEY (role_id) REFERENCES role(id) ON DELETE CASCADE,
	CONSTRAINT fk_permission FOREIGN KEY (permission_id) REFERENCES permission(id) ON DELETE CASCADE
);

CREATE TABLE public.user_role_history (
	id bigserial NOT NULL,
	created_by int4 NOT NULL,
	organization_id int4 NOT NULL,
	"timestamp" timestamptz NOT NULL DEFAULT now(),
	user_id int4 NOT NULL,
	"action" varchar NOT NULL,
	"old_role" int4,
	"new_role" int4
);

CREATE TABLE public.permission_role_history (
	id bigserial NOT NULL,
	created_by int4 NOT NULL,
	organization_id int4 NOT NULL,
	"timestamp" timestamptz NOT NULL DEFAULT now(),
	role_id int4 NOT NULL,
	"action" varchar NOT NULL,
	"old_permissions" jsonb,
	"new_permissions" jsonb
);






GRANT ALL ON TABLE public."role" TO api_server;
GRANT ALL ON TABLE public."role" TO dev_users;
GRANT ALL ON TABLE public."role" TO postgres;

GRANT ALL ON TABLE public."permission" TO api_server;
GRANT ALL ON TABLE public."permission" TO dev_users;
GRANT ALL ON TABLE public."permission" TO postgres;

GRANT ALL ON TABLE public."user_role" TO api_server;
GRANT ALL ON TABLE public."user_role" TO dev_users;
GRANT ALL ON TABLE public."user_role" TO postgres;

GRANT ALL ON TABLE public.role_permission TO api_server;
GRANT ALL ON TABLE public.role_permission TO dev_users;
GRANT ALL ON TABLE public.role_permission TO postgres;

GRANT ALL ON TABLE public.user_role_history TO api_server;
GRANT ALL ON TABLE public.user_role_history TO dev_users;
GRANT ALL ON TABLE public.user_role_history TO postgres;

GRANT ALL ON TABLE public.permission_role_history TO api_server;
GRANT ALL ON TABLE public.permission_role_history TO dev_users;
GRANT ALL ON TABLE public.permission_role_history TO postgres;




INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name, parent_id)
VALUES(1, '2022-04-29 11:21:59.905', 'greenhouse_access', 'group'::public.resource_types, 'Greenhouse', NULL);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(2, '2022-04-29 11:21:59.905', 'crm_access', 'group'::public.resource_types, 'CRM', NULL);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(3, '2022-04-29 11:21:59.905', 'warehouse_access', 'group'::public.resource_types, 'Warehouse', NULL);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(4, '2022-04-29 11:21:59.905', 'qa_access', 'group'::public.resource_types, 'QA', NULL);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(5, '2022-04-29 11:21:59.905', 'accounting_access', 'group'::public.resource_types, 'Accounting', NULL);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(6, '2022-04-29 11:21:59.905', 'documents_access', 'group'::public.resource_types, 'Documents', NULL);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(7, '2022-04-29 11:21:59.905', 'administration_access', 'group'::public.resource_types, 'Administration', NULL);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(8, '2022-04-29 12:07:37.099', 'greenhouse_batches_access', 'subgroup'::public.resource_types, 'Batches', 1);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(9, '2022-04-29 12:07:37.099', 'greenhouse_mothers_access', 'subgroup'::public.resource_types, 'Mothers', 1);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(10, '2022-04-29 12:07:37.099', 'crm_accounts_access', 'subgroup'::public.resource_types, 'Accounts', 2);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(11, '2022-04-29 12:07:37.099', 'crm_orders_access', 'subgroup'::public.resource_types, 'Orders', 2);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(12, '2022-04-29 12:07:37.099', 'crm_shipments_access', 'subgroup'::public.resource_types, 'Shipments', 2);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(13, '2022-04-29 12:07:37.099', 'warehouse_received_inventory_access', 'subgroup'::public.resource_types, 'Received Inventory', 3);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(14, '2022-04-29 12:07:37.099', 'warehouse_lots_access', 'subgroup'::public.resource_types, 'Lots', 3);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(15, '2022-04-29 12:07:37.099', 'warehouse_lot_items_access', 'subgroup'::public.resource_types, 'Lot Items', 3);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(16, '2022-04-29 12:07:37.099', 'warehouse_supplies_access', 'subgroup'::public.resource_types, 'Supplies', 3);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(17, '2022-04-29 12:07:37.099', 'qa_activity_log_access', 'subgroup'::public.resource_types, 'Activity Log', 4);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(18, '2022-04-29 12:07:37.099', 'qa_samples_access', 'subgroup'::public.resource_types, 'Samples', 4);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(19, '2022-04-29 12:07:37.099', 'qa_outstanding_testing_needs_access', 'subgroup'::public.resource_types, 'Outstanding Testing Needs', 4);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(20, '2022-04-29 12:07:37.099', 'qa_destruction_queue_access', 'subgroup'::public.resource_types, 'Destruction Queue', 4);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(21, '2022-04-29 12:07:37.099', 'qa_destruction_reports_access', 'subgroup'::public.resource_types, 'Destruction Reports', 4);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(22, '2022-04-29 12:07:37.099', 'qa_destruction_history_access', 'subgroup'::public.resource_types, 'Destruction History', 4);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(23, '2022-04-29 12:07:37.099', 'qa_reports_access', 'subgroup'::public.resource_types, 'Reports', 4);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(24, '2022-04-29 12:07:37.099', 'qa_recalls_access', 'subgroup'::public.resource_types, 'Recalls', 4);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(25, '2022-04-29 12:07:37.099', 'qa_capas_access', 'subgroup'::public.resource_types, 'Capas', 4);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(26, '2022-04-29 12:07:37.099', 'qa_deviation_reports_access', 'subgroup'::public.resource_types, 'Deviation Reports', 4);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(27, '2022-04-29 12:07:37.099', 'qa_data_changes_access', 'subgroup'::public.resource_types, 'Data Changes', 4);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(28, '2022-04-29 12:07:37.099', 'qa_sanitation_activities_access', 'subgroup'::public.resource_types, 'Sanitation Activities', 4);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(29, '2022-04-29 12:07:37.099', 'accounting_transactions_access', 'subgroup'::public.resource_types, 'Transactions', 5);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(30, '2022-04-29 12:07:37.099', 'accounting_customer_invoices_access', 'subgroup'::public.resource_types, 'Customer Invoices', 5);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(31, '2022-04-29 12:07:37.099', 'documents_sop_training_access', 'subgroup'::public.resource_types, 'SOP Training', 6);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(32, '2022-04-29 12:07:37.099', 'documents_business_operations_access', 'subgroup'::public.resource_types, 'Business Operations', 6);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(33, '2022-04-29 12:07:37.099', 'administration_users_access', 'subgroup'::public.resource_types, 'Users', 7);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(34, '2022-04-29 12:07:37.099', 'administration_departments_access', 'subgroup'::public.resource_types, 'Departments', 7);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(35, '2022-04-29 12:07:37.099', 'administration_user_roles_access', 'subgroup'::public.resource_types, 'User Roles', 7);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(36, '2022-04-29 12:07:37.099', 'administration_rooms_access', 'subgroup'::public.resource_types, 'Rooms', 7);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(37, '2022-04-29 12:07:37.099', 'administration_skus_access', 'subgroup'::public.resource_types, 'SKUs', 7);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(38, '2022-04-29 12:07:37.099', 'administration_destruction_methods_access', 'subgroup'::public.resource_types, 'Destruction Methods', 7);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(39, '2022-04-29 12:07:37.099', 'administration_waste_types_access', 'subgroup'::public.resource_types, 'Waste Types', 7);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(40, '2022-04-29 12:07:37.099', 'administration_destruction_reasons_access', 'subgroup'::public.resource_types, 'Destruction Reasons', 7);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(41, '2022-04-29 12:07:37.099', 'administration_equipment_access', 'subgroup'::public.resource_types, 'Equipment', 7);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(42, '2022-04-29 12:07:37.099', 'administration_labels_access', 'subgroup'::public.resource_types, 'Labels', 7);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(43, '2022-04-29 12:07:37.099', 'administration_compost_types_access', 'subgroup'::public.resource_types, 'Compost Types', 7);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(44, '2022-04-29 12:07:37.099', 'administration_pest_types_access', 'subgroup'::public.resource_types, 'Pest Types', 7);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(45, '2022-04-29 12:07:37.099', 'administration_varieties_access', 'subgroup'::public.resource_types, 'Varieties', 7);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(46, '2022-04-29 12:07:37.099', 'administration_organization_settings_access', 'subgroup'::public.resource_types, 'Organization Settings', 7);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(47, '2022-04-29 12:07:37.099', 'administration_thresholds_access', 'subgroup'::public.resource_types, 'Thresholds', 7);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(48, '2022-04-29 12:07:37.099', 'administration_supply_types_access', 'subgroup'::public.resource_types, 'Supply Types', 7);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(49, '2022-04-29 12:07:37.099', 'administration_sanitation_activity_names_access', 'subgroup'::public.resource_types, 'Sanitation Activity Names', 7);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(50, '2022-04-29 12:07:37.099', 'administration_notifications_access', 'subgroup'::public.resource_types, 'Notifications', 7);
INSERT INTO public."permission"
(id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
VALUES(51, '2022-04-29 12:07:37.099', 'administration_data_changes_access', 'subgroup'::public.resource_types, 'Data Changes', 7);










INSERT INTO public."role" (organization_id, created_by, "name", role_description)
SELECT id, 1, 'Admin', 'This role provides access to everything in the system' FROM organizations;

INSERT INTO public."role" (organization_id, created_by, "name")
SELECT id, 1, 'Cultivation' FROM organizations;

INSERT INTO public."role" (organization_id, created_by, "name")
SELECT id, 1, 'QA' FROM organizations;

INSERT INTO public."role" (organization_id, created_by, "name")
SELECT id, 1, 'Inventory Manager' FROM organizations;

INSERT INTO public."role" (organization_id, created_by, "name")
SELECT id, 1, 'Accounting' FROM organizations;















do $$
declare
    row_ record;
begin 
for row_ in (SELECT id FROM public."role" WHERE name = 'Admin') loop



INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 1);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 2);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 3);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 4);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 5);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 6);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 7);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 8);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 9);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 10);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 11);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 12);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 13);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 14);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 15);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 16);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 17);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 18);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 19);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 20);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 21);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 22);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 23);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 24);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 25);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 26);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 27);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 28);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 29);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 30);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 31);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 32);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 33);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 34);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 35);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 36);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 37);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 38);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 39);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 40);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 41);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 42);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 43);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 44);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 45);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 46);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 47);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 48);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 49);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 50);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 51);


end loop;
end;
$$;













do $$
declare
    row_ record;
begin 
for row_ in (SELECT id FROM public."role" WHERE name = 'Cultivation') loop


INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 1);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 3);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 6);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 8);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 9);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 13);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 14);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 15);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 16);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 31);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 32);

end loop;
end;
$$;





























do $$
declare
    row_ record;
begin 
for row_ in (SELECT id FROM public."role" WHERE name = 'QA') loop



INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 1);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 3);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 4);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 6);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 8);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 9);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 13);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 14);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 15);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 16);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 17);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 18);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 19);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 20);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 21);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 22);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 23);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 24);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 25);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 26);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 27);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 28);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 31);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 32);


end loop;
end;
$$;





















do $$
declare
    row_ record;
begin 
for row_ in (SELECT id FROM public."role" WHERE name = 'Inventory Manager') loop


INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 3);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 6);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 13);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 14);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 15);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 16);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 31);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 32);


end loop;
end;
$$;



















do $$
declare
    row_ record;
begin 
for row_ in (SELECT id FROM public."role" WHERE name = 'Accounting') loop



INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 1);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 2);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 5);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 6);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 8);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 9);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 10);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 11);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 12);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 29);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 30);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 31);
INSERT INTO public.role_permission
(role_id, permission_id)
VALUES(row_.id, 32);


end loop;
end;
$$;








do $$
declare
    row_ record;
begin 
for row_ in (SELECT id FROM organizations) loop

INSERT INTO user_role (user_id, role_id)
SELECT id, (SELECT id FROM public."role" WHERE organization_id = row_.id and name = 'Admin') FROM users WHERE organization_id = row_.id;

end loop;
end;
$$;



        """)


def downgrade():
    connection = op.get_bind()
    connection.execute(
        """
        DROP TABLE role_permission;
        DROP TABLE user_role;
        DROP TABLE permission_role_history;
        DROP TABLE user_role_history;
        DROP TABLE "role";
        DROP TABLE "permission";
        DROP TYPE resource_types;
        """)
