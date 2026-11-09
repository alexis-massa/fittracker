// Workout timer that runs entirely in the browser, so it keeps going (and answers
// lock-screen controls) with no server round trip. createRunner is pure and testable.
(function (root) {
  "use strict";

  const DOUBLE_PRESS_MS = 2000;
  const SILENCE_SECONDS = 10; // browsers ignore media sessions for audio shorter than ~5s
  const MEDIA_ACTIONS = ["play", "pause", "nexttrack", "previoustrack", "stop"];

  function createRunner(phases, now = Date.now) {
    const listeners = [];
    const state = {
      started: false,
      finished: false,
      paused: false,
      index: 0,
      endAt: null,
      remainingMs: 0,
      lastPreviousAt: -Infinity,
    };

    const isTimed = (i) => i < phases.length && phases[i].seconds > 0;
    const isActive = () => state.started && !state.finished;

    function remainingMs() {
      if (state.finished) return 0;
      return state.endAt === null ? state.remainingMs : Math.max(0, state.endAt - now());
    }

    function snapshot() {
      return {
        started: state.started,
        finished: state.finished,
        paused: state.paused,
        index: state.index,
        count: phases.length,
        timed: isTimed(state.index),
        remainingMs: remainingMs(),
      };
    }

    function notify(reason) {
      const snap = snapshot();
      listeners.forEach((listener) => listener(snap, reason));
    }

    function enter(index, startedAt) {
      state.index = index;
      state.finished = index >= phases.length;
      state.remainingMs = state.finished ? 0 : phases[index].seconds * 1000;
      const runs = isTimed(index) && !state.paused;
      state.endAt = runs ? startedAt + state.remainingMs : null;
    }

    function start() {
      if (state.started) return;
      state.started = true;
      enter(0, now());
      notify("start");
    }

    function pause() {
      if (!isActive() || state.paused) return;
      state.remainingMs = remainingMs();
      state.endAt = null;
      state.paused = true;
      notify("pause");
    }

    function resume() {
      if (!isActive() || !state.paused) return;
      state.paused = false;
      if (isTimed(state.index)) state.endAt = now() + state.remainingMs;
      notify("resume");
    }

    function toggle() {
      if (state.paused) resume();
      else pause();
    }

    function next() {
      if (!isActive()) return;
      enter(state.index + 1, now());
      notify(state.finished ? "finish" : "phase");
    }

    function restartPhase() {
      if (!isActive()) return;
      enter(state.index, now());
      notify("restart");
    }

    // Like a music player: once restarts this step, twice in a row goes back one.
    function previous() {
      if (!isActive()) return;
      const t = now();
      const doubled = t - state.lastPreviousAt < DOUBLE_PRESS_MS;
      state.lastPreviousAt = doubled ? -Infinity : t;
      enter(doubled ? Math.max(0, state.index - 1) : state.index, t);
      notify(doubled ? "previous" : "restart");
    }

    function restartWorkout() {
      if (!state.started) return;
      state.paused = false;
      enter(0, now());
      notify("reset");
    }

    // Phases chain from the previous end time, so a gap (throttled or frozen tab)
    // catches up exactly instead of drifting.
    function tick() {
      if (!isActive() || state.endAt === null) return;
      let advanced = false;
      while (state.endAt !== null && now() >= state.endAt) {
        enter(state.index + 1, state.endAt);
        advanced = true;
      }
      if (advanced) notify(state.finished ? "finish" : "phase");
    }

    return {
      snapshot,
      subscribe: (listener) => listeners.push(listener),
      start,
      pause,
      resume,
      toggle,
      next,
      restartPhase,
      previous,
      restartWorkout,
      tick,
    };
  }

  const api = { createRunner };

  if (typeof module !== "undefined" && module.exports) {
    module.exports = api;
    return;
  }

  // ---------------------------------------------------------------------------
  // Browser layer
  // ---------------------------------------------------------------------------

  function silentWavUrl() {
    const rate = 8000;
    const samples = rate * SILENCE_SECONDS;
    const buffer = new ArrayBuffer(44 + samples);
    const view = new DataView(buffer);
    const text = (offset, value) =>
      [...value].forEach((c, i) => view.setUint8(offset + i, c.charCodeAt(0)));
    text(0, "RIFF");
    view.setUint32(4, 36 + samples, true);
    text(8, "WAVEfmt ");
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, 1, true);
    view.setUint32(24, rate, true);
    view.setUint32(28, rate, true);
    view.setUint16(32, 1, true);
    view.setUint16(34, 8, true);
    text(36, "data");
    view.setUint32(40, samples, true);
    new Uint8Array(buffer, 44).fill(128);
    return URL.createObjectURL(new Blob([buffer], { type: "audio/wav" }));
  }

  function mmss(ms) {
    const seconds = Math.ceil(ms / 1000);
    return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`;
  }

  function init(config) {
    const runner = createRunner(config.phases);
    const handlers = {};
    let audioContext = null;
    let keepAlive = null;
    let wakeLock = null;
    let ticker = null;

    function renderClock() {
      const element = document.getElementById("run-clock");
      if (element) element.textContent = mmss(runner.snapshot().remainingMs);
    }

    function syncServer(snap) {
      try {
        root.emitEvent("run_state", {
          index: snap.index,
          paused: snap.paused,
          started: snap.started,
        });
      } catch (error) {
        // Offline while locked: visibilitychange re-syncs when the page is back.
      }
    }

    function beep() {
      if (!audioContext) return;
      const oscillator = audioContext.createOscillator();
      oscillator.frequency.value = 880;
      oscillator.connect(audioContext.destination);
      oscillator.start();
      oscillator.stop(audioContext.currentTime + 0.15);
    }

    async function holdWakeLock() {
      try {
        if (!("wakeLock" in navigator) || wakeLock) return;
        wakeLock = await navigator.wakeLock.request("screen");
        wakeLock.addEventListener("release", () => (wakeLock = null));
      } catch (error) {
        // Unsupported or page hidden: the lock-screen controls still work.
      }
    }

    function updateMediaSession(snap) {
      const session = navigator.mediaSession;
      if (!session) return;
      const phase = config.phases[snap.index];
      session.metadata = new MediaMetadata({
        title: phase.title,
        artist: phase.subtitle,
        album: config.name,
        artwork: [{ src: config.icon, sizes: "512x512", type: "image/png" }],
      });
      session.playbackState = snap.paused ? "paused" : "playing";
      try {
        if (snap.timed) {
          const duration = phase.seconds;
          const position = Math.min(duration, duration - snap.remainingMs / 1000);
          session.setPositionState({ duration, position: Math.max(0, position), playbackRate: 1 });
        } else {
          session.setPositionState();
        }
      } catch (error) {
        // Position display is optional.
      }
    }

    function registerMediaHandlers() {
      if (!navigator.mediaSession) return;
      Object.assign(handlers, {
        play: runner.resume,
        pause: runner.pause,
        nexttrack: runner.next,
        previoustrack: runner.previous,
        stop,
      });
      MEDIA_ACTIONS.forEach((action) => {
        try {
          navigator.mediaSession.setActionHandler(action, handlers[action]);
        } catch (error) {
          // This browser doesn't support that action.
        }
      });
    }

    function release() {
      clearInterval(ticker);
      if (keepAlive) keepAlive.pause();
      if (wakeLock) wakeLock.release().catch(() => {});
      const session = navigator.mediaSession;
      if (!session) return;
      MEDIA_ACTIONS.forEach((action) => {
        try {
          session.setActionHandler(action, null);
        } catch (error) {
          // Nothing to clear.
        }
      });
      session.metadata = null;
      session.playbackState = "none";
    }

    function stop() {
      release();
      root.location.href = config.backUrl;
    }

    // Must run inside a click: browsers only allow audio to start from a user gesture.
    function begin() {
      if (runner.snapshot().started) return;
      audioContext = new (root.AudioContext || root.webkitAudioContext)();
      audioContext.resume();
      // A silent looping track is what makes the OS show lock-screen controls and
      // keeps the page running while the screen is off.
      keepAlive = new Audio(silentWavUrl());
      keepAlive.loop = true;
      keepAlive.play().catch(() => {});
      registerMediaHandlers();
      holdWakeLock();
      ticker = setInterval(() => {
        runner.tick();
        renderClock();
      }, 250);
      runner.start();
    }

    runner.subscribe((snap, reason) => {
      if (reason === "phase" || reason === "finish") beep();
      if (snap.finished) release();
      else updateMediaSession(snap);
      syncServer(snap);
      renderClock();
    });

    document.addEventListener("visibilitychange", () => {
      const snap = runner.snapshot();
      if (document.visibilityState !== "visible" || !snap.started || snap.finished) return;
      holdWakeLock();
      runner.tick();
      renderClock();
      syncServer(runner.snapshot());
    });

    Object.assign(api, {
      begin,
      stop,
      toggle: runner.toggle,
      next: runner.next,
      restartPhase: runner.restartPhase,
      restartWorkout: runner.restartWorkout,
      handlers,
    });
  }

  root.FitRunner = Object.assign(api, { init });
})(typeof window !== "undefined" ? window : globalThis);
