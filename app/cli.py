import click
from flask.cli import with_appcontext
from app import db
from sqlalchemy import text

@click.command('create-tables')
@with_appcontext
def create_tables_command():
    """Cria todas as tabelas no banco de dados."""
    db.create_all()
    click.echo("✅ Tabelas criadas com sucesso!")

@click.command('drop-tables')
@with_appcontext
def drop_tables_command():
    """Remove todas as tabelas do banco de dados."""
    db.drop_all()
    click.echo("🗑️ Tabelas removidas com sucesso!")

@click.command('seed-db')
@with_appcontext
def seed_db_command():
    """Popula o banco com dados iniciais."""
    try:
        from app.scripts.seed_data import seed_database
        seed_database()
        click.echo("🌱 Dados iniciais inseridos com sucesso!")
    except Exception as e:
        click.echo(f"❌ Erro ao inserir dados: {str(e)}")

@click.command('init-advanced-features')
@with_appcontext
def init_advanced_features_command():
    """Inicializa recursos avançados do PostgreSQL (visões, funções, gatilhos, regras)."""
    try:
        from app.scripts.setup import setup_db_features
        setup_db_features()
        click.echo("✅ Recursos avançados do PostgreSQL configurados com sucesso!")
    except Exception as e:
        click.echo(f"❌ Erro ao configurar recursos avançados: {str(e)}")

def register_commands(app):
    """Registra todos os comandos personalizados no app Flask."""
    app.cli.add_command(create_tables_command)
    app.cli.add_command(drop_tables_command)
    app.cli.add_command(seed_db_command)
    app.cli.add_command(init_advanced_features_command)