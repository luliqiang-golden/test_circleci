class AuthError(Exception):
    """Error handler for auth0_authentication"""

    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


class ClientBadRequest(Exception):
    """Error handler for class_users and class_roles"""

    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


class EngineError(Exception):
    """Error handler for rule_engine"""

    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


class DatabaseError(Exception):
    """Error handler for db_functions"""

    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code
