// The API client and the shapes it returns (mirrors src/model.rs and src/routes.rs).
import { createApi } from 'pi-ui';

export const api = createApi();

/** The logged-in user (POST /api/login, GET /api/me). */
export interface Me {
  username: string;
  csrf_token: string;
  dark_mode: boolean;
}

export interface Variant {
  name: string;
  label: string;
}

export interface Exercise {
  name: string;
  label: string;
  variants: Variant[];
}

export interface SessionExercise {
  name: string;
  label: string;
  variant_name: string;
  variant_label: string;
  sets: number;
  reps: number;
  /** Seconds; used instead of reps when not 0. */
  duration: number;
  rest_before: number;
  rest_seconds: number;
}

export type Progress = 'PROGRESS' | 'MAINTAIN' | 'REGRESS';

export interface Session {
  date: string;
  weight: number | null;
  notes: string | null;
  /** 1 (low) to 5 (high). */
  energy_level: number | null;
  progress: Progress;
  warmup: SessionExercise[];
  workout: SessionExercise[];
  stretches: SessionExercise[];
  completed: boolean;
}

/** A stored document: its row id and its fields. */
export type Stored<T> = T & { id: number };

/** The three exercise groups of a session, in order. */
export const GROUPS = [
  { key: 'warmup', title: 'Warmup' },
  { key: 'workout', title: 'Workout' },
  { key: 'stretches', title: 'Stretches' },
] as const;

export type GroupKey = (typeof GROUPS)[number]['key'];

/** A fresh session exercise with the Python version's defaults. */
export function newSessionExercise(fields: Partial<SessionExercise> = {}): SessionExercise {
  return {
    name: '',
    label: '',
    variant_name: '',
    variant_label: '',
    sets: 3,
    reps: 10,
    duration: 0,
    rest_before: 0,
    rest_seconds: 90,
    ...fields,
  };
}

/** Today in the browser's time zone, as YYYY-MM-DD. */
export function todayIso(now = new Date()): string {
  const local = new Date(now.getTime() - now.getTimezoneOffset() * 60_000);
  return local.toISOString().slice(0, 10);
}

/** A fresh, not yet completed plan. */
export function newSession(): Session {
  return {
    date: todayIso(),
    weight: null,
    notes: null,
    energy_level: null,
    progress: 'MAINTAIN',
    warmup: [],
    workout: [],
    stretches: [],
    completed: false,
  };
}
