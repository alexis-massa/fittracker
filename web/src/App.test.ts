import { cleanup, render, screen } from '@testing-library/svelte';
import { afterEach, describe, expect, it, vi } from 'vitest';

import App from './App.svelte';

function serve(routes: Record<string, unknown>) {
  vi.stubGlobal(
    'fetch',
    vi.fn(async (url: string) =>
      url in routes
        ? Response.json(routes[url])
        : Response.json({ detail: 'not logged in' }, { status: 401 }),
    ),
  );
}

describe('App', () => {
  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
    history.replaceState({}, '', '/');
  });

  it('sends anonymous visitors to the login page, remembering the page', async () => {
    history.replaceState({}, '', '/exercises');
    serve({});
    render(App);
    expect(await screen.findByRole('button', { name: 'Sign in' })).toBeTruthy();
    expect(location.pathname + location.search).toBe('/login?redirect_to=%2Fexercises');
  });

  it('shows the sessions of the logged-in user', async () => {
    serve({
      '/api/me': { username: 'ann', csrf_token: 't', dark_mode: true },
      '/api/sessions': [
        {
          id: 1,
          date: '2026-11-08',
          completed: false,
          progress: 'MAINTAIN',
          energy_level: null,
          weight: null,
          notes: null,
          warmup: [],
          workout: [],
          stretches: [],
        },
      ],
    });
    render(App);
    expect(await screen.findByText('2026-11-08')).toBeTruthy();
    expect(screen.getByText('0 exercises · 0 warmups · 0 stretches · Not completed yet')).toBeTruthy();
    expect(document.documentElement.dataset.theme).toBe('dark');
  });
});
