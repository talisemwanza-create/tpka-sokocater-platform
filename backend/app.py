import os
from flask import Flask, jsonify
from extensions import db, jwt
import models
from routes.auth_routes import auth_bp
from routes.caterer_routes import caterer_bp
from routes.menu_routes import menu_bp
from routes.package_routes import package_bp
from routes.booking_routes import booking_bp

def create_app(test_config=None):
    app = Flask(__name__)
    os.makedirs(app.instance_path, exist_ok=True)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sokocater.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "sokocater-development-secret-key")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600
    if test_config:
        app.config.update(test_config)
    db.init_app(app)
    jwt.init_app(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(caterer_bp)
    app.register_blueprint(menu_bp)
    app.register_blueprint(package_bp)
    app.register_blueprint(booking_bp)
    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"status": "healthy", "message": "SokoCater backend is running"}), 200
    return app

app = create_app()
if __name__ == "__main__":
    app.run(debug=True)
