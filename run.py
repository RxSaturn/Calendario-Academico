from app import create_app, db
from app.models.models import Periodo, TipoCalendario, Calendario, CategoriaCalendario, Eventos
import click
from datetime import datetime
from flask.cli import with_appcontext

app = create_app()

@app.context_processor
def inject_now():
    return {'now': datetime.now()}

@app.cli.command('create-tables')
@with_appcontext
def create_tables():
    """Cria as tabelas do banco de dados."""
    db.create_all()
    click.echo('Tabelas criadas com sucesso!')

@app.cli.command('seed-db')
@with_appcontext
def seed_db_command():
    """Popular o banco de dados com dados iniciais."""
    from app.scripts.seed_data import seed_database
    seed_database()
    click.echo('Banco de dados populado com sucesso!')

if __name__ == '__main__':
    app.run(debug=True)