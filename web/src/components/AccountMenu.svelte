<!-- The account button in the header: user name, change password, sign out. -->
<script lang="ts">
  import { Button, Dialog, Field, toasts } from 'pi-ui';

  import { account, attempt } from '../lib/account.svelte';
  import { api } from '../lib/api';

  let { username }: { username: string } = $props();

  let menuOpen = $state(false);
  let dialogOpen = $state(false);
  let current = $state('');
  let fresh = $state('');
  let repeat = $state('');
  let error = $state<string | null>(null);

  function openPasswordDialog() {
    menuOpen = false;
    current = fresh = repeat = '';
    error = null;
    dialogOpen = true;
  }

  async function savePassword() {
    if (fresh !== repeat) {
      error = 'New passwords do not match.';
      return;
    }
    error = null;
    try {
      await api.post('/me/password', { current, new: fresh });
      dialogOpen = false;
      toasts.show('Password changed', 'success');
    } catch (e) {
      error = e instanceof Error ? e.message : 'Could not change the password.';
    }
  }
</script>

<div class="menu">
  <Button
    variant="ghost"
    aria-haspopup="menu"
    aria-expanded={menuOpen}
    onclick={() => (menuOpen = !menuOpen)}
  >
    {username} ▾
  </Button>
  {#if menuOpen}
    <div class="items" role="menu">
      <button role="menuitem" onclick={openPasswordDialog}>Change password</button>
      <button role="menuitem" onclick={() => attempt(() => account.logout())}>Sign out</button>
    </div>
  {/if}
</div>

<Dialog bind:open={dialogOpen} title="Change password">
  <Field label="Current password" type="password" autocomplete="current-password" bind:value={current} />
  <Field label="New password" type="password" autocomplete="new-password" bind:value={fresh} />
  <Field
    label="Repeat new password"
    type="password"
    autocomplete="new-password"
    bind:value={repeat}
    {error}
  />
  {#snippet actions()}
    <Button variant="ghost" onclick={() => (dialogOpen = false)}>Cancel</Button>
    <Button onclick={savePassword}>Save</Button>
  {/snippet}
</Dialog>

<style>
  .menu {
    position: relative;
  }
  .items {
    position: absolute;
    right: 0;
    z-index: 5;
    display: grid;
    min-width: 12rem;
    margin-top: var(--space-1);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    background: var(--bg);
    box-shadow: var(--shadow);
  }
  .items button {
    min-height: var(--tap);
    padding: 0 var(--space-4);
    border: 0;
    background: none;
    color: var(--ink);
    font: inherit;
    text-align: left;
    cursor: pointer;
  }
  .items button:hover {
    background: var(--surface);
  }
</style>
