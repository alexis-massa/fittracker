// The phases of a guided run (the Python version's session_run._build_phases and _phase_payload): for each
// exercise of warmup, workout and stretches, and each set: a rest (before the first set, between the
// others) when it is longer than 0, then the work, timed or reps-based.
import { GROUPS, type Session, type SessionExercise } from './api';
import { shortName } from './format';

export interface Phase {
  kind: 'rest' | 'work';
  group: string;
  exercise: SessionExercise;
  /** 1-based set number. */
  series: number;
  exerciseIndex: number;
  totalExercises: number;
  /** Countdown length; 0 for reps-based work (advanced by hand). */
  seconds: number;
  /** Lock-screen text. */
  title: string;
  subtitle: string;
}

export function buildPhases(s: Session): Phase[] {
  const groups = GROUPS.map(({ key, title }) => ({ title, exercises: s[key] }));
  const totalExercises = groups.reduce((n, g) => n + g.exercises.length, 0);
  const phases: Phase[] = [];
  let exerciseIndex = 0;
  for (const { title: group, exercises } of groups) {
    for (const exercise of exercises) {
      for (let series = 1; series <= exercise.sets; series++) {
        const base = { group, exercise, series, exerciseIndex, totalExercises };
        const rest = series === 1 ? exercise.rest_before : exercise.rest_seconds;
        if (rest > 0) phases.push(withText({ ...base, kind: 'rest', seconds: rest }));
        phases.push(withText({ ...base, kind: 'work', seconds: exercise.duration }));
      }
      exerciseIndex++;
    }
  }
  return phases;
}

function withText(p: Omit<Phase, 'title' | 'subtitle'>): Phase {
  const ex = p.exercise;
  const name = [shortName(ex), ex.label].filter(Boolean).join(' ');
  let subtitle = `Series ${p.series}/${ex.sets} · ${p.group} ${p.exerciseIndex + 1}/${p.totalExercises}`;
  if (p.kind === 'work' && p.seconds <= 0) subtitle += ` · ${ex.reps} reps`;
  return { ...p, title: `${p.kind === 'rest' ? 'Rest' : 'Work'} · ${name}`, subtitle };
}
