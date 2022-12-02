"""create_currencies_table

Revision ID: 13fc696bc0df
Revises: b131159a37c9
Create Date: 2021-09-30 11:45:43.795072

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = '13fc696bc0df'
down_revision = 'b131159a37c9'
branch_labels = None
depends_on = None


CURRENCIES = [
    {
        'name': 'Canadian Dollar', 
        'alphabetic_code': 'CAD',
        'minor_unit': 2,
        'sign': 'CA$',
        'entity': [
            'Canada'
        ]
    },
    {
        'name': 'Colombian Peso', 
        'alphabetic_code': 'COP',
        'minor_unit': 2,
        'sign': 'COL$', # Currently we are using "COP" as sign for this currency which seems to be wrong. To cross check visit https://en.wikipedia.org/wiki/Colombian_peso
        'entity': [
            'Colombia'
        ]
    },
    {
        'name': 'Argentine Peso', 
        'alphabetic_code': 'ARS',
        'minor_unit': 2,
        'sign': '$', # This is conflicting with USD sign.
        'entity': [
            'Argentina'
        ]
    },
    {
        'name': 'Danish Krone', 
        'alphabetic_code': 'DKK',
        'minor_unit': 2,
        'sign': 'kr.', # https://en.wikipedia.org/wiki/Danish_krone
        'entity': [
            'Denmark',
            'Faroe Islands',
            'Greenland'
        ]
    },
    {
        'name': 'Rand', 
        'alphabetic_code': 'ZAR',
        'minor_unit': 2,
        'sign': 'R', # https://en.wikipedia.org/wiki/South_African_rand
        'entity': [
            'Lesotho',
            'Namibia',
            'South Africa'
        ]
    },
    {
        'name': 'US Dollar', 
        'alphabetic_code': 'USD',
        'minor_unit': 2,
        'sign': '$', # This is conflicting with 'Argentine Peso' sign.
        'entity': [
            'American Samoa',
            'Bonaire, Sint Eustatius and Saba',
            'British Indian Ocean Territory',
            'Ecuador',
            'El Salvador',
            'Guam',
            'Haiti',
            'Marshall Islands',
            'Federated States of Micronesia',
            'Northern Mariana Islands',
            'Palau',
            'Panama',
            'Puerto Rico',
            'Timor-Leste',
            'Turks and Caicos Islands',
            'United States Minor Outlying Islands',
            'United States of America',
            'Virgin Islands',
        ]
    },
    {   
        'name': 'Euro', 
        'alphabetic_code': 'EUR',
        'minor_unit': 2,
        'sign': '€',
        'entity': [
            'Åland Island',
            'Andorra',
            'Austria',
            'Belgium',
            'Cyprus',
            'Estonia',
            'European Union',
            'Finland',
            'France',
            'French Guiana',
            'French Southern Territories',
            'Germany',
            'Greece',
            'Guadeloupe',
            'Holy See',
            'Ireland',
            'Italy',
            'Latvia',
            'Lithuania',
            'Luxembourg',
            'Malta',
            'Martinique',
            'Mayotte',
            'Monaco',
            'Montenegro',
            'Netherlands',
            'Portugal',
            'Reunion',
            'Saint Barthelemy',
            'Saint Martin (French part)',
            'Saint Pierre and Miquelon',
            'San Marino',
            'Slovakia',
            'Spain',
        ]
    }
]

def upgrade():

    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    tables = inspector.get_table_names()

    if ('currencies' not in tables):
        '''Creates "currencies" table and populates fixtures data into it'''
        op.create_table(
            'currencies',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('alphabetic_code', sa.String(), unique=True, nullable=False),
            sa.Column('minor_unit', sa.Integer, nullable=False),
            sa.Column('sign', sa.String(), nullable=False),
            sa.Column('entity', sa.ARRAY(sa.String), nullable=False), # "entity" column is equivalent to country/territory
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        )
        connection = op.get_bind()
        for obj in CURRENCIES:
            connection.execute(
                f'''
                INSERT INTO currencies (
                    name, 
                    alphabetic_code, 
                    minor_unit,
                    sign,
                    entity
                )
                VALUES (
                    '{obj.get('name')}',
                    '{obj.get('alphabetic_code')}', 
                    '{obj.get('minor_unit')}',
                    '{obj.get('sign')}',
                    ARRAY {obj.get('entity')}
                )
                '''
            )


def downgrade():
    '''Drops "currencies" table'''
    op.drop_table('currencies')
