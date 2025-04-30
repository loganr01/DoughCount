from flask import Flask, render_template_string, request, make_response
import math
import csv
import io

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
  <title>Batch Calc</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body {
      background-color: #1c1c1e;
      color: #f1f1f1;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .card {
      background-color: #2c2c2e;
      border: 1px solid #444;
    }
    .btn-primary {
      background-color: #ff5722;
      border: none;
    }
    .btn-primary:hover {
      background-color: #e64a19;
    }
    h1, h2, h5 {
      font-weight: 600;
      color: #ffffff;
    }
    .lead {
      color: #aaaaaa;
    }
    .form-label {
      font-weight: 500;
    }
    .list-group-item {
      background-color: transparent;
      color: #e2e2e2;
      border: none;
      padding-left: 0;
    }
    .progress {
      height: 20px;
    }
    .progress-bar {
      font-size: 0.75rem;
    }
    @media print {
      button, input, .btn, form { display: none !important; }
    }
  </style>
</head>
<body>

<div class="container mt-5 mb-5">
  <div class="text-center mb-4">
    <h1 class="display-5">MOMS Batch Calculator</h1>
    <p class="lead">Batch out dough like a pro. No waste. No guesswork.</p>
  </div>

  <form method="post" class="card p-4 shadow-sm">
    <div class="row g-3">
      {% for dough in dough_types %}
        <div class="col-md-6">
          <label class="form-label">{{ dough }} trays:</label>
          <input type="number" name="{{ dough }}" class="form-control" min="0" value="{{ request.form.get(dough, 0) }}">
        </div>
      {% endfor %}
    </div>
    <div class="text-center mt-4">
      <button type="submit" class="btn btn-primary btn-lg px-5">Calculate Batches</button>
      <a href="/export" class="btn btn-outline-light btn-lg px-5 ms-3">Export CSV</a>
      <button onclick="window.print()" class="btn btn-secondary btn-lg px-5 ms-3">Print</button>
    </div>
  </form>

  {% if batches %}
    <div class="mt-5">
      <h2 class="text-center mb-4">Batch Breakdown</h2>
      {% for batch in batches %}
        <div class="card mb-3 shadow-sm">
          <div class="card-body">
            <h5 class="card-title">Batch {{ loop.index }}</h5>
            <ul class="list-group list-group-flush">
              {% for name, count in batch.items() if count > 0 %}
                <li class="list-group-item">{{ name }}: {{ count }} trays {{ icons[name] }}</li>
              {% endfor %}
            </ul>
            <div class="mt-3">
              <strong>Total Weight:</strong> {{ total_weights[loop.index0] }} oz
              <br>
              <strong>Efficiency:</strong> {{ efficiency[loop.index0] }}%
              <div class="progress mt-2">
                <div class="progress-bar bg-success" role="progressbar" style="width: {{ efficiency[loop.index0] }}%">
                  {{ efficiency[loop.index0] }}%
                </div>
              </div>
              {% if overspill[loop.index0] > 0 %}
                <div class="mt-2 text-warning">Unused dough: {{ overspill[loop.index0] }} oz</div>
              {% endif %}
            </div>
          </div>
        </div>
      {% endfor %}

      <div class="card mt-4">
        <div class="card-body">
          <h5 class="card-title">Total Tray Summary</h5>
          <ul class="list-group list-group-flush">
            {% for name, total in tray_totals.items() %}
              <li class="list-group-item">{{ name }}: {{ total }} trays</li>
            {% endfor %}
          </ul>
        </div>
      </div>
    </div>
  {% endif %}
</div>

</body>
</html>
"""

ICONS = {
    "Pizzoli": "🍕",
    "Small": "🍕",
    "Medium": "🍕",
    "Large": "🍕",
    "XLarge": "🍕"
}

last_batches = []
last_weights = []


def pack_batches(projections):
    remaining = projections.copy()
    batches = []
    tray_totals = {name: 0 for name in DOUGH_TYPES}

    while any(remaining.values()):
        batch = {name: 0 for name in DOUGH_TYPES}
        batch_weight = 0

        for name, tray_weight in sorted(DOUGH_TYPES.items(), key=lambda x: -x[1]):
            while remaining[name] > 0 and batch_weight + tray_weight <= BATCH_SIZE:
                batch[name] += 1
                tray_totals[name] += 1
                batch_weight += tray_weight
                remaining[name] -= 1

        batches.append(batch)

    total_weights = [sum(DOUGH_TYPES[name] * count for name, count in batch.items()) for batch in batches]
    efficiency = [round(w / BATCH_SIZE * 100) for w in total_weights]
    overspill = [BATCH_SIZE - w for w in total_weights]

    return batches, total_weights, efficiency, overspill, tray_totals

@app.route('/', methods=['GET', 'POST'])
def index():
    global last_batches, last_weights
    batches = []
    total_weights = []
    efficiency = []
    overspill = []
    tray_totals = {}

    if request.method == 'POST':
        projections = {}
        for name in DOUGH_TYPES:
            try:
                projections[name] = int(request.form.get(name, 0))
            except ValueError:
                projections[name] = 0

        batches, total_weights, efficiency, overspill, tray_totals = pack_batches(projections)
        last_batches = batches
        last_weights = total_weights

    return render_template_string(
        HTML_TEMPLATE,
        dough_types=DOUGH_TYPES.keys(),
        request=request,
        batches=batches,
        total_weights=total_weights,
        efficiency=efficiency,
        overspill=overspill,
        tray_totals=tray_totals,
        icons=ICONS
    )

@app.route('/export')
def export_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Batch #'] + list(DOUGH_TYPES.keys()) + ['Total Weight'])

    for i, batch in enumerate(last_batches):
        row = [f"Batch {i+1}"] + [batch.get(name, 0) for name in DOUGH_TYPES] + [last_weights[i]]
        writer.writerow(row)

    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=batch_breakdown.csv'
    response.headers['Content-type'] = 'text/csv'
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
