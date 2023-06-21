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

  Alpine.store('nav', {
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

  document.addEventListener('notify', event => {
    Alpine.store('notification').notify(event.detail.title, event.detail.message, event.detail.variant, event.detail.autoHide);
  });

    Alpine.directive('localtime', (el, {expression} )=> {
      el.textContent = new Date(expression).toLocaleString(undefined, { hour: 'numeric', minute: 'numeric', hour12: true });
    });

    Alpine.directive('localdate', (el, {expression}) => {
      el.textContent = new Date(expression).toLocaleString(undefined, {
        day: "numeric",
        year: "numeric",
        month: "short",
      });
    });
});

function closeDjangoMessages() {
  document.querySelectorAll('[data-django-message]').forEach((el) => {
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
})

document.addEventListener('htmx:afterSettle', () => {
  Alpine.store('nav').closeNav();
  setTimeout(() => {
    Alpine.store('location').update();
  })
  closeDjangoMessages();
})
