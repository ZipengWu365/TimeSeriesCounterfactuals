# Try now

This release ships two low-friction ways to evaluate the package before you commit to a bigger workflow.

## 1. Zero-install static gallery

If you publish `docs/` with GitHub Pages, the share cards and downloadable demo outputs in `docs/assets/` and `docs/assets/downloads/` already work as a hosted gallery.

Recommended first pages:

- `showcase-gallery.md`
- `demo-gallery.md`
- `plain-language-guide.md`

## 2. Colab-style quickstart notebook

Open `notebooks/21_colab_quickstart.ipynb` in Jupyter locally, or upload it to Colab after publishing the repo.

The notebook is designed to show the narrow path first:

```bash
python -m pip install -e ".[starter]"
python -m tscfbench quickstart
python -m tscfbench demo repo-breakout
```

## If you need one thing to send another person

Use a share package:

```bash
python -m tscfbench make-share-package --demo-id repo-breakout
```

That produces a chart, a share card, a report, a summary JSON file, and a citation block.
