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
  <title>Marco's Dough Batch Calculator</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-dark text-light">

<div class="container mt-5">
  <div class="text-center mb-4">
    <h1 class="display-5">Marco's Dough Batch Calculator</h1>
    <p class="lead">This calculates batches of dough when given dough projections.</p>
  </div>

  <form method="post" class="card p-4 shadow-sm bg-secondary">
    <div class="row g-3">
      {% for dough in dough_types %}
        <div class="col-md-6">
          <label class="form-label">{{ dough }} trays:</label>
          <input type="number" name="{{ dough }}" class="form-control" min="0" value="{{ request.form.get(dough, 0) }}">
        </div>
      {% endfor %}
    </div>
    <div class="text-center mt-4">
      <button type="submit" class="btn btn-primary btn-lg">Calculate Batches</button>
    </div>
  </form>

  {% if batches %}
    <div class="mt-5">
      <h2 class="text-center mb-4">Batch Breakdown</h2>
      {% for batch in batches %}
        <div class="card mb-3 shadow-sm bg-dark border-light">
          <div class="card-body">
            <h5 class="card-title">Batch {{ loop.index }}</h5>
            <ul class="list-group list-group-flush">
              {% for name, count in batch.items() if count > 0 %}
                <li class="list-group-item bg-dark text-light">{{ name }}: {{ count }} trays</li>
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
