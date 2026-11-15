// Port of the Python version's tests/ui/test_session_run.py (the phase list and its lock-screen text).
import { describe, expect, it } from 'vitest';

import { newSession, newSessionExercise } from './api';
import { mmss, sessionStatus, sessionSummary } from './format';
import { buildPhases } from './phases';
import { pictogramSvg, PICTOGRAMS, FALLBACK } from './pictograms';

function session() {
  return {
    ...newSession(),
    date: '2026-03-04',
    workout: [
      newSessionExercise({
        name: 'A',
        label: 'Pushup',
        variant_name: '1',
        sets: 2,
        reps: 8,
        rest_before: 10,
      }),
      newSessionExercise({ name: 'B', sets: 1, duration: 30, rest_seconds: 0, reps: 0 }),
    ],
  };
}

describe('buildPhases', () => {
  it('rest before, then work and rest between sets', () => {
    const kinds = buildPhases(session()).map((p) => `${p.kind}:${p.seconds}`);
    expect(kinds).toEqual(['rest:10', 'work:0', 'rest:90', 'work:0', 'work:30']);
  });

  it('rest phase title and subtitle describe the next series', () => {
    const [rest] = buildPhases(session());
    expect([rest.seconds, rest.title, rest.subtitle]).toEqual([
      10,
      'Rest · A1 Pushup',
      'Series 1/2 · Workout 1/2',
    ]);
  });

  it('reps-based work phase shows reps and has no countdown', () => {
    const work = buildPhases(session())[1];
    expect(work.seconds).toBe(0);
    expect(work.title).toBe('Work · A1 Pushup');
    expect(work.subtitle.endsWith('· 8 reps')).toBe(true);
  });

  it('timed work phase keeps its duration', () => {
    const last = buildPhases(session()).at(-1)!;
    expect(last.seconds).toBe(30);
    expect(last.subtitle).not.toContain('reps');
  });

  it('counts exercises across warmup, workout and stretches', () => {
    const s = { ...session(), warmup: [newSessionExercise({ name: 'W', sets: 1 })] };
    expect(buildPhases(s)[0].subtitle).toBe('Series 1/1 · Warmup 1/3 · 10 reps');
  });
});

describe('format', () => {
  it('summarises sessions like the Python list', () => {
    const s = session();
    expect(sessionSummary(s)).toBe('2 exercises · 0 warmups · 0 stretches');
    expect(sessionStatus(s)).toBe('Not completed yet');
    expect(sessionStatus({ ...s, completed: true, energy_level: 4, progress: 'PROGRESS' })).toBe(
      'Medium High energy · Progress',
    );
  });

  it('formats the clock rounding up', () => {
    expect([mmss(65_000), mmss(64_001), mmss(0), mmss(-5)]).toEqual(['1:05', '1:05', '0:00', '0:00']);
  });
});

describe('pictograms', () => {
  it('has one per base letter and a fallback, case-insensitively', () => {
    expect(Object.keys(PICTOGRAMS)).toHaveLength(26);
    expect(pictogramSvg('a')).toBe(PICTOGRAMS.A);
    expect(pictogramSvg('Squat')).toBe(FALLBACK);
  });
});
