// Workout timer core: pure and clock-injected, so it is testable and catches up exactly after the tab was
// frozen (phases chain from the previous end time instead of drifting). Port of the Python version's
// static/runner.js `createRunner`; the browser side (sound, lock screen) is in workout.ts.

export interface TimedPhase {
  /** Countdown length; 0 for a reps-based phase, which only advances on `next()`. */
  seconds: number;
}

export interface Snapshot {
  started: boolean;
  finished: boolean;
  paused: boolean;
  index: number;
  count: number;
  /** The current phase counts down. */
  timed: boolean;
  remainingMs: number;
}

export type Reason = 'start' | 'pause' | 'resume' | 'phase' | 'finish' | 'restart' | 'previous' | 'reset';
export type Listener = (snapshot: Snapshot, reason: Reason) => void;
export type Runner = ReturnType<typeof createRunner>;

/** Two "previous" presses closer than this go back one phase; one press restarts the current one. */
const DOUBLE_PRESS_MS = 2000;

export function createRunner(phases: TimedPhase[], now: () => number = Date.now) {
  const listeners: Listener[] = [];
  const state = {
    started: false,
    finished: false,
    paused: false,
    index: 0,
    endAt: null as number | null,
    remainingMs: 0,
    lastPreviousAt: -Infinity,
  };

  const isTimed = (i: number) => i < phases.length && phases[i].seconds > 0;
  const isActive = () => state.started && !state.finished;

  function remainingMs(): number {
    if (state.finished) return 0;
    return state.endAt === null ? state.remainingMs : Math.max(0, state.endAt - now());
  }

  function snapshot(): Snapshot {
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

  function notify(reason: Reason) {
    const snap = snapshot();
    listeners.forEach((listener) => listener(snap, reason));
  }

  function enter(index: number, startedAt: number) {
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
    notify('start');
  }

  function pause() {
    if (!isActive() || state.paused) return;
    state.remainingMs = remainingMs();
    state.endAt = null;
    state.paused = true;
    notify('pause');
  }

  function resume() {
    if (!isActive() || !state.paused) return;
    state.paused = false;
    if (isTimed(state.index)) state.endAt = now() + state.remainingMs;
    notify('resume');
  }

  function toggle() {
    if (state.paused) resume();
    else pause();
  }

  function next() {
    if (!isActive()) return;
    enter(state.index + 1, now());
    notify(state.finished ? 'finish' : 'phase');
  }

  function restartPhase() {
    if (!isActive()) return;
    enter(state.index, now());
    notify('restart');
  }

  /** Like a music player: once restarts this phase, twice in a row goes back one. */
  function previous() {
    if (!isActive()) return;
    const t = now();
    const doubled = t - state.lastPreviousAt < DOUBLE_PRESS_MS;
    state.lastPreviousAt = doubled ? -Infinity : t;
    enter(doubled ? Math.max(0, state.index - 1) : state.index, t);
    notify(doubled ? 'previous' : 'restart');
  }

  function restartWorkout() {
    if (!state.started) return;
    state.paused = false;
    enter(0, now());
    notify('reset');
  }

  /** Advance past every phase that has ended; call it often (and when the page becomes visible). */
  function tick() {
    if (!isActive() || state.endAt === null) return;
    let advanced = false;
    while (state.endAt !== null && now() >= state.endAt) {
      enter(state.index + 1, state.endAt);
      advanced = true;
    }
    if (advanced) notify(state.finished ? 'finish' : 'phase');
  }

  return {
    snapshot,
    subscribe: (listener: Listener) => listeners.push(listener),
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
