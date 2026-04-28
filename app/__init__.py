from flask import Flask
from flask_login import LoginManager
import os

login_manager = LoginManager()


def create_app():
    app = Flask(__name__,
                template_folder="templates",
                static_folder="static")

    app.config["SECRET_KEY"]         = "sugarcane-secret-2026"
    app.config["UPLOAD_FOLDER"]      = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "uploads")
    app.config["REPORTS_FOLDER"]     = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "reports")
    app.config["MODEL_PATH"]         = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "model", "caneguard_v2_best.keras")
    app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024

    os.makedirs(app.config["UPLOAD_FOLDER"],  exist_ok=True)
    os.makedirs(app.config["REPORTS_FOLDER"], exist_ok=True)

    login_manager.init_app(app)
    login_manager.login_view    = "auth.login"
    login_manager.login_message = ""

    from .auth   import auth_bp
    from .routes import main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    # ── Model startup par load karo ──────────────────────────────
    with app.app_context():
        try:
            from modules.disease_detector import load_model
            print("=" * 50)
            print("Loading AI model at startup...")
            app._sc_model = load_model()
            print("Model loaded successfully!")
            print("=" * 50)
        except Exception as e:
            import traceback
            print(f"Startup model load ERROR: {e}")
            traceback.print_exc()
            app._sc_model = None

    return app