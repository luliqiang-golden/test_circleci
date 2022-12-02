"""Create a new user in the organization"""

import re
import random
import string

from auth0.v3 import Auth0Error
from db_functions import insert_into_db
from class_errors import ClientBadRequest
from activities.activity_handler_class import ActivityHandler
from auth0_authentication import auth0_client, AUTH0_CONNECTION, auth0_reset_pw


class CreateUser(ActivityHandler):
    """
    Create a new user in the organization.
    Will also create a user in Auth0 if one doesn't exist for this email yet.

    :param user_name: User's full name
    :param email: User's email address
    :param enabled: Is the user enabled or not?
    :type enabled: boolean

    :returns: Object with activity_id and user_id fields

    :raises: 400 incorrect_email_format
    :raises: 500 auth0_create_error
    :raises: 500 auth0_pw_reset_error
    """

    required_args = {
        'name',
        'user_name',
        'email',
        'enabled',
        'job_title'
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """Implementation function for the user_create activity"""

        cls.check_required_args(args)

        if not re.match(r"[^@]+@[^@]+\.[^@]+", args['email']):
            raise ClientBadRequest({
                "code":
                "incorrect_email_format",
                "message":
                "Email address does not appear to be properly formatted."
            }, 400)

        user_email = args["email"].lower()

        user_object = {
            'organization_id': args["organization_id"],
            "created_by": args["created_by"],
            "name": args['user_name'],
            "email": user_email,
            "enabled": args["enabled"],
            "job_title":  args["job_title"],
        }

        user_result = insert_into_db('users', user_object)

        auth0 = auth0_client()

        # long random password so the new user has to do a PW reset
        new_password = ''.join(
            random.choice(string.ascii_letters + string.digits)
            for _ in range(20))

        auth0_user = {
            "connection": AUTH0_CONNECTION,
            "email": user_email,
            "password": new_password
        }

        try:
            auth0.users.create(auth0_user)
        except Auth0Error as error:

            # if user already exists (409 error), that's fine
            # otherwise throw an error
            if error.status_code != 409:
                raise ClientBadRequest({
                    "code": "auth0_create_error",
                    "message": "Auth0 returned an error when creating the user"
                }, 500)

        try:
            auth0_reset_pw(user_email)
        except Auth0Error:
            raise ClientBadRequest({
                "code": "auth0_pw_reset_error",
                "message": "Auth0 returned an error when attempting a password reset"
            }, 500)

        args["user_id"] = user_result["id"]

        activity_result = cls.insert_activity_into_db(args)

        return {
            "activity_id": activity_result["id"],
            "user_id": user_result["id"]
        }
