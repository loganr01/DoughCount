from flask import Flask, render_template_string, request
import math

app = Flask(__name__)

DOUGH_TYPES = {
    "Pizzoli": 60,
    "Small": 100,
    "Medium": 126,
    "Large": 152,
    "XLarge": 150
}

BATCH_SIZE = 1216

HTML_TEMPLATE = """
<!doctype html>
<html lang="en" data-bs-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>MOMS Badass Batch Calc</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body {
      background: url('https://media.giphy.com/media/3o7abldj0b3rxrZUxW/giphy.gif') repeat-y center center fixed;
      background-size: cover;
      color: #FFD700;
      font-family: 'Impact', 'Arial Black', sans-serif;
      text-shadow: 2px 2px 5px #000000;
      animation: scrollBackground 60s linear infinite;
    }

    @keyframes scrollBackground {
      from { background-position: 0 0; }
      to { background-position: 0 1000px; }
    }

    .card {
      background-color: rgba(0, 0, 0, 0.8) !important;
      border: 2px solid #FFD700;
    }

    .btn-primary {
      background-color: #ff4500;
      border: none;
      font-weight: bold;
      font-size: 1.3rem;
    }

    .btn-primary:hover {
      background-color: #ff2200;
    }

    h1, h2, h5 {
      font-weight: bold;
      color: #ffcc00;
    }

    .list-group-item {
      background-color: transparent !important;
      color: #FFD700;
      border: none;
    }

    label {
      font-size: 1.1rem;
    }

    .lead {
      font-size: 1.3rem;
      font-style: italic;
    }
  </style>
</head>
<body>

<div class="container mt-5">
  <div class="text-center mb-4">
    <h1 class="display-3">🔥 MOMS Badass Batch Calc 🔥</h1>
    <p class="lead">Built for only the strongest batches.</p>
  </div>

  <form method="post" class="card p-4 shadow-lg">
    <div class="row g-3">
      {% for dough in dough_types %}
        <div class="col-md-6">
          <label class="form-label">{{ dough }} trays:</label>
          <input type="number" name="{{ dough }}" class="form-control" min="0" value="{{ request.form.get(dough, 0) }}">
        </div>
      {% endfor %}
    </div>
    <div class="text-center mt-4">
      <button type="submit" class="btn btn-primary btn-lg">🔥 Calculate Batches 🔥</button>
    </div>
  </form>

  {% if batches %}
    <div class="mt-5">
      <h2 class="text-center mb-4">🔥 Batch Breakdown 🔥</h2>
      {% for batch in batches %}
        <div class="card mb-3 shadow-lg">
          <div class="card-body">
            <h5 class="card-title">Batch {{ loop.index }}</h5>
            <ul class="list-group list-group-flush">
              {% for name, count in batch.items() if count > 0 %}
                <li class="list-group-item">{{ name }}: {{ count }} trays</li>
              {% endfor %}
            </ul>
            <div class="mt-2"><strong>Total Weight:</strong> {{ total_weights[loop.index0] }} oz</div>
          </div>
        </div>
      {% endfor %}
    </div>
  {% endif %}
</div>

</body>
</html>
"""


def pack_batches(projections):
    remaining = projections.copy()
    batches = []

    while any(remaining.values()):
        batch = {name: 0 for name in DOUGH_TYPES}
        batch_weight = 0

        for name, tray_weight in sorted(DOUGH_TYPES.items(), key=lambda x: -x[1]):
            while remaining[name] > 0 and batch_weight + tray_weight <= BATCH_SIZE:
                batch[name] += 1
                batch_weight += tray_weight
                remaining[name] -= 1

        batches.append(batch)

    total_weights = [sum(DOUGH_TYPES[name] * count for name, count in batch.items()) for batch in batches]
    return batches, total_weights

@app.route('/', methods=['GET', 'POST'])
def index():
    batches = []
    total_weights = []
    if request.method == 'POST':
        projections = {}
        for name in DOUGH_TYPES:
            try:
                projections[name] = int(request.form.get(name, 0))
            except ValueError:
                projections[name] = 0

        batches, total_weights = pack_batches(projections)

    return render_template_string(HTML_TEMPLATE, dough_types=DOUGH_TYPES.keys(), batches=batches, total_weights=total_weights)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
