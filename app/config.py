import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chave-secreta-padrao'
    
    # Use SQLite para desenvolvimento local
    if os.environ.get('USE_SQLITE', 'False').lower() == 'true':
        SQLALCHEMY_DATABASE_URI = 'sqlite:///calendario_academico.db'
    else:
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
            'postgresql://postgres:postgres@localhost/calendario_academico'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False