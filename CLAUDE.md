# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Bluestar Economy Simulator — a Streamlit app for modeling game economy mechanics (card drops, dual-resource progression, pet/hero/gear systems). Used for balancing and A/B testing structural game economy variants.

## Commands

```bash
# Run the app
streamlit run app.py

# Run all tests
pytest tests/

# Run a single test file
pytest tests/test_drop_algorithm.py

# Run a single test
pytest tests/test_drop_algorithm.py::test_function_name

# Run with coverage
pytest tests/ --cov=simulation

# Skip slow tests
pytest tests/ -m "not slow"

# Install dependencies
pip install -r requirements.txt          # production
pip install -r requirements-dev.txt      # dev (includes pytest)
```

## Architecture

### Layer Separation

The codebase has a strict separation between **simulation engine** (`simulation/`) and **UI** (`app_pages/`, `app.py`). The simulation package has zero Streamlit imports — it is pure Python with Pydantic models. All Streamlit code lives in `app_pages/` and `app.py`.

### Simulation Engine (`simulation/`)

The daily simulation loop is orchestrated by `simulation/orchestrator.py`:
1. Check unique unlock schedule (`progression.py`)
2. Process packs for the day (`pack_system.py`)
3. For each card pull: `drop_algorithm.py` → then `upgrade_engine.py`
4. Record daily snapshot with coin ledger (`coin_economy.py`)

Key modules:
- `models.py` — Pydantic v2 models (`SimConfig`, `GameState`, `Card`, `SimResult`, `StreakState`)
- `monte_carlo.py` — Runs N simulations with different RNG seeds, aggregates results
- `config_loader.py` — Loads/validates JSON configs from `data/defaults/`
- `pet_system.py`, `hero_system.py`, `gear_system.py` — Subsystem simulators

### A/B Variant Framework (`simulation/variants/`)

Variants are self-registering modules that implement `VariantInfo` (defined in `protocol.py`). Each variant provides its own `run_simulation`, `load_defaults`, config class, and result class. Registration happens at import time in `variants/__init__.py`.

- `variant_a/` — Original economy (uses shared simulation engine directly)
- `variant_b/` — Alternative economy with hero card packs replacing unique cards
- `comparison.py` — Cross-variant comparison utilities

The UI dispatches to variant-specific editors (`app_pages/variant_editors/`) and dashboards (`app_pages/variant_dashboards/`) based on the active variant selected in the sidebar.

### UI Pages (`app_pages/`)

- `config_editor.py` + `config_tabs.py` — Table-driven config editing with `st.data_editor`
- `simulation_controls.py` — Run deterministic or Monte Carlo simulations
- `dashboard.py` + `dashboard_charts.py` — 4-chart analytics dashboard (Plotly)
- `bulk_edit_helpers.py` — CSV/Excel upload and paste for config tables
- `gacha_simulator.py` — Interactive pull simulator tool

### Data

- `data/defaults/` — Default config JSON files (pack configs, upgrade tables, progression mapping, pet/hero/gear tables)
- `data/profiles/` — Player profiles (NonPayer, Payer variants) used as simulation presets

### Config Flow

User edits config in UI → stored in `st.session_state.configs[variant_id]` → passed to simulation engine → results stored in `st.session_state`. Configs can be shared via URL encoding (JSON → gzip → base64url, handled by `url_config.py`).

## Key Conventions

- All data models use **Pydantic v2** (`BaseModel`, `model_dump_json()`, `model_validate_json()`)
- Simulation functions accept an optional `rng: Random` parameter for reproducibility
- Config validation rules are strict (e.g., pet tier probabilities must sum to 100 per tier, gear slot costs must cover all slot/level pairs)
- The orchestrator uses `DailySnapshot` dataclasses (not Pydantic) for per-day state recording
