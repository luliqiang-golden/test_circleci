"""new-end-types-hcr-received-inventory

Revision ID: cc3ff5b23164
Revises: 6e3e38537d4c
Create Date: 2021-06-15 09:24:01.437900

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cc3ff5b23164'
down_revision = '6e3e38537d4c'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
        """
            CREATE OR REPLACE FUNCTION public.f_hc_report_received_inventory(report_id integer, initial_date character varying, final_date character varying, org_id integer)
             RETURNS void
             LANGUAGE plpgsql
            AS $function$
            BEGIN		
                --received inventories
                UPDATE health_canada_report
                SET	
                    --unpackaged domestic
                    unpackaged_seed_received_domestic = COALESCE(T3.unpackaged_seed_received_domestic ,0)/1000,
                    unpackaged_vegetative_plants_received_domestic = COALESCE(T3.unpackaged_vegetative_plants_received_domestic,0),
                    unpackaged_fresh_cannabis_received_domestic = COALESCE(T3.unpackaged_fresh_cannabis_received_domestic ,0)/1000,
                    unpackaged_dried_cannabis_received_domestic = COALESCE(T3.unpackaged_dried_cannabis_received_domestic ,0)/1000,
                    unpackaged_extracts_received_domestic = COALESCE(T3.unpackaged_extracts_received_domestic ,0)/1000,
                    
                    unpackaged_extracts_inhaled_received_domestic = COALESCE(T3.unpackaged_extracts_inhaled_received_domestic ,0)/1000,
                    unpackaged_extracts_ingested_received_domestic = COALESCE(T3.unpackaged_extracts_ingested_received_domestic,0)/1000,
                    unpackaged_extracts_other_received_domestic = COALESCE(T3.unpackaged_extracts_other_received_domestic ,0)/1000,
                    unpackaged_edibles_solid_received_domestic = COALESCE(T3.unpackaged_edibles_solid_received_domestic ,0)/1000,
                    unpackaged_edibles_nonsolid_received_domestic = COALESCE(T3.unpackaged_edibles_nonsolid_received_domestic ,0)/1000,
                    unpackaged_topicals_received_domestic = COALESCE(T3.unpackaged_topicals_received_domestic ,0)/1000,
                    
                    --unpackaged imported		
                    unpackaged_seed_received_imported = COALESCE(T3.unpackaged_seed_received_imported ,0)/1000,
                    unpackaged_vegetative_plants_received_imported = COALESCE(T3.unpackaged_vegetative_plants_received_imported,0),
                    unpackaged_fresh_cannabis_received_imported = COALESCE(T3.unpackaged_fresh_cannabis_received_imported ,0)/1000,
                    unpackaged_dried_cannabis_received_imported = COALESCE(T3.unpackaged_dried_cannabis_received_imported ,0)/1000,
                    unpackaged_extracts_received_imported = COALESCE(T3.unpackaged_extracts_received_imported ,0)/1000,
                    
                    unpackaged_extracts_inhaled_received_imported = COALESCE(T3.unpackaged_extracts_inhaled_received_imported ,0)/1000,
                    unpackaged_extracts_ingested_received_imported = COALESCE(T3.unpackaged_extracts_ingested_received_imported,0)/1000,
                    unpackaged_extracts_other_received_imported = COALESCE(T3.unpackaged_extracts_other_received_imported ,0)/1000,
                    unpackaged_edibles_solid_received_imported = COALESCE(T3.unpackaged_edibles_solid_received_imported ,0)/1000,
                    unpackaged_edibles_nonsolid_received_imported = COALESCE(T3.unpackaged_edibles_nonsolid_received_imported ,0)/1000,
                    unpackaged_topicals_received_imported = COALESCE(T3.unpackaged_topicals_received_imported ,0)/1000,
                    
                    --packaged domestic
                    packaged_seed_received_domestic = COALESCE(T3.packaged_seed_received_domestic ,0),
                    packaged_vegetative_plants_received_domestic = COALESCE(T3.packaged_vegetative_plants_received_domestic,0),
                    packaged_fresh_cannabis_received_domestic = COALESCE(T3.packaged_fresh_cannabis_received_domestic ,0),
                    packaged_dried_cannabis_received_domestic = COALESCE(T3.packaged_dried_cannabis_received_domestic ,0),
                    packaged_extracts_received_domestic = COALESCE(T3.packaged_extracts_received_domestic ,0),	
                    
                    packaged_extracts_inhaled_received_domestic = COALESCE(T3.packaged_extracts_inhaled_received_domestic ,0),
                    packaged_extracts_ingested_received_domestic = COALESCE(T3.packaged_extracts_ingested_received_domestic,0),
                    packaged_extracts_other_received_domestic = COALESCE(T3.packaged_extracts_other_received_domestic ,0),
                    packaged_edibles_solid_received_domestic = COALESCE(T3.packaged_edibles_solid_received_domestic ,0),
                    packaged_edibles_nonsolid_received_domestic = COALESCE(T3.packaged_edibles_nonsolid_received_domestic ,0),
                    packaged_topicals_received_domestic = COALESCE(T3.packaged_topicals_received_domestic ,0)
                    
                FROM (
                    -- here i do the pivot (rows to column and columns to rows)
                    SELECT 
                        -- unpackage domestic(kg)
                        SUM(COALESCE(T2.seeds_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_seed_received_domestic,
                        SUM(COALESCE(T2.vegetative_plants,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_vegetative_plants_received_domestic,
                        SUM(COALESCE(T2.fresh_cannabis_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_fresh_cannabis_received_domestic,
                        SUM(COALESCE(T2.extracts_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_extracts_received_domestic,
                        SUM(COALESCE(T2.dried_cannabis_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_dried_cannabis_received_domestic,
            
                        SUM(COALESCE(T2.extracts_inhaled_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_extracts_inhaled_received_domestic,
                        SUM(COALESCE(T2.extracts_ingested_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_extracts_ingested_received_domestic,
                        SUM(COALESCE(T2.extracts_other_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_extracts_other_received_domestic,
                        SUM(COALESCE(T2.edibles_solid_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_edibles_solid_received_domestic,
                        SUM(COALESCE(T2.edibles_non_solid_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_edibles_nonsolid_received_domestic,
                        SUM(COALESCE(T2.topicals_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_topicals_received_domestic,
                        
                        -- unpackage imported(kg)
                        SUM(COALESCE(T2.seeds_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_seed_received_imported,
                        SUM(COALESCE(T2.vegetative_plants,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_vegetative_plants_received_imported,
                        SUM(COALESCE(T2.fresh_cannabis_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_fresh_cannabis_received_imported,
                        SUM(COALESCE(T2.extracts_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_extracts_received_imported,
                        SUM(COALESCE(T2.dried_cannabis_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_dried_cannabis_received_imported,
                        
                        SUM(COALESCE(T2.extracts_inhaled_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_extracts_inhaled_received_imported,
                        SUM(COALESCE(T2.extracts_ingested_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_extracts_ingested_received_imported,
                        SUM(COALESCE(T2.extracts_other_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_extracts_other_received_imported,
                        SUM(COALESCE(T2.edibles_solid_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_edibles_solid_received_imported,
                        SUM(COALESCE(T2.edibles_non_solid_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_edibles_nonsolid_received_imported,
                        SUM(COALESCE(T2.topicals_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_topicals_received_imported,
                        
                        -- packaged domestic(#)
                        SUM(COALESCE(T2.packaged_seeds_qty,0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_seed_received_domestic,
                        SUM(COALESCE(T2.packaged_vegetative_plants_qty,0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_vegetative_plants_received_domestic,				
                        SUM(COALESCE(T2.fresh_cannabis_qty, 0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_fresh_cannabis_received_domestic,
                        SUM(COALESCE(T2.dried_cannabis_qty,0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_dried_cannabis_received_domestic,
                        SUM(COALESCE(T2.extracts_qty,0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_extracts_received_domestic,
                        
                        SUM(COALESCE(T2.extracts_inhaled_qty,0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_extracts_inhaled_received_domestic,
                        SUM(COALESCE(T2.extracts_ingested_qty,0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_extracts_ingested_received_domestic,
                        SUM(COALESCE(T2.extracts_other_qty, 0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_extracts_other_received_domestic,
                        SUM(COALESCE(T2.edibles_solid_qty,0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_edibles_solid_received_domestic,
                        SUM(COALESCE(T2.edibles_non_solid_qty, 0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_edibles_nonsolid_received_domestic,
                        SUM(COALESCE(T2.topicals_qty, 0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_topicals_received_domestic
                        
                        FROM (
                        SELECT SUM(COALESCE((f).seeds_weight,0)) AS seeds_weight,
                            SUM(COALESCE((f).packaged_seeds_qty,0)) AS packaged_seeds_qty,
                            SUM(COALESCE((f).vegetative_plants,0)) AS vegetative_plants,
                            SUM(COALESCE((f).packaged_vegetative_plants_qty,0)) AS packaged_vegetative_plants_qty,
                            SUM(COALESCE((f).fresh_cannabis_weight, 0)) AS fresh_cannabis_weight,
                            SUM(COALESCE((f).extracts_weight,0)) AS extracts_weight,
                            SUM(COALESCE((f).dried_cannabis_weight, 0)) AS dried_cannabis_weight,				
                            SUM(COALESCE((f).fresh_cannabis_qty, 0)) AS fresh_cannabis_qty,
                            SUM(COALESCE((f).extracts_qty,0)) AS extracts_qty,
                            SUM(COALESCE((f).dried_cannabis_qty, 0)) AS dried_cannabis_qty,		
                            
                            SUM(COALESCE((f).extracts_inhaled_weight,0)) AS extracts_inhaled_weight,
                            SUM(COALESCE((f).extracts_inhaled_qty, 0)) AS extracts_inhaled_qty,	
                            SUM(COALESCE((f).extracts_ingested_weight,0)) AS extracts_ingested_weight,
                            SUM(COALESCE((f).extracts_ingested_qty, 0)) AS extracts_ingested_qty,	
                            SUM(COALESCE((f).extracts_other_weight,0)) AS extracts_other_weight,
                            SUM(COALESCE((f).extracts_other_qty, 0)) AS extracts_other_qty,	
                            SUM(COALESCE((f).edibles_solid_weight,0)) AS edibles_solid_weight,
                            SUM(COALESCE((f).edibles_solid_qty, 0)) AS edibles_solid_qty,	
                            SUM(COALESCE((f).edibles_non_solid_weight,0)) AS edibles_non_solid_weight,
                            SUM(COALESCE((f).edibles_non_solid_qty, 0)) AS edibles_non_solid_qty,
                            SUM(COALESCE((f).topicals_weight,0)) AS topicals_weight,
                            SUM(COALESCE((f).topicals_qty, 0)) AS topicals_qty,
                            T1.type_shipping,
                            (f).package_type as package_type
                        FROM (
                            SELECT f_serialize_stats_fields(CAST(act.data->>'to_qty' as numeric), inv.latest_unit, null, inv.type, inv.data, inv.attributes, st.data->>'subtype') AS f,
                            (f_serialize_stats_fields(CAST(act.data->>'to_qty' as numeric), inv.latest_unit, null, inv.type, inv.data, inv.attributes, st.data->>'subtype')).fresh_cannabis_weight,
                                    CASE
                                        WHEN crm.data->'residing_address'->>'country' != org.data->'facility_details'->'facilityAddress'->>'country'  THEN 'imported' 
                                        ELSE 'domestic'
                                    END AS type_shipping
                                    
                            --FROM f_inventories_latest_stats_stage('2021-06-30') as inv
                            FROM f_inventories_latest_stats_stage(final_date)  as inv
                                INNER JOIN activities AS act ON act.name = 'receive_inventory' and act.data->>'inventory_id' = CAST(inv.id AS VARCHAR)
                                INNER JOIN crm_accounts AS crm ON CAST(crm.id AS VARCHAR) = act.data->>'vendor_id'
                                INNER JOIN organizations as org on inv.organization_id = org.id
                                inner join stats_taxonomies as st on st.name = inv.latest_unit
                            WHERE type = 'received inventory' AND 
                                --inv.organization_id = 1 and
                                --TO_CHAR(inv.timestamp,'YYYY-MM-DD') BETWEEN '2021-06-01'  AND '2021-06-30'
                                inv.organization_id = org_id AND
                                TO_CHAR(inv.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
                        ) AS T1
                        GROUP BY T1.type_shipping, (f).package_type
                    ) AS T2
                ) AS T3
                WHERE id = report_id;	
                            
            END;$function$
            ;
        """
    )


def downgrade():
    connection = op.get_bind()
    connection.execute(
        """
            CREATE OR REPLACE FUNCTION public.f_hc_report_received_inventory(report_id integer, initial_date character varying, final_date character varying, org_id integer)
             RETURNS void
             LANGUAGE plpgsql
            AS $function$
            BEGIN		
                --received inventories
                UPDATE health_canada_report
                SET	
                    --unpackaged domestic
                    unpackaged_seed_received_domestic = COALESCE(T3.unpackaged_seed_received_domestic ,0)/1000,
                    unpackaged_vegetative_plants_received_domestic = COALESCE(T3.unpackaged_vegetative_plants_received_domestic,0),
                    unpackaged_fresh_cannabis_received_domestic = COALESCE(T3.unpackaged_fresh_cannabis_received_domestic ,0)/1000,
                    unpackaged_dried_cannabis_received_domestic = COALESCE(T3.unpackaged_dried_cannabis_received_domestic ,0)/1000,
                    unpackaged_extracts_received_domestic = COALESCE(T3.unpackaged_extracts_received_domestic ,0)/1000, 		
                    --unpackaged imported		
                    unpackaged_seed_received_imported = COALESCE(T3.unpackaged_seed_received_imported ,0)/1000,
                    unpackaged_vegetative_plants_received_imported = COALESCE(T3.unpackaged_vegetative_plants_received_imported,0),
                    unpackaged_fresh_cannabis_received_imported = COALESCE(T3.unpackaged_fresh_cannabis_received_imported ,0)/1000,
                    unpackaged_dried_cannabis_received_imported = COALESCE(T3.unpackaged_dried_cannabis_received_imported ,0)/1000,
                    unpackaged_extracts_received_imported = COALESCE(T3.unpackaged_extracts_received_imported ,0)/1000,
                    --packaged domestic
                    packaged_seed_received_domestic = COALESCE(T3.packaged_seed_received_domestic ,0),
                    packaged_vegetative_plants_received_domestic = COALESCE(T3.packaged_vegetative_plants_received_domestic,0),
                    packaged_fresh_cannabis_received_domestic = COALESCE(T3.packaged_fresh_cannabis_received_domestic ,0),
                    packaged_dried_cannabis_received_domestic = COALESCE(T3.packaged_dried_cannabis_received_domestic ,0),
                    packaged_extracts_received_domestic = COALESCE(T3.packaged_extracts_received_domestic ,0)	
                    
                FROM (
                    -- here i do the pivot (rows to column and columns to rows)
                    SELECT 
                        -- unpackage domestic(kg)
                        SUM(COALESCE(T2.seeds_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_seed_received_domestic,
                        SUM(COALESCE(T2.vegetative_plants,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_vegetative_plants_received_domestic,
                        SUM(COALESCE(T2.fresh_cannabis_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_fresh_cannabis_received_domestic,
                        SUM(COALESCE(T2.extracts_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_extracts_received_domestic,
                        SUM(COALESCE(T2.dried_cannabis_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_dried_cannabis_received_domestic,
                        -- unpackage imported(kg)
                        SUM(COALESCE(T2.seeds_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_seed_received_imported,
                        SUM(COALESCE(T2.vegetative_plants,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_vegetative_plants_received_imported,
                        SUM(COALESCE(T2.fresh_cannabis_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_fresh_cannabis_received_imported,
                        SUM(COALESCE(T2.extracts_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_extracts_received_imported,
                        SUM(COALESCE(T2.dried_cannabis_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_dried_cannabis_received_imported,
                        -- packaged domestic(#)
                        SUM(COALESCE(T2.packaged_seeds_qty,0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_seed_received_domestic,
                        SUM(COALESCE(T2.packaged_vegetative_plants_qty,0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_vegetative_plants_received_domestic,				
                        SUM(COALESCE(T2.fresh_cannabis_qty, 0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_fresh_cannabis_received_domestic,
                        SUM(COALESCE(T2.dried_cannabis_qty,0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_dried_cannabis_received_domestic,
                        SUM(COALESCE(T2.extracts_qty,0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_extracts_received_domestic
                        FROM (
                        SELECT SUM(COALESCE((f).seeds_weight,0)) AS seeds_weight,
                            SUM(COALESCE((f).packaged_seeds_qty,0)) AS packaged_seeds_qty,
                            SUM(COALESCE((f).vegetative_plants,0)) AS vegetative_plants,
                            SUM(COALESCE((f).packaged_vegetative_plants_qty,0)) AS packaged_vegetative_plants_qty,
                            SUM(COALESCE((f).fresh_cannabis_weight, 0)) AS fresh_cannabis_weight,
                            SUM(COALESCE((f).extracts_weight,0)) AS extracts_weight,
                            SUM(COALESCE((f).dried_cannabis_weight, 0)) AS dried_cannabis_weight,				
                            SUM(COALESCE((f).fresh_cannabis_qty, 0)) AS fresh_cannabis_qty,
                            SUM(COALESCE((f).extracts_qty,0)) AS extracts_qty,
                            SUM(COALESCE((f).dried_cannabis_qty, 0)) AS dried_cannabis_qty,				
                            T1.type_shipping,
                            (f).package_type as package_type
                        FROM (
                            SELECT f_serialize_stats_fields(CAST(act.data->>'to_qty' as numeric), inv.latest_unit, null, inv.type, inv.data, inv.attributes) AS f,
                                    CASE
                                        WHEN crm.data->'residing_address'->>'country' != org.data->'facility_details'->'facilityAddress'->>'country'  THEN 'imported' 
                                        ELSE 'domestic'
                                    END AS type_shipping
                                    
                            --FROM f_inventories_latest_stats_stage('2020-05-31') as inv
                            FROM f_inventories_latest_stats_stage(final_date)  as inv
                                INNER JOIN activities AS act ON act.name = 'receive_inventory' and act.data->>'inventory_id' = CAST(inv.id AS VARCHAR)
                                INNER JOIN crm_accounts AS crm ON CAST(crm.id AS VARCHAR) = act.data->>'vendor_id'
                                INNER JOIN organizations as org on inv.organization_id = org.id
                            WHERE type = 'received inventory' AND 
                                --inv.organization_id = 1 and
                                --TO_CHAR(inv.timestamp,'YYYY-MM-DD') BETWEEN '2020-05-01'  AND '2020-05-31'
                                inv.organization_id = org_id AND
                                TO_CHAR(inv.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
                        ) AS T1
                        GROUP BY T1.type_shipping, (f).package_type
                    ) AS T2
                ) AS T3
                WHERE id = report_id;	
                            
            END;$function$
            ;
        """
    )
