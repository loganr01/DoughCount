# MOMS Dough Batch Calculator (Flask Web App)

A lightweight Flask app that turns Marco’s Pizza dough tray projections into **precise 1216‑oz batch plans**—so your prep list is accurate, easy to follow, and wastes as little dough as possible.

### Live demo

[doughcount.onrender.com](https://doughcount.onrender.com)

> Hosted on Render’s free tier. The instance may sleep when idle and briefly cold‑start on the first request after inactivity.

---

## What this app does

Given a target number of trays for each dough ball size (Pizzoli, Small, Medium, Large, XLarge), the app:

1. **Calculates the minimum number of full 1216‑oz dough batches** required to meet or slightly exceed your projections (always rounds up to fully meet demand).
2. **Packs trays into each 1216‑oz batch** using a fill strategy that aims to **minimize leftover dough** per batch.
3. **Produces a clear packing list** per batch and a summary of totals, including any leftover ounces.
4. **Preserves your inputs** so you can tweak numbers and instantly compare scenarios.

> **Why 1216 oz?** That’s one standard Marco’s batch. The constant is configurable if your operation uses a different batch size.

---

## Who it’s for

* Marco’s Pizza shift leads, dough makers, and managers
* Operators who want consistent batch planning with reduced mental math
* Anyone standardizing dough prep across multiple stores

---

## Key features

* **Batch rounding logic:** Never under‑produces—rounds up as needed to satisfy tray counts.
* **Leftover‑aware packing:** Tries to fit trays in a way that reduces leftover dough per batch while still hitting the totals.
* **Dark‑mode UI:** Clean Bootstrap 5 dark theme that’s easy on the eyes in the kitchen.
* **Sticky form values:** Inputs persist after calculation for fast, iterative planning.
* **Configurable dough ball sizes:** Change or add sizes and weights without touching core logic.

---

## How the math works (high level)

* Define a **batch capacity** (default `1216 oz`).
* Define a mapping of **dough ball weights by size** (e.g., `{"Pizzoli": W1, "Small": W2, ...}` in ounces).
* Given target **tray counts per size**, convert to **total required ounces** and **minimum batch count** by `ceil(total_ounces / 1216)`.
* **Packing strategy:**

  * Start from the user’s requested distribution and greedily place trays by size into the current batch without exceeding `1216 oz`.
  * If a greedy pass leaves high leftovers, attempt small backtracks/swaps (e.g., replace one tray of Size A with two trays of Size B) to bring leftover down **without** violating per‑size totals.
  * Continue until all requested trays are placed; if the last batch isn’t full, it’s still created (so totals are met).

> Note: Exact weights are **configurable**. If your operation updates dough ball weights, edit the configuration and the calculator will adapt automatically.

---

## Example (illustrative only)

Suppose you need:

* 1 × Pizzoli trays
* 5 × Small trays
* 10 × Medium trays
* 20 × Large trays
* 6 × XLarge trays

The app will:

1. Compute the total dough ounces implied by those trays.
2. Determine the **minimum number of 1216‑oz batches** required to meet or slightly exceed that total.
3. Build a **batch‑by‑batch packing plan** that aims to minimize leftover per batch while respecting the requested tray counts.
4. Show a **summary**: total batches, trays per size, and leftover ounces.

---

## Tech stack

* **Backend:** Python, Flask, Jinja2
* **Frontend:** Bootstrap 5 (dark theme), HTML templates
* **Runtime:** Works locally or on PaaS (Render, Railway, Fly.io). Any WSGI‑friendly host will work.

---

## Getting started (local)

### Prerequisites

* Python 3.10+ (3.11 recommended)
* `pip` and (optionally) `virtualenv`

### Setup

```bash
# 1) Clone
git clone <your-repo-url>.git
cd <your-repo-name>

# 2) Create and activate a virtual environment (recommended)
python -m venv .venv
# Windows
. .venv/Scripts/activate
# macOS/Linux
source .venv/bin/activate

# 3) Install dependencies
pip install -r requirements.txt

# 4) Set env vars (example)
# Windows (PowerShell)
$env:FLASK_APP = "app.py"
$env:FLASK_ENV = "development"
$env:SECRET_KEY = "change-me"

# macOS/Linux
export FLASK_APP=app.py
export FLASK_ENV=development
export SECRET_KEY=change-me

# 5) Run
flask run
```

Open [http://localhost:5000](http://localhost:5000) and enter your tray projections.

---

## Configuration

Edit `config.py` (or `.env` if you prefer environment‑based settings) to customize:

```python
# Example (illustrative)
BATCH_WEIGHT_OZ = 1216
DOUGH_BALL_WEIGHTS_OZ = {
    "Pizzoli":  %% FILL ME %%,
    "Small":    %% FILL ME %%,
    "Medium":   %% FILL ME %%,
    "Large":    %% FILL ME %%,
    "XLarge":   %% FILL ME %%,
}
```

> Replace `%% FILL ME %%` with your current spec weights. Once set, everything else updates automatically.

You can also toggle UI options (e.g., show/hide leftover column), or adjust heuristic knobs for the packing strategy (e.g., backtrack depth, allowed swap patterns).

---

## Project structure (typical)

```
.
├─ app.py                 # Flask app entry
├─ config.py              # Batch size & dough ball weight config
├─ logic/
│  ├─ batching.py         # Core batch math & packing strategy
│  └─ validators.py       # Input validation helpers
├─ templates/
│  ├─ base.html           # Layout (Bootstrap 5 dark)
│  └─ index.html          # Form + results
├─ static/
│  ├─ style.css           # Minor theme overrides
│  └─ ...
├─ tests/                 # (Optional) unit tests
├─ requirements.txt
└─ README.md
```

---

## Deployment

You can deploy anywhere that supports Python/Flask:

### Render (example)

1. Push to GitHub.
2. Create a **Web Service** on Render, connect the repo.
3. Set the **Build Command**: `pip install -r requirements.txt`
4. Set the **Start Command**: `gunicorn app:app`
5. Add environment variables (`SECRET_KEY`, any custom configs).

### Alternative options

* **Railway, Fly.io, Azure App Service, AWS Elastic Beanstalk, Google Cloud Run**

> For serverless, consider wrapping with a WSGI adapter like `werkzeug.middleware.proxy_fix` or dedicated adapters for the platform.

---

## Troubleshooting

* **App runs but styles look off** → Ensure Bootstrap is properly linked and not blocked by a CSP.
* **Numbers don’t match expectations** → Double‑check `DOUGH_BALL_WEIGHTS_OZ` and tray counts entered. The app always rounds **up** to meet demand.
* **Too much leftover per batch** → Adjust the packing heuristic in `logic/batching.py` (enable deeper backtracking or more swap patterns).
* **State not sticking between runs** → Ensure you’ve set `SECRET_KEY` for session persistence.

---

## Roadmap

* Optional CSV/Excel export of the batch plan
* Per‑store presets and saved scenarios
* Role‑based access (maker vs. manager)
* Print‑friendly mode

---

## Contributing

1. Fork the repo and create a feature branch.
2. Make your changes with clear commit messages.
3. Add/adjust unit tests if you touch core logic.
4. Open a PR describing the change and rationale.

---

## License

Choose a license that fits your needs (MIT recommended for most use cases). Add a `LICENSE` file at the repo root.

---

## Screenshots (optional)

Add screenshots to `docs/` and embed them here, e.g.:

```
![Form](docs/form.png)
![Results](docs/results.png)
```

---

## Credits

Built by Logan for streamlining Marco’s dough prep and eliminating avoidable waste.
