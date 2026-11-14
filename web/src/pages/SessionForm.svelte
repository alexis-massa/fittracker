<!-- New, edit or duplicate a session. Its info ("how did it go") is only edited on an existing session;
     a new or duplicated plan gets it when it is run (SessionRun). -->
<script lang="ts">
  import { Button } from 'pi-ui';

  import ExercisePicker from '../components/ExercisePicker.svelte';
  import ExerciseRow from '../components/ExerciseRow.svelte';
  import SessionInfoFields, {
    applyInfo,
    infoFrom,
    type SessionInfo,
  } from '../components/SessionInfoFields.svelte';
  import { attempt } from '../lib/account.svelte';
  import {
    api,
    GROUPS,
    newSession,
    type Exercise,
    type GroupKey,
    type Session,
    type SessionExercise,
    type Stored,
  } from '../lib/api';
  import { displayName, pluralize } from '../lib/format';
  import { router } from '../lib/router.svelte';

  let { mode, id }: { mode: 'new' | 'edit' | 'duplicate'; id?: number } = $props();

  let library = $state<Stored<Exercise>[]>([]);
  let groups = $state<Record<GroupKey, SessionExercise[]>>({ warmup: [], workout: [], stretches: [] });
  let source = $state<Session | null>(null);
  let info = $state<SessionInfo | null>(null);
  let dateError = $state<string | null>(null);
  /** The row being added (index null) or edited. */
  let editing = $state<{ group: GroupKey; index: number | null } | null>(null);

  const title = $derived({ new: 'New Session', edit: 'Edit Session', duplicate: 'Duplicate Session' }[mode]);

  const loaded = (async () => {
    library = await api.get<Stored<Exercise>[]>('/exercises');
    if (id === undefined) return;
    const s = await api.get<Stored<Session>>(`/sessions/${id}`);
    groups = { warmup: s.warmup, workout: s.workout, stretches: s.stretches };
    if (mode === 'edit') {
      source = s;
      info = infoFrom(s);
    }
  })();

  function move(group: GroupKey, index: number, by: number) {
    const list = groups[group];
    const target = index + by;
    if (target < 0 || target >= list.length) return;
    [list[index], list[target]] = [list[target], list[index]];
  }

  function saveRow(ex: SessionExercise) {
    if (!editing) return;
    const list = groups[editing.group];
    if (editing.index === null) list.push(ex);
    else list[editing.index] = ex;
    editing = null;
  }

  async function save() {
    let s: Session = { ...(source ?? newSession()), ...groups };
    if (info) {
      if (!info.date.trim()) {
        dateError = 'Date is required';
        return;
      }
      s = applyInfo(s, info);
    }
    const saved =
      mode === 'edit'
        ? await attempt(() => api.put<Stored<Session>>(`/sessions/${id}`, s), 'Session updated')
        : await attempt(() => api.post<Stored<Session>>('/sessions', s), 'Plan saved');
    if (saved) router.navigate(`/sessions/${saved.id}`);
  }
</script>

<h1>{title}</h1>

{#await loaded}
  <p class="muted">Loading…</p>
{:then}
  {#if info}
    <h2>Session info</h2>
    <div class="card"><SessionInfoFields bind:info {dateError} /></div>
  {/if}

  {#each GROUPS as group (group.key)}
    <h2>{group.title} — {pluralize(groups[group.key].length, 'exercise')}</h2>
    {#each groups[group.key] as exercise, i (i)}
      {#if editing?.group === group.key && editing.index === i}
        <ExercisePicker bind:library initial={exercise} onsave={saveRow} oncancel={() => (editing = null)} />
      {:else}
        <ExerciseRow {exercise}>
          {#snippet before()}
            <div class="reorder">
              <button aria-label="Move {displayName(exercise)} up" onclick={() => move(group.key, i, -1)}
                >▲</button
              >
              <button aria-label="Move {displayName(exercise)} down" onclick={() => move(group.key, i, 1)}
                >▼</button
              >
            </div>
          {/snippet}
          {#snippet after()}
            <Button variant="ghost" onclick={() => (editing = { group: group.key, index: i })}>Edit</Button>
            <Button
              variant="danger"
              aria-label="Remove {displayName(exercise)}"
              onclick={() => groups[group.key].splice(i, 1)}>×</Button
            >
          {/snippet}
        </ExerciseRow>
      {/if}
    {/each}
    {#if editing?.group === group.key && editing.index === null}
      <ExercisePicker bind:library initial={null} onsave={saveRow} oncancel={() => (editing = null)} />
    {:else}
      <Button variant="ghost" onclick={() => (editing = { group: group.key, index: null })}
        >+ Add exercise</Button
      >
    {/if}
  {/each}

  <div class="actions">
    <Button onclick={save}>Save Session</Button>
    <Button variant="ghost" onclick={() => router.navigate('/')}>Cancel</Button>
  </div>
{:catch}
  <p class="muted">Session not found.</p>
{/await}

<style>
  .reorder {
    display: grid;
    gap: 2px;
  }
  .reorder button {
    width: 1.75rem;
    height: 1.25rem;
    padding: 0;
    border: 1px solid var(--border);
    border-radius: 4px;
    background: var(--bg);
    color: var(--ink);
    font-size: 0.6rem;
    cursor: pointer;
  }
</style>
