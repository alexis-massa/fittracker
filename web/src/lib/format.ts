// Display helpers (the Python version's src/utils/formatting.py and model display properties).
import type { Exercise, Progress, Session, SessionExercise, Variant } from './api';

export const ENERGY_LEVELS = [
  { value: 1, label: 'Low' },
  { value: 2, label: 'Medium Low' },
  { value: 3, label: 'Medium' },
  { value: 4, label: 'Medium High' },
  { value: 5, label: 'High' },
];

export const PROGRESS_OPTIONS: { value: Progress; label: string }[] = [
  { value: 'PROGRESS', label: 'Progress' },
  { value: 'MAINTAIN', label: 'Maintain' },
  { value: 'REGRESS', label: 'Regress' },
];

export function pluralize(count: number, singular: string, plural = `${singular}s`): string {
  return `${count} ${count === 1 ? singular : plural}`;
}

export function energyLabel(level: number | null): string {
  return ENERGY_LEVELS.find((e) => e.value === level)?.label ?? '—';
}

export function progressLabel(progress: Progress): string {
  return PROGRESS_OPTIONS.find((p) => p.value === progress)!.label;
}

/** `A — Pushup`, or just `A`. */
export function displayName(item: Exercise | Variant): string {
  return item.label ? `${item.name} — ${item.label}` : item.name;
}

/** `A1`: name and variant. */
export function shortName(ex: SessionExercise): string {
  return `${ex.name}${ex.variant_name}`;
}

/** `Pushup / Wide`: the labels of a session exercise, if any. */
export function description(ex: SessionExercise): string {
  return [ex.label, ex.variant_label].filter(Boolean).join(' / ');
}

/** `3 sets · 10 reps · 90s rest` (the Python version always shows reps here). */
export function effortSummary(ex: SessionExercise): string {
  return `${ex.sets} sets · ${ex.reps} reps · ${ex.rest_seconds}s rest`;
}

/** `Medium energy · Maintain`, or `Not completed yet`. */
export function sessionStatus(s: Session): string {
  return s.completed
    ? `${energyLabel(s.energy_level)} energy · ${progressLabel(s.progress)}`
    : 'Not completed yet';
}

/** `2 exercises · 1 warmup · 0 stretches`. */
export function sessionSummary(s: Session): string {
  return [
    pluralize(s.workout.length, 'exercise'),
    pluralize(s.warmup.length, 'warmup'),
    pluralize(s.stretches.length, 'stretch', 'stretches'),
  ].join(' · ');
}

/** `1:05` from milliseconds, rounding up so the clock reaches 0:00 only at the end. */
export function mmss(ms: number): string {
  const seconds = Math.ceil(Math.max(ms, 0) / 1000);
  return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`;
}
