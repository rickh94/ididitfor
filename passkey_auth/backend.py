import base64
import datetime

import webauthn
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from webauthn.helpers.exceptions import InvalidAuthenticationResponse
from webauthn.helpers.structs import AuthenticationCredential

from passkey_auth.models import PasskeyCredential

User = get_user_model()


class PasskeyBackend(BaseBackend):
    """
    Authenticate against passkey credentials.
    """

    def authenticate(self, request):
        auth_state = request.session.get("auth_state")
        if not auth_state:
            return None
        try:
            submitted_credential = AuthenticationCredential.parse_raw(
                request.body)
        except:
            return None
        if (
            datetime.datetime.fromtimestamp(auth_state["created"])
            + datetime.timedelta(minutes=5)
            < datetime.datetime.now()
        ):
            request.session["auth_state"] = None
            return None

        try:
            user = User.objects.get(pk=auth_state["user_id"])
        except User.DoesNotExist:
            return None

        stored_credential = user.credentials.get(
            credential_id=webauthn.base64url_to_bytes(submitted_credential.id),
        )

        expected_challenge = base64.b64decode(auth_state["challenge"])

        # TODO: un hardcode
        try:
            webauthn.verify_authentication_response(
                credential=submitted_credential,
                expected_challenge=expected_challenge,
                expected_origin="https://ididitfor.localhost",
                expected_rp_id="ididitfor.localhost",
                credential_public_key=stored_credential.credential_public_key,
                credential_current_sign_count=0,
            )
            request.session["auth_state"] = None
            return user
        except InvalidAuthenticationResponse:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
