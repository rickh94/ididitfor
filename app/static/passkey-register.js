async function startRegistration() {
  const dataEl = document.getElementById('passkey-data');
  const startRegistrationEndpoint = dataEl.dataset.startRegistrationEndpoint; 
  const finishRegistrationEndpoint = dataEl.dataset.finishRegistrationEndpoint;
  let res = await fetch(startRegistrationEndpoint, {
    method: 'GET',
  });

  let creationOptions = await res.json();
  console.log(creationOptions);

  let attResp;
  try {
    attResp = await SimpleWebAuthnBrowser.startRegistration(creationOptions);
  } catch (error) {
    Alpine.store('notification').notify('Registration Failed', 'Could not register device', 'error', false);
    console.log(error);
    return;
  }


  const verificationResponse = await fetch(finishRegistrationEndpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(attResp),
  });

  if (verificationResponse.ok) {
    Alpine.store('notification').notify('Registration Succeeded', 'You can now log in using just this device!', 'success');
  } else {
    Alpine.store('notification').notify('Registration Failed', 'Your device could not be registered', 'error');
  }
}

