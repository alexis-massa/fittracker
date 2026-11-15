<!-- Name, label and variants of a library exercise: the one form for creating and editing. -->
<script lang="ts">
  import { Button, Field } from 'pi-ui';

  import type { Exercise } from '../lib/api';

  interface Props {
    title: string;
    initial?: Exercise;
    submitLabel: string;
    /** Called with the cleaned-up exercise; throw to keep the form open. */
    onsubmit: (exercise: Exercise) => Promise<void>;
    oncancel: () => void;
  }

  let { title, initial, submitLabel, onsubmit, oncancel }: Props = $props();

  // The form starts from `initial` once, then edits its own copy.
  const start = startingValues();
  function startingValues(): Exercise {
    return initial ?? { name: '', label: '', variants: [] };
  }
  let name = $state(start.name);
  let label = $state(start.label);
  let variants = $state(start.variants.map((v) => ({ ...v })));
  let error = $state<string | null>(null);
  let pending = $state(false);

  async function submit(event: SubmitEvent) {
    event.preventDefault();
    if (!name.trim()) {
      error = 'Name is required';
      return;
    }
    pending = true;
    try {
      await onsubmit({
        name: name.trim(),
        label: label.trim(),
        variants: variants.map((v) => ({ name: v.name.trim(), label: v.label.trim() })).filter((v) => v.name),
      });
    } finally {
      pending = false;
    }
  }
</script>

<form class="card" onsubmit={submit}>
  <h3>{title}</h3>
  <div class="fields">
    <Field label="Name (e.g. A)" bind:value={name} {error} oninput={() => (error = null)} />
    <Field label="Label (e.g. Pushup)" bind:value={label} />
  </div>
  <h4>Variants</h4>
  {#each variants as variant, i (i)}
    <div class="fields variant">
      <Field label="Name (e.g. 1)" bind:value={variant.name} />
      <Field label="Label (e.g. Wide)" bind:value={variant.label} />
      <Button variant="ghost" aria-label="Remove variant {variant.name}" onclick={() => variants.splice(i, 1)}
        >×</Button
      >
    </div>
  {/each}
  <Button variant="ghost" onclick={() => variants.push({ name: '', label: '' })}>+ Add variant</Button>
  <div class="actions">
    <Button type="submit" disabled={pending}>{submitLabel}</Button>
    <Button variant="ghost" onclick={oncancel}>Cancel</Button>
  </div>
</form>

<style>
  .variant {
    align-items: end;
  }
</style>
