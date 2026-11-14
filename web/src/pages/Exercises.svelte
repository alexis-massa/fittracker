<script lang="ts">
  import { Button } from 'pi-ui';

  import ExerciseEditor from '../components/ExerciseEditor.svelte';
  import Pictogram from '../components/Pictogram.svelte';
  import { attempt } from '../lib/account.svelte';
  import { api, type Exercise, type Stored } from '../lib/api';
  import { displayName, pluralize } from '../lib/format';
  import { router } from '../lib/router.svelte';

  let exercises = $state<Stored<Exercise>[] | null>(null);
  let creating = $state(false);

  async function load() {
    exercises = await api.get<Stored<Exercise>[]>('/exercises');
  }
  load();

  async function create(ex: Exercise) {
    const stored = await attempt(() => api.post('/exercises', ex), `'${displayName(ex)}' added to library`);
    if (!stored) throw new Error('not created');
    creating = false;
    await load();
  }

  async function remove(ex: Stored<Exercise>) {
    if (!confirm(`Delete '${displayName(ex)}' from the library? This cannot be undone.`)) return;
    if ((await attempt(() => api.delete(`/exercises/${ex.id}`), 'Exercise deleted')) !== undefined)
      await load();
  }
</script>

<div class="page-header">
  <h1>Exercise Library</h1>
  <Button onclick={() => (creating = !creating)}>+ New Exercise</Button>
</div>

{#if creating}
  <ExerciseEditor
    title="New Exercise"
    submitLabel="Create"
    onsubmit={create}
    oncancel={() => (creating = false)}
  />
{/if}

{#if exercises}
  {#if !exercises.length}
    <p class="muted">No exercises yet. Add your first one.</p>
  {:else}
    <h2>{pluralize(exercises.length, 'exercise')}</h2>
    {#each exercises as ex (ex.id)}
      <div class="card row">
        <Pictogram name={ex.name} />
        <div class="grow">
          <strong>{displayName(ex)}</strong>
          {#each ex.variants as v (v.name)}
            <div class="muted small">{displayName(v)}</div>
          {/each}
        </div>
        <div class="actions">
          <Button variant="ghost" onclick={() => router.navigate(`/exercises/${ex.id}/edit`)}>Edit</Button>
          <Button variant="danger" onclick={() => remove(ex)}>Delete</Button>
        </div>
      </div>
    {/each}
  {/if}
{/if}
