// A small client-side router over lib/routes.ts: History API, no dependency.
import { match } from './routes';

class Router {
  url = $state(location.pathname + location.search);
  route = $derived(match(this.url));

  navigate(to: string, { replace = false } = {}) {
    if (to === this.url) return;
    history[replace ? 'replaceState' : 'pushState']({}, '', to);
    this.url = to;
    window.scrollTo(0, 0);
  }

  /** Start from the current address, then follow history buttons and same-origin link clicks. */
  install() {
    this.url = location.pathname + location.search;
    addEventListener('popstate', () => (this.url = location.pathname + location.search));
    document.addEventListener('click', (event) => {
      const link = (event.target as Element | null)?.closest('a');
      if (
        !link ||
        link.target ||
        link.hasAttribute('download') ||
        link.origin !== location.origin ||
        event.defaultPrevented ||
        event.button !== 0 ||
        event.metaKey ||
        event.ctrlKey ||
        event.shiftKey ||
        event.altKey
      ) {
        return;
      }
      event.preventDefault();
      this.navigate(link.pathname + link.search);
    });
  }
}

export const router = new Router();
