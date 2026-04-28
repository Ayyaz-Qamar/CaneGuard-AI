from flask import (Blueprint, render_template, request, redirect,
                   url_for, session, jsonify, send_file, current_app)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os, sys, uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from .models import (save_scan, get_scans, delete_scan_db,
                     get_stats, update_scan_pdf, get_db, init_db,
                     update_profile_pic, reset_user_data)

main_bp = Blueprint("main", __name__)

ALLOWED_IMG   = {"jpg", "jpeg", "png"}
ALLOWED_VIDEO = {"mp4", "avi", "mov"}


def _lang():
    return session.get("lang", "en")


def _city():
    return session.get("city", "Rahim Yar Khan")


def _ext(filename):
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def _run_analysis(img_path, lang, city):
    from modules.disease_detector  import predict_image, load_model
    from modules.damage_calculator import calculate_damage
    from modules.treatment_engine  import (get_treatment, get_name, get_desc,
                                           get_fungicide, get_fertilizer,
                                           get_precautions, get_weather_advice)
    from modules.weather_module    import get_weather_forecast

    model = load_model()

    if model is None:
        raise Exception("Model not loaded. Check model/caneguard_v2_best.keras")

    print(f"Predicting: {img_path}")
    detection = predict_image(img_path, model)
    print(f"Result: {detection}")

    damage        = calculate_damage(img_path)
    trt           = get_treatment(detection["disease"])
    weather       = get_weather_forecast(city)
    w_adv         = get_weather_advice(
        detection["disease"],
        weather["overall_risk"]["level"], lang)
    overall_label = weather["overall_risk"].get(
        "label_ur" if lang == "ur" else "label",
        weather["overall_risk"]["label"])

    return {
        "detection":         detection,
        "damage":            damage,
        "trt":               trt,
        "weather":           weather,
        "w_adv":             w_adv,
        "overall_label":     overall_label,
        "disease_name":      get_name(detection["disease"], lang),
        "description":       get_desc(detection["disease"], lang),
        "fungicide":         get_fungicide(detection["disease"], lang),
        "fertilizer":        get_fertilizer(detection["disease"], lang),
        "precautions":       get_precautions(detection["disease"], lang),
        "all_scores_labels": {
            get_name(k, lang): round(v, 1)
            for k, v in detection.get("all_scores", {}).items()
        },
    }


@main_bp.route("/")
@login_required
def home():
    from modules.treatment_engine import get_name
    lang     = _lang()
    stats    = get_stats(current_user.id)
    diseased = sum(r["cnt"] for r in stats["by_disease"]
                   if r["disease_name"] != "healthy")
    scans    = get_scans(current_user.id)[:5]
    for s in scans:
        s["disease_label"] = get_name(s["disease_name"], lang)
    return render_template("home.html", lang=lang, stats=stats,
                           diseased=diseased, city=_city(),
                           user=current_user, recent_scans=scans)


@main_bp.route("/set-lang", methods=["POST"])
def set_lang():
    session["lang"] = request.get_json(force=True).get("lang", "en")
    return jsonify({"ok": True})


@main_bp.route("/set-city", methods=["POST"])
def set_city():
    session["city"] = request.get_json(force=True).get("city", "Rahim Yar Khan")
    return jsonify({"ok": True})


@main_bp.route("/set-theme", methods=["POST"])
def set_theme():
    session["theme"] = request.get_json(force=True).get("theme", "dark")
    return jsonify({"ok": True})


@main_bp.route("/detect-location")
def detect_location():
    from modules.weather_module import get_city_from_ip
    loc = get_city_from_ip()
    if loc["success"]:
        session["city"] = loc["city"]
    return jsonify(loc)


@main_bp.route("/upload-profile-pic", methods=["POST"])
@login_required
def upload_profile_pic_route():
    if "profile_pic" not in request.files:
        return jsonify({"error": "No file"}), 400
    f = request.files["profile_pic"]
    if not f.filename or _ext(f.filename) not in ALLOWED_IMG:
        return jsonify({"error": "Invalid file"}), 400
    filename = (f"profile_{current_user.id}_"
                f"{uuid.uuid4().hex[:8]}.{_ext(f.filename)}")
    folder   = os.path.join(current_app.config["UPLOAD_FOLDER"], "profiles")
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)
    f.save(path)
    update_profile_pic(current_user.id, f"profiles/{filename}")
    return jsonify({"success": True})


@main_bp.route("/profile-pic/<path:filename>")
@login_required
def profile_pic(filename):
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    if not os.path.exists(path):
        return "Not found", 404
    return send_file(path)


@main_bp.route("/update-profile", methods=["POST"])
@login_required
def update_profile():
    data      = request.get_json(force=True)
    full_name = data.get("full_name", "").strip()
    if not full_name:
        return jsonify({"success": False, "error": "Empty name"})
    init_db()
    conn = get_db()
    conn.execute("UPDATE users SET full_name=? WHERE id=?",
                 (full_name, current_user.id))
    conn.commit()
    conn.close()
    current_user.full_name = full_name
    return jsonify({"success": True})


@main_bp.route("/settings")
@login_required
def settings():
    return render_template("settings.html", lang=_lang(), user=current_user)


@main_bp.route("/detect", methods=["GET", "POST"])
@login_required
def detect():
    if request.method == "GET":
        return render_template("detect.html", lang=_lang(), city=_city(),
                               user=current_user,
                               tab=request.args.get("tab", "image"))

    if "image" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    f = request.files["image"]
    if not f.filename or _ext(f.filename) not in ALLOWED_IMG:
        return jsonify({"error": "Invalid file. Use JPG or PNG."}), 400

    lang = request.form.get("lang", _lang())
    city = request.form.get("city", _city())
    session["city"] = city

    filename = f"{uuid.uuid4().hex}.{_ext(f.filename)}"
    img_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    f.save(img_path)

    try:
        r       = _run_analysis(img_path, lang, city)
        scan_id = save_scan(
            user_id      = current_user.id,
            image_path   = img_path,
            input_type   = "Image Upload",
            disease_name = r["detection"]["disease"],
            confidence   = r["detection"]["confidence"],
            damage_pct   = r["damage"]["damage_percent"],
            severity     = r["damage"]["severity"],
            weather_risk = r["weather"]["overall_risk"]["level"],
            city         = city,
        )
        return jsonify({
            "scan_id":           scan_id,
            "disease":           r["detection"]["disease"],
            "disease_name":      r["disease_name"],
            "confidence":        round(r["detection"]["confidence"], 1),
            "damage_pct":        r["damage"]["damage_percent"],
            "severity":          r["damage"]["severity"],
            "description":       r["description"],
            "fungicide":         r["fungicide"],
            "fertilizer":        r["fertilizer"],
            "precautions":       r["precautions"],
            "all_scores_labels": r["all_scores_labels"],
            "weather_advice":    r["w_adv"],
            "weather": {
                "overall_label": r["overall_label"],
                "overall_level": r["weather"]["overall_risk"]["level"],
                "city":          r["weather"]["city"],
                "updated":       r["weather"]["fetched_at"],
                "demo":          r["weather"].get("demo_mode", False),
            },
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@main_bp.route("/detect-video", methods=["POST"])
@login_required
def detect_video():
    return jsonify({"error": "Coming Soon in Version 2.0"}), 200


@main_bp.route("/weather")
@login_required
def weather():
    from modules.weather_module   import get_weather_forecast
    from modules.treatment_engine import get_name, get_weather_advice

    lang = _lang()
    city = request.args.get("city", _city())
    session["city"] = city

    data = get_weather_forecast(city)
    for day in data["forecast"]:
        day["risk_label_display"] = day.get(
            "risk_label_ur" if lang == "ur" else "risk_label",
            day["risk_label"])
    data["overall_label"] = data["overall_risk"].get(
        "label_ur" if lang == "ur" else "label",
        data["overall_risk"]["label"])
    advices = {
        dis: {
            "name":   get_name(dis, lang),
            "advice": get_weather_advice(
                dis, data["overall_risk"]["level"], lang),
        }
        for dis in ["redrot", "mosaic", "yellow", "rust", "bacterialblights"]
    }
    return render_template("weather.html", lang=lang, city=city,
                           weather=data, advices=advices,
                           user=current_user)


@main_bp.route("/history")
@login_required
def history():
    from modules.treatment_engine import get_name
    lang       = _lang()
    filter_dis = request.args.get("filter", "all")
    search     = request.args.get("search", "").strip()
    scans      = get_scans(current_user.id)
    stats      = get_stats(current_user.id)

    if filter_dis != "all":
        scans = [s for s in scans if s["disease_name"] == filter_dis]
    if search:
        scans = [s for s in scans
                 if search.lower() in s["disease_name"].lower()]
    for s in scans:
        s["disease_label"] = get_name(s["disease_name"], lang)

    return render_template("history.html", lang=lang, scans=scans,
                           stats=stats, filter_dis=filter_dis,
                           user=current_user)


@main_bp.route("/delete-scan/<int:scan_id>", methods=["POST"])
@login_required
def delete_scan(scan_id):
    delete_scan_db(scan_id, current_user.id)
    return redirect(url_for("main.history"))


@main_bp.route("/generate-pdf/<int:scan_id>")
@login_required
def generate_pdf(scan_id):
    from modules.treatment_engine import get_treatment
    from modules.weather_module   import get_weather_forecast
    from modules.pdf_generator    import generate_report

    init_db()
    conn = get_db()
    scan = conn.execute(
        "SELECT * FROM scans WHERE id=? AND user_id=?",
        (scan_id, current_user.id)).fetchone()
    conn.close()

    if not scan:
        return "Scan not found", 404

    scan    = dict(scan)
    trt     = get_treatment(scan["disease_name"])
    weather = get_weather_forecast(scan.get("city", "Rahim Yar Khan"))

    pdf_path = generate_report(
        scan_data={
            "disease":    scan["disease_name"],
            "confidence": scan["confidence"],
            "damage_pct": scan["damage_pct"],
            "severity":   scan["severity"],
            "image_path": scan.get("image_path", ""),
            "input_type": scan.get("input_type", "Image"),
        },
        treatment_data={
            "name":        trt["name"]["en"],
            "description": trt["desc"]["en"],
            "fungicide":   trt["fungicide"]["en"],
            "fertilizer":  trt["fertilizer"]["en"],
            "precautions": trt["precautions"]["en"],
        },
        weather_data=weather,
        reports_folder=current_app.config["REPORTS_FOLDER"],
    )
    update_scan_pdf(scan_id, pdf_path)
    fname    = os.path.basename(pdf_path)
    response = send_file(
        pdf_path, mimetype="application/octet-stream",
        as_attachment=True, download_name=fname)
    response.headers["Content-Disposition"] = (
        f'attachment; filename="{fname}"')
    response.headers["Cache-Control"] = (
        "no-cache, no-store, must-revalidate")
    return response


@main_bp.route("/reports")
@login_required
def reports():
    folder = current_app.config["REPORTS_FOLDER"]
    pdfs   = []
    if os.path.exists(folder):
        for f in sorted(os.listdir(folder), reverse=True):
            if f.endswith(".pdf"):
                pdfs.append({
                    "name": f,
                    "size": round(
                        os.path.getsize(
                            os.path.join(folder, f)) / 1024, 1)
                })
    return render_template("reports.html", lang=_lang(),
                           pdfs=pdfs, user=current_user)


@main_bp.route("/download-report/<filename>")
@login_required
def download_report(filename):
    path = os.path.join(current_app.config["REPORTS_FOLDER"],
                        secure_filename(filename))
    if not os.path.exists(path):
        return "Not found", 404
    response = send_file(
        path, mimetype="application/octet-stream",
        as_attachment=True, download_name=filename)
    response.headers["Content-Disposition"] = (
        f'attachment; filename="{filename}"')
    response.headers["Cache-Control"] = (
        "no-cache, no-store, must-revalidate")
    return response


@main_bp.route("/help")
@login_required
def help_page():
    from modules.treatment_engine import (get_treatment, get_name, get_desc,
                                          get_fungicide, get_fertilizer,
                                          get_precautions)
    lang     = _lang()
    diseases = {}
    for key in ["healthy", "bacterialblights", "redrot",
                "mosaic", "yellow", "rust"]:
        diseases[key] = {
            "name":        get_name(key, lang),
            "desc":        get_desc(key, lang),
            "fungicide":   get_fungicide(key, lang),
            "fertilizer":  get_fertilizer(key, lang),
            "precautions": get_precautions(key, lang),
            "risk":        get_treatment(key)["risk_level"],
        }
    return render_template("help.html", lang=lang,
                           diseases=diseases, user=current_user)


@main_bp.route("/reset-data", methods=["POST"])
@login_required
def reset_data():
    reset_user_data(current_user.id)
    return jsonify({"success": True})