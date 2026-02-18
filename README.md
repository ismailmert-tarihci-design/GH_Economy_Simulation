# Bluestar Economy Simulator

A game economy simulation tool for analyzing card drop algorithms, dual-resource progression, and economic balancing. Built with Streamlit for interactive modeling and Plotly for real-time visualization.

## Features

- **Card Drop Algorithm**: Simulate drop rates and card acquisition patterns
- **Dual-Resource Progression**: Model currency and card progression systems
- **Configurable Tables**: Edit drop rates, progression curves, and simulation parameters in the browser
- **URL Sharing**: Encode/decode configuration as shareable links for team collaboration
- **Two Simulation Modes**: Deterministic (single outcome) and Monte Carlo (probability distribution)
- **Analytics Dashboard**: 4 interactive charts showing progression, distribution, and economic trends

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the app:
```bash
streamlit run app.py
```

Visit `http://localhost:8501` in your browser.

## Configuration Guide

The **Config Editor** page lets you customize:
- Drop rate tables (probability per tier)
- Progression curves (level vs resource cost)
- Simulation parameters (player count, duration)

Changes are reflected immediately in previews.

## URL Sharing

Share configurations with colleagues using encoded URLs. The app compresses your config (JSON → gzip → base64url) to ~2-3KB for easy sharing.

## Simulation Modes

- **Deterministic**: Single simulation run with fixed seed (reproducible results)
- **Monte Carlo**: 1000 runs with probability distribution (realistic variance analysis)

## Dashboard

Four charts analyze simulation results:
1. **Progression Over Time**: Average player level by day
2. **Resource Distribution**: Player earnings distribution by tier
3. **Drop Rate Analysis**: Actual vs expected card drop rates
4. **Economic Health**: Overall system resource flows

## Deployment (Streamlit Cloud)

1. Push repository to GitHub
2. Visit https://share.streamlit.io
3. Connect your GitHub account and repo
4. Set entry point: `app.py`
5. Deploy

## Development

Run tests:
```bash
pip install -r requirements-dev.txt
pytest tests/
```

176 unit and integration tests validate card drop logic, progression curves, and simulation accuracy.

## License

MIT License
