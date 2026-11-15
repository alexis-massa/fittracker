<!-- Guided run: Ready → phases (timer in the browser, lock-screen controls) → reflection → saved. -->
<script lang="ts">
  import { Button } from 'pi-ui';
  import { onDestroy } from 'svelte';

  import Pictogram from '../components/Pictogram.svelte';
  import SessionInfoFields, {
    applyInfo,
    infoFrom,
    type SessionInfo,
  } from '../components/SessionInfoFields.svelte';
  import { attempt } from '../lib/account.svelte';
  import { api, type Session, type Stored } from '../lib/api';
  import { description, mmss, shortName } from '../lib/format';
  import { buildPhases, type Phase } from '../lib/phases';
  import { router } from '../lib/router.svelte';
  import type { Snapshot } from '../lib/runner';
  import { createWorkout, type Workout } from '../lib/workout';

  let { id }: { id: number } = $props();

  let session = $state<Stored<Session> | null>(null);
  let phases = $state<Phase[]>([]);
  let workout: Workout | null = null;
  let snap = $state<Snapshot | null>(null);
  let info = $state<SessionInfo | null>(null);
  let dateError = $state<string | null>(null);
  let saved = $state(false);

  const loaded = (async () => {
    const s = await api.get<Stored<Session>>(`/sessions/${id}`);
    session = s;
    phases = buildPhases(s);
    workout = createWorkout(phases, {
      name: `Session ${s.date}`,
      icon: '/icons/icon-512.png',
      onUpdate: (update) => (snap = update),
      onStop: stop,
    });
    snap = workout.snapshot();
  })();

  const phase = $derived(snap && !snap.finished ? phases[snap.index] : null);

  // The reflection starts with the session's values, the weight from the last completed session.
  $effect(() => {
    if (snap?.finished && session && !info) {
      const s = session;
      api.get<number | null>('/sessions/last-weight').then(
        (weight) => (info = infoFrom(s, weight)),
        () => (info = infoFrom(s)),
      );
    }
  });

  onDestroy(() => workout?.release());

  function stop() {
    workout?.release();
    router.navigate(`/sessions/${id}`);
  }

  async function save() {
    if (!session || !info) return;
    if (!info.date.trim()) {
      dateError = 'Date is required';
      return;
    }
    const s = applyInfo(session, info);
    const done = await attempt(() => api.put(`/sessions/${id}`, s), 'Session saved');
    if (done) saved = true;
  }
</script>

<Button variant="ghost" onclick={stop}>← Back</Button>

{#await loaded then}
  {#if session && snap}
    <h1>Session — {session.date}</h1>
    {#if !phases.length}
      <p class="muted">This session has no exercises to run.</p>
    {:else}
      <progress max={phases.length} value={Math.min(snap.index, phases.length)}></progress>
      <div class="run">
        {#if !snap.started}
          <h2>Ready?</h2>
          <p class="muted small">Keeps the screen on and puts pause / skip on your lock screen.</p>
          <Button onclick={() => workout?.begin()}>Start workout</Button>
        {:else if phase}
          {@const ex = phase.exercise}
          <p class="muted small">
            {phase.group.toUpperCase()} · exercise {phase.exerciseIndex + 1}/{phase.totalExercises}
          </p>
          <h2>{shortName(ex)}</h2>
          {#if description(ex)}<p class="muted small">{description(ex)}</p>{/if}
          <Pictogram name={ex.name} size="6rem" />
          {#if phase.kind === 'rest'}
            <p class="muted small">REST</p>
            <p class="clock">{mmss(snap.remainingMs)}</p>
            <p class="muted small">series {phase.series}/{ex.sets} next</p>
          {:else if phase.seconds > 0}
            <p class="muted small">series {phase.series}/{ex.sets}</p>
            <p class="clock">{mmss(snap.remainingMs)}</p>
          {:else}
            <p class="muted small">series {phase.series}/{ex.sets}</p>
            <p class="clock">{ex.reps} reps</p>
            <Button onclick={() => workout?.next()}>Series done</Button>
          {/if}
          <div class="actions">
            <Button variant="ghost" onclick={() => workout?.toggle()}
              >{snap.paused ? 'Resume' : 'Pause'}</Button
            >
            <Button variant="ghost" onclick={() => workout?.next()}>Skip</Button>
            <Button variant="ghost" onclick={() => workout?.restartPhase()}>Restart</Button>
          </div>
          <div class="actions">
            <Button
              variant="ghost"
              onclick={() => confirm('Start the whole workout over?') && workout?.restartWorkout()}
              >Reset workout</Button
            >
            <Button variant="danger" onclick={() => confirm('Stop this workout? Nothing is saved.') && stop()}
              >Stop</Button
            >
          </div>
        {:else if saved}
          <h2>Session saved</h2>
          <div class="actions">
            <Button onclick={() => router.navigate(`/sessions/${id}`)}>Back to session</Button>
            <Button variant="ghost" onclick={() => router.navigate('/')}>All sessions</Button>
          </div>
        {:else if info}
          <h2>Session complete — how did it go?</h2>
          <div class="card"><SessionInfoFields bind:info {dateError} /></div>
          <div class="actions">
            <Button onclick={save}>Save</Button>
            <Button variant="ghost" onclick={() => router.navigate(`/sessions/${id}`)}>Skip</Button>
          </div>
        {/if}
      </div>
    {/if}
  {/if}
{:catch}
  <p class="muted">Session not found.</p>
{/await}

<style>
  progress {
    width: 100%;
    height: 0.5rem;
    margin-bottom: var(--space-4);
    border: 0;
    border-radius: var(--radius);
    background: var(--border);
    appearance: none;
  }
  progress::-webkit-progress-bar {
    border-radius: var(--radius);
    background: var(--border);
  }
  progress::-webkit-progress-value {
    border-radius: var(--radius);
    background: var(--accent);
  }
  progress::-moz-progress-bar {
    border-radius: var(--radius);
    background: var(--accent);
  }
  .run {
    display: grid;
    justify-items: center;
    text-align: center;
  }
  .run > :global(.card) {
    justify-self: stretch;
    text-align: left;
  }
  .run h2 {
    margin-bottom: var(--space-1);
  }
  .clock {
    margin: var(--space-3) 0;
    font-size: 3.5rem;
    font-weight: 700;
    font-variant-numeric: tabular-nums;
  }
</style>
