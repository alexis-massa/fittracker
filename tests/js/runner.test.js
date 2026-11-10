const test = require("node:test");
const assert = require("node:assert/strict");
const { createRunner } = require("../../static/runner.js");

function setup(seconds) {
  const clock = { t: 1_000_000 };
  const runner = createRunner(
    seconds.map((s) => ({ seconds: s })),
    () => clock.t,
  );
  const events = [];
  runner.subscribe((snap, reason) => events.push([reason, snap.index]));
  return { clock, runner, events, advance: (s) => (clock.t += s * 1000) };
}

test("nothing runs before start", () => {
  const { runner, advance } = setup([10]);
  advance(30);
  runner.tick();
  assert.equal(runner.snapshot().started, false);
  assert.equal(runner.snapshot().index, 0);
});

test("start enters the first phase with its full duration", () => {
  const { runner } = setup([10, 5]);
  runner.start();
  const snap = runner.snapshot();
  assert.equal(snap.started, true);
  assert.equal(snap.remainingMs, 10_000);
  assert.equal(snap.timed, true);
});

test("countdown follows the clock and advances when a phase ends", () => {
  const { runner, advance, events } = setup([10, 5]);
  runner.start();
  advance(4);
  runner.tick();
  assert.equal(runner.snapshot().remainingMs, 6_000);
  advance(6);
  runner.tick();
  assert.equal(runner.snapshot().index, 1);
  assert.equal(runner.snapshot().remainingMs, 5_000);
  assert.deepEqual(events.at(-1), ["phase", 1]);
});

test("a long gap catches up through several phases without drifting", () => {
  const { runner, advance, events } = setup([10, 5, 20]);
  runner.start();
  advance(17); // 10 + 5 elapsed, 2s into the third phase
  runner.tick();
  assert.equal(runner.snapshot().index, 2);
  assert.equal(runner.snapshot().remainingMs, 18_000);
  assert.equal(events.filter(([reason]) => reason === "phase").length, 1);
});

test("finishing the last phase reports finish once", () => {
  const { runner, advance, events } = setup([5]);
  runner.start();
  advance(60);
  runner.tick();
  runner.tick();
  assert.equal(runner.snapshot().finished, true);
  assert.equal(events.filter(([reason]) => reason === "finish").length, 1);
});

test("pause freezes the countdown and resume continues from there", () => {
  const { runner, advance } = setup([10]);
  runner.start();
  advance(3);
  runner.pause();
  advance(100);
  runner.tick();
  assert.equal(runner.snapshot().paused, true);
  assert.equal(runner.snapshot().remainingMs, 7_000);
  runner.resume();
  advance(7);
  runner.tick();
  assert.equal(runner.snapshot().finished, true);
});

test("toggle flips between paused and running", () => {
  const { runner } = setup([10]);
  runner.start();
  runner.toggle();
  assert.equal(runner.snapshot().paused, true);
  runner.toggle();
  assert.equal(runner.snapshot().paused, false);
});

test("skip jumps to the next phase with a fresh countdown", () => {
  const { runner, advance } = setup([10, 5]);
  runner.start();
  advance(2);
  runner.next();
  assert.equal(runner.snapshot().index, 1);
  assert.equal(runner.snapshot().remainingMs, 5_000);
});

test("skipping while paused stays paused on the new phase", () => {
  const { runner, advance } = setup([10, 5]);
  runner.start();
  runner.pause();
  runner.next();
  advance(100);
  runner.tick();
  assert.equal(runner.snapshot().index, 1);
  assert.equal(runner.snapshot().paused, true);
  assert.equal(runner.snapshot().remainingMs, 5_000);
});

test("skipping the last phase finishes the workout", () => {
  const { runner, events } = setup([10]);
  runner.start();
  runner.next();
  assert.equal(runner.snapshot().finished, true);
  assert.deepEqual(events.at(-1), ["finish", 1]);
});

test("restart puts the current phase back to its full duration", () => {
  const { runner, advance } = setup([10, 5]);
  runner.start();
  runner.next();
  advance(3);
  runner.restartPhase();
  assert.equal(runner.snapshot().index, 1);
  assert.equal(runner.snapshot().remainingMs, 5_000);
});

test("previous once restarts the phase, twice in a row goes back one", () => {
  const { runner, advance } = setup([10, 10, 10]);
  runner.start();
  runner.next();
  runner.next();
  advance(4);
  runner.previous();
  assert.equal(runner.snapshot().index, 2);
  assert.equal(runner.snapshot().remainingMs, 10_000);
  advance(1);
  runner.previous();
  assert.equal(runner.snapshot().index, 1);
});

test("previous presses far apart each just restart", () => {
  const { runner, advance } = setup([10, 10]);
  runner.start();
  runner.next();
  runner.previous();
  advance(5);
  runner.previous();
  assert.equal(runner.snapshot().index, 1);
});

test("previous on the first phase never goes below zero", () => {
  const { runner } = setup([10, 10]);
  runner.start();
  runner.previous();
  runner.previous();
  assert.equal(runner.snapshot().index, 0);
});

test("reset returns to the first phase, running", () => {
  const { runner } = setup([10, 5]);
  runner.start();
  runner.next();
  runner.pause();
  runner.restartWorkout();
  assert.equal(runner.snapshot().index, 0);
  assert.equal(runner.snapshot().paused, false);
  assert.equal(runner.snapshot().remainingMs, 10_000);
});

test("a reps-based phase never advances by itself", () => {
  const { runner, advance } = setup([0, 5]);
  runner.start();
  advance(3600);
  runner.tick();
  assert.equal(runner.snapshot().index, 0);
  assert.equal(runner.snapshot().timed, false);
  runner.next();
  assert.equal(runner.snapshot().index, 1);
});

test("catching up stops at a reps-based phase", () => {
  const { runner, advance } = setup([5, 0, 5]);
  runner.start();
  advance(100);
  runner.tick();
  assert.equal(runner.snapshot().index, 1);
});

test("controls do nothing once finished", () => {
  const { runner, events } = setup([5]);
  runner.start();
  runner.next();
  const count = events.length;
  runner.pause();
  runner.next();
  runner.previous();
  runner.restartPhase();
  assert.equal(events.length, count);
});
