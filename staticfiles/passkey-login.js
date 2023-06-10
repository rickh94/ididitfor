async function startLogin() {
  const dataEl = document.getElementById('passkey-data');
  const startLoginEndpoint = dataEl.dataset.startLoginEndpoint;
  const redirectTo = dataEl.dataset.redirectTo;
  const finishLoginEndpoint = dataEl.dataset.finishLoginEndpoint;

  const usernameElId = dataEl.dataset.usernameId;
  const username = document.getElementById(usernameElId).value;

  const body = new FormData();
  body.append('username', username);

  const res = await fetch(startLoginEndpoint, {
    method: 'POST',
    body
  });
  const loginOptions = await res.json();
  let loginInfo;
  try {
    loginInfo = await SimpleWebAuthnBrowser.startAuthentication(loginOptions);
  } catch (error) {
    console.error(error);
    Alpine.store('notification')
  }

  const verificationResp = await fetch(finishLoginEndpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(loginInfo)
  })

  if (verificationResp.status == 200) {
    window.location.replace(redirectTo);
  } else {
    alert('auth failed');
    // Alpine.store('notification').show("Auth Failure","Could not authenticate, please try again", 'failure');
    // window.location.replace();
  }
}
