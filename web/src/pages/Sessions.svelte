<script lang="ts">
  import { Button } from 'pi-ui';

  import { api, type Session, type Stored } from '../lib/api';
  import { pluralize, sessionStatus, sessionSummary } from '../lib/format';
  import { router } from '../lib/router.svelte';

  const sessions = api.get<Stored<Session>[]>('/sessions');
</script>

<div class="page-header">
  <h1>Sessions</h1>
  <Button onclick={() => router.navigate('/sessions/new')}>+ New Session</Button>
</div>

{#await sessions then list}
  <p class="muted small">
    {list.length ? `${pluralize(list.length, 'session')} logged` : 'No sessions yet. Log your first workout.'}
  </p>
  {#each list as s (s.id)}
    <div class="card row">
      <div class="grow">
        <strong>{s.date}</strong>
        <div class="muted small">{sessionSummary(s)} · {sessionStatus(s)}</div>
      </div>
      <div class="actions">
        <Button onclick={() => router.navigate(`/sessions/${s.id}/run`)}>Start</Button>
        <Button variant="ghost" onclick={() => router.navigate(`/sessions/${s.id}/duplicate`)}
          >Duplicate</Button
        >
        <Button variant="ghost" onclick={() => router.navigate(`/sessions/${s.id}`)}>View →</Button>
      </div>
    </div>
  {/each}
{/await}
