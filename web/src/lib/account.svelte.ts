// Who is logged in, and the actions on the account.
import { ApiError, applyTheme, toasts } from 'pi-ui';

import { api, type Me } from './api';

class Account {
  /** undefined while loading, null when logged out. */
  me = $state<Me | null | undefined>(undefined);

  set(me: Me | null) {
    api.setCsrf(me?.csrf_token ?? null);
    applyTheme(me ? me.dark_mode : null);
    this.me = me;
  }

  async load() {
    api.onUnauthorized(() => this.set(null));
    this.set(await api.get<Me>('/me').catch(() => null));
  }

  async login(username: string, password: string) {
    this.set(await api.post<Me>('/login', { username, password }));
  }

  async logout() {
    await api.post('/logout');
    this.set(null);
  }

  async setDarkMode(dark: boolean) {
    const prefs = await api.patch<{ dark_mode: boolean }>('/me/preferences', { dark_mode: dark });
    if (this.me) this.set({ ...this.me, dark_mode: prefs.dark_mode });
  }
}

export const account = new Account();

/** Run an API call; show its error as a toast and return undefined instead of throwing. */
export async function attempt<T>(call: () => Promise<T>, success?: string): Promise<T | undefined> {
  try {
    const result = await call();
    if (success) toasts.show(success, 'success');
    return result;
  } catch (e) {
    toasts.show(e instanceof ApiError ? e.message : 'Something went wrong', 'error');
    return undefined;
  }
}
