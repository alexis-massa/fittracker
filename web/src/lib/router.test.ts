// Includes the Python version's tests/test_auth.py redirect cases.
import { describe, expect, it } from 'vitest';

import { loginUrl, match, safeRedirect } from './routes';

describe('router', () => {
  it('matches the Python version URLs', () => {
    expect(match('/')).toMatchObject({ name: 'sessions', id: null });
    expect(match('/sessions/12/run')).toMatchObject({ name: 'session-run', id: 12 });
    expect(match('/exercises/3/edit')).toMatchObject({ name: 'exercise-edit', id: 3 });
    expect(match('/sessions/abc').name).toBe('not-found');
    expect(match('/login?redirect_to=%2Fexercises').query.get('redirect_to')).toBe('/exercises');
  });

  it('local paths are valid redirect targets', () => {
    for (const target of ['/', '/sessions/1', '/exercises?x=1']) expect(safeRedirect(target)).toBe(target);
  });

  it('anything that could leave the site redirects home', () => {
    for (const target of [
      '//evil.example',
      'https://evil.example',
      '/\\evil.example',
      'javascript:alert(1)',
      '',
      null,
    ]) {
      expect(safeRedirect(target)).toBe('/');
    }
  });

  it('remembers the page that asked for a login', () => {
    expect(loginUrl('/')).toBe('/login');
    expect(loginUrl('/sessions/4')).toBe('/login?redirect_to=%2Fsessions%2F4');
  });
});
