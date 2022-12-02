# coding: utf-8
from sqlalchemy import ARRAY, BigInteger, Boolean, Column, DateTime, Float, ForeignKey, Integer, JSON, Numeric, String, Table, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Organization(Base):
    __tablename__ = 'organizations'

    name = Column(String, nullable=False, unique=True)
    id = Column(Integer, primary_key=True, server_default=text("nextval('organizations_id_seq'::regclass)"))
    timestamp = Column(DateTime(True), nullable=False, server_default=text("now()"))
    data = Column(JSONB(astext_type=Text()), index=True)


class Srfax(Base):
    __tablename__ = 'srfax'

    id = Column(Integer, primary_key=True, server_default=text("nextval('srfax_id_seq'::regclass)"))
    file_name = Column(String, nullable=False)
    receive_status = Column(String)
    epoch_time = Column(String)
    date = Column(String)
    caller_id = Column(String)
    remote_id = Column(String)
    pages = Column(Integer)
    size = Column(BigInteger)
    viewed_status = Column(String)
    pdf_content = Column(Text)


class Tax(Base):
    __tablename__ = 'taxes'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('taxes_seq'::regclass)"))
    timestamp = Column(DateTime(True), nullable=False, server_default=text("now()"))
    created_by = Column(Integer, nullable=False)
    organization_id = Column(Integer, nullable=False)
    country = Column(String, nullable=False)
    province = Column(String, nullable=False)
    attributes = Column(JSONB(astext_type=Text()), server_default=text("'{}'::jsonb"))


t_vw_deviation_reports_with_assignments = Table(
    'vw_deviation_reports_with_assignments', metadata,
    Column('assignments', JSON),
    Column('id', BigInteger),
    Column('created_by', Integer),
    Column('organization_id', Integer),
    Column('timestamp', DateTime(True)),
    Column('name', String),
    Column('type', String),
    Column('status', String),
    Column('effective_date', DateTime(True)),
    Column('relates_to', ARRAY(String())),
    Column('potential_impact', ARRAY(String())),
    Column('impact_details', Text),
    Column('planned_reason', Text),
    Column('additional_details', Text),
    Column('investigation_details', Text),
    Column('root_cause', Text),
    Column('data', JSONB(astext_type=Text())),
    Column('attributes', JSONB(astext_type=Text()))
)


t_vw_mother_with_mother_batch_id = Table(
    'vw_mother_with_mother_batch_id', metadata,
    Column('mother_batch_id', Text),
    Column('id', BigInteger),
    Column('organization_id', Integer),
    Column('created_by', Integer),
    Column('timestamp', DateTime(True)),
    Column('name', String),
    Column('type', String),
    Column('variety', String),
    Column('data', JSONB(astext_type=Text())),
    Column('stats', JSONB(astext_type=Text())),
    Column('attributes', JSONB(astext_type=Text()))
)


t_vw_sop_assignments = Table(
    'vw_sop_assignments', metadata,
    Column('id', BigInteger),
    Column('name', String),
    Column('version_id', BigInteger),
    Column('timestamp', DateTime(True)),
    Column('organization_id', Integer),
    Column('signature_status', String),
    Column('data', JSONB(astext_type=Text())),
    Column('status', String),
    Column('assignment_date', DateTime(True)),
    Column('assigned_by_id', BigInteger),
    Column('assigned_to_id', BigInteger),
    Column('assigned_by', String),
    Column('assigned_to', String),
    Column('department', String),
    Column('version_number', BigInteger)
)


t_vw_sop_logs = Table(
    'vw_sop_logs', metadata,
    Column('id', BigInteger),
    Column('version_number', BigInteger),
    Column('name', String),
    Column('department', String),
    Column('activity', String),
    Column('user', String),
    Column('timestamp', DateTime(True)),
    Column('organization_id', Integer)
)


t_vw_sop_notifications = Table(
    'vw_sop_notifications', metadata,
    Column('id', BigInteger),
    Column('sop_id', BigInteger),
    Column('sop_version_number', BigInteger),
    Column('sop_name', String),
    Column('assigned_by', String),
    Column('timestamp', DateTime(True)),
    Column('organization_id', Integer),
    Column('assigned_to', String)
)


t_vw_sop_versions = Table(
    'vw_sop_versions', metadata,
    Column('id', BigInteger),
    Column('sop_id', BigInteger),
    Column('description', String),
    Column('revision_description', String),
    Column('revision_reason', String),
    Column('approved_date', DateTime(True)),
    Column('effective_date', DateTime(True)),
    Column('review_due_date', DateTime(True)),
    Column('review_approval_date', DateTime(True)),
    Column('timestamp', DateTime(True)),
    Column('created_by', Integer),
    Column('organization_id', Integer),
    Column('name', String),
    Column('status', String),
    Column('department', String),
    Column('version_number', BigInteger)
)


t_vw_sops = Table(
    'vw_sops', metadata,
    Column('version_id', BigInteger),
    Column('timestamp', DateTime(True)),
    Column('description', String),
    Column('approved_date', DateTime(True)),
    Column('effective_date', DateTime(True)),
    Column('organization_id', Integer),
    Column('version_number', BigInteger),
    Column('id', BigInteger),
    Column('status', String),
    Column('name', String),
    Column('department', String)
)

class Sop(Base):
    __tablename__ = 'sops'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('sops_id_seq'::regclass)"))
    name = Column(String, nullable=False)
    status = Column(String, nullable=False, server_default=text("'enabled'::character varying"))
    organization_id = Column(ForeignKey('organizations.id'), nullable=False)

    organization = relationship('Organization')


class WebhookSubscription(Base):
    __tablename__ = 'webhook_subscriptions'

    id = Column(Integer, primary_key=True, server_default=text("nextval('webhook_subscriptions_id_seq'::regclass)"))
    event = Column(String, nullable=False)
    url = Column(String, nullable=False)
    name = Column(String)
    created_by = Column(Integer)
    organization_id = Column(ForeignKey('organizations.id'))
    timestamp = Column(DateTime(True), server_default=text("now()"))

    organization = relationship('Organization')


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, server_default=text("nextval('users_id_seq'::regclass)"))
    name = Column(String, nullable=False)
    organization_id = Column(ForeignKey('organizations.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False, index=True)
    auth0_id = Column(String)
    enabled = Column(Boolean, nullable=False)
    created_by = Column(Integer)
    timestamp = Column(DateTime(True), nullable=False, server_default=text("now()"))
    data = Column(JSONB(astext_type=Text()), index=True)
    email = Column(String, nullable=False)

    organization = relationship('Organization')


class Activity(Base):
    __tablename__ = 'activities'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('activities_id_seq'::regclass)"))
    organization_id = Column(ForeignKey('organizations.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False)
    created_by = Column(ForeignKey('users.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False)
    timestamp = Column(DateTime(True), nullable=False, server_default=text("now()"))
    name = Column(String, nullable=False)
    data = Column(JSONB(astext_type=Text()), nullable=False, index=True)

    user = relationship('User')
    organization = relationship('Organization')


class Audit(Base):
    __tablename__ = 'audit'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('audit_id_seq'::regclass)"))
    organization_id = Column(ForeignKey('organizations.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False)
    created_by = Column(ForeignKey('users.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False)
    requested_by = Column(ForeignKey('users.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False)
    timestamp = Column(DateTime(True), nullable=False, server_default=text("now()"))
    date_request = Column(DateTime(True), nullable=False)
    type = Column(String, nullable=False)
    description = Column(String, nullable=False)
    service_desk_ticket = Column(JSONB(astext_type=Text()), server_default=text("'{}'::jsonb"))
    data = Column(JSONB(astext_type=Text()), server_default=text("'{\"status\": \"completed\"}'::jsonb"))

    user = relationship('User', primaryjoin='Audit.created_by == User.id')
    organization = relationship('Organization')
    user1 = relationship('User', primaryjoin='Audit.requested_by == User.id')


class Capa(Base):
    __tablename__ = 'capas'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('capas_id_seq'::regclass)"))
    description = Column(String, nullable=False)
    status = Column(String, nullable=False, server_default=text("'reported'::character varying"))
    actions_approved = Column(Integer, nullable=False, server_default=text("0"))
    actions_closed = Column(Integer, nullable=False, server_default=text("0"))
    actions_total = Column(Integer, nullable=False, server_default=text("0"))
    reported_by = Column(String, nullable=False)
    timestamp = Column(DateTime(True), nullable=False, server_default=text("now()"))
    created_by = Column(ForeignKey('users.id'), nullable=False)
    organization_id = Column(ForeignKey('organizations.id'), nullable=False)
    data = Column(JSONB(astext_type=Text()), server_default=text("'{}'::jsonb"))

    user = relationship('User')
    organization = relationship('Organization')


class ConsumableClass(Base):
    __tablename__ = 'consumable_classes'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('consumable_classes_id_seq'::regclass)"))
    organization_id = Column(ForeignKey('organizations.id'), nullable=False)
    created_by = Column(ForeignKey('users.id'), nullable=False)
    timestamp = Column(DateTime(True), nullable=False, server_default=text("now()"))
    type = Column(String, nullable=False)
    subtype = Column(String)
    unit = Column(String, nullable=False)
    data = Column(JSONB(astext_type=Text()), server_default=text("'{}'::jsonb"))
    status = Column(String, nullable=False)

    user = relationship('User')
    organization = relationship('Organization')


class CrmAccount(Base):
    __tablename__ = 'crm_accounts'

    id = Column(Integer, primary_key=True, server_default=text("nextval('crm_account_id_seq'::regclass)"))
    created_by = Column(ForeignKey('users.id'), nullable=False)
    data = Column(JSONB(astext_type=Text()), nullable=False, server_default=text("'{}'::jsonb"))
    name = Column(String, nullable=False)
    organization_id = Column(ForeignKey('organizations.id'), nullable=False)
    timestamp = Column(DateTime(True), nullable=False, server_default=text("now()"))
    attributes = Column(JSONB(astext_type=Text()), nullable=False, server_default=text("'{}'::jsonb"))
    account_type = Column(String)

    user = relationship('User')
    organization = relationship('Organization')


class Department(Base):
    __tablename__ = 'departments'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('sop_departments_id_seq'::regclass)"))
    name = Column(String, nullable=False)
    created_by = Column(ForeignKey('users.id'), nullable=False)
    organization_id = Column(ForeignKey('organizations.id'), nullable=False)
    status = Column(String, nullable=False, server_default=text("'enabled'::character varying"))

    user = relationship('User')
    organization = relationship('Organization')


class DeviationReport(Base):
    __tablename__ = 'deviation_reports'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('deviation_reports_id_seq'::regclass)"))
    created_by = Column(ForeignKey('users.id'), nullable=False)
    organization_id = Column(ForeignKey('organizations.id'), nullable=False)
    timestamp = Column(DateTime(True), nullable=False, server_default=text("now()"))
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    status = Column(String, nullable=False)
    effective_date = Column(DateTime(True), nullable=False)
    relates_to = Column(ARRAY(String()), nullable=False)
    potential_impact = Column(ARRAY(String()), nullable=False)
    impact_details = Column(Text)
    planned_reason = Column(Text)
    additional_details = Column(Text)
    investigation_details = Column(Text)
    root_cause = Column(Text)
    data = Column(JSONB(astext_type=Text()), server_default=text("'{}'::jsonb"))
    attributes = Column(JSONB(astext_type=Text()), server_default=text("'{}'::jsonb"))

    user = relationship('User')
    organization = relationship('Organization')


class Equipment(Base):
    __tablename__ = 'equipment'
    __table_args__ = (
        UniqueConstraint('external_id', 'type', 'organization_id'),
    )

    id = Column(Integer, primary_key=True, server_default=text("nextval('equipment_id_seq'::regclass)"))
    organization_id = Column(ForeignKey('organizations.id'), nullable=False)
    created_by = Column(ForeignKey('users.id'), nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    data = Column(JSONB(astext_type=Text()), nullable=False, server_default=text("'{}'::jsonb"))
    timestamp = Column(DateTime(True), nullable=False, server_default=text("now()"))
    external_id = Column(String)
    stats = Column(JSONB(astext_type=Text()), nullable=False, server_default=text("'{}'::jsonb"))
    sub_type = Column(String)
    room = Column(String)
    default_unit_type = Column(String)
    attributes = Column(JSONB(astext_type=Text()), server_default=text("'{}'::jsonb"))

    user = relationship('User')
    organization = relationship('Organization')


class HealthCanadaReport(Base):
    __tablename__ = 'health_canada_report'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('health_canada_report_seq'::regclass)"))
    timestamp = Column(DateTime(True), nullable=False, server_default=text("now()"))
    created_by = Column(ForeignKey('users.id'), nullable=False)
    organization_id = Column(ForeignKey('organizations.id'), nullable=False)
    data = Column(JSONB(astext_type=Text()), server_default=text("'{}'::jsonb"))
    report_period_year = Column(String, nullable=False)
    report_period_month = Column(String, nullable=False)
    province = Column(String)
    type = Column(String)
    company_name = Column(String)
    site_id = Column(String)
    city = Column(String)
    postal_code = Column(String)
    license_id = Column(String)
    total_buildings_area = Column(Numeric, server_default=text("0"))
    licensed_growing_area = Column(Numeric, server_default=text("0"))
    licensed_processing_area = Column(Numeric, server_default=text("0"))
    licensed_outdoor_growing_area = Column(Numeric, server_default=text("0"))
    unpackaged_seed_opening_inventory = Column(Numeric, server_default=text("0"))
    unpackaged_vegetative_plants_opening_inventory = Column(Numeric, server_default=text("0"))
    unpackaged_whole_cannabis_plants_opening_inventory = Column(Numeric, server_default=text("0"))
    unpackaged_fresh_cannabis_opening_inventory = Column(Numeric, server_default=text("0"))
    unpackaged_dried_cannabis_opening_inventory = Column(Numeric, server_default=text("0"))
    unpackaged_extracts_opening_inventory = Column(Numeric, server_default=text("0"))
    packaged_seed_opening_inventory = Column(Numeric, server_default=text("0"))
    packaged_vegetative_plants_opening_inventory = Column(Numeric, server_default=text("0"))
    packaged_fresh_cannabis_opening_inventory = Column(Numeric, server_default=text("0"))
    packaged_dried_cannabis_opening_inventory = Column(Numeric, server_default=text("0"))
    packaged_extracts_opening_inventory = Column(Numeric, server_default=text("0"))
    unpackaged_seed_closing_inventory = Column(Numeric, server_default=text("0"))
    unpackaged_vegetative_cannabis_plants_closing_inventory = Column(Numeric, server_default=text("0"))
    unpackaged_whole_cannabis_plants_closing_inventory = Column(Numeric, server_default=text("0"))
    unpackaged_fresh_cannabis_closing_inventory = Column(Numeric, server_default=text("0"))
    unpackaged_dried_cannabis_closing_inventory = Column(Numeric, server_default=text("0"))
    unpackaged_extracts_closing_inventory = Column(Numeric, server_default=text("0"))
    packaged_seed_closing_inventory = Column(Numeric, server_default=text("0"))
    packaged_vegetative_cannabis_plants_closing_inventory = Column(Numeric, server_default=text("0"))
    packaged_fresh_cannabis_closing_inventory = Column(Numeric, server_default=text("0"))
    packaged_dried_cannabis_closing_inventory = Column(Numeric, server_default=text("0"))
    packaged_extracts_closing_inventory = Column(Numeric, server_default=text("0"))
    packaged_seed_closing_inventory_weight = Column(Numeric, server_default=text("0"))
    packaged_fresh_cannabis_closing_inventory_weight = Column(Numeric, server_default=text("0"))
    packaged_dried_cannabis_closing_inventory_weight = Column(Numeric, server_default=text("0"))
    packaged_extracts_closing_inventory_weight = Column(Numeric, server_default=text("0"))
    unpackaged_seed_received_domestic = Column(Numeric, server_default=text("0"))
    unpackaged_vegetative_plants_received_domestic = Column(Numeric, server_default=text("0"))
    unpackaged_whole_cannabis_plants_received_domestic = Column(Numeric, server_default=text("0"))
    unpackaged_fresh_cannabis_received_domestic = Column(Numeric, server_default=text("0"))
    unpackaged_dried_cannabis_received_domestic = Column(Numeric, server_default=text("0"))
    unpackaged_extracts_received_domestic = Column(Numeric, server_default=text("0"))
    unpackaged_seed_received_imported = Column(Numeric, server_default=text("0"))
    unpackaged_vegetative_plants_received_imported = Column(Numeric, server_default=text("0"))
    unpackaged_whole_cannabis_plants_received_imported = Column(Numeric, server_default=text("0"))
    unpackaged_fresh_cannabis_received_imported = Column(Numeric, server_default=text("0"))
    unpackaged_dried_cannabis_received_imported = Column(Numeric, server_default=text("0"))
    unpackaged_extracts_received_imported = Column(Numeric, server_default=text("0"))
    unpackaged_seed_received_returned = Column(Numeric, server_default=text("0"))
    unpackaged_vegetative_plants_received_returned = Column(Numeric, server_default=text("0"))
    unpackaged_whole_cannabis_plants_received_returned = Column(Numeric, server_default=text("0"))
    unpackaged_fresh_cannabis_received_returned = Column(Numeric, server_default=text("0"))
    unpackaged_dried_cannabis_received_returned = Column(Numeric, server_default=text("0"))
    unpackaged_extracts_received_returned = Column(Numeric, server_default=text("0"))
    packaged_seed_received_domestic = Column(Numeric, server_default=text("0"))
    packaged_vegetative_plants_received_domestic = Column(Numeric, server_default=text("0"))
    packaged_fresh_cannabis_received_domestic = Column(Numeric, server_default=text("0"))
    packaged_dried_cannabis_received_domestic = Column(Numeric, server_default=text("0"))
    packaged_extracts_received_domestic = Column(Numeric, server_default=text("0"))
    packaged_seed_received_returned = Column(Numeric, server_default=text("0"))
    packaged_vegetative_plants_received_returned = Column(Numeric, server_default=text("0"))
    packaged_fresh_cannabis_received_returned = Column(Numeric, server_default=text("0"))
    packaged_dried_cannabis_received_returned = Column(Numeric, server_default=text("0"))
    packaged_extracts_received_returned = Column(Numeric, server_default=text("0"))
    unpackaged_seed_packaged_label = Column(Numeric, server_default=text("0"))
    unpackaged_vegetative_plants_packaged_label = Column(Numeric, server_default=text("0"))
    unpackaged_whole_cannabis_plants_packaged_label = Column(Numeric, server_default=text("0"))
    unpackaged_fresh_cannabis_packaged_label = Column(Numeric, server_default=text("0"))
    unpackaged_dried_cannabis_packaged_label = Column(Numeric, server_default=text("0"))
    unpackaged_extracts_packaged_label = Column(Numeric, server_default=text("0"))
    packaged_seed_quantity_packaged = Column(Numeric, server_default=text("0"))
    packaged_vegetative_plants_quantity_packaged = Column(Numeric, server_default=text("0"))
    packaged_fresh_cannabis_quantity_packaged = Column(Numeric, server_default=text("0"))
    packaged_dried_cannabis_quantity_packaged = Column(Numeric, server_default=text("0"))
    packaged_extracts_quantity_packaged = Column(Numeric, server_default=text("0"))
    unpackaged_vegetative_plants_adjustment_loss = Column(Numeric, server_default=text("0"))
    unpackaged_whole_cannabis_plants_adjustment_loss = Column(Numeric, server_default=text("0"))
    unpackaged_fresh_cannabis_adjustment_loss = Column(Numeric, server_default=text("0"))
    unpackaged_dried_cannabis_adjustment_loss = Column(Numeric, server_default=text("0"))
    unpackaged_extracts_adjustment_loss = Column(Numeric, server_default=text("0"))
    unpackaged_seed_destroyed = Column(Numeric, server_default=text("0"))
    unpackaged_vegetative_plants_destroyed = Column(Numeric, server_default=text("0"))
    unpackaged_whole_cannabis_plants_destroyed = Column(Numeric, server_default=text("0"))
    unpackaged_fresh_cannabis_destroyed = Column(Numeric, server_default=text("0"))
    unpackaged_dried_cannabis_destroyed = Column(Numeric, server_default=text("0"))
    unpackaged_extracts_destroyed = Column(Numeric, server_default=text("0"))
    packaged_seed_destroyed = Column(Numeric, server_default=text("0"))
    packaged_vegetative_plants_destroyed = Column(Numeric, server_default=text("0"))
    packaged_fresh_cannabis_destroyed = Column(Numeric, server_default=text("0"))
    packaged_dried_cannabis_destroyed = Column(Numeric, server_default=text("0"))
    packaged_extracts_destroyed = Column(Numeric, server_default=text("0"))
    unpackaged_seed_shipped_analytical_testers = Column(Numeric, server_default=text("0"))
    unpackaged_vegetative_plants_shipped_analytical_testers = Column(Numeric, server_default=text("0"))
    unpackaged_whole_cannabis_plants_shipped_analytical_testers = Column(Numeric, server_default=text("0"))
    unpackaged_fresh_shipped_analytical_testers = Column(Numeric, server_default=text("0"))
    unpackaged_dried_shipped_analytical_testers = Column(Numeric, server_default=text("0"))
    unpackaged_extracts_shipped_analytical_testers = Column(Numeric, server_default=text("0"))
    unpackaged_seed_produced = Column(Numeric, server_default=text("0"))
    unpackaged_vegetative_plants_produced = Column(Numeric, server_default=text("0"))
    unpackaged_whole_cannabis_plants_produced = Column(Numeric, server_default=text("0"))
    unpackaged_fresh_cannabis_produced = Column(Numeric, server_default=text("0"))
    unpackaged_dried_cannabis_produced = Column(Numeric, server_default=text("0"))
    unpackaged_extracts_produced = Column(Numeric, server_default=text("0"))
    unpackaged_seed_processed = Column(Numeric, server_default=text("0"))
    unpackaged_vegetative_plants_processed = Column(Numeric, server_default=text("0"))
    unpackaged_whole_cannabis_plants_processed = Column(Numeric, server_default=text("0"))
    unpackaged_fresh_cannabis_processed = Column(Numeric, server_default=text("0"))
    unpackaged_dried_cannabis_processed = Column(Numeric, server_default=text("0"))
    packaged_seed_shipped_domestic = Column(Numeric, server_default=text("0"))
    packaged_vegetative_plants_shipped_domestic = Column(Numeric, server_default=text("0"))
    packaged_fresh_cannabis_shipped_domestic = Column(Numeric, server_default=text("0"))
    packaged_dried_cannabis_shipped_domestic = Column(Numeric, server_default=text("0"))
    packaged_extracts_shipped_domestic = Column(Numeric, server_default=text("0"))
    unpackaged_vegetative_plants_other_additions = Column(Numeric, server_default=text("0"))
    ab_unpackaged_intra_industry_seeds_weight = Column(Numeric, server_default=text("0"))
    bc_unpackaged_intra_industry_seeds_weight = Column(Numeric, server_default=text("0"))
    mb_unpackaged_intra_industry_seeds_weight = Column(Numeric, server_default=text("0"))
    nb_unpackaged_intra_industry_seeds_weight = Column(Numeric, server_default=text("0"))
    nl_unpackaged_intra_industry_seeds_weight = Column(Numeric, server_default=text("0"))
    ns_unpackaged_intra_industry_seeds_weight = Column(Numeric, server_default=text("0"))
    nt_unpackaged_intra_industry_seeds_weight = Column(Numeric, server_default=text("0"))
    nu_unpackaged_intra_industry_seeds_weight = Column(Numeric, server_default=text("0"))
    on_unpackaged_intra_industry_seeds_weight = Column(Numeric, server_default=text("0"))
    pe_unpackaged_intra_industry_seeds_weight = Column(Numeric, server_default=text("0"))
    qc_unpackaged_intra_industry_seeds_weight = Column(Numeric, server_default=text("0"))
    sk_unpackaged_intra_industry_seeds_weight = Column(Numeric, server_default=text("0"))
    yt_unpackaged_intra_industry_seeds_weight = Column(Numeric, server_default=text("0"))
    total_unpackaged_intra_industry_seeds_weight = Column(Numeric, server_default=text("0"))
    ab_unpackaged_intra_industry_veg_plants_amount = Column(Numeric, server_default=text("0"))
    bc_unpackaged_intra_industry_veg_plants_amount = Column(Numeric, server_default=text("0"))
    mb_unpackaged_intra_industry_veg_plants_amount = Column(Numeric, server_default=text("0"))
    nb_unpackaged_intra_industry_veg_plants_amount = Column(Numeric, server_default=text("0"))
    nl_unpackaged_intra_industry_veg_plants_amount = Column(Numeric, server_default=text("0"))
    ns_unpackaged_intra_industry_veg_plants_amount = Column(Numeric, server_default=text("0"))
    nt_unpackaged_intra_industry_veg_plants_amount = Column(Numeric, server_default=text("0"))
    nu_unpackaged_intra_industry_veg_plants_amount = Column(Numeric, server_default=text("0"))
    on_unpackaged_intra_industry_veg_plants_amount = Column(Numeric, server_default=text("0"))
    pe_unpackaged_intra_industry_veg_plants_amount = Column(Numeric, server_default=text("0"))
    qc_unpackaged_intra_industry_veg_plants_amount = Column(Numeric, server_default=text("0"))
    sk_unpackaged_intra_industry_veg_plants_amount = Column(Numeric, server_default=text("0"))
    yt_unpackaged_intra_industry_veg_plants_amount = Column(Numeric, server_default=text("0"))
    total_unpackaged_intra_industry_veg_plants_amount = Column(Numeric, server_default=text("0"))
    ab_unpackaged_intra_industry_fresh_cannabis_weight = Column(Numeric, server_default=text("0"))
    bc_unpackaged_intra_industry_fresh_cannabis_weight = Column(Numeric, server_default=text("0"))
    mb_unpackaged_intra_industry_fresh_cannabis_weight = Column(Numeric, server_default=text("0"))
    nb_unpackaged_intra_industry_fresh_cannabis_weight = Column(Numeric, server_default=text("0"))
    nl_unpackaged_intra_industry_fresh_cannabis_weight = Column(Numeric, server_default=text("0"))
    ns_unpackaged_intra_industry_fresh_cannabis_weight = Column(Numeric, server_default=text("0"))
    nt_unpackaged_intra_industry_fresh_cannabis_weight = Column(Numeric, server_default=text("0"))
    nu_unpackaged_intra_industry_fresh_cannabis_weight = Column(Numeric, server_default=text("0"))
    on_unpackaged_intra_industry_fresh_cannabis_weight = Column(Numeric, server_default=text("0"))
    pe_unpackaged_intra_industry_fresh_cannabis_weight = Column(Numeric, server_default=text("0"))
    qc_unpackaged_intra_industry_fresh_cannabis_weight = Column(Numeric, server_default=text("0"))
    sk_unpackaged_intra_industry_fresh_cannabis_weight = Column(Numeric, server_default=text("0"))
    yt_unpackaged_intra_industry_fresh_cannabis_weight = Column(Numeric, server_default=text("0"))
    total_unpackaged_intra_industry_fresh_cannabis_weight = Column(Numeric, server_default=text("0"))
    ab_unpackaged_intra_industry_dried_cannabis_weight = Column(Numeric, server_default=text("0"))
    bc_unpackaged_intra_industry_dried_cannabis_weight = Column(Numeric, server_default=text("0"))
    mb_unpackaged_intra_industry_dried_cannabis_weight = Column(Numeric, server_default=text("0"))
    nb_unpackaged_intra_industry_dried_cannabis_weight = Column(Numeric, server_default=text("0"))
    nl_unpackaged_intra_industry_dried_cannabis_weight = Column(Numeric, server_default=text("0"))
    ns_unpackaged_intra_industry_dried_cannabis_weight = Column(Numeric, server_default=text("0"))
    nt_unpackaged_intra_industry_dried_cannabis_weight = Column(Numeric, server_default=text("0"))
    nu_unpackaged_intra_industry_dried_cannabis_weight = Column(Numeric, server_default=text("0"))
    on_unpackaged_intra_industry_dried_cannabis_weight = Column(Numeric, server_default=text("0"))
    pe_unpackaged_intra_industry_dried_cannabis_weight = Column(Numeric, server_default=text("0"))
    qc_unpackaged_intra_industry_dried_cannabis_weight = Column(Numeric, server_default=text("0"))
    sk_unpackaged_intra_industry_dried_cannabis_weight = Column(Numeric, server_default=text("0"))
    yt_unpackaged_intra_industry_dried_cannabis_weight = Column(Numeric, server_default=text("0"))
    total_unpackaged_intra_industry_dried_cannabis_weight = Column(Numeric, server_default=text("0"))
    ab_unpackaged_intra_industry_extracts_weight = Column(Numeric, server_default=text("0"))
    bc_unpackaged_intra_industry_extracts_weight = Column(Numeric, server_default=text("0"))
    mb_unpackaged_intra_industry_extracts_weight = Column(Numeric, server_default=text("0"))
    nb_unpackaged_intra_industry_extracts_weight = Column(Numeric, server_default=text("0"))
    nl_unpackaged_intra_industry_extracts_weight = Column(Numeric, server_default=text("0"))
    ns_unpackaged_intra_industry_extracts_weight = Column(Numeric, server_default=text("0"))
    nt_unpackaged_intra_industry_extracts_weight = Column(Numeric, server_default=text("0"))
    nu_unpackaged_intra_industry_extracts_weight = Column(Numeric, server_default=text("0"))
    on_unpackaged_intra_industry_extracts_weight = Column(Numeric, server_default=text("0"))
    pe_unpackaged_intra_industry_extracts_weight = Column(Numeric, server_default=text("0"))
    qc_unpackaged_intra_industry_extracts_weight = Column(Numeric, server_default=text("0"))
    sk_unpackaged_intra_industry_extracts_weight = Column(Numeric, server_default=text("0"))
    yt_unpackaged_intra_industry_extracts_weight = Column(Numeric, server_default=text("0"))
    total_unpackaged_intra_industry_extracts_weight = Column(Numeric, server_default=text("0"))
    ab_packaged_intra_industry_seeds_amount = Column(Numeric, server_default=text("0"))
    bc_packaged_intra_industry_seeds_amount = Column(Numeric, server_default=text("0"))
    mb_packaged_intra_industry_seeds_amount = Column(Numeric, server_default=text("0"))
    nb_packaged_intra_industry_seeds_amount = Column(Numeric, server_default=text("0"))
    nl_packaged_intra_industry_seeds_amount = Column(Numeric, server_default=text("0"))
    ns_packaged_intra_industry_seeds_amount = Column(Numeric, server_default=text("0"))
    nt_packaged_intra_industry_seeds_amount = Column(Numeric, server_default=text("0"))
    nu_packaged_intra_industry_seeds_amount = Column(Numeric, server_default=text("0"))
    on_packaged_intra_industry_seeds_amount = Column(Numeric, server_default=text("0"))
    pe_packaged_intra_industry_seeds_amount = Column(Numeric, server_default=text("0"))
    qc_packaged_intra_industry_seeds_amount = Column(Numeric, server_default=text("0"))
    sk_packaged_intra_industry_seeds_amount = Column(Numeric, server_default=text("0"))
    yt_packaged_intra_industry_seeds_amount = Column(Numeric, server_default=text("0"))
    total_packaged_intra_industry_seeds_amount = Column(Numeric, server_default=text("0"))
    ab_packaged_intra_industry_veg_plants_amount = Column(Numeric, server_default=text("0"))
    bc_packaged_intra_industry_veg_plants_amount = Column(Numeric, server_default=text("0"))
    mb_packaged_intra_industry_veg_plants_amount = Column(Numeric, server_default=text("0"))
    nb_packaged_intra_industry_veg_plants_amount = Column(Numeric, server_default=text("0"))
    nl_packaged_intra_industry_veg_plants_amount = Column(Numeric, server_default=text("0"))
    ns_packaged_intra_industry_veg_plants_amount = Column(Numeric, server_default=text("0"))
    nt_packaged_intra_industry_veg_plants_amount = Column(Numeric, server_default=text("0"))
    nu_packaged_intra_industry_veg_plants_amount = Column(Numeric, server_default=text("0"))
    on_packaged_intra_industry_veg_plants_amount = Column(Numeric, server_default=text("0"))
    pe_packaged_intra_industry_veg_plants_amount = Column(Numeric, server_default=text("0"))
    qc_packaged_intra_industry_veg_plants_amount = Column(Numeric, server_default=text("0"))
    sk_packaged_intra_industry_veg_plants_amount = Column(Numeric, server_default=text("0"))
    yt_packaged_intra_industry_veg_plants_amount = Column(Numeric, server_default=text("0"))
    total_packaged_intra_industry_veg_plants_amount = Column(Numeric, server_default=text("0"))
    ab_packaged_intra_industry_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    bc_packaged_intra_industry_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    mb_packaged_intra_industry_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    nb_packaged_intra_industry_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    nl_packaged_intra_industry_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    ns_packaged_intra_industry_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    nt_packaged_intra_industry_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    nu_packaged_intra_industry_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    on_packaged_intra_industry_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    pe_packaged_intra_industry_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    qc_packaged_intra_industry_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    sk_packaged_intra_industry_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    yt_packaged_intra_industry_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    total_packaged_intra_industry_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    ab_packaged_intra_industry_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    bc_packaged_intra_industry_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    mb_packaged_intra_industry_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    nb_packaged_intra_industry_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    nl_packaged_intra_industry_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    ns_packaged_intra_industry_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    nt_packaged_intra_industry_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    nu_packaged_intra_industry_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    on_packaged_intra_industry_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    pe_packaged_intra_industry_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    qc_packaged_intra_industry_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    sk_packaged_intra_industry_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    yt_packaged_intra_industry_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    total_packaged_intra_industry_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    ab_packaged_intra_industry_extracts_amount = Column(Numeric, server_default=text("0"))
    bc_packaged_intra_industry_extracts_amount = Column(Numeric, server_default=text("0"))
    mb_packaged_intra_industry_extracts_amount = Column(Numeric, server_default=text("0"))
    nb_packaged_intra_industry_extracts_amount = Column(Numeric, server_default=text("0"))
    nl_packaged_intra_industry_extracts_amount = Column(Numeric, server_default=text("0"))
    ns_packaged_intra_industry_extracts_amount = Column(Numeric, server_default=text("0"))
    nt_packaged_intra_industry_extracts_amount = Column(Numeric, server_default=text("0"))
    nu_packaged_intra_industry_extracts_amount = Column(Numeric, server_default=text("0"))
    on_packaged_intra_industry_extracts_amount = Column(Numeric, server_default=text("0"))
    pe_packaged_intra_industry_extracts_amount = Column(Numeric, server_default=text("0"))
    qc_packaged_intra_industry_extracts_amount = Column(Numeric, server_default=text("0"))
    sk_packaged_intra_industry_extracts_amount = Column(Numeric, server_default=text("0"))
    yt_packaged_intra_industry_extracts_amount = Column(Numeric, server_default=text("0"))
    total_packaged_intra_industry_extracts_amount = Column(Numeric, server_default=text("0"))
    ab_retailer_seeds_amount = Column(Numeric, server_default=text("0"))
    bc_retailer_seeds_amount = Column(Numeric, server_default=text("0"))
    mb_retailer_seeds_amount = Column(Numeric, server_default=text("0"))
    nb_retailer_seeds_amount = Column(Numeric, server_default=text("0"))
    nl_retailer_seeds_amount = Column(Numeric, server_default=text("0"))
    ns_retailer_seeds_amount = Column(Numeric, server_default=text("0"))
    nt_retailer_seeds_amount = Column(Numeric, server_default=text("0"))
    nu_retailer_seeds_amount = Column(Numeric, server_default=text("0"))
    on_retailer_seeds_amount = Column(Numeric, server_default=text("0"))
    pe_retailer_seeds_amount = Column(Numeric, server_default=text("0"))
    qc_retailer_seeds_amount = Column(Numeric, server_default=text("0"))
    sk_retailer_seeds_amount = Column(Numeric, server_default=text("0"))
    yt_retailer_seeds_amount = Column(Numeric, server_default=text("0"))
    total_retailer_seeds_amount = Column(Numeric, server_default=text("0"))
    ab_retailer_veg_plants_amount = Column(Numeric, server_default=text("0"))
    bc_retailer_veg_plants_amount = Column(Numeric, server_default=text("0"))
    mb_retailer_veg_plants_amount = Column(Numeric, server_default=text("0"))
    nb_retailer_veg_plants_amount = Column(Numeric, server_default=text("0"))
    nl_retailer_veg_plants_amount = Column(Numeric, server_default=text("0"))
    ns_retailer_veg_plants_amount = Column(Numeric, server_default=text("0"))
    nt_retailer_veg_plants_amount = Column(Numeric, server_default=text("0"))
    nu_retailer_veg_plants_amount = Column(Numeric, server_default=text("0"))
    on_retailer_veg_plants_amount = Column(Numeric, server_default=text("0"))
    pe_retailer_veg_plants_amount = Column(Numeric, server_default=text("0"))
    qc_retailer_veg_plants_amount = Column(Numeric, server_default=text("0"))
    sk_retailer_veg_plants_amount = Column(Numeric, server_default=text("0"))
    yt_retailer_veg_plants_amount = Column(Numeric, server_default=text("0"))
    total_retailer_veg_plants_amount = Column(Numeric, server_default=text("0"))
    ab_retailer_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    bc_retailer_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    mb_retailer_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    nb_retailer_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    nl_retailer_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    ns_retailer_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    nt_retailer_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    nu_retailer_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    on_retailer_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    pe_retailer_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    qc_retailer_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    sk_retailer_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    yt_retailer_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    total_retailer_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    ab_retailer_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    bc_retailer_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    mb_retailer_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    nb_retailer_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    nl_retailer_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    ns_retailer_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    nt_retailer_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    nu_retailer_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    on_retailer_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    pe_retailer_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    qc_retailer_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    sk_retailer_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    yt_retailer_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    total_retailer_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    ab_retailer_extracts_amount = Column(Numeric, server_default=text("0"))
    bc_retailer_extracts_amount = Column(Numeric, server_default=text("0"))
    mb_retailer_extracts_amount = Column(Numeric, server_default=text("0"))
    nb_retailer_extracts_amount = Column(Numeric, server_default=text("0"))
    nl_retailer_extracts_amount = Column(Numeric, server_default=text("0"))
    ns_retailer_extracts_amount = Column(Numeric, server_default=text("0"))
    nt_retailer_extracts_amount = Column(Numeric, server_default=text("0"))
    nu_retailer_extracts_amount = Column(Numeric, server_default=text("0"))
    on_retailer_extracts_amount = Column(Numeric, server_default=text("0"))
    pe_retailer_extracts_amount = Column(Numeric, server_default=text("0"))
    qc_retailer_extracts_amount = Column(Numeric, server_default=text("0"))
    sk_retailer_extracts_amount = Column(Numeric, server_default=text("0"))
    yt_retailer_extracts_amount = Column(Numeric, server_default=text("0"))
    total_retailer_extracts_amount = Column(Numeric, server_default=text("0"))
    ab_distributor_seeds_amount = Column(Numeric, server_default=text("0"))
    bc_distributor_seeds_amount = Column(Numeric, server_default=text("0"))
    mb_distributor_seeds_amount = Column(Numeric, server_default=text("0"))
    nb_distributor_seeds_amount = Column(Numeric, server_default=text("0"))
    nl_distributor_seeds_amount = Column(Numeric, server_default=text("0"))
    ns_distributor_seeds_amount = Column(Numeric, server_default=text("0"))
    nt_distributor_seeds_amount = Column(Numeric, server_default=text("0"))
    nu_distributor_seeds_amount = Column(Numeric, server_default=text("0"))
    on_distributor_seeds_amount = Column(Numeric, server_default=text("0"))
    pe_distributor_seeds_amount = Column(Numeric, server_default=text("0"))
    qc_distributor_seeds_amount = Column(Numeric, server_default=text("0"))
    sk_distributor_seeds_amount = Column(Numeric, server_default=text("0"))
    yt_distributor_seeds_amount = Column(Numeric, server_default=text("0"))
    total_distributor_seeds_amount = Column(Numeric, server_default=text("0"))
    ab_distributor_veg_plants_amount = Column(Numeric, server_default=text("0"))
    bc_distributor_veg_plants_amount = Column(Numeric, server_default=text("0"))
    mb_distributor_veg_plants_amount = Column(Numeric, server_default=text("0"))
    nb_distributor_veg_plants_amount = Column(Numeric, server_default=text("0"))
    nl_distributor_veg_plants_amount = Column(Numeric, server_default=text("0"))
    ns_distributor_veg_plants_amount = Column(Numeric, server_default=text("0"))
    nt_distributor_veg_plants_amount = Column(Numeric, server_default=text("0"))
    nu_distributor_veg_plants_amount = Column(Numeric, server_default=text("0"))
    on_distributor_veg_plants_amount = Column(Numeric, server_default=text("0"))
    pe_distributor_veg_plants_amount = Column(Numeric, server_default=text("0"))
    qc_distributor_veg_plants_amount = Column(Numeric, server_default=text("0"))
    sk_distributor_veg_plants_amount = Column(Numeric, server_default=text("0"))
    yt_distributor_veg_plants_amount = Column(Numeric, server_default=text("0"))
    total_distributor_veg_plants_amount = Column(Numeric, server_default=text("0"))
    ab_distributor_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    bc_distributor_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    mb_distributor_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    nb_distributor_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    nl_distributor_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    ns_distributor_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    nt_distributor_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    nu_distributor_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    on_distributor_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    pe_distributor_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    qc_distributor_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    sk_distributor_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    yt_distributor_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    total_distributor_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    ab_distributor_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    bc_distributor_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    mb_distributor_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    nb_distributor_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    nl_distributor_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    ns_distributor_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    nt_distributor_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    nu_distributor_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    on_distributor_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    pe_distributor_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    qc_distributor_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    sk_distributor_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    yt_distributor_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    total_distributor_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    ab_distributor_extracts_amount = Column(Numeric, server_default=text("0"))
    bc_distributor_extracts_amount = Column(Numeric, server_default=text("0"))
    mb_distributor_extracts_amount = Column(Numeric, server_default=text("0"))
    nb_distributor_extracts_amount = Column(Numeric, server_default=text("0"))
    nl_distributor_extracts_amount = Column(Numeric, server_default=text("0"))
    ns_distributor_extracts_amount = Column(Numeric, server_default=text("0"))
    nt_distributor_extracts_amount = Column(Numeric, server_default=text("0"))
    nu_distributor_extracts_amount = Column(Numeric, server_default=text("0"))
    on_distributor_extracts_amount = Column(Numeric, server_default=text("0"))
    pe_distributor_extracts_amount = Column(Numeric, server_default=text("0"))
    qc_distributor_extracts_amount = Column(Numeric, server_default=text("0"))
    sk_distributor_extracts_amount = Column(Numeric, server_default=text("0"))
    yt_distributor_extracts_amount = Column(Numeric, server_default=text("0"))
    total_distributor_extracts_amount = Column(Numeric, server_default=text("0"))
    ab_recreational_consumer_seeds_amount = Column(Numeric, server_default=text("0"))
    bc_recreational_consumer_seeds_amount = Column(Numeric, server_default=text("0"))
    mb_recreational_consumer_seeds_amount = Column(Numeric, server_default=text("0"))
    nb_recreational_consumer_seeds_amount = Column(Numeric, server_default=text("0"))
    nl_recreational_consumer_seeds_amount = Column(Numeric, server_default=text("0"))
    ns_recreational_consumer_seeds_amount = Column(Numeric, server_default=text("0"))
    nt_recreational_consumer_seeds_amount = Column(Numeric, server_default=text("0"))
    nu_recreational_consumer_seeds_amount = Column(Numeric, server_default=text("0"))
    on_recreational_consumer_seeds_amount = Column(Numeric, server_default=text("0"))
    pe_recreational_consumer_seeds_amount = Column(Numeric, server_default=text("0"))
    qc_recreational_consumer_seeds_amount = Column(Numeric, server_default=text("0"))
    sk_recreational_consumer_seeds_amount = Column(Numeric, server_default=text("0"))
    yt_recreational_consumer_seeds_amount = Column(Numeric, server_default=text("0"))
    total_recreational_consumer_seeds_amount = Column(Numeric, server_default=text("0"))
    ab_recreational_consumer_veg_plants_amount = Column(Numeric, server_default=text("0"))
    bc_recreational_consumer_veg_plants_amount = Column(Numeric, server_default=text("0"))
    mb_recreational_consumer_veg_plants_amount = Column(Numeric, server_default=text("0"))
    nb_recreational_consumer_veg_plants_amount = Column(Numeric, server_default=text("0"))
    nl_recreational_consumer_veg_plants_amount = Column(Numeric, server_default=text("0"))
    ns_recreational_consumer_veg_plants_amount = Column(Numeric, server_default=text("0"))
    nt_recreational_consumer_veg_plants_amount = Column(Numeric, server_default=text("0"))
    nu_recreational_consumer_veg_plants_amount = Column(Numeric, server_default=text("0"))
    on_recreational_consumer_veg_plants_amount = Column(Numeric, server_default=text("0"))
    pe_recreational_consumer_veg_plants_amount = Column(Numeric, server_default=text("0"))
    qc_recreational_consumer_veg_plants_amount = Column(Numeric, server_default=text("0"))
    sk_recreational_consumer_veg_plants_amount = Column(Numeric, server_default=text("0"))
    yt_recreational_consumer_veg_plants_amount = Column(Numeric, server_default=text("0"))
    total_recreational_consumer_veg_plants_amount = Column(Numeric, server_default=text("0"))
    ab_recreational_consumer_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    bc_recreational_consumer_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    mb_recreational_consumer_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    nb_recreational_consumer_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    nl_recreational_consumer_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    ns_recreational_consumer_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    nt_recreational_consumer_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    nu_recreational_consumer_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    on_recreational_consumer_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    pe_recreational_consumer_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    qc_recreational_consumer_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    sk_recreational_consumer_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    yt_recreational_consumer_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    total_recreational_consumer_fresh_cannabis_amount = Column(Numeric, server_default=text("0"))
    ab_recreational_consumer_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    bc_recreational_consumer_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    mb_recreational_consumer_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    nb_recreational_consumer_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    nl_recreational_consumer_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    ns_recreational_consumer_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    nt_recreational_consumer_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    nu_recreational_consumer_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    on_recreational_consumer_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    pe_recreational_consumer_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    qc_recreational_consumer_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    sk_recreational_consumer_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    yt_recreational_consumer_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    total_recreational_consumer_dried_cannabis_amount = Column(Numeric, server_default=text("0"))
    ab_recreational_consumer_extracts_amount = Column(Numeric, server_default=text("0"))
    bc_recreational_consumer_extracts_amount = Column(Numeric, server_default=text("0"))
    mb_recreational_consumer_extracts_amount = Column(Numeric, server_default=text("0"))
    nb_recreational_consumer_extracts_amount = Column(Numeric, server_default=text("0"))
    nl_recreational_consumer_extracts_amount = Column(Numeric, server_default=text("0"))
    ns_recreational_consumer_extracts_amount = Column(Numeric, server_default=text("0"))
    nt_recreational_consumer_extracts_amount = Column(Numeric, server_default=text("0"))
    nu_recreational_consumer_extracts_amount = Column(Numeric, server_default=text("0"))
    on_recreational_consumer_extracts_amount = Column(Numeric, server_default=text("0"))
    pe_recreational_consumer_extracts_amount = Column(Numeric, server_default=text("0"))
    qc_recreational_consumer_extracts_amount = Column(Numeric, server_default=text("0"))
    sk_recreational_consumer_extracts_amount = Column(Numeric, server_default=text("0"))
    yt_recreational_consumer_extracts_amount = Column(Numeric, server_default=text("0"))
    total_recreational_consumer_extracts_amount = Column(Numeric, server_default=text("0"))
    ab_distributor_seeds_value = Column(Numeric(14, 2), server_default=text("0"))
    bc_distributor_seeds_value = Column(Numeric(14, 2), server_default=text("0"))
    mb_distributor_seeds_value = Column(Numeric(14, 2), server_default=text("0"))
    nb_distributor_seeds_value = Column(Numeric(14, 2), server_default=text("0"))
    nl_distributor_seeds_value = Column(Numeric(14, 2), server_default=text("0"))
    ns_distributor_seeds_value = Column(Numeric(14, 2), server_default=text("0"))
    nt_distributor_seeds_value = Column(Numeric(14, 2), server_default=text("0"))
    nu_distributor_seeds_value = Column(Numeric(14, 2), server_default=text("0"))
    on_distributor_seeds_value = Column(Numeric(14, 2), server_default=text("0"))
    pe_distributor_seeds_value = Column(Numeric(14, 2), server_default=text("0"))
    qc_distributor_seeds_value = Column(Numeric(14, 2), server_default=text("0"))
    sk_distributor_seeds_value = Column(Numeric(14, 2), server_default=text("0"))
    yt_distributor_seeds_value = Column(Numeric(14, 2), server_default=text("0"))
    total_distributor_seeds_value = Column(Numeric(14, 2), server_default=text("0"))
    ab_recreational_consumer_seeds_value = Column(Numeric(14, 2), server_default=text("0"))
    bc_recreational_consumer_seeds_value = Column(Numeric(14, 2), server_default=text("0"))
    mb_recreational_consumer_seeds_value = Column(Numeric(14, 2), server_default=text("0"))
    nb_recreational_consumer_seeds_value = Column(Numeric(14, 2), server_default=text("0"))
    nl_recreational_consumer_seeds_value = Column(Numeric(14, 2), server_default=text("0"))
    ns_recreational_consumer_seeds_value = Column(Numeric(14, 2), server_default=text("0"))
    nt_recreational_consumer_seeds_value = Column(Numeric(14, 2), server_default=text("0"))
    nu_recreational_consumer_seeds_value = Column(Numeric(14, 2), server_default=text("0"))
    on_recreational_consumer_seeds_value = Column(Numeric(14, 2), server_default=text("0"))
    pe_recreational_consumer_seeds_value = Column(Numeric(14, 2), server_default=text("0"))
    qc_recreational_consumer_seeds_value = Column(Numeric(14, 2), server_default=text("0"))
    sk_recreational_consumer_seeds_value = Column(Numeric(14, 2), server_default=text("0"))
    yt_recreational_consumer_seeds_value = Column(Numeric(14, 2), server_default=text("0"))
    total_recreational_consumer_seeds_value = Column(Numeric(14, 2), server_default=text("0"))
    ab_retailer_seeds_value = Column(Numeric(14, 2), server_default=text("0"))
    bc_retailer_seeds_value = Column(Numeric(14, 2), server_default=text("0"))
    mb_retailer_seeds_value = Column(Numeric(14, 2), server_default=text("0"))
    nb_retailer_seeds_value = Column(Numeric(14, 2), server_default=text("0"))
    nl_retailer_seeds_value = Column(Numeric(14, 2), server_default=text("0"))
    ns_retailer_seeds_value = Column(Numeric(14, 2), server_default=text("0"))
    nt_retailer_seeds_value = Column(Numeric(14, 2), server_default=text("0"))
    nu_retailer_seeds_value = Column(Numeric(14, 2), server_default=text("0"))
    on_retailer_seeds_value = Column(Numeric(14, 2), server_default=text("0"))
    pe_retailer_seeds_value = Column(Numeric(14, 2), server_default=text("0"))
    qc_retailer_seeds_value = Column(Numeric(14, 2), server_default=text("0"))
    sk_retailer_seeds_value = Column(Numeric(14, 2), server_default=text("0"))
    yt_retailer_seeds_value = Column(Numeric(14, 2), server_default=text("0"))
    total_retailer_seeds_value = Column(Numeric(14, 2), server_default=text("0"))
    ab_distributor_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    bc_distributor_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    mb_distributor_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    nb_distributor_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    nl_distributor_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    ns_distributor_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    nt_distributor_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    nu_distributor_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    on_distributor_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    pe_distributor_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    qc_distributor_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    sk_distributor_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    yt_distributor_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    total_distributor_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    ab_recreational_consumer_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    bc_recreational_consumer_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    mb_recreational_consumer_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    nb_recreational_consumer_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    nl_recreational_consumer_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    ns_recreational_consumer_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    nt_recreational_consumer_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    nu_recreational_consumer_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    on_recreational_consumer_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    pe_recreational_consumer_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    qc_recreational_consumer_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    sk_recreational_consumer_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    yt_recreational_consumer_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    total_recreational_consumer_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    ab_retailer_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    bc_retailer_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    mb_retailer_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    nb_retailer_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    nl_retailer_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    ns_retailer_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    nt_retailer_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    nu_retailer_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    on_retailer_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    pe_retailer_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    qc_retailer_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    sk_retailer_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    yt_retailer_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    total_retailer_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    ab_unpackaged_intra_industry_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    mb_unpackaged_intra_industry_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    bc_unpackaged_intra_industry_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    nb_unpackaged_intra_industry_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    nl_unpackaged_intra_industry_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    ns_unpackaged_intra_industry_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    nt_unpackaged_intra_industry_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    nu_unpackaged_intra_industry_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    on_unpackaged_intra_industry_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    pe_unpackaged_intra_industry_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    qc_unpackaged_intra_industry_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    sk_unpackaged_intra_industry_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    yt_unpackaged_intra_industry_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    total_unpackaged_intra_industry_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    ab_distributor_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    bc_distributor_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    mb_distributor_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    nb_distributor_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    nl_distributor_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    ns_distributor_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    nt_distributor_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    nu_distributor_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    on_distributor_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    pe_distributor_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    qc_distributor_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    sk_distributor_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    yt_distributor_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    total_distributor_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    ab_recreational_consumer_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    bc_recreational_consumer_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    mb_recreational_consumer_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    nb_recreational_consumer_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    nl_recreational_consumer_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    ns_recreational_consumer_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    nt_recreational_consumer_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    nu_recreational_consumer_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    on_recreational_consumer_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    pe_recreational_consumer_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    qc_recreational_consumer_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    sk_recreational_consumer_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    yt_recreational_consumer_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    total_recreational_consumer_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    ab_retailer_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    bc_retailer_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    mb_retailer_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    nb_retailer_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    nl_retailer_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    ns_retailer_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    nt_retailer_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    nu_retailer_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    on_retailer_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    pe_retailer_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    qc_retailer_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    sk_retailer_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    yt_retailer_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    total_retailer_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    ab_unpackaged_intra_industry_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    bc_unpackaged_intra_industry_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    mb_unpackaged_intra_industry_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    nb_unpackaged_intra_industry_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    nl_unpackaged_intra_industry_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    ns_unpackaged_intra_industry_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    nt_unpackaged_intra_industry_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    nu_unpackaged_intra_industry_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    on_unpackaged_intra_industry_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    pe_unpackaged_intra_industry_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    qc_unpackaged_intra_industry_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    sk_unpackaged_intra_industry_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    yt_unpackaged_intra_industry_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    total_unpackaged_intra_industry_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    ab_distributor_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    bc_distributor_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    mb_distributor_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    nb_distributor_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    nl_distributor_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    ns_distributor_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    nt_distributor_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    nu_distributor_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    on_distributor_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    pe_distributor_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    qc_distributor_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    sk_distributor_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    yt_distributor_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    total_distributor_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    ab_recreational_consumer_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    bc_recreational_consumer_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    mb_recreational_consumer_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    nb_recreational_consumer_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    nl_recreational_consumer_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    ns_recreational_consumer_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    nt_recreational_consumer_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    nu_recreational_consumer_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    on_recreational_consumer_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    pe_recreational_consumer_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    qc_recreational_consumer_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    sk_recreational_consumer_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    yt_recreational_consumer_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    total_recreational_consumer_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    ab_retailer_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    bc_retailer_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    mb_retailer_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    nb_retailer_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    nl_retailer_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    ns_retailer_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    nt_retailer_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    nu_retailer_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    on_retailer_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    pe_retailer_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    qc_retailer_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    sk_retailer_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    yt_retailer_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    total_retailer_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    ab_unpackaged_intra_industry_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    bc_unpackaged_intra_industry_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    mb_unpackaged_intra_industry_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    nb_unpackaged_intra_industry_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    nl_unpackaged_intra_industry_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    ns_unpackaged_intra_industry_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    nt_unpackaged_intra_industry_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    nu_unpackaged_intra_industry_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    on_unpackaged_intra_industry_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    pe_unpackaged_intra_industry_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    qc_unpackaged_intra_industry_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    sk_unpackaged_intra_industry_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    yt_unpackaged_intra_industry_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    total_unpackaged_intra_industry_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    ab_distributor_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    bc_distributor_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    mb_distributor_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    nb_distributor_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    nl_distributor_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    ns_distributor_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    nt_distributor_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    nu_distributor_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    on_distributor_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    pe_distributor_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    qc_distributor_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    sk_distributor_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    yt_distributor_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    total_distributor_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    ab_recreational_consumer_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    bc_recreational_consumer_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    mb_recreational_consumer_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    nb_recreational_consumer_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    nl_recreational_consumer_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    ns_recreational_consumer_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    nt_recreational_consumer_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    nu_recreational_consumer_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    on_recreational_consumer_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    pe_recreational_consumer_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    qc_recreational_consumer_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    sk_recreational_consumer_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    yt_recreational_consumer_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    total_recreational_consumer_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    ab_retailer_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    bc_retailer_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    mb_retailer_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    nb_retailer_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    nl_retailer_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    ns_retailer_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    nt_retailer_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    nu_retailer_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    on_retailer_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    pe_retailer_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    qc_retailer_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    sk_retailer_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    yt_retailer_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    total_retailer_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    ab_unpackaged_intra_industry_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    bc_unpackaged_intra_industry_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    mb_unpackaged_intra_industry_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    nb_unpackaged_intra_industry_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    nl_unpackaged_intra_industry_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    ns_unpackaged_intra_industry_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    nt_unpackaged_intra_industry_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    nu_unpackaged_intra_industry_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    on_unpackaged_intra_industry_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    pe_unpackaged_intra_industry_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    qc_unpackaged_intra_industry_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    sk_unpackaged_intra_industry_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    yt_unpackaged_intra_industry_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    total_unpackaged_intra_industry_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    ab_packaged_intra_industry_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    mb_packaged_intra_industry_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    bc_packaged_intra_industry_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    nb_packaged_intra_industry_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    nl_packaged_intra_industry_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    ns_packaged_intra_industry_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    nt_packaged_intra_industry_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    nu_packaged_intra_industry_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    on_packaged_intra_industry_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    pe_packaged_intra_industry_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    qc_packaged_intra_industry_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    sk_packaged_intra_industry_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    yt_packaged_intra_industry_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    total_packaged_intra_industry_veg_plants_value = Column(Numeric(14, 2), server_default=text("0"))
    ab_packaged_intra_industry_fresh_cannabis_weight = Column(Numeric(14, 2), server_default=text("0"))
    bc_packaged_intra_industry_fresh_cannabis_weight = Column(Numeric(14, 2), server_default=text("0"))
    mb_packaged_intra_industry_fresh_cannabis_weight = Column(Numeric(14, 2), server_default=text("0"))
    nb_packaged_intra_industry_fresh_cannabis_weight = Column(Numeric(14, 2), server_default=text("0"))
    nl_packaged_intra_industry_fresh_cannabis_weight = Column(Numeric(14, 2), server_default=text("0"))
    ns_packaged_intra_industry_fresh_cannabis_weight = Column(Numeric(14, 2), server_default=text("0"))
    nt_packaged_intra_industry_fresh_cannabis_weight = Column(Numeric(14, 2), server_default=text("0"))
    nu_packaged_intra_industry_fresh_cannabis_weight = Column(Numeric(14, 2), server_default=text("0"))
    on_packaged_intra_industry_fresh_cannabis_weight = Column(Numeric(14, 2), server_default=text("0"))
    pe_packaged_intra_industry_fresh_cannabis_weight = Column(Numeric(14, 2), server_default=text("0"))
    qc_packaged_intra_industry_fresh_cannabis_weight = Column(Numeric(14, 2), server_default=text("0"))
    sk_packaged_intra_industry_fresh_cannabis_weight = Column(Numeric(14, 2), server_default=text("0"))
    yt_packaged_intra_industry_fresh_cannabis_weight = Column(Numeric(14, 2), server_default=text("0"))
    total_packaged_intra_industry_fresh_cannabis_weight = Column(Numeric(14, 2), server_default=text("0"))
    ab_packaged_intra_industry_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    bc_packaged_intra_industry_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    mb_packaged_intra_industry_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    nb_packaged_intra_industry_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    nl_packaged_intra_industry_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    ns_packaged_intra_industry_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    nt_packaged_intra_industry_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    nu_packaged_intra_industry_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    on_packaged_intra_industry_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    pe_packaged_intra_industry_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    qc_packaged_intra_industry_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    sk_packaged_intra_industry_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    yt_packaged_intra_industry_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    total_packaged_intra_industry_fresh_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    ab_packaged_intra_industry_dried_cannabis_weight = Column(Numeric(14, 2), server_default=text("0"))
    bc_packaged_intra_industry_dried_cannabis_weight = Column(Numeric(14, 2), server_default=text("0"))
    mb_packaged_intra_industry_dried_cannabis_weight = Column(Numeric(14, 2), server_default=text("0"))
    nb_packaged_intra_industry_dried_cannabis_weight = Column(Numeric(14, 2), server_default=text("0"))
    nl_packaged_intra_industry_dried_cannabis_weight = Column(Numeric(14, 2), server_default=text("0"))
    ns_packaged_intra_industry_dried_cannabis_weight = Column(Numeric(14, 2), server_default=text("0"))
    nt_packaged_intra_industry_dried_cannabis_weight = Column(Numeric(14, 2), server_default=text("0"))
    nu_packaged_intra_industry_dried_cannabis_weight = Column(Numeric(14, 2), server_default=text("0"))
    on_packaged_intra_industry_dried_cannabis_weight = Column(Numeric(14, 2), server_default=text("0"))
    pe_packaged_intra_industry_dried_cannabis_weight = Column(Numeric(14, 2), server_default=text("0"))
    qc_packaged_intra_industry_dried_cannabis_weight = Column(Numeric(14, 2), server_default=text("0"))
    sk_packaged_intra_industry_dried_cannabis_weight = Column(Numeric(14, 2), server_default=text("0"))
    yt_packaged_intra_industry_dried_cannabis_weight = Column(Numeric(14, 2), server_default=text("0"))
    total_packaged_intra_industry_dried_cannabis_weight = Column(Numeric(14, 2), server_default=text("0"))
    ab_packaged_intra_industry_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    bc_packaged_intra_industry_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    mb_packaged_intra_industry_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    nb_packaged_intra_industry_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    nl_packaged_intra_industry_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    ns_packaged_intra_industry_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    nt_packaged_intra_industry_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    nu_packaged_intra_industry_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    on_packaged_intra_industry_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    pe_packaged_intra_industry_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    qc_packaged_intra_industry_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    sk_packaged_intra_industry_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    yt_packaged_intra_industry_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    total_packaged_intra_industry_dried_cannabis_value = Column(Numeric(14, 2), server_default=text("0"))
    ab_packaged_intra_industry_extracts_weight = Column(Numeric(14, 2), server_default=text("0"))
    bc_packaged_intra_industry_extracts_weight = Column(Numeric(14, 2), server_default=text("0"))
    mb_packaged_intra_industry_extracts_weight = Column(Numeric(14, 2), server_default=text("0"))
    nb_packaged_intra_industry_extracts_weight = Column(Numeric(14, 2), server_default=text("0"))
    nl_packaged_intra_industry_extracts_weight = Column(Numeric(14, 2), server_default=text("0"))
    ns_packaged_intra_industry_extracts_weight = Column(Numeric(14, 2), server_default=text("0"))
    nt_packaged_intra_industry_extracts_weight = Column(Numeric(14, 2), server_default=text("0"))
    nu_packaged_intra_industry_extracts_weight = Column(Numeric(14, 2), server_default=text("0"))
    on_packaged_intra_industry_extracts_weight = Column(Numeric(14, 2), server_default=text("0"))
    pe_packaged_intra_industry_extracts_weight = Column(Numeric(14, 2), server_default=text("0"))
    qc_packaged_intra_industry_extracts_weight = Column(Numeric(14, 2), server_default=text("0"))
    sk_packaged_intra_industry_extracts_weight = Column(Numeric(14, 2), server_default=text("0"))
    yt_packaged_intra_industry_extracts_weight = Column(Numeric(14, 2), server_default=text("0"))
    total_packaged_intra_industry_extracts_weight = Column(Numeric(14, 2), server_default=text("0"))
    ab_packaged_intra_industry_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    bc_packaged_intra_industry_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    mb_packaged_intra_industry_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    nb_packaged_intra_industry_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    nl_packaged_intra_industry_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    ns_packaged_intra_industry_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    nt_packaged_intra_industry_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    nu_packaged_intra_industry_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    on_packaged_intra_industry_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    pe_packaged_intra_industry_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    qc_packaged_intra_industry_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    sk_packaged_intra_industry_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    yt_packaged_intra_industry_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    total_packaged_intra_industry_extracts_value = Column(Numeric(14, 2), server_default=text("0"))
    unpackaged_seed_reductions_shipped_returned = Column(Numeric, server_default=text("0"))
    unpackaged_vegetative_plants_reductions_shipped_returned = Column(Numeric, server_default=text("0"))
    unpackaged_fresh_cannabis_reductions_shipped_returned = Column(Numeric, server_default=text("0"))
    unpackaged_dried_cannabis_reductions_shipped_returned = Column(Numeric, server_default=text("0"))
    unpackaged_extracts_reductions_shipped_returned = Column(Numeric, server_default=text("0"))
    unpackaged_seed_shipped_cultivators_processors = Column(Numeric(14, 2), server_default=text("0"))
    unpackaged_vegetative_plants_shipped_cultivators_processors = Column(Numeric(14, 2), server_default=text("0"))
    unpackaged_whole_cannabis_plants_shipped_cultivators_processors = Column(Numeric(14, 2), server_default=text("0"))
    unpackaged_fresh_shipped_cultivators_processors = Column(Numeric(14, 2), server_default=text("0"))
    unpackaged_dried_shipped_cultivators_processors = Column(Numeric(14, 2), server_default=text("0"))
    unpackaged_extracts_shipped_cultivators_processors = Column(Numeric(14, 2), server_default=text("0"))

    user = relationship('User')
    organization = relationship('Organization')


class Inventory(Base):
    __tablename__ = 'inventories'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('inventories_id_seq'::regclass)"))
    organization_id = Column(ForeignKey('organizations.id'), nullable=False)
    created_by = Column(ForeignKey('users.id'), nullable=False)
    timestamp = Column(DateTime(True), nullable=False, server_default=text("now()"))
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    variety = Column(String, nullable=False)
    data = Column(JSONB(astext_type=Text()), index=True)
    stats = Column(JSONB(astext_type=Text()), index=True, server_default=text("'{}'::jsonb"))
    attributes = Column(JSONB(astext_type=Text()), nullable=False, index=True, server_default=text("'{}'::jsonb"))

    user = relationship('User')
    organization = relationship('Organization')


class Recall(Base):
    __tablename__ = 'recalls'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('recalls_id_seq'::regclass)"))
    description = Column(String, nullable=False)
    timestamp = Column(DateTime(True), nullable=False, server_default=text("now()"))
    active_date = Column(DateTime(True))
    end_date = Column(DateTime(True))
    created_by = Column(ForeignKey('users.id'), nullable=False)
    organization_id = Column(ForeignKey('organizations.id'), nullable=False)
    lot_ids = Column(JSONB(astext_type=Text()), nullable=False, server_default=text("'[]'::jsonb"))
    data = Column(JSONB(astext_type=Text()), server_default=text("'{}'::jsonb"))
    contact_user = Column(Integer, nullable=False)

    user = relationship('User')
    organization = relationship('Organization')


class Room(Base):
    __tablename__ = 'rooms'
    __table_args__ = (
        UniqueConstraint('organization_id', 'name'),
    )

    id = Column(Integer, primary_key=True, server_default=text("nextval('rooms_id_seq'::regclass)"))
    organization_id = Column(ForeignKey('organizations.id'), nullable=False)
    created_by = Column(ForeignKey('users.id'), nullable=False)
    name = Column(String, nullable=False)
    data = Column(JSONB(astext_type=Text()))
    timestamp = Column(DateTime(True), nullable=False, server_default=text("now()"))

    user = relationship('User')
    organization = relationship('Organization')


class Rule(Base):
    __tablename__ = 'rules'

    id = Column(Integer, primary_key=True, server_default=text("nextval('rules_id_seq'::regclass)"))
    organization_id = Column(ForeignKey('organizations.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False)
    created_by = Column(ForeignKey('users.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False)
    timestamp = Column(DateTime(True), nullable=False, server_default=text("now()"))
    name = Column(String, nullable=False)
    description = Column(String)
    activity = Column(String, nullable=False)
    conditions = Column(JSONB(astext_type=Text()), nullable=False)
    data = Column(JSONB(astext_type=Text()), index=True)

    user = relationship('User')
    organization = relationship('Organization')


class Sku(Base):
    __tablename__ = 'skus'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('skus_id_seq'::regclass)"))
    organization_id = Column(ForeignKey('organizations.id'), nullable=False)
    created_by = Column(ForeignKey('users.id'), nullable=False)
    timestamp = Column(DateTime(True), nullable=False, server_default=text("now()"))
    name = Column(String, nullable=False)
    variety = Column(String, nullable=False)
    cannabis_class = Column(String)
    target_qty = Column(Float(53), nullable=False)
    data = Column(JSONB(astext_type=Text()), nullable=False, server_default=text("'{}'::jsonb"))
    attributes = Column(JSONB(astext_type=Text()), nullable=False, server_default=text("'{}'::jsonb"))
    target_qty_unit = Column(String, nullable=False)
    sales_class = Column(String)
    price = Column(Numeric(14, 2), server_default=text("0"))
    current_inventory = Column(Integer, server_default=text("0"))

    user = relationship('User')
    organization = relationship('Organization')


class SopVersion(Base):
    __tablename__ = 'sop_versions'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('sop_versions_id_seq'::regclass)"))
    sop_id = Column(ForeignKey('sops.id'), nullable=False)
    description = Column(String, nullable=False)
    revision_description = Column(String)
    revision_reason = Column(String)
    approved_date = Column(DateTime(True))
    effective_date = Column(DateTime(True))
    review_due_date = Column(DateTime(True))
    review_approval_date = Column(DateTime(True))
    timestamp = Column(DateTime(True), nullable=False, server_default=text("now()"))
    created_by = Column(ForeignKey('users.id'), nullable=False)
    organization_id = Column(ForeignKey('organizations.id'), nullable=False)

    user = relationship('User')
    organization = relationship('Organization')
    sop = relationship('Sop')


class Taxonomy(Base):
    __tablename__ = 'taxonomies'
    __table_args__ = (
        UniqueConstraint('organization_id', 'name'),
    )

    id = Column(Integer, primary_key=True, server_default=text("nextval('taxonomies_id_seq'::regclass)"))
    organization_id = Column(ForeignKey('organizations.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False, index=True)
    created_by = Column(ForeignKey('users.id'), nullable=False, index=True)
    timestamp = Column(DateTime(True), nullable=False, server_default=text("now()"))
    name = Column(String, nullable=False)
    data = Column(JSONB(astext_type=Text()))

    user = relationship('User')
    organization = relationship('Organization')


class Upload(Base):
    __tablename__ = 'uploads'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('uploads_id_seq'::regclass)"))
    organization_id = Column(ForeignKey('organizations.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False)
    name = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    upload_exists = Column(Boolean, nullable=False, server_default=text("false"))
    data = Column(JSONB(astext_type=Text()), index=True)
    created_by = Column(ForeignKey('users.id'), nullable=False)
    timestamp = Column(DateTime(True), nullable=False, server_default=text("now()"))

    user = relationship('User')
    organization = relationship('Organization')


class AuditDetail(Base):
    __tablename__ = 'audit_detail'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('audit_detail_id_seq'::regclass)"))
    organization_id = Column(Integer, nullable=False)
    audit_id = Column(ForeignKey('audit.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False)
    type = Column(String, nullable=False)
    table_name = Column(String, nullable=False)
    where = Column(String, nullable=False)
    new_values = Column(JSONB(astext_type=Text()), nullable=False)
    old_values = Column(JSONB(astext_type=Text()), nullable=False)
    rows_affected = Column(Integer, nullable=False)

    audit = relationship('Audit')


class CapaAction(Base):
    __tablename__ = 'capa_actions'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('capa_actions_id_seq'::regclass)"))
    capa_id = Column(ForeignKey('capas.id'), nullable=False)
    description = Column(String, nullable=False)
    comment = Column(String)
    status = Column(String, nullable=False, server_default=text("'awaiting approval'::character varying"))
    timestamp = Column(DateTime(True), nullable=False, server_default=text("now()"))
    created_by = Column(ForeignKey('users.id'), nullable=False)
    organization_id = Column(ForeignKey('organizations.id'), nullable=False)
    data = Column(JSONB(astext_type=Text()), server_default=text("'{}'::jsonb"))
    staff_assigned = Column(String)
    due_date = Column(DateTime(True))
    result = Column(String)

    capa = relationship('Capa')
    user = relationship('User')
    organization = relationship('Organization')


class CapaLink(Base):
    __tablename__ = 'capa_links'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('capa_links_id_seq'::regclass)"))
    capa_id = Column(ForeignKey('capas.id'), nullable=False)
    timestamp = Column(DateTime(True), nullable=False, server_default=text("now()"))
    created_by = Column(ForeignKey('users.id'), nullable=False)
    organization_id = Column(ForeignKey('organizations.id'), nullable=False)
    data = Column(JSONB(astext_type=Text()), server_default=text("'{}'::jsonb"))
    status = Column(String, nullable=False, server_default=text("'enabled'::character varying"))
    link_id = Column(BigInteger, nullable=False)
    link_type = Column(String, nullable=False)

    capa = relationship('Capa')
    user = relationship('User')
    organization = relationship('Organization')


class ConsumableLot(Base):
    __tablename__ = 'consumable_lots'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('consumable_lots_id_seq'::regclass)"))
    organization_id = Column(ForeignKey('organizations.id'), nullable=False)
    created_by = Column(ForeignKey('users.id'), nullable=False)
    timestamp = Column(DateTime(True), nullable=False, server_default=text("now()"))
    status = Column(String, nullable=False)
    expiration_date = Column(DateTime(True))
    class_id = Column(ForeignKey('consumable_classes.id'), nullable=False)
    current_qty = Column(Numeric, nullable=False)
    initial_qty = Column(Numeric, nullable=False)
    unit = Column(String, nullable=False)
    data = Column(JSONB(astext_type=Text()), server_default=text("'{}'::jsonb"))

    _class = relationship('ConsumableClass')
    user = relationship('User')
    organization = relationship('Organization')


class DeviationReportsAssignment(Base):
    __tablename__ = 'deviation_reports_assignments'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('deviation_reports_assignments_id_seq'::regclass)"))
    created_by = Column(ForeignKey('users.id'), nullable=False)
    organization_id = Column(ForeignKey('organizations.id'), nullable=False)
    timestamp = Column(DateTime(True), nullable=False, server_default=text("now()"))
    deviation_reports_id = Column(ForeignKey('deviation_reports.id'), nullable=False)
    user_id = Column(ForeignKey('users.id'), nullable=False)
    type = Column(String, nullable=False)
    status = Column(String, nullable=False)
    data = Column(JSONB(astext_type=Text()), server_default=text("'{}'::jsonb"))

    user = relationship('User', primaryjoin='DeviationReportsAssignment.created_by == User.id')
    deviation_reports = relationship('DeviationReport')
    organization = relationship('Organization')
    user1 = relationship('User', primaryjoin='DeviationReportsAssignment.user_id == User.id')


class Order(Base):
    __tablename__ = 'orders'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('orders_id_seq'::regclass)"))
    crm_account_id = Column(ForeignKey('crm_accounts.id'))
    created_by = Column(ForeignKey('users.id'), nullable=False)
    organization_id = Column(ForeignKey('organizations.id'), nullable=False)
    description = Column(String)
    order_type = Column(String)
    order_received_date = Column(String)
    order_placed_by = Column(String)
    timestamp = Column(DateTime(True), nullable=False, server_default=text("now()"))
    data = Column(JSONB(astext_type=Text()), server_default=text("'{}'::jsonb"))
    shipping_address = Column(JSONB(astext_type=Text()), server_default=text("'{}'::jsonb"))
    ordered_stats = Column(JSONB(astext_type=Text()), nullable=False, server_default=text("'{}'::jsonb"))
    shipped_stats = Column(JSONB(astext_type=Text()), nullable=False, server_default=text("'{}'::jsonb"))
    status = Column(String)
    shipping_status = Column(String)
    due_date = Column(String)
    sub_total = Column(Numeric(14, 2), server_default=text("0"))
    provincial_tax = Column(Numeric(14, 2), server_default=text("0"))
    excise_tax = Column(Numeric(14, 2), server_default=text("0"))
    discount_percent = Column(Numeric(14, 2), server_default=text("0"))
    discount = Column(Numeric(14, 2), server_default=text("0"))
    shipping_value = Column(Numeric(14, 2), server_default=text("0"))
    total = Column(Numeric(14, 2), server_default=text("0"))
    include_tax = Column(Boolean, server_default=text("true"))

    user = relationship('User')
    crm_account = relationship('CrmAccount')
    organization = relationship('Organization')


class SensorsDatum(Base):
    __tablename__ = 'sensors_data'

    id = Column(Integer, primary_key=True, server_default=text("nextval('sensor_id_seq'::regclass)"))
    sensor_reading = Column(String, nullable=False)
    sensor_id = Column(ForeignKey('equipment.id'), nullable=False)
    data = Column(JSONB(astext_type=Text()))
    organization_id = Column(ForeignKey('organizations.id'))
    created_by = Column(Integer)
    timestamp = Column(DateTime(True), server_default=text("now()"))
    sensor_type = Column(String)
    reading_timestamp = Column(DateTime(True))

    organization = relationship('Organization')
    sensor = relationship('Equipment')


class Shipment(Base):
    __tablename__ = 'shipments'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('shipment_id_seq'::regclass)"))
    tracking_number = Column(String)
    shipped_date = Column(DateTime(True))
    delivered_date = Column(DateTime(True))
    created_by = Column(ForeignKey('users.id'), nullable=False)
    organization_id = Column(ForeignKey('organizations.id'), nullable=False)
    timestamp = Column(DateTime(True), nullable=False, server_default=text("now()"))
    shipping_address = Column(JSONB(astext_type=Text()), server_default=text("'{}'::jsonb"))
    crm_account_id = Column(ForeignKey('crm_accounts.id'))
    status = Column(String)
    data = Column(JSONB(astext_type=Text()), server_default=text("'{}'::jsonb"))
    attributes = Column(JSONB(astext_type=Text()), server_default=text("'{}'::jsonb"))

    user = relationship('User')
    crm_account = relationship('CrmAccount')
    organization = relationship('Organization')


class Signature(Base):
    __tablename__ = 'signatures'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('signatures_id_seq'::regclass)"))
    field = Column(String, nullable=False)
    timestamp = Column(DateTime(True), nullable=False, server_default=text("now()"))
    created_by = Column(ForeignKey('users.id'), nullable=False)
    signed_by = Column(ForeignKey('users.id'), nullable=False)
    organization_id = Column(ForeignKey('organizations.id'), nullable=False)
    activity_id = Column(ForeignKey('activities.id'), nullable=False)
    data = Column(JSONB(astext_type=Text()), server_default=text("'{}'::jsonb"))

    activity = relationship('Activity')
    user = relationship('User', primaryjoin='Signature.created_by == User.id')
    organization = relationship('Organization')
    user1 = relationship('User', primaryjoin='Signature.signed_by == User.id')


class SopAssignment(Base):
    __tablename__ = 'sop_assignments'

    assigned_by_id = Column(ForeignKey('users.id'), nullable=False)
    assigned_to_id = Column(ForeignKey('users.id'), nullable=False)
    sop_version_id = Column(ForeignKey('sop_versions.id'), nullable=False)
    status = Column(String, nullable=False, server_default=text("'enabled'::character varying"))
    timestamp = Column(DateTime(True), nullable=False, server_default=text("now()"))
    signature_status = Column(String, nullable=False, server_default=text("'unsigned'::character varying"))
    data = Column(JSONB(astext_type=Text()), server_default=text("'{}'::jsonb"))
    id = Column(BigInteger, primary_key=True, server_default=text("nextval('sop_assignments_id_seq'::regclass)"))
    organization_id = Column(Integer, nullable=False, server_default=text("0"))

    assigned_by = relationship('User', primaryjoin='SopAssignment.assigned_by_id == User.id')
    assigned_to = relationship('User', primaryjoin='SopAssignment.assigned_to_id == User.id')
    sop_version = relationship('SopVersion')


class SopVersionsDepartment(Base):
    __tablename__ = 'sop_versions_departments'

    sop_version_id = Column(ForeignKey('sop_versions.id'), nullable=False)
    department_id = Column(ForeignKey('departments.id'), nullable=False)
    id = Column(BigInteger, primary_key=True, server_default=text("nextval('sop_versions_departments_id_seq'::regclass)"))
    organization_id = Column(Integer, nullable=False, server_default=text("0"))

    department = relationship('Department')
    sop_version = relationship('SopVersion')


class TaxonomyOption(Base):
    __tablename__ = 'taxonomy_options'
    __table_args__ = (
        UniqueConstraint('taxonomy_id', 'name'),
    )

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('taxonomy_options_id_seq'::regclass)"))
    organization_id = Column(ForeignKey('organizations.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False)
    created_by = Column(ForeignKey('users.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False)
    timestamp = Column(DateTime(True), nullable=False, server_default=text("now()"))
    name = Column(String, nullable=False)
    data = Column(JSONB(astext_type=Text()), index=True)
    taxonomy_id = Column(ForeignKey('taxonomies.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False)

    user = relationship('User')
    organization = relationship('Organization')
    taxonomy = relationship('Taxonomy')


class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('transactions_id_seq'::regclass)"))
    organization_id = Column(ForeignKey('organizations.id'), nullable=False)
    created_by = Column(ForeignKey('users.id'), nullable=False)
    timestamp = Column(DateTime(True), nullable=False, server_default=text("now()"))
    description = Column(String)
    total_amount = Column(Numeric(14, 2), nullable=False)
    data = Column(JSONB(astext_type=Text()), server_default=text("'{}'::jsonb"))
    crm_account_id = Column(ForeignKey('crm_accounts.id'))
    purchase_order = Column(String)

    user = relationship('User')
    crm_account = relationship('CrmAccount')
    organization = relationship('Organization')


class Invoice(Base):
    __tablename__ = 'invoices'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('invoices_id_seq'::regclass)"))
    order_id = Column(ForeignKey('orders.id'), nullable=False)
    organization_id = Column(ForeignKey('organizations.id'), nullable=False)
    created_by = Column(ForeignKey('users.id'), nullable=False)
    timestamp = Column(DateTime(True))
    data = Column(JSONB(astext_type=Text()), server_default=text("'{}'::jsonb"))
    attributes = Column(JSONB(astext_type=Text()), server_default=text("'{}'::jsonb"))

    user = relationship('User')
    order = relationship('Order')
    organization = relationship('Organization')


class OrderItem(Base):
    __tablename__ = 'order_items'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('order_items_id_seq'::regclass)"))
    sku_id = Column(ForeignKey('skus.id'), nullable=False)
    sku_name = Column(String, nullable=False)
    order_id = Column(ForeignKey('orders.id'), nullable=False)
    data = Column(JSONB(astext_type=Text()), server_default=text("'{}'::jsonb"))
    created_by = Column(ForeignKey('users.id'), nullable=False)
    shipment_id = Column(ForeignKey('shipments.id'))
    organization_id = Column(ForeignKey('organizations.id'), nullable=False)
    ordered_stats = Column(JSONB(astext_type=Text()), server_default=text("'{}'::jsonb"))
    variety = Column(String, nullable=False)
    timestamp = Column(DateTime(True), nullable=False, server_default=text("now()"))
    shipped_stats = Column(JSONB(astext_type=Text()), nullable=False, server_default=text("'{}'::jsonb"))
    status = Column(String)
    quantity = Column(Integer)
    filled = Column(Integer)
    price = Column(Numeric(14, 2), server_default=text("0"))
    excise_tax = Column(Numeric(14, 2), server_default=text("0"))
    provincial_tax = Column(Numeric(14, 2), server_default=text("0"))
    attributes = Column(JSONB(astext_type=Text()), nullable=False, server_default=text("'{}'::jsonb"))
    discount = Column(Numeric(14, 2), server_default=text("0"))
    shipping_value = Column(Numeric(14, 2), server_default=text("0"))

    user = relationship('User')
    order = relationship('Order')
    organization = relationship('Organization')
    shipment = relationship('Shipment')
    sku = relationship('Sku')


class TransactionAllocation(Base):
    __tablename__ = 'transaction_allocations'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('transaction_allocations_id_seq'::regclass)"))
    organization_id = Column(ForeignKey('organizations.id'), nullable=False)
    created_by = Column(ForeignKey('users.id'), nullable=False)
    timestamp = Column(DateTime(True), nullable=False, server_default=text("now()"))
    amount = Column(Numeric(14, 2), nullable=False)
    transaction_id = Column(ForeignKey('transactions.id'), nullable=False)
    data = Column(JSONB(astext_type=Text()), server_default=text("'{}'::jsonb"))
    description = Column(String)
    type = Column(String)

    user = relationship('User')
    organization = relationship('Organization')
    transaction = relationship('Transaction')
