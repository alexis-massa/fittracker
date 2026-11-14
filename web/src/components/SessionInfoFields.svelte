<!-- "How did it go": date, weight, energy, progress, notes. Saving them marks a session completed. -->
<script lang="ts" module>
  import type { Progress, Session } from '../lib/api';

  export interface SessionInfo {
    date: string;
    weight: number | null;
    energy: number;
    progress: Progress;
    notes: string;
  }

  /** The fields' starting values: the session's own if completed, otherwise Medium / Maintain. */
  export function infoFrom(s: Session, defaultWeight: number | null = null): SessionInfo {
    return {
      date: s.date,
      weight: s.weight ?? defaultWeight ?? 0,
      energy: s.energy_level ?? 3,
      progress: s.progress,
      notes: s.notes ?? '',
    };
  }

  /** The session with this info applied and marked completed. */
  export function applyInfo(s: Session, info: SessionInfo): Session {
    return {
      ...s,
      date: info.date.trim(),
      weight: info.weight ? info.weight : null,
      energy_level: info.energy,
      progress: info.progress,
      notes: info.notes.trim() || null,
      completed: true,
    };
  }
</script>

<script lang="ts">
  import { Field, Select, TextArea } from 'pi-ui';

  import { ENERGY_LEVELS, PROGRESS_OPTIONS } from '../lib/format';

  let { info = $bindable(), dateError = null }: { info: SessionInfo; dateError?: string | null } = $props();
</script>

<div class="fields">
  <Field label="Date" type="date" required bind:value={info.date} error={dateError} />
  <Field label="Weight (kg)" type="number" min="0" max="999" step="0.1" bind:value={info.weight} />
  <Select label="Energy" options={ENERGY_LEVELS} bind:value={info.energy} />
  <Select label="Progress" options={PROGRESS_OPTIONS} bind:value={info.progress} />
</div>
<TextArea label="Notes" bind:value={info.notes} />
