// The browser side of a guided run (the Python version's static/runner.js `init`): a beep on every phase
// change, the screen kept on, and lock-screen controls. Those controls only appear while audio plays, so a
// silent looping track keeps the page "playing" with the screen off.
import type { Phase } from './phases';
import { createRunner, type Snapshot } from './runner';

/** Browsers ignore media sessions for audio shorter than about 5 s. */
const SILENCE_SECONDS = 10;
const TICK_MS = 250;
const MEDIA_ACTIONS: MediaSessionAction[] = ['play', 'pause', 'nexttrack', 'previoustrack', 'stop'];

export interface WorkoutOptions {
  /** Album line on the lock screen. */
  name: string;
  /** Square artwork for the lock screen. */
  icon: string;
  /** Called on every change and every tick, with the current state. */
  onUpdate: (snapshot: Snapshot) => void;
  /** Called by the lock screen's stop button. */
  onStop: () => void;
}

export type Workout = ReturnType<typeof createWorkout>;

export function createWorkout(phases: Phase[], options: WorkoutOptions) {
  const runner = createRunner(phases);
  let audio: AudioContext | null = null;
  let keepAlive: HTMLAudioElement | null = null;
  let wakeLock: WakeLockSentinel | null = null;
  let ticker: ReturnType<typeof setInterval> | undefined;

  function beep() {
    if (!audio) return;
    const oscillator = audio.createOscillator();
    oscillator.frequency.value = 880;
    oscillator.connect(audio.destination);
    oscillator.start();
    oscillator.stop(audio.currentTime + 0.15);
  }

  async function holdWakeLock() {
    try {
      if (!('wakeLock' in navigator) || wakeLock) return;
      wakeLock = await navigator.wakeLock.request('screen');
      wakeLock.addEventListener('release', () => (wakeLock = null));
    } catch {
      // Unsupported or page hidden: the lock-screen controls still work.
    }
  }

  function updateMediaSession(snap: Snapshot) {
    const session = navigator.mediaSession;
    if (!session) return;
    const phase = phases[snap.index];
    session.metadata = new MediaMetadata({
      title: phase.title,
      artist: phase.subtitle,
      album: options.name,
      artwork: [{ src: options.icon, sizes: '512x512', type: 'image/png' }],
    });
    session.playbackState = snap.paused ? 'paused' : 'playing';
    try {
      if (snap.timed) {
        const duration = phase.seconds;
        const position = Math.max(0, Math.min(duration, duration - snap.remainingMs / 1000));
        session.setPositionState({ duration, position, playbackRate: 1 });
      } else {
        session.setPositionState();
      }
    } catch {
      // Position display is optional.
    }
  }

  function setMediaHandlers(on: boolean) {
    const session = navigator.mediaSession;
    if (!session) return;
    const handlers: Record<string, () => void> = {
      play: runner.resume,
      pause: runner.pause,
      nexttrack: runner.next,
      previoustrack: runner.previous,
      stop: options.onStop,
    };
    for (const action of MEDIA_ACTIONS) {
      try {
        session.setActionHandler(action, on ? handlers[action] : null);
      } catch {
        // This browser does not support that action.
      }
    }
    if (!on) {
      session.metadata = null;
      session.playbackState = 'none';
    }
  }

  function onVisible() {
    const snap = runner.snapshot();
    if (document.visibilityState !== 'visible' || !snap.started || snap.finished) return;
    holdWakeLock();
    runner.tick();
    options.onUpdate(runner.snapshot());
  }

  /** Stop the clock, the audio, the wake lock and the lock-screen controls. */
  function release() {
    clearInterval(ticker);
    keepAlive?.pause();
    wakeLock?.release().catch(() => {});
    setMediaHandlers(false);
    document.removeEventListener('visibilitychange', onVisible);
  }

  /** Start; must run inside a tap, since browsers only start audio from a user gesture. */
  function begin() {
    if (runner.snapshot().started) return;
    audio = new AudioContext();
    audio.resume();
    keepAlive = new Audio(silentWavUrl());
    keepAlive.loop = true;
    keepAlive.play().catch(() => {});
    setMediaHandlers(true);
    holdWakeLock();
    document.addEventListener('visibilitychange', onVisible);
    ticker = setInterval(() => {
      runner.tick();
      options.onUpdate(runner.snapshot());
    }, TICK_MS);
    runner.start();
  }

  runner.subscribe((snap, reason) => {
    if (reason === 'phase' || reason === 'finish') beep();
    if (snap.finished) release();
    else updateMediaSession(snap);
    options.onUpdate(snap);
  });

  return { ...runner, begin, release };
}

/** A silent 8 kHz 8-bit mono WAV, as an object URL. */
function silentWavUrl(): string {
  const rate = 8000;
  const samples = rate * SILENCE_SECONDS;
  const buffer = new ArrayBuffer(44 + samples);
  const view = new DataView(buffer);
  const text = (offset: number, value: string) =>
    [...value].forEach((c, i) => view.setUint8(offset + i, c.charCodeAt(0)));
  text(0, 'RIFF');
  view.setUint32(4, 36 + samples, true);
  text(8, 'WAVEfmt ');
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, 1, true);
  view.setUint32(24, rate, true);
  view.setUint32(28, rate, true);
  view.setUint16(32, 1, true);
  view.setUint16(34, 8, true);
  text(36, 'data');
  view.setUint32(40, samples, true);
  new Uint8Array(buffer, 44).fill(128);
  return URL.createObjectURL(new Blob([buffer], { type: 'audio/wav' }));
}
