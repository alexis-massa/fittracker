# src/ui/styles.py

STYLES = """
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;700;800&display=swap');

/* ── Fonts ──────────────────────────────────────────────────────────────── */

body, .q-field__native, .q-field__input, .q-field__label,
.q-btn, .q-item__label, .q-chip {
    font-family: 'DM Mono', monospace !important;
}

.app-title, .text-h4, .text-h5, .text-h6, .text-subtitle1 {
    font-family: 'Syne', sans-serif !important;
}

/* ── App header ─────────────────────────────────────────────────────────── */

.app-header {
    min-height: 56px;
    display: flex;
    align-items: center;
    gap: 2rem;
    padding: 0.5rem 2rem;
    position: sticky;
    top: 0;
    z-index: 100;
    border-bottom: 1px solid rgba(128,128,128,0.2);
}

@media (max-width: 599px) {
    .app-header {
        gap: 0.75rem;
        padding: 0.5rem 1rem;
    }
}

.app-title {
    font-weight: 800;
    font-size: 1.05rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    user-select: none;
}

/* ── Page layout ────────────────────────────────────────────────────────── */

.page-content {
    max-width: 900px;
    margin: 0 auto;
    padding: 2rem 1.5rem;
    width: 100%;
}

/* ── Section title ──────────────────────────────────────────────────────── */

.letter-spacing-wide {
    letter-spacing: 0.12em;
}

/* ── Nav buttons ────────────────────────────────────────────────────────── */

.nav-btn.active {
    border-bottom: 2px solid currentColor;
    border-radius: 0 !important;
}

/* ── Reorder buttons ────────────────────────────────────────────────────── */

.btn-reorder {
    min-width: 0 !important;
    min-height: 0 !important;
    height: 18px !important;
    width: 24px !important;
    padding: 0 !important;
}
"""
