import base64
import datetime

import webauthn
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from webauthn.helpers.exceptions import InvalidRegistrationResponse
from webauthn.helpers.structs import (
    PublicKeyCredentialDescriptor,
    RegistrationCredential,
)

from .models import PasskeyCredential

User = get_user_model()


@require_GET
@login_required
def user_profile(request):
    return render(request, "user_profile.html", {})


@require_GET
@login_required
def start_passkey_registration(request):
    pcco = webauthn.generate_registration_options(
        rp_id=settings.WEBAUTHN_RP_ID,
        rp_name=settings.WEBAUTHN_SERVER_NAME,
        user_id=str(request.user.id),
        user_name=request.user.username,
    )
    challenge = base64.b64encode(pcco.challenge).decode("utf-8")
    request.session["registration_state"] = {
        "challenge": challenge,
        "created": datetime.datetime.now().timestamp(),
    }

    return HttpResponse(webauthn.options_to_json(pcco), content_type="application/json")


@require_POST
@csrf_exempt
@login_required
def finish_passkey_registration(request):
    registration_credential = RegistrationCredential.parse_raw(request.body)

    try:
        challenge_info = request.session["registration_state"]
        if (
            datetime.datetime.fromtimestamp(challenge_info["created"])
            + datetime.timedelta(minutes=5)
            < datetime.datetime.now()
        ):
            request.session["registration_state"] = None
            return HttpResponseBadRequest("Expired Challenge")
        expected = base64.b64decode(challenge_info["challenge"])
        verification = webauthn.verify_registration_response(
            credential=registration_credential,
            expected_challenge=expected,
            expected_rp_id=settings.WEBAUTHN_RP_ID,
            expected_origin=settings.WEBAUTHN_ORIGIN,
        )
    except InvalidRegistrationResponse as e:
        print(e)
        return HttpResponseBadRequest("Invalid registration response")

    credential = PasskeyCredential(
        user=request.user,
        credential_id=verification.credential_id,
        credential_public_key=verification.credential_public_key,
        current_sign_count=0,
    )
    credential.save()

    return HttpResponse("Passkey Created")


@require_POST
@csrf_exempt
def start_passkey_login(request):
    username = request.POST.get("username")
    if not username:
        return HttpResponseBadRequest("Username required")
    try:
        user = User.objects.get(username=username.lower().strip())
    except User.DoesNotExist:
        return HttpResponseBadRequest("Cannot log in with username")
    # TODO: notification on frontend

    allowed_credentials = [
        PublicKeyCredentialDescriptor(id=credential.credential_id)
        for credential in user.credentials.all()
    ]

    authentication_options = webauthn.generate_authentication_options(
        rp_id=settings.WEBAUTHN_RP_ID,
        allow_credentials=allowed_credentials,
    )

    request.session["auth_state"] = {
        "challenge": base64.b64encode(authentication_options.challenge).decode("utf-8"),
        "created": datetime.datetime.now().timestamp(),
        "user_id": user.id,
    }

    return HttpResponse(
        webauthn.options_to_json(authentication_options),
        content_type="application/json",
    )


@require_POST
@csrf_exempt
def finish_passkey_login(request):
    user = authenticate(request)
    if user is not None:
        login(request, user)
        return HttpResponse("Login successful")
    else:
        return HttpResponseBadRequest("Login Failed")
