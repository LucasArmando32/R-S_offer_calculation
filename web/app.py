from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

OPTION_NAMES = {
    1: "Option 1 – EKAS 6503",
    2: "Option 2 – Factsheet 33077 (Fliesen < 5 m²)",
    3: "Option 3 – Factsheet 33036 (LBP < 0.5 m²)",
    4: "Option 4 – Factsheet 33049 (Vinyl schw. Kleber)",
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/calculate", methods=["POST"])
def calculate():
    data    = request.get_json()
    T       = float(data.get("T", 0))
    S       = float(data.get("S", 0))
    LM      = float(data.get("LM", 0))
    option  = int(data.get("option", 1))

    if T <= 0:
        return jsonify({"error": "Anzahl Tage muss grösser als 0 sein."}), 400

    base  = (T * 2 * 8 * 65) + (150 * T) + (S * 10)
    total = base + (LM * 800) if option in (1, 3) else base

    return jsonify({
        "total":       total,
        "base":        base,
        "lm_cost":     LM * 800 if option in (1, 3) else 0,
        "option_name": OPTION_NAMES[option],
        "formatted":   f"CHF {total:,.2f}".replace(",", "'"),
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 80))
    app.run(host="0.0.0.0", port=port)
