from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from app.config import Config

# Inicializa extensões
db = SQLAlchemy()
migrate = Migrate()
bootstrap = Bootstrap()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializa extensões com o aplicativo
    db.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)

    # Registra blueprints
    from app.controllers.main_routes import main
    from app.controllers.periodo_routes import periodo_bp
    from app.controllers.calendario_routes import calendario_bp
    from app.controllers.categoria_routes import categoria_bp
    from app.controllers.evento_routes import evento_bp

    app.register_blueprint(main)
    app.register_blueprint(periodo_bp)
    app.register_blueprint(calendario_bp)
    app.register_blueprint(categoria_bp)
    app.register_blueprint(evento_bp)

    return app