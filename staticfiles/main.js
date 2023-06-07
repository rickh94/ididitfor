document.addEventListener('alpine:init', () => {
  Alpine.store('location', {
    path: '',

    update() {
      setTimeout(() => {

        this.path = window.location.pathname;
      }, 50);
    }
  });
  Alpine.store('location').update();

  document.addEventListener('updateLocation', () => {
    Alpine.store('location').update();
  });
})
