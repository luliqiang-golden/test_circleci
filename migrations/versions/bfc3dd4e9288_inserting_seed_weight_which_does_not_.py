"""inserting seed weight which does not have it

Revision ID: bfc3dd4e9288
Revises: a0258cf85b16
Create Date: 2021-12-14 19:50:05.198058

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bfc3dd4e9288'
down_revision = 'a0258cf85b16'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute("""
    UPDATE inventories inv_update
    SET attributes = jsonb_set(attributes, '{alembic_revision}', to_jsonb('bfc3dd4e9288'::text), true)
    FROM (
    		select 
                ROUND(COALESCE(AVG(T1.seed_weight),0),3) as seed_weight,
                t1.batch_id
            from (
                select 
                    CAST(inv_received.data->>'seed_weight' as decimal) as seed_weight,
                    act.data->>'to_inventory_id' as batch_id
                from inventories as inv_batch 
                    inner join activities as act on act.name = 'transfer_inventory' and act.data->>'to_inventory_id' = cast(inv_batch.id as varchar) and act.organization_id = inv_batch.organization_id 
                    inner join inventories as inv_received on cast(inv_received.id as varchar) = act.data->>'from_inventory_id' and inv_received.organization_id = inv_batch.organization_id
                where inv_batch.type = 'batch'      
                	and inv_received.stats->>'seeds' is not null
                	and inv_batch.attributes->>'seed_weight' is null
                group by inv_received.id, act.id
            ) as T1
            group by t1.batch_id
    ) AS subquery
    WHERE inv_update.type = 'batch' and cast(subquery.batch_id as numeric) = inv_update.id;

    UPDATE inventories inv_update
    SET attributes = jsonb_set(attributes, '{seed_weight}', to_jsonb(subquery.seed_weight), true)
    FROM (
    		select 
                ROUND(COALESCE(AVG(T1.seed_weight),0),3) as seed_weight,
                t1.batch_id
            from (
                select 
                    CAST(inv_received.data->>'seed_weight' as decimal) as seed_weight,
                    act.data->>'to_inventory_id' as batch_id
                from inventories as inv_batch 
                    inner join activities as act on act.name = 'transfer_inventory' and act.data->>'to_inventory_id' = cast(inv_batch.id as varchar) and act.organization_id = inv_batch.organization_id 
                    inner join inventories as inv_received on cast(inv_received.id as varchar) = act.data->>'from_inventory_id' and inv_received.organization_id = inv_batch.organization_id
                where inv_batch.type = 'batch'      
                	and inv_received.stats->>'seeds' is not null
                	and inv_batch.attributes->>'seed_weight' is null
                group by inv_received.id, act.id
            ) as T1
            group by t1.batch_id
    ) AS subquery
    WHERE inv_update.type = 'batch' and cast(subquery.batch_id as numeric) = inv_update.id;
    
    """)


def downgrade():
    connection = op.get_bind()
    connection.execute("""
    UPDATE inventories inv_update
    SET attributes = attributes - 'seed_weight'
    WHERE attributes->>'alembic_revision' = 'bfc3dd4e9288';

    UPDATE inventories inv_update
    SET attributes = attributes - 'alembic_revision'
    WHERE attributes->>'alembic_revision' = 'bfc3dd4e9288';
    
    """)
