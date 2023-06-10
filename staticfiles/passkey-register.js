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
    // Alpine.store('notification').show('Registration Failed', 'Could not register device', 'failure');
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
    alert("registration completed");
    // Alpine.store('notification').show('Registration Succeeded', 'You can now log in using just this device!', 'success');
  }
}

