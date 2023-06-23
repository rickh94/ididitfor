document.addEventListener("alpine:init", () => {
  Alpine.store("location", {
    path: "",

    update() {
      setTimeout(() => {
        this.path = window.location.pathname;
      }, 50);
    },
  });
  Alpine.store("location").update();

  Alpine.store("nav", {
    open: false,

    openNav() {
      this.open = true;
    },

    closeNav() {
      this.open = false;
    },

    toggleNav() {
      this.open = !this.open;
    },
  });

  document.addEventListener("updateLocation", () => {
    Alpine.store("location").update();
  });

  Alpine.store("notification", {
    messages: [],
    notify(title, text, level, autoHide = true) {
      const messageId = Math.random().toString(36).substring(7);
      this.messages.push({
        title,
        messageId,
        text,
        level,
      });

      if (autoHide) {
        setTimeout(() => {
          this.clearMessage(messageId);
        }, 2000);
      }
    },

    clearMessage(messageId) {
      this.messages = this.messages.filter(
        (message) => message.messageId !== messageId
      );
    },
  });

  document.addEventListener("notify", (event) => {
    Alpine.store("notification").notify(
      event.detail.title,
      event.detail.message,
      event.detail.variant,
      event.detail.autoHide
    );
  });

  Alpine.directive("localtime", (el, { expression }) => {
    el.textContent = new Date(expression).toLocaleString(undefined, {
      hour: "numeric",
      minute: "numeric",
      hour12: true,
    });
  });

  Alpine.directive("localdate", (el, { expression }) => {
    el.textContent = new Date(expression).toLocaleString(undefined, {
      day: "numeric",
      year: "numeric",
      month: "short",
    });
  });


});

function closeDjangoMessages() {
  document.querySelectorAll("[data-django-message]").forEach((el) => {
    let i = 0;
    if (el.dataset.autoHide) {
      setTimeout(() => {
        el.remove();
      }, 1500 + i);
      i += 1000;
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  closeDjangoMessages();
});

document.addEventListener("htmx:afterSettle", () => {
  Alpine.store("nav").closeNav();
  setTimeout(() => {
    Alpine.store("location").update();
  });
  closeDjangoMessages();
});

async function startLogin() {
  const dataEl = document.getElementById("passkey-data");
  if (!dataEl) {
    Alpine.store("notification").notify(
      "Error",
      "That's not supported on this page",
      "error"
    );
    return;
  }
  const startLoginEndpoint = dataEl.dataset.startLoginEndpoint;
  const redirectTo = dataEl.dataset.redirectTo;
  const finishLoginEndpoint = dataEl.dataset.finishLoginEndpoint;
  if (!startLoginEndpoint || !redirectTo || !finishLoginEndpoint) {
    Alpine.store("notification").notify(
      "Error",
      "That's not supported on this page",
      "error"
    );
    return;
  }

  const usernameElId = dataEl.dataset.usernameId;
  if (!usernameElId) {
    Alpine.store("notification").notify(
      "Error",
      "That's not supported on this page",
      "error"
    );
    return;
  }

  const username = document.getElementById(usernameElId).value;
  if (!username) {
    Alpine.store("notification").notify(
      "Username Required",
      "Please enter your username to login with a passkey",
      "error"
    );
    return;
  }

  const startLoginBody = new FormData();
  startLoginBody.append("username", username);

  const res = await fetch(startLoginEndpoint, {
    method: "POST",
    body: startLoginBody,
  });
  const loginOptions = await res.json();
  let loginInfo;
  try {
    loginInfo = await SimpleWebAuthnBrowser.startAuthentication(loginOptions);
  } catch (error) {
    console.error(error);
    Alpine.store("notification").notify(
      "Auth Failure",
      "Could not log you in, please try again or use your password",
      "error"
    );
  }

  const verificationResp = await fetch(finishLoginEndpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(loginInfo),
  });

  if (verificationResp.status == 200) {
    window.location.replace(redirectTo);
  } else {
    Alpine.store("notification").notify(
      "Auth Failure",
      "Could not authenticate, please try again",
      "error"
    );
    window.location.replace();
  }
}


async function startRegistration() {
  const dataEl = document.getElementById('passkey-data');
  if (!dataEl) {
    Alpine.store("notification").notify(
      "Error",
      "That's not supported on this page",
      "error"
    );
    return;
  }
  const startRegistrationEndpoint = dataEl.dataset.startRegistrationEndpoint; 
  const finishRegistrationEndpoint = dataEl.dataset.finishRegistrationEndpoint;

  if (!startRegistrationEndpoint || !finishRegistrationEndpoint) {
    Alpine.store("notification").notify(
      "Error",
      "That's not supported on this page",
      "error"
    );
    return;
  }

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


