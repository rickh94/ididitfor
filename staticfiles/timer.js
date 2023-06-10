document.addEventListener('alpine:init', function () {
  Alpine.store('timer', {
    secondsRemaining: 0,
    completed: false,
    started: false,
    ticker: null,
    ready: false,
    initialTime: null,

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
      this.secondsRemaining--;
      if (this.secondsRemaining <= 0) {
        this.pause();
        this.completed = true;
      };
    },

    reset() {
      this.init();
    },

    init() {
      let durationMins;
      try {
        durationMins = parseInt(document.getElementById('timer-data').dataset.durationMins);
      } catch (err) {
        alert('Invalid duration');
        console.log(err);
        return;
      }
      this.secondsRemaining = durationMins * 60;
      this.initialTime = durationMins * 60;
      this.completed = false;
      if (this.ticker) {
        clearInterval(this.ticker);
        this.ticker = null;
      }
      this.ready = true;
      this.started = false;
    },

    get mins() {
      const m =  Math.floor(this.secondsRemaining / 60);
      return m.toString().padStart(2, "0");
    },

    get secs() {
      const s = this.secondsRemaining % 60;
      return s.toString().padStart(2, "0");
    },

    get running() {
      return this.ticker != null;
    },

    get elapsedTimeSeconds() {
      return this.initialTime - this.secondsRemaining;
    },

    get elapsedTimeMins() {
      return Math.round(this.elapsedTimeSeconds / 60);
    },
  });

  Alpine.store('timer').init();
});
