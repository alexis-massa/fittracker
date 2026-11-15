<!-- One exercise of a session: pose, name, labels and effort, with optional buttons. -->
<script lang="ts">
  import type { Snippet } from 'svelte';

  import type { SessionExercise } from '../lib/api';
  import { description, effortSummary, shortName } from '../lib/format';
  import Pictogram from './Pictogram.svelte';

  interface Props {
    exercise: SessionExercise;
    /** Warmup and stretches are shown dimmed. */
    dim?: boolean;
    /** Controls before the pose (reordering). */
    before?: Snippet;
    /** Controls at the end (edit, remove). */
    after?: Snippet;
  }

  let { exercise, dim = false, before, after }: Props = $props();
</script>

<div class="card row" class:dim>
  {@render before?.()}
  <Pictogram name={exercise.name} />
  <div class="grow">
    <div><strong>{shortName(exercise)}</strong> <span class="muted">{description(exercise)}</span></div>
    <div class="muted small">{effortSummary(exercise)}</div>
  </div>
  {@render after?.()}
</div>

<style>
  .dim {
    opacity: 0.6;
  }
</style>
