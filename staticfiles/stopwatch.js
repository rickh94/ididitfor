document.addEventListener('alpine:init', function () {
  Alpine.store('stopwatch', {
    secondsPassed: 0,
    started: false,
    ticker: null,
    ready: false,

    start() {
      this.ticker = setInterval(() => {
        this.tick();
      }, 1000);
      this.started = true;
    },

    pause() {
      clearInterval(this.ticker);
      this.ticker = null;
    },

    tick() {
      this.secondsPassed +=1;
    },

    reset() {
      this.init();
    },

    init() {
      this.secondsPassed = 0;
      if (this.ticker) {
        clearInterval(this.ticker);
        this.ticker = null;
      }
      this.ready = true;
      this.started = false;
    },

    get mins() {
      const m =  Math.floor(this.secondsPassed / 60);
      return m.toString().padStart(2, "0");
    },

    get secs() {
      const s = Math.floor(this.secondsPassed % 60);
      return s.toString().padStart(2, "0");
    },

    get running() {
      return this.ticker != null;
    },

    get elapsedTimeMins() {
      return Math.round(this.secondsPassed / 60);
    },

  });

  Alpine.store('stopwatch').init();
});
