import os
from fpdf import FPDF
from datetime import datetime


def _clean(text):
    if not text:
        return ""
    text = str(text)
    text = text.replace("\u2014", "--")
    text = text.replace("\u2013", "-")
    text = text.replace("\u2019", "'")
    text = text.replace("\u2018", "'")
    text = text.replace("\u201c", '"')
    text = text.replace("\u201d", '"')
    text = text.replace("\u2022", "-")
    text = text.replace("\u00b0", " deg")
    text = text.replace("\u00e9", "e")
    text = text.replace("\u00e0", "a")
    text = text.replace("\u00e8", "e")
    text = text.replace("\u2026", "...")
    text = text.replace("\u00b7", "-")
    text = text.replace("\u2012", "-")
    text = text.replace("\u2015", "--")
    text = text.replace("\u2010", "-")
    text = text.replace("\u2011", "-")
    text = text.replace("\u00fc", "u")
    text = text.replace("\u00f6", "o")
    text = text.replace("\u00e4", "a")
    text = text.replace("\u00dc", "U")
    text = text.replace("\u00d6", "O")
    text = text.replace("\u00c4", "A")
    text = text.replace("\u00df", "ss")
    text = text.replace("\u00f1", "n")
    text = text.replace("\u00e7", "c")
    text = text.replace("\u00e1", "a")
    text = text.replace("\u00ed", "i")
    text = text.replace("\u00f3", "o")
    text = text.replace("\u00fa", "u")
    text = text.encode("ascii", "ignore").decode("ascii")
    return text.strip()


def _trim(text, max_len=90):
    t = _clean(text)
    return t[:max_len] + "..." if len(t) > max_len else t


class SugarcanePDF(FPDF):

    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.set_fill_color(10, 50, 18)
        self.set_text_color(255, 255, 255)
        self.cell(0, 12, "CANEGUARD AI DISEASE DETECTION REPORT",
                  align="C", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(3)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(150, 150, 150)
        self.cell(
            0, 8,
            "Generated: " + datetime.now().strftime("%Y-%m-%d %H:%M") +
            "  |  SugarScan  |  Page " + str(self.page_no()) +
            "  |  Ayyaz Qamar & M.Hamza",
            align="C"
        )

    def section_title(self, title):
        self.set_font("Helvetica", "B", 10)
        self.set_fill_color(232, 248, 235)
        self.set_draw_color(14, 100, 40)
        self.set_text_color(10, 70, 25)
        self.cell(0, 8, "  " + _clean(title),
                  border="LB", fill=True,
                  new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.set_draw_color(0, 0, 0)
        self.ln(2)

    def kv(self, label, value, vc=None):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(80, 80, 80)
        self.cell(48, 7, _clean(label) + ":")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*(vc or (30, 30, 30)))
        val = _clean(str(value))
        if len(val) > 100:
            val = val[:100] + "..."
        self.cell(0, 7, val, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)

    def bullet(self, text):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(40, 40, 40)
        clean = _clean(str(text))
        if len(clean) > 88:
            clean = clean[:88] + "..."
        margin = self.l_margin
        self.set_x(margin + 5)
        available = self.epw - 5
        self.multi_cell(available, 6, "- " + clean,
                        new_x="LMARGIN", new_y="NEXT")

    def bullets(self, items):
        lst = items if isinstance(items, list) else [items]
        for item in lst:
            self.bullet(item)
        self.ln(1)

    def sub_title(self, text):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(60, 60, 60)
        self.cell(0, 7, _clean(text),
                  new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)


def generate_report(scan_data, treatment_data,
                    weather_data=None, reports_folder="reports"):

    pdf = SugarcanePDF()
    pdf.set_margins(15, 15, 15)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=16)

    # ── Scan Info ─────────────────────────────────────────────────────────────
    pdf.section_title("Scan Information")
    pdf.kv("Date & Time",
           datetime.now().strftime("%d %b %Y  %I:%M %p"))
    pdf.kv("Input Type",
           scan_data.get("input_type", "Image Upload"))
    pdf.kv("Image File",
           os.path.basename(scan_data.get("image_path", "N/A")))
    pdf.ln(3)

    # ── Detection Result ──────────────────────────────────────────────────────
    pdf.section_title("Disease Detection Result")

    disease  = scan_data.get("disease", "Unknown")
    conf     = scan_data.get("confidence", 0)
    damage   = scan_data.get("damage_pct", 0)
    severity = scan_data.get("severity", "Unknown")

    sev_c = {
        "Mild":     (22, 163, 74),
        "Moderate": (202, 138, 4),
        "Severe":   (220, 38, 38),
    }
    dis_c = (220, 38, 38) if disease != "healthy" else (22, 163, 74)

    pdf.kv("Disease",
           treatment_data.get("name", disease), vc=dis_c)
    pdf.kv("Confidence",  f"{float(conf):.1f}%")
    pdf.kv("Leaf Damage", f"{float(damage):.1f}%")
    pdf.kv("Severity",    severity, vc=sev_c.get(severity))

    desc = _clean(treatment_data.get("description", ""))
    if len(desc) > 120:
        desc = desc[:120] + "..."
    pdf.kv("Description", desc)
    pdf.ln(3)

    # ── Treatment ─────────────────────────────────────────────────────────────
    pdf.section_title("Treatment Recommendations")

    pdf.sub_title("Fungicide / Chemical Spray:")
    pdf.bullets(treatment_data.get("fungicide", []))

    pdf.sub_title("Fertilizer Recommendations:")
    pdf.bullets(treatment_data.get("fertilizer", []))

    pdf.sub_title("Precautions:")
    pdf.bullets(treatment_data.get("precautions", []))
    pdf.ln(3)

    # ── Weather ───────────────────────────────────────────────────────────────
    if weather_data:
        pdf.section_title("Weather Risk Assessment")
        overall = weather_data.get("overall_risk", {})
        rc = {
            "high":   (220, 38, 38),
            "medium": (202, 138, 4),
            "low":    (22, 163, 74),
        }
        pdf.kv("City",
               weather_data.get("city", ""))
        pdf.kv("Overall Risk",
               overall.get("label", ""),
               vc=rc.get(overall.get("level", "low")))
        pdf.kv("Fetched At",
               weather_data.get("fetched_at", ""))
        if weather_data.get("demo_mode"):
            pdf.kv("Note",
                   "Demo data -- add OpenWeatherMap API key for live forecast")
        pdf.ln(2)

        pdf.sub_title("7-Day Forecast:")
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(50, 50, 50)
        for day in weather_data.get("forecast", [])[:7]:
            line = (
                str(day.get("date", "")) +
                "  |  " + str(day.get("temp", "")) + "C" +
                "  |  Humidity: " + str(day.get("humidity", "")) + "%" +
                "  |  Rain: " + str(day.get("rain", "")) + "mm" +
                "  |  " + _clean(str(day.get("risk_label", "")))
            )
            pdf.cell(0, 5, line, new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(3)

    # ── Contact ───────────────────────────────────────────────────────────────
    pdf.section_title("Contact Information")
    pdf.kv("Developers", "Ayyaz Qamar & M.Hamza")
    pdf.kv("Email",      "ayyazqamar12@gmail.com")
    pdf.kv("Phone",      "+92 355 6931418")
    pdf.kv("Project",
           "CaneGuard AI")

    # ── Save ──────────────────────────────────────────────────────────────────
    os.makedirs(reports_folder, exist_ok=True)
    fname = "report_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".pdf"
    fpath = os.path.join(reports_folder, fname)
    pdf.output(fpath)
    return fpath