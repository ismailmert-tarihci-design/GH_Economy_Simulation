# Deployment Guide - Bluestar Economy Simulator

## 🚀 Quick Deploy to Streamlit Cloud

### Prerequisites
- GitHub account
- Git repository pushed to GitHub
- Streamlit Cloud account (free at https://share.streamlit.io)

### Step-by-Step Instructions

#### 1. Push to GitHub (if not already done)

```bash
# Initialize git repository (if needed)
git init
git add .
git commit -m "feat: complete Bluestar Economy Simulator"

# Add remote and push
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

#### 2. Deploy on Streamlit Cloud

1. **Visit Streamlit Cloud**
   - Go to https://share.streamlit.io
   - Click "Sign in with GitHub"
   - Authorize Streamlit Cloud

2. **Create New App**
   - Click "New app" button
   - Select your repository: `YOUR_USERNAME/YOUR_REPO_NAME`
   - Branch: `main`
   - Main file path: `app.py`
   - Click "Deploy!"

3. **Wait for Deployment**
   - Streamlit Cloud will install dependencies from `requirements.txt`
   - Initial deployment takes 2-3 minutes
   - App will be available at: `https://YOUR_USERNAME-YOUR_REPO_NAME.streamlit.app`

#### 3. Verify Deployment

Once deployed, test the following:
- ✅ App loads without errors (HTTP 200)
- ✅ All 4 config editor tabs render correctly
- ✅ Deterministic simulation runs successfully
- ✅ Monte Carlo simulation completes
- ✅ All 4 dashboard charts display
- ✅ URL sharing generates shareable links

---

## 📦 Deployment Files

### Required Files (Already Configured)
- ✅ `app.py` - Streamlit entry point
- ✅ `requirements.txt` - Python dependencies
- ✅ `.streamlit/config.toml` - Streamlit configuration
- ✅ `README.md` - Project documentation

### File Structure
```
coin_sim/
├── app.py                      # Entry point
├── requirements.txt            # Dependencies (streamlit, plotly, pydantic)
├── .streamlit/
│   └── config.toml            # Streamlit settings
├── simulation/                 # Core engine (Streamlit-free)
│   ├── __init__.py
│   ├── models.py
│   ├── config_loader.py
│   ├── pack_system.py
│   ├── progression.py
│   ├── coin_economy.py
│   ├── drop_algorithm.py
│   ├── upgrade_engine.py
│   ├── orchestrator.py
│   └── monte_carlo.py
├── pages/                      # Streamlit UI pages
│   ├── config_editor.py
│   ├── simulation_controls.py
│   └── dashboard.py
├── data/defaults/              # Default configuration JSON files
│   ├── pack_config.json
│   ├── unique_upgrades.json
│   ├── gold_upgrades.json
│   ├── blue_upgrades.json
│   ├── card_economy.json
│   ├── progression_mapping.json
│   └── simulation_schedule.json
├── tests/                      # Test suite (176 tests)
└── README.md                   # Documentation
```

---

## 🔧 Configuration

### Streamlit Cloud Settings

**Resource Limits** (Streamlit Cloud Free Tier):
- Memory: 1GB
- CPU: 1 shared core
- Storage: Ephemeral

**Environment Variables**: None required

**Python Version**: 3.9+ (auto-detected from requirements.txt)

### Performance on Streamlit Cloud

Expected performance (based on local benchmarks):
- **100-day deterministic**: < 1 second
- **100×100 Monte Carlo**: < 15 seconds
- **App startup**: 10-15 seconds (first load)
- **Subsequent loads**: 2-3 seconds (cached)

---

## 🐛 Troubleshooting

### Common Issues

#### 1. "ModuleNotFoundError: No module named 'X'"
**Solution**: Ensure `requirements.txt` includes all dependencies
```txt
streamlit>=1.30.0
plotly>=5.18.0
numpy>=1.24.0
pandas>=2.0.0
pydantic>=2.5.0
```

#### 2. App crashes on simulation run
**Symptom**: "TypeError: '<=' not supported between instances of 'str' and 'int'"
**Solution**: Already fixed in `simulation/pack_system.py` (line 43 uses `int(k)` coercion)

#### 3. Config Editor tables not editable
**Known Issue**: `st.data_editor` may render as read-only in some browsers
**Workaround**: Test with Chrome/Firefox latest versions, or modify config programmatically

#### 4. Streamlit disconnects during long simulations
**Solution**: Reduce Monte Carlo runs to < 200 for web UI, or use Python CLI for large batches

---

## 📊 Monitoring & Maintenance

### Post-Deployment Checks

**Day 1**:
- [ ] Verify app loads for new users
- [ ] Test config editor data persistence
- [ ] Run sample deterministic simulation
- [ ] Test URL sharing round-trip

**Week 1**:
- [ ] Monitor Streamlit Cloud logs for errors
- [ ] Check for Pydantic serialization warnings
- [ ] Verify performance meets targets (< 30s det, < 120s MC)

**Month 1**:
- [ ] Review user feedback (if applicable)
- [ ] Address UI rendering issues if reported
- [ ] Consider refactoring large files (drop_algorithm.py, config_editor.py)

### Update Procedure

To deploy updates:
```bash
# Make changes locally
git add .
git commit -m "fix: description of change"
git push origin main

# Streamlit Cloud auto-deploys on push to main branch
# Monitor deployment at https://share.streamlit.io/YOUR_USERNAME/YOUR_REPO_NAME
```

---

## ✅ Deployment Checklist

Before deploying, verify:
- [x] All 176 tests passing (`pytest tests/ -v`)
- [x] App launches locally (`streamlit run app.py`)
- [x] All Python files compile (`python -m py_compile *.py`)
- [x] requirements.txt has all dependencies
- [x] .streamlit/config.toml exists
- [x] README.md is up to date
- [x] Git repository pushed to GitHub
- [x] No secrets in code (API keys, passwords)

---

## 📈 Performance Targets

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| 100-day deterministic | < 30s | 0.08s | ✅ 375× faster |
| 100×100 Monte Carlo | < 120s | 8.35s | ✅ 14× faster |
| Test suite runtime | < 60s | 49.85s | ✅ |
| App startup | < 30s | ~12s | ✅ |

---

## 🔗 Useful Links

- **Streamlit Cloud Dashboard**: https://share.streamlit.io
- **Streamlit Docs**: https://docs.streamlit.io
- **Deployment Docs**: https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app
- **Resource Limits**: https://docs.streamlit.io/streamlit-community-cloud/manage-your-app#app-resources-and-limits

---

## 🎯 Success Criteria

Deployment is successful when:
- ✅ App URL is publicly accessible
- ✅ No errors on page load
- ✅ All 3 pages render (Config Editor, Simulation Controls, Dashboard)
- ✅ Simulations complete without crashes
- ✅ Charts display correctly

---

## 📞 Support

For issues with:
- **Streamlit Cloud**: https://discuss.streamlit.io
- **This Application**: Check `.sisyphus/evidence/FINAL-VERIFICATION-REPORT.md`

---

**Deployment Date**: February 18, 2026  
**Version**: 1.0.0  
**Status**: Production Ready ✅
