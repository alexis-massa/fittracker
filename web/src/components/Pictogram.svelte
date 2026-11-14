<!-- The line-art pose of an exercise; tap to see it large. The SVGs are constants (lib/pictograms.ts). -->
<script lang="ts">
  import { Button, Dialog } from 'pi-ui';

  import { pictogramSvg } from '../lib/pictograms';

  let { name, size = '2.5rem' }: { name: string; size?: string } = $props();
  let open = $state(false);
  const svg = $derived(pictogramSvg(name));
</script>

<button
  class="pictogram"
  style:width={size}
  style:height={size}
  aria-label="Show the {name} pose"
  onclick={() => (open = true)}
>
  <!-- eslint-disable-next-line svelte/no-at-html-tags -- constant SVG from lib/pictograms.ts -->
  {@html svg}
</button>

<Dialog bind:open>
  <!-- eslint-disable-next-line svelte/no-at-html-tags -- constant SVG from lib/pictograms.ts -->
  <div class="large">{@html svg}</div>
  {#snippet actions()}
    <Button variant="ghost" onclick={() => (open = false)}>Close</Button>
  {/snippet}
</Dialog>

<style>
  .pictogram {
    flex-shrink: 0;
    padding: 0;
    border: 0;
    background: none;
    color: var(--ink);
    cursor: pointer;
  }
  .large {
    width: min(70vw, 20rem);
    height: min(70vw, 20rem);
    margin: 0 auto;
  }
  .pictogram :global(svg),
  .large :global(svg) {
    width: 100%;
    height: 100%;
  }
</style>
