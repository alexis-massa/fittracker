<!-- Add or edit one exercise of a session: pick it (and a variant) from the library, or create it, then
     set its effort. A new row is pre-filled from the last time that exercise was done. -->
<script lang="ts">
  import { Button, Field, Select } from 'pi-ui';

  import { attempt } from '../lib/account.svelte';
  import { api, newSessionExercise, type Exercise, type SessionExercise, type Stored } from '../lib/api';
  import { displayName } from '../lib/format';
  import ExerciseEditor from './ExerciseEditor.svelte';

  interface Props {
    /** The user's library; grows when an exercise is created here. */
    library: Stored<Exercise>[];
    /** The row being edited, or null to add one. */
    initial: SessionExercise | null;
    onsave: (exercise: SessionExercise) => void;
    oncancel: () => void;
  }

  let { library = $bindable(), initial, onsave, oncancel }: Props = $props();

  // The form starts from `initial` once, then edits its own copy.
  const start = startingValues();
  function startingValues() {
    const ex = initial ?? newSessionExercise();
    return {
      name: initial ? ex.name : null,
      variantName: ex.variant_name || null,
      effort: {
        sets: ex.sets,
        reps: ex.reps,
        duration: ex.duration,
        rest_before: ex.rest_before,
        rest_seconds: ex.rest_seconds,
      },
    };
  }
  let name = $state<string | null>(start.name);
  let variantName = $state<string | null>(start.variantName);
  let effort = $state(start.effort);
  let creating = $state(false);
  let nameError = $state<string | null>(null);
  let effortError = $state<string | null>(null);

  const chosen = $derived(library.find((e) => e.name === name));
  const nameOptions = $derived(library.map((e) => ({ value: e.name, label: displayName(e) })));
  const variantOptions = $derived(
    (chosen?.variants ?? []).map((v) => ({ value: v.name, label: displayName(v) })),
  );

  const isEdit = () => initial !== null;

  /** Only for a new row: editing keeps its own values. */
  async function prefill() {
    if (isEdit() || !name) return;
    const query = new URLSearchParams({ name, variant: variantName ?? '' });
    const last = await attempt(() => api.get<SessionExercise | null>(`/sessions/last-used?${query}`));
    if (last) {
      const { sets, reps, duration, rest_before, rest_seconds } = last;
      effort = { sets, reps, duration, rest_before, rest_seconds };
    }
  }

  function pickName() {
    nameError = null;
    variantName = null;
    prefill();
  }

  async function create(ex: Exercise) {
    const stored = await attempt(
      () => api.post<Stored<Exercise>>('/exercises', ex),
      `'${displayName(ex)}' added to library`,
    );
    if (!stored) throw new Error('not created');
    library = [...library, stored].sort((a, b) => a.name.localeCompare(b.name));
    creating = false;
    name = stored.name;
    pickName();
  }

  function save() {
    if (!name) {
      nameError = 'Exercise name is required';
      return;
    }
    if (effort.reps !== 0 && effort.duration !== 0) {
      effortError = 'Choose reps or duration, not both';
      return;
    }
    const variant = chosen?.variants.find((v) => v.name === variantName);
    onsave({
      ...effort,
      name,
      label: chosen?.label ?? '',
      variant_name: variant?.name ?? '',
      variant_label: variant?.label ?? '',
    });
  }
</script>

<div class="card">
  <h3>{initial ? 'Edit Exercise' : 'Add Exercise'}</h3>
  {#if creating}
    <ExerciseEditor
      title="New Exercise"
      submitLabel="Create"
      onsubmit={create}
      oncancel={() => (creating = false)}
    />
  {/if}
  <div class="fields">
    <Select
      label="Exercise"
      options={nameOptions}
      placeholder="—"
      bind:value={name}
      error={nameError}
      onchange={pickName}
    />
    <Select
      label="Variant"
      options={variantOptions}
      placeholder="—"
      bind:value={variantName}
      onchange={prefill}
    />
  </div>
  <button class="link" type="button" onclick={() => (creating = true)}>+ Create new exercise</button>

  <h4>Sets &amp; timing</h4>
  <div class="fields">
    <Field
      label="Rest before this exercise (s)"
      type="number"
      min="0"
      max="3600"
      bind:value={effort.rest_before}
    />
    <Field label="Sets" type="number" min="1" max="100" bind:value={effort.sets} />
    <Field label="Rest between sets (s)" type="number" min="0" max="3600" bind:value={effort.rest_seconds} />
  </div>
  <h4>Reps or duration — fill exactly one</h4>
  <div class="fields">
    <Field
      label="Reps"
      type="number"
      min="0"
      max="200"
      bind:value={effort.reps}
      error={effortError}
      oninput={() => (effortError = null)}
    />
    <Field
      label="Duration (s)"
      type="number"
      min="0"
      max="999"
      bind:value={effort.duration}
      error={effortError}
      oninput={() => (effortError = null)}
    />
  </div>
  <div class="actions">
    <Button onclick={save}>Save</Button>
    <Button variant="ghost" onclick={oncancel}>Cancel</Button>
  </div>
</div>
