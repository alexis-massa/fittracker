"""
Application stylesheet — one place for all CSS.
Injected once at page load via ui.add_head_html.
"""

STYLES = """
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; }

body {
    font-family: 'DM Mono', monospace;
    margin: 0;
}

/* ── Layout ─────────────────────────────────────────────────────────────── */

.app-header {
    border-bottom: 1px solid #1e1e1e;
    padding: 0 2rem;
    height: 56px;
    display: flex;
    align-items: center;
    gap: 2rem;
    position: sticky;
    top: 0;
    z-index: 100;
}

.app-title {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 1.05rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    user-select: none;
}

.page-content {
    max-width: 900px;
    margin: 0 auto;
    padding: 2rem 1.5rem;
    width: 100%;
}

.divider {
    border: none;
    border-top: 1px solid #1e1e1e;
    margin: 1.5rem 0;
}

/* ── Navigation ─────────────────────────────────────────────────────────── */

.nav-btn {
    background: none !important;
    border: none !important;
    box-shadow: none !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    cursor: pointer;
    padding: 4px 0 !important;
    border-bottom: 1px solid transparent !important;
    border-radius: 0 !important;
    transition: color 0.15s, border-color 0.15s;
}

/* ── Buttons ────────────────────────────────────────────────────────────── */

.btn-primary {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    border-radius: 3px !important;
    padding: 6px 18px !important;
    border: none !important;
    box-shadow: none !important;
    transition: opacity 0.15s !important;
}
.btn-primary:hover { opacity: 0.82 !important; }

.btn-ghost {
    background: transparent !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    border: 1px solid #2a2a2a !important;
    border-radius: 3px !important;
    padding: 6px 14px !important;
    box-shadow: none !important;
    transition: border-color 0.15s, color 0.15s !important;
}

.btn-danger {
    background: transparent !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.68rem !important;
    border: 1px solid #3a1a1a !important;
    border-radius: 3px !important;
    padding: 4px 10px !important;
    box-shadow: none !important;
    transition: border-color 0.15s !important;
}

/* ── Cards ──────────────────────────────────────────────────────────────── */

.card {
    border: 1px solid #1e1e1e;
    border-radius: 4px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 0.6rem;
    transition: border-color 0.15s;
}

.card-title {
    font-family: 'Syne', sans-serif;
    font-weight: 600;
    font-size: 0.95rem;
}

/* ── Labels & tags ──────────────────────────────────────────────────────── */

.section-title {
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 0.85rem;
}

.meta-row {
    font-size: 0.72rem;
    margin-top: 3px;
}

.tag {
    display: inline-block;
    border: 1px solid #2a2a2a;
    font-size: 0.62rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 1px 7px;
    border-radius: 2px;
    margin-right: 4px;
}

.energy-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 0.8rem;
    flex-shrink: 0;
}

/* ── Form inputs (NiceGUI / Quasar overrides) ───────────────────────────── */

.nicegui-input .q-field__control,
.nicegui-select .q-field__control,
.nicegui-textarea .q-field__control {
    border-radius: 3px !important;
}

.nicegui-input .q-field__native,
.nicegui-select .q-field__native,
.nicegui-select .q-field__input,
.nicegui-textarea .q-field__native {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.82rem !important;
}

.nicegui-input .q-field__label,
.nicegui-select .q-field__label,
.nicegui-textarea .q-field__label {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
}
"""
