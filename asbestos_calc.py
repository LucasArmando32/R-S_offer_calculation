import sys
import os
import re
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QDoubleSpinBox, QRadioButton,
    QPushButton, QButtonGroup, QFrame, QLineEdit,
    QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt


STYLE = """
    QMainWindow {
        background-color: #f5f5f5;
    }
    QWidget#central {
        background-color: #f5f5f5;
    }
    QFrame#card {
        background-color: #ffffff;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
    }
    QLabel#title {
        color: #1a1a2e;
        font-size: 20px;
        font-weight: bold;
    }
    QLabel#subtitle {
        color: #666666;
        font-size: 12px;
    }
    QLabel#section_label {
        color: #333333;
        font-size: 13px;
        font-weight: bold;
    }
    QLabel#field_label {
        color: #555555;
        font-size: 12px;
    }
    QDoubleSpinBox {
        background-color: #f9f9f9;
        border: 1px solid #cccccc;
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 13px;
        color: #222222;
        min-width: 120px;
    }
    QDoubleSpinBox:focus {
        border: 1.5px solid #3a7bd5;
        background-color: #ffffff;
    }
    QLineEdit {
        background-color: #f9f9f9;
        border: 1px solid #cccccc;
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 13px;
        color: #222222;
        min-width: 180px;
    }
    QLineEdit:focus {
        border: 1.5px solid #3a7bd5;
        background-color: #ffffff;
    }
    QRadioButton {
        font-size: 12px;
        color: #333333;
        spacing: 8px;
        padding: 6px 4px;
    }
    QRadioButton::indicator {
        width: 16px;
        height: 16px;
    }
    QRadioButton:checked {
        color: #1a1a2e;
        font-weight: bold;
    }
    QPushButton#calc_btn {
        background-color: #3a7bd5;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-size: 14px;
        font-weight: bold;
    }
    QPushButton#calc_btn:hover {
        background-color: #2d6abf;
    }
    QPushButton#calc_btn:pressed {
        background-color: #245aa8;
    }
    QPushButton#reset_btn {
        background-color: transparent;
        color: #888888;
        border: 1px solid #cccccc;
        border-radius: 8px;
        padding: 12px 24px;
        font-size: 13px;
    }
    QPushButton#reset_btn:hover {
        background-color: #eeeeee;
        color: #555555;
    }
    QPushButton#save_btn {
        background-color: #27ae60;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-size: 13px;
        font-weight: bold;
    }
    QPushButton#save_btn:hover {
        background-color: #219a52;
    }
    QPushButton#save_btn:pressed {
        background-color: #1a7d42;
    }
    QFrame#result_box {
        background-color: #1a1a2e;
        border-radius: 10px;
    }
    QLabel#result_label {
        color: #aaaacc;
        font-size: 12px;
    }
    QLabel#result_value {
        color: #ffffff;
        font-size: 28px;
        font-weight: bold;
    }
    QLabel#error_label {
        color: #e05555;
        font-size: 12px;
    }
"""

OPTION_NAMES = {
    1: "Option 1 – EKAS 6503",
    2: "Option 2 – Factsheet 33077 (Fliesen < 5 m²)",
    3: "Option 3 – Factsheet 33036 (LBP < 0.5 m²)",
    4: "Option 4 – Factsheet 33049 (Vinyl schw. Kleber)",
}


class AsbestosCalc(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Asbestsanierung – Kalkulation")
        self.setMinimumWidth(480)
        self.setMaximumWidth(580)

        # Track last calculated result for saving
        self._last_result = None

        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)

        outer = QVBoxLayout(central)
        outer.setContentsMargins(24, 24, 24, 24)
        outer.setSpacing(16)

        # ── Header ──────────────────────────────────────────────
        header_lbl = QLabel("Asbestsanierung")
        header_lbl.setObjectName("title")
        sub_lbl = QLabel("Kalkulation ohne MwSt · CHF")
        sub_lbl.setObjectName("subtitle")
        outer.addWidget(header_lbl)
        outer.addWidget(sub_lbl)

        # ── Inputs card ─────────────────────────────────────────
        inputs_card = QFrame()
        inputs_card.setObjectName("card")
        inputs_layout = QVBoxLayout(inputs_card)
        inputs_layout.setContentsMargins(20, 20, 20, 20)
        inputs_layout.setSpacing(12)

        inp_title = QLabel("Eingabeparameter")
        inp_title.setObjectName("section_label")
        inputs_layout.addWidget(inp_title)

        # Baustelle name field
        self.baustelle_input = self._make_text_row(inputs_layout, "Baustelle")

        self.spin_T  = self._make_spin_row(inputs_layout, "T  – Anzahl Tage",        1, 365,   1)
        self.spin_S  = self._make_spin_row(inputs_layout, "S  – Fläche (m²)",        0, 99999, 0)
        self.spin_LM = self._make_spin_row(inputs_layout, "LM – Anzahl Luftmessung", 0, 999,   0)

        outer.addWidget(inputs_card)

        # ── Options card ─────────────────────────────────────────
        options_card = QFrame()
        options_card.setObjectName("card")
        options_layout = QVBoxLayout(options_card)
        options_layout.setContentsMargins(20, 20, 20, 20)
        options_layout.setSpacing(4)

        opt_title = QLabel("Sanierungsart")
        opt_title.setObjectName("section_label")
        options_layout.addWidget(opt_title)

        self.btn_group = QButtonGroup(self)
        for idx, (val, text) in enumerate(OPTION_NAMES.items()):
            rb = QRadioButton(text)
            if idx == 0:
                rb.setChecked(True)
            self.btn_group.addButton(rb, val)
            options_layout.addWidget(rb)

        outer.addWidget(options_card)

        # ── Buttons ──────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        reset_btn = QPushButton("Zurücksetzen")
        reset_btn.setObjectName("reset_btn")
        reset_btn.clicked.connect(self.reset)

        calc_btn = QPushButton("Berechnen")
        calc_btn.setObjectName("calc_btn")
        calc_btn.clicked.connect(self.calculate)

        save_btn = QPushButton("Speichern")
        save_btn.setObjectName("save_btn")
        save_btn.clicked.connect(self.save_result)

        btn_row.addWidget(reset_btn)
        btn_row.addWidget(calc_btn)
        btn_row.addWidget(save_btn)
        outer.addLayout(btn_row)

        # ── Result box ───────────────────────────────────────────
        result_box = QFrame()
        result_box.setObjectName("result_box")
        result_inner = QVBoxLayout(result_box)
        result_inner.setContentsMargins(20, 16, 20, 16)
        result_inner.setSpacing(4)

        res_lbl = QLabel("Total (ohne MwSt)")
        res_lbl.setObjectName("result_label")
        res_lbl.setAlignment(Qt.AlignCenter)

        self.result_value = QLabel("–")
        self.result_value.setObjectName("result_value")
        self.result_value.setAlignment(Qt.AlignCenter)

        self.error_label = QLabel("")
        self.error_label.setObjectName("error_label")
        self.error_label.setAlignment(Qt.AlignCenter)

        result_inner.addWidget(res_lbl)
        result_inner.addWidget(self.result_value)
        result_inner.addWidget(self.error_label)

        outer.addWidget(result_box)
        outer.addStretch()

    # ── Helpers ──────────────────────────────────────────────────
    def _make_text_row(self, layout, label_text):
        row = QHBoxLayout()
        lbl = QLabel(label_text)
        lbl.setObjectName("field_label")
        lbl.setMinimumWidth(220)

        field = QLineEdit()
        field.setPlaceholderText("z.B. Küche, Könizstrasse 14")

        row.addWidget(lbl)
        row.addStretch()
        row.addWidget(field)
        layout.addLayout(row)
        return field

    def _make_spin_row(self, layout, label_text, min_val, max_val, default):
        row = QHBoxLayout()
        lbl = QLabel(label_text)
        lbl.setObjectName("field_label")
        lbl.setMinimumWidth(220)

        spin = QDoubleSpinBox()
        spin.setMinimum(min_val)
        spin.setMaximum(max_val)
        spin.setValue(default)
        spin.setDecimals(1)
        spin.setSingleStep(1)

        row.addWidget(lbl)
        row.addStretch()
        row.addWidget(spin)
        layout.addLayout(row)
        return spin

    # ── Logic ────────────────────────────────────────────────────
    def calculate(self):
        self.error_label.setText("")
        self._last_result = None

        T      = self.spin_T.value()
        S      = self.spin_S.value()
        LM     = self.spin_LM.value()
        option = self.btn_group.checkedId()

        if T <= 0:
            self.error_label.setText("Anzahl Tage muss grösser als 0 sein.")
            self.result_value.setText("–")
            return

        base = (T * 2 * 8 * 65) + (150 * T) + (S * 10)

        if option in (1, 3):
            total = base + (LM * 800)
        else:
            total = base

        formatted = f"CHF {total:,.2f}".replace(",", "'")
        self.result_value.setText(formatted)

        # Store for saving
        self._last_result = {
            "baustelle": self.baustelle_input.text().strip(),
            "T": T, "S": S, "LM": LM,
            "option": option,
            "base": base,
            "total": total,
            "formatted": formatted,
        }

    def save_result(self):
        if self._last_result is None:
            QMessageBox.warning(self, "Nichts zu speichern",
                                "Bitte zuerst eine Berechnung durchführen.")
            return

        r = self._last_result
        baustelle = r["baustelle"] or "Unbekannt"

        # Build a safe filename
        safe_name  = re.sub(r'[^\w\s\-]', '', baustelle).strip().replace(" ", "_")
        price_str  = f"CHF_{r['total']:,.0f}".replace(",", "'")
        opt_short  = f"Opt{r['option']}"
        default_fn = f"{safe_name}_{price_str}_{opt_short}.txt"

        # Let user choose save location
        path, _ = QFileDialog.getSaveFileName(
            self, "Kalkulation speichern",
            os.path.join(os.path.expanduser("~"), "Desktop", default_fn),
            "Textdateien (*.txt)"
        )
        if not path:
            return  # user cancelled

        # Build file content
        option_name = OPTION_NAMES[r["option"]]
        now         = datetime.now().strftime("%d.%m.%Y %H:%M")

        if r["option"] in (1, 3):
            formula_line = (
                f"  (T × 2 × 8 × 65) + (150 × T) + (S × 10) + (LM × 800)\n"
                f"  ({r['T']:.0f} × 2 × 8 × 65) + (150 × {r['T']:.0f}) + "
                f"({r['S']:.0f} × 10) + ({r['LM']:.0f} × 800)"
            )
        else:
            formula_line = (
                f"  (T × 2 × 8 × 65) + (150 × T) + (S × 10)\n"
                f"  ({r['T']:.0f} × 2 × 8 × 65) + (150 × {r['T']:.0f}) + "
                f"({r['S']:.0f} × 10)"
            )

        content = f"""========================================
  ASBESTSANIERUNG – KALKULATION
========================================
Datum:       {now}
Baustelle:   {baustelle}

----------------------------------------
EINGABEPARAMETER
----------------------------------------
  Anzahl Tage (T)         : {r['T']:.0f}
  Fläche in m² (S)        : {r['S']:.0f}
  Anzahl Luftmessung (LM) : {r['LM']:.0f}

----------------------------------------
SANIERUNGSART
----------------------------------------
  {option_name}

----------------------------------------
BERECHNUNG
----------------------------------------
{formula_line}

  Zwischentotal (Basis)   : CHF {r['base']:>10,.2f}
{"  Luftmessung (LM × 800) : CHF " + f"{r['LM'] * 800:>10,.2f}" if r['option'] in (1,3) else ""}
----------------------------------------
  TOTAL (ohne MwSt)       : {r['formatted']}
========================================
""".replace(",", "'")

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            QMessageBox.information(self, "Gespeichert",
                                    f"Datei gespeichert:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Konnte nicht speichern:\n{e}")

    def reset(self):
        self.baustelle_input.clear()
        self.spin_T.setValue(1)
        self.spin_S.setValue(0)
        self.spin_LM.setValue(0)
        self.btn_group.button(1).setChecked(True)
        self.result_value.setText("–")
        self.error_label.setText("")
        self._last_result = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)
    window = AsbestosCalc()
    window.show()
    sys.exit(app.exec())
