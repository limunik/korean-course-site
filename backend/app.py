import os
from flask import Flask
from models.database import init_db
from routes.main import main_bp
from routes.admin import admin_bp

# ===========================
# App Factory
# ===========================
def create_app():
    app = Flask(
        __name__,
        template_folder="../frontend/templates",
        static_folder="../frontend/static",
    )

    # ── Secret key (required for flash messages & sessions) ──
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    # ── Database ──────────────────────────────────────────────
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///korean_school.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # ── Initialize DB ─────────────────────────────────────────
    init_db(app)

    # ── Register Blueprints ───────────────────────────────────
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    return app


# ===========================
# Run
# ===========================
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)