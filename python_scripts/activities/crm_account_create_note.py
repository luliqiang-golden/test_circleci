"""CRM Account Create Note"""

from activities.activity_handler_class import ActivityHandler


class CRMAccountCreateNote(ActivityHandler):
    """CRM Account Create Note"""

    required_args = {
        'name', 'crm_account_id', 'description', 'detail'
    }
