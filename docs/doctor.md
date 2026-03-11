# Environment doctor

This report is meant to reduce confusion on first run.

- core_ready: True
- viz_ready: True
- built_in_backends: simple_scm_builtin, did_builtin, ols_impact_builtin
- optional_available: (none)
- optional_missing: pysyncon, scpi, synthetic_control_methods, causalpy, tfp_causalimpact, cimpact, darts_forecast_cf, statsforecast_cf, pytorch_forecasting_tft

## Safe first run

The built-in quickstart path avoids optional dependencies and is designed to run cleanly before you install specialist backends.

```bash
python -m pip install -e ".[starter]"
python -m tscfbench quickstart
python -m tscfbench doctor
```

## Notes

- Recommended first run: install the starter extra so PNG chart assets are guaranteed without adding the full research stack.
- Quickstart and report generation do not depend on undeclared markdown-table backends; the core package closes that path in clean environments.
- Minimal installs still work. If matplotlib is unavailable, tscfbench falls back to SVG visuals for quickstart and demos.
- Optional backends are for deeper comparison runs, not for the first-run experience.
- If you explicitly include optional backends and they are not installed, tscfbench should mark them as skipped optional dependencies rather than hard benchmark failures.
- For OpenAI tool calling, export the starter tool profile first, then promote to minimal or research only after the narrow path succeeds.
- If the `tscfbench` executable is not on PATH, `python -m tscfbench ...` should still work.
- The package metadata is PyPI-ready, but this repo snapshot cannot publish externally from the current environment.
