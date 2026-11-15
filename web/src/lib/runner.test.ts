// Port of the Python version's tests/js/runner.test.js, case for case.
import { describe, expect, it } from 'vitest';

import { createRunner, type Reason } from './runner';

function setup(seconds: number[]) {
  const clock = { t: 1_000_000 };
  const runner = createRunner(
    seconds.map((s) => ({ seconds: s })),
    () => clock.t,
  );
  const events: [Reason, number][] = [];
  runner.subscribe((snap, reason) => events.push([reason, snap.index]));
  return { runner, events, advance: (s: number) => (clock.t += s * 1000) };
}

describe('createRunner', () => {
  it('nothing runs before start', () => {
    const { runner, advance } = setup([10]);
    advance(30);
    runner.tick();
    expect(runner.snapshot()).toMatchObject({ started: false, index: 0 });
  });

  it('start enters the first phase with its full duration', () => {
    const { runner } = setup([10, 5]);
    runner.start();
    expect(runner.snapshot()).toMatchObject({ started: true, remainingMs: 10_000, timed: true });
  });

  it('countdown follows the clock and advances when a phase ends', () => {
    const { runner, advance, events } = setup([10, 5]);
    runner.start();
    advance(4);
    runner.tick();
    expect(runner.snapshot().remainingMs).toBe(6_000);
    advance(6);
    runner.tick();
    expect(runner.snapshot()).toMatchObject({ index: 1, remainingMs: 5_000 });
    expect(events.at(-1)).toEqual(['phase', 1]);
  });

  it('a long gap catches up through several phases without drifting', () => {
    const { runner, advance, events } = setup([10, 5, 20]);
    runner.start();
    advance(17); // 10 + 5 elapsed, 2s into the third phase
    runner.tick();
    expect(runner.snapshot()).toMatchObject({ index: 2, remainingMs: 18_000 });
    expect(events.filter(([reason]) => reason === 'phase')).toHaveLength(1);
  });

  it('finishing the last phase reports finish once', () => {
    const { runner, advance, events } = setup([5]);
    runner.start();
    advance(60);
    runner.tick();
    runner.tick();
    expect(runner.snapshot().finished).toBe(true);
    expect(events.filter(([reason]) => reason === 'finish')).toHaveLength(1);
  });

  it('pause freezes the countdown and resume continues from there', () => {
    const { runner, advance } = setup([10]);
    runner.start();
    advance(3);
    runner.pause();
    advance(100);
    runner.tick();
    expect(runner.snapshot()).toMatchObject({ paused: true, remainingMs: 7_000 });
    runner.resume();
    advance(7);
    runner.tick();
    expect(runner.snapshot().finished).toBe(true);
  });

  it('toggle flips between paused and running', () => {
    const { runner } = setup([10]);
    runner.start();
    runner.toggle();
    expect(runner.snapshot().paused).toBe(true);
    runner.toggle();
    expect(runner.snapshot().paused).toBe(false);
  });

  it('skip jumps to the next phase with a fresh countdown', () => {
    const { runner, advance } = setup([10, 5]);
    runner.start();
    advance(2);
    runner.next();
    expect(runner.snapshot()).toMatchObject({ index: 1, remainingMs: 5_000 });
  });

  it('skipping while paused stays paused on the new phase', () => {
    const { runner, advance } = setup([10, 5]);
    runner.start();
    runner.pause();
    runner.next();
    advance(100);
    runner.tick();
    expect(runner.snapshot()).toMatchObject({ index: 1, paused: true, remainingMs: 5_000 });
  });

  it('skipping the last phase finishes the workout', () => {
    const { runner, events } = setup([10]);
    runner.start();
    runner.next();
    expect(runner.snapshot().finished).toBe(true);
    expect(events.at(-1)).toEqual(['finish', 1]);
  });

  it('restart puts the current phase back to its full duration', () => {
    const { runner, advance } = setup([10, 5]);
    runner.start();
    runner.next();
    advance(3);
    runner.restartPhase();
    expect(runner.snapshot()).toMatchObject({ index: 1, remainingMs: 5_000 });
  });

  it('previous once restarts the phase, twice in a row goes back one', () => {
    const { runner, advance } = setup([10, 10, 10]);
    runner.start();
    runner.next();
    runner.next();
    advance(4);
    runner.previous();
    expect(runner.snapshot()).toMatchObject({ index: 2, remainingMs: 10_000 });
    advance(1);
    runner.previous();
    expect(runner.snapshot().index).toBe(1);
  });

  it('previous presses far apart each just restart', () => {
    const { runner, advance } = setup([10, 10]);
    runner.start();
    runner.next();
    runner.previous();
    advance(5);
    runner.previous();
    expect(runner.snapshot().index).toBe(1);
  });

  it('previous on the first phase never goes below zero', () => {
    const { runner } = setup([10, 10]);
    runner.start();
    runner.previous();
    runner.previous();
    expect(runner.snapshot().index).toBe(0);
  });

  it('reset returns to the first phase, running', () => {
    const { runner } = setup([10, 5]);
    runner.start();
    runner.next();
    runner.pause();
    runner.restartWorkout();
    expect(runner.snapshot()).toMatchObject({ index: 0, paused: false, remainingMs: 10_000 });
  });

  it('a reps-based phase never advances by itself', () => {
    const { runner, advance } = setup([0, 5]);
    runner.start();
    advance(3600);
    runner.tick();
    expect(runner.snapshot()).toMatchObject({ index: 0, timed: false });
    runner.next();
    expect(runner.snapshot().index).toBe(1);
  });

  it('catching up stops at a reps-based phase', () => {
    const { runner, advance } = setup([5, 0, 5]);
    runner.start();
    advance(100);
    runner.tick();
    expect(runner.snapshot().index).toBe(1);
  });

  it('controls do nothing once finished', () => {
    const { runner, events } = setup([5]);
    runner.start();
    runner.next();
    const count = events.length;
    runner.pause();
    runner.next();
    runner.previous();
    runner.restartPhase();
    expect(events).toHaveLength(count);
  });
});
