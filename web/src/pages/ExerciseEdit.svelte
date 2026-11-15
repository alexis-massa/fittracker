<script lang="ts">
  import ExerciseEditor from '../components/ExerciseEditor.svelte';
  import { attempt } from '../lib/account.svelte';
  import { api, type Exercise, type Stored } from '../lib/api';
  import { router } from '../lib/router.svelte';

  let { id }: { id: number } = $props();
  const exercise = $derived(api.get<Stored<Exercise>>(`/exercises/${id}`));

  async function save(ex: Exercise) {
    if ((await attempt(() => api.put(`/exercises/${id}`, ex), 'Exercise updated')) !== undefined) {
      router.navigate('/exercises');
    }
  }
</script>

<h1>Edit Exercise</h1>
{#await exercise then ex}
  <ExerciseEditor
    title="Exercise details"
    initial={ex}
    submitLabel="Save"
    onsubmit={save}
    oncancel={() => router.navigate('/exercises')}
  />
{:catch}
  <p class="muted">Exercise not found.</p>
{/await}
