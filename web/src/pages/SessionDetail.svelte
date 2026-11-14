<script lang="ts">
  import { Button } from 'pi-ui';

  import ExerciseRow from '../components/ExerciseRow.svelte';
  import { attempt } from '../lib/account.svelte';
  import { api, GROUPS, type Session, type Stored } from '../lib/api';
  import { energyLabel, pluralize, progressLabel } from '../lib/format';
  import { router } from '../lib/router.svelte';

  let { id }: { id: number } = $props();
  const session = $derived(api.get<Stored<Session>>(`/sessions/${id}`));

  async function remove() {
    if (!confirm('Delete this session? This cannot be undone.')) return;
    if ((await attempt(() => api.delete(`/sessions/${id}`), 'Session deleted')) !== undefined)
      router.navigate('/');
  }
</script>

<Button variant="ghost" onclick={() => router.navigate('/')}>← Back</Button>

{#await session then s}
  <h1>Session — {s.date}</h1>
  <p class="muted info">
    {#if s.completed}
      <span>Energy: {energyLabel(s.energy_level)}</span>
      <span>Progress: {progressLabel(s.progress)}</span>
      {#if s.weight}<span>{s.weight} kg</span>{/if}
      {#if s.notes}<em>{s.notes}</em>{/if}
    {:else}
      <span class="tag">Not completed yet</span>
    {/if}
  </p>
  {#each GROUPS as group (group.key)}
    {#if group.key === 'workout' || s[group.key].length}
      <h2>{group.title} — {pluralize(s[group.key].length, 'exercise')}</h2>
      {#each s[group.key] as exercise, i (i)}
        <ExerciseRow {exercise} dim={group.key !== 'workout'} />
      {/each}
    {/if}
  {/each}
  <div class="actions">
    <Button onclick={() => router.navigate(`/sessions/${id}/run`)}>Start</Button>
    <Button variant="ghost" onclick={() => router.navigate(`/sessions/${id}/edit`)}>Edit</Button>
    <Button variant="ghost" onclick={() => router.navigate(`/sessions/${id}/duplicate`)}>Duplicate</Button>
    <Button variant="danger" onclick={remove}>Delete</Button>
  </div>
{:catch}
  <p class="muted">Session not found.</p>
{/await}

<style>
  .info {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-2) var(--space-6);
  }
</style>
