import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from datetime import datetime

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=None):
    app = Flask(__name__)
    
    # Carregar variáveis de ambiente do arquivo .env
    load_dotenv()
    
    # Configuração do banco de dados
    if os.environ.get('USE_SQLITE', 'False').lower() == 'true':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///calendario_academico.db'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost/calendario_academico')
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-secreta-dev')
    
    # Inicializar extensões
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Adicionar variáveis globais para templates
    @app.context_processor
    def inject_now():
        return {'now': datetime.now()}
    
    # Importar e registrar blueprints
    from app.controllers.main_routes import main as main_bp
    app.register_blueprint(main_bp)
    
    from app.controllers.tipo_calendario_routes import tipo_calendario_bp
    app.register_blueprint(tipo_calendario_bp)
    
    from app.controllers.periodo_routes import periodo_bp
    app.register_blueprint(periodo_bp)
    
    from app.controllers.calendario_routes import calendario_bp
    app.register_blueprint(calendario_bp)
    
    from app.controllers.categoria_routes import categoria_bp
    app.register_blueprint(categoria_bp)
    
    from app.controllers.evento_routes import evento_bp
    app.register_blueprint(evento_bp)

    # Registrar o novo blueprint de relatórios
    from app.controllers.relatorio_routes import relatorio_bp
    app.register_blueprint(relatorio_bp)
    
    # Registrar comandos CLI
    from app.cli import register_commands
    register_commands(app)
    
    # Configurar tratamento de erros
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500
    
    return app

# Importar modelos
from app.models import models
# Importar também os modelos de views
from app.models import views