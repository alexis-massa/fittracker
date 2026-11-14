<script lang="ts">
  import { AppShell, Button, LoginForm } from 'pi-ui';

  import AccountMenu from './components/AccountMenu.svelte';
  import { account } from './lib/account.svelte';
  import { router } from './lib/router.svelte';
  import { loginUrl, safeRedirect } from './lib/routes';
  import ExerciseEdit from './pages/ExerciseEdit.svelte';
  import Exercises from './pages/Exercises.svelte';
  import SessionDetail from './pages/SessionDetail.svelte';
  import SessionForm from './pages/SessionForm.svelte';
  import SessionRun from './pages/SessionRun.svelte';
  import Sessions from './pages/Sessions.svelte';

  router.install();
  account.load();

  const route = $derived(router.route);
  const section = $derived(route.name.startsWith('exercise') ? 'exercises' : 'sessions');

  // Logged out anywhere: go to the login page, remembering where we were. Logged in on it: leave.
  $effect(() => {
    if (account.me === null && route.name !== 'login')
      router.navigate(loginUrl(router.url), { replace: true });
    if (account.me && route.name === 'login')
      router.navigate(safeRedirect(route.query.get('redirect_to')), { replace: true });
  });
</script>

{#if account.me === null && route.name === 'login'}
  <LoginForm
    title="FitTracker"
    labels={{ submit: 'Sign in', invalid: 'Invalid username or password.' }}
    onlogin={(u, p) => account.login(u, p)}
  />
{:else if account.me}
  {@const me = account.me}
  <AppShell title="FitTracker">
    {#snippet nav()}
      <a href="/" class:active={section === 'sessions'}>Sessions</a>
      <a href="/exercises" class:active={section === 'exercises'}>Exercises</a>
    {/snippet}
    {#snippet actions()}
      <div class="header-actions">
        <Button
          variant="ghost"
          aria-label={me.dark_mode ? 'Use the light theme' : 'Use the dark theme'}
          onclick={() => account.setDarkMode(!me.dark_mode)}>{me.dark_mode ? '☾' : '☀'}</Button
        >
        <AccountMenu username={me.username} />
      </div>
    {/snippet}
    {#key router.url}
      {#if route.name === 'sessions'}
        <Sessions />
      {:else if route.name === 'session'}
        <SessionDetail id={route.id!} />
      {:else if route.name === 'session-new'}
        <SessionForm mode="new" />
      {:else if route.name === 'session-edit'}
        <SessionForm mode="edit" id={route.id!} />
      {:else if route.name === 'session-duplicate'}
        <SessionForm mode="duplicate" id={route.id!} />
      {:else if route.name === 'session-run'}
        <SessionRun id={route.id!} />
      {:else if route.name === 'exercises'}
        <Exercises />
      {:else if route.name === 'exercise-edit'}
        <ExerciseEdit id={route.id!} />
      {:else}
        <p class="muted">Page not found. <a href="/">Back to sessions</a></p>
      {/if}
    {/key}
  </AppShell>
{/if}

<style>
  a.active {
    font-weight: 700;
    text-decoration: underline;
  }
  .header-actions {
    display: flex;
    align-items: center;
    gap: var(--space-2);
  }
</style>
