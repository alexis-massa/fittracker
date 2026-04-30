# src/ui/styles.py

STYLES = """
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; }

/* ── Theme tokens ───────────────────────────────────────────────────────── */

body.body--dark {
    --bg:            #0f0f0f;
    --bg-card:       #141414;
    --bg-inline:     #1a1a1a;
    --border:        #1e1e1e;
    --border-mid:    #2a2a2a;
    --border-hover:  #3a3a3a;
    --text:          #e8e4dc;
    --text-muted:    #888;
    --text-dim:      #555;
    --text-dimmer:   #444;
    --accent:        #c8f566;
    --accent-bg:     #192200;
    --accent-border: #304000;
    --danger:        #c0392b;
    --danger-border: #3a1a1a;
}

body.body--light {
    --bg:            #f5f5f0;
    --bg-card:       #ffffff;
    --bg-inline:     #f0f0eb;
    --border:        #e0e0d8;
    --border-mid:    #ccccc4;
    --border-hover:  #999;
    --text:          #1a1a1a;
    --text-muted:    #666;
    --text-dim:      #888;
    --text-dimmer:   #aaa;
    --accent:        #5a8a00;
    --accent-bg:     #eef7d0;
    --accent-border: #c8e880;
    --danger:        #c0392b;
    --danger-border: #f5c6c2;
}

body {
    font-family: 'DM Mono', monospace;
    margin: 0;
    background: var(--bg) !important;
    color: var(--text) !important;
    transition: background 0.2s, color 0.2s;
}

/* ── Layout ─────────────────────────────────────────────────────────────── */

.app-header {
    background: var(--bg) !important;
    border-bottom: 1px solid var(--border);
    padding: 0 2rem;
    height: 56px;
    display: flex;
    align-items: center;
    gap: 2rem;
    position: sticky;
    top: 0;
    z-index: 100;
    transition: background 0.2s, border-color 0.2s;
}

.app-title {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 1.05rem;
    letter-spacing: 0.1em;
    color: var(--accent);
    text-transform: uppercase;
    user-select: none;
}

/* List pages — constrained width */
.page-content {
    max-width: 90%;
    margin: 0 auto;
    padding: 2rem 1.5rem;
    width: 70%;
}

/* Form pages — full width, generous padding */
.page-content-wide {
    width: 100%;
    padding: 2rem 2.5rem;
}

.divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1.5rem 0;
}

/* ── Cards ──────────────────────────────────────────────────────────────── */

.card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 0.6rem;
    transition: border-color 0.15s, background 0.2s;
}
.card:hover { border-color: var(--border-hover); }

/* Inline card — used for inline exercise creation form */
.card-inline {
    background: var(--bg-inline);
    border: 1px solid var(--border-mid);
    border-radius: 4px;
    padding: 1rem;
    width: 100%;
    margin-top: 0.5rem;
    transition: background 0.2s, border-color 0.2s;
}

/* Form card — main form container */
.card-form {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 1.5rem;
    width: 100%;
    transition: background 0.2s, border-color 0.2s;
}

.card-title {
    font-family: 'Syne', sans-serif;
    font-weight: 600;
    font-size: 0.95rem;
    color: var(--text);
}

/* ── Spacing utilities ──────────────────────────────────────────────────── */

.spacer-sm  { height: 0.5rem; }
.spacer-md  { height: 1.25rem; }
.spacer-lg  { height: 1.5rem; }

/* ── Form layout ────────────────────────────────────────────────────────── */

.page-content-wide {
    width: 100%;
    padding: 2rem 2.5rem;
    display: flex;
    flex-direction: column;
}

.card-form {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 1.5rem;
    width: 100%;
    transition: background 0.2s, border-color 0.2s;
}

.card-inline {
    background: var(--bg-inline);
    border: 1px solid var(--border-mid);
    border-radius: 4px;
    padding: 1rem;
    width: 100%;
    margin-top: 0.5rem;
    transition: background 0.2s, border-color 0.2s;
}

/* ── Exercise group ─────────────────────────────────────────────────────── */

.exercise-group {
    width: 100%;
    gap: 0;
}

.exercise-row {
    align-items: center;
    gap: 8px;
    margin-bottom: 4px;
    width: 100%;
}

.exercise-label {
    flex: 1;
    font-size: 0.82rem;
}

/* ── Input rows ─────────────────────────────────────────────────────────── */

.input-row {
    gap: 8px;
    margin-top: 0.5rem;
    align-items: center;
    flex-wrap: wrap;
    width: 100%;
}

.input-row-grow {
    flex: 1;
    width: auto;
    min-width: 160px;
}

/* ── Inline form ────────────────────────────────────────────────────────── */

.inline-form-title {
    font-size: 0.72rem;
    color: var(--text-dim);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}

/* ── Action row ─────────────────────────────────────────────────────────── */

.action-row {
    gap: 0.75rem;
    margin-top: 1.5rem;
    align-items: center;
}

/* Fix: ui.card() Quasar background override for theme responsiveness */
.q-card {
    background: var(--bg-card) !important;
    color: var(--text) !important;
    transition: background 0.2s, color 0.2s;
}

.card-inline {
    background: var(--bg-inline) !important;
    border: 1px solid var(--border-mid);
    border-radius: 4px;
    padding: 1rem;
    width: 100%;
    margin-top: 0.5rem;
    transition: background 0.2s, border-color 0.2s;
}

/* ── Exercise row ───────────────────────────────────────────────────────── */

.exercise-row {
    align-items: center;
    gap: 8px;
    margin-bottom: 4px;
    width: 100%;
    padding: 0.4rem 0;
    border-bottom: 1px solid var(--border);
}

.exercise-info {
    flex: 1;
    gap: 2px;
}

.exercise-label {
    font-size: 0.85rem;
    font-weight: 500;
}

/* ── Labels & tags ──────────────────────────────────────────────────────── */

.section-title {
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--text-dimmer);
    margin-bottom: 0.85rem;
}

.meta-row {
    font-size: 0.72rem;
    color: var(--text-dim);
    margin-top: 3px;
}

.tag {
    display: inline-block;
    background: var(--bg-inline);
    border: 1px solid var(--border-mid);
    color: var(--text-muted);
    font-size: 0.62rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 1px 7px;
    border-radius: 2px;
    margin-right: 4px;
    transition: background 0.2s, border-color 0.2s;
}
.tag.accent {
    background: var(--accent-bg);
    border-color: var(--accent-border);
    color: var(--accent);
}

/* ── Form inputs (NiceGUI / Quasar overrides) ───────────────────────────── */

.nicegui-input .q-field__control,
.nicegui-select .q-field__control,
.nicegui-textarea .q-field__control {
    background: var(--bg-card) !important;
    border-radius: 3px !important;
    transition: background 0.2s;
}

.nicegui-input .q-field__native,
.nicegui-select .q-field__native,
.nicegui-select .q-field__input,
.nicegui-textarea .q-field__native {
    color: var(--text) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.82rem !important;
}

.nicegui-input .q-field__label,
.nicegui-select .q-field__label,
.nicegui-textarea .q-field__label {
    color: var(--text-dim) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
}

.nicegui-input .q-field--outlined .q-field__control:before,
.nicegui-select .q-field--outlined .q-field__control:before,
.nicegui-textarea .q-field--outlined .q-field__control:before {
    border-color: var(--border-mid) !important;
    transition: border-color 0.15s;
}

.nicegui-input .q-field--outlined .q-field__control:hover:before,
.nicegui-select .q-field--outlined .q-field__control:hover:before,
.nicegui-textarea .q-field--outlined .q-field__control:hover:before {
    border-color: var(--border-hover) !important;
}

.nicegui-input .q-field--focused .q-field__control:before,
.nicegui-select .q-field--focused .q-field__control:before,
.nicegui-textarea .q-field--focused .q-field__control:before {
    border-color: var(--accent) !important;
}
"""
