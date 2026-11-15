// The app's URLs (the same as the Python version's) and the pure helpers around them.

export type RouteName =
  | 'login'
  | 'sessions'
  | 'session-new'
  | 'session'
  | 'session-edit'
  | 'session-duplicate'
  | 'session-run'
  | 'exercises'
  | 'exercise-edit'
  | 'not-found';

export interface Route {
  name: RouteName;
  /** `:id` of the path, as a number. */
  id: number | null;
  /** Query string parameters. */
  query: URLSearchParams;
}

const PATTERNS: [RegExp, RouteName][] = [
  [/^\/$/, 'sessions'],
  [/^\/login$/, 'login'],
  [/^\/sessions\/new$/, 'session-new'],
  [/^\/sessions\/(\d+)$/, 'session'],
  [/^\/sessions\/(\d+)\/edit$/, 'session-edit'],
  [/^\/sessions\/(\d+)\/duplicate$/, 'session-duplicate'],
  [/^\/sessions\/(\d+)\/run$/, 'session-run'],
  [/^\/exercises$/, 'exercises'],
  [/^\/exercises\/(\d+)\/edit$/, 'exercise-edit'],
];

export function match(url: string): Route {
  const { pathname, searchParams } = new URL(url, 'http://local');
  for (const [pattern, name] of PATTERNS) {
    const m = pattern.exec(pathname);
    if (m) return { name, id: m[1] ? Number(m[1]) : null, query: searchParams };
  }
  return { name: 'not-found', id: null, query: searchParams };
}

/** Only local paths, so a login link cannot send users to another site. */
export function safeRedirect(target: string | null): string {
  return target && target.startsWith('/') && !target.startsWith('//') && !target.includes('\\')
    ? target
    : '/';
}

/** The login page, coming back to `from` afterwards. */
export function loginUrl(from: string): string {
  return from === '/' ? '/login' : `/login?redirect_to=${encodeURIComponent(from)}`;
}
