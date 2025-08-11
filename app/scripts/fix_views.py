#!/usr/bin/env python3
import os
import sys
import sqlite3
import psycopg2
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

def get_connection_string():
    """Obter string de conexão do banco de dados"""
    load_dotenv()
    if os.environ.get('USE_SQLITE', 'False').lower() == 'true':
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                              'instance', 'calendario_academico.db')
        conn_string = f'sqlite:///{db_path}'
        db_type = 'sqlite'
        direct_path = db_path
    else:
        conn_string = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost/calendario_academico')
        db_type = 'postgresql'
        direct_path = conn_string.replace('postgresql://', '')
        
    return conn_string, db_type, direct_path

def fix_postgresql_views():
    """Corrige as views no PostgreSQL"""
    conn_string, _, direct_conn = get_connection_string()
    
    # Parse da string de conexão PostgreSQL
    if '@' in direct_conn:
        user_pass, host_db = direct_conn.split('@')
        if ':' in user_pass:
            user, password = user_pass.split(':')
        else:
            user, password = user_pass, ''
            
        if '/' in host_db:
            host_port, dbname = host_db.split('/')
            if ':' in host_port:
                host, port = host_port.split(':')
            else:
                host, port = host_port, '5432'
        else:
            host, port = host_db, '5432'
            dbname = 'calendario_academico'
    else:
        print("Formato de string de conexão PostgreSQL inválido")
        return False
        
    try:
        # Conexão direta ao PostgreSQL
        conn = psycopg2.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=dbname
        )
        cursor = conn.cursor()
        
        print(f"Conectado ao PostgreSQL: {host}:{port}/{dbname}")
        
        # Verificar objetos existentes
        cursor.execute("""
            SELECT table_name, table_type 
            FROM information_schema.tables 
            WHERE table_name LIKE 'vw_%'
        """)
        
        objects = cursor.fetchall()
        print(f"\nObjetos encontrados com prefixo 'vw_': {len(objects)}")
        
        for obj_name, obj_type in objects:
            print(f"  - {obj_name} ({obj_type})")
            
            # Determinar o comando correto para remover
            if obj_type == 'VIEW':
                drop_sql = f"DROP VIEW {obj_name} CASCADE;"
            else:
                drop_sql = f"DROP TABLE {obj_name} CASCADE;"
                
            try:
                cursor.execute(drop_sql)
                print(f"    ✓ Removido com sucesso usando: {drop_sql}")
            except Exception as e:
                print(f"    ✗ Erro ao remover: {str(e)}")
                
        conn.commit()
        conn.close()
        
        print("\nLimpeza PostgreSQL concluída com sucesso!")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao conectar/manipular PostgreSQL: {str(e)}")
        return False

def fix_sqlite_views():
    """Corrige as views no SQLite"""
    _, _, db_path = get_connection_string()
    
    try:
        # Verificar se o arquivo existe
        if not os.path.exists(db_path):
            print(f"Arquivo do banco SQLite não encontrado: {db_path}")
            return False
            
        # Conexão direta ao SQLite
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"Conectado ao SQLite: {db_path}")
        
        # Verificar objetos existentes
        cursor.execute("SELECT name, type FROM sqlite_master WHERE name LIKE 'vw_%'")
        objects = cursor.fetchall()
        
        print(f"\nObjetos encontrados com prefixo 'vw_': {len(objects)}")
        
        for obj_name, obj_type in objects:
            print(f"  - {obj_name} ({obj_type})")
            
            # No SQLite, precisamos dropar explicitamente o tipo correto
            if obj_type.upper() == 'VIEW':
                drop_sql = f"DROP VIEW IF EXISTS {obj_name}"
            else:
                drop_sql = f"DROP TABLE IF EXISTS {obj_name}"
                
            try:
                cursor.execute(drop_sql)
                print(f"    ✓ Removido com sucesso usando: {drop_sql}")
            except Exception as e:
                print(f"    ✗ Erro ao remover: {str(e)}")
                
        conn.commit()
        conn.close()
        
        print("\nLimpeza SQLite concluída com sucesso!")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao conectar/manipular SQLite: {str(e)}")
        return False

def main():
    """Função principal que detecta o tipo de banco e corrige as views"""
    _, db_type, _ = get_connection_string()
    
    print(f"Tipo de banco de dados detectado: {db_type.upper()}")
    print("Iniciando correção das views...")
    
    success = False
    if db_type == 'postgresql':
        success = fix_postgresql_views()
    else:
        success = fix_sqlite_views()
        
    if success:
        print("\n✅ Correção concluída! Agora execute:")
        print("  flask init-advanced-features")
    else:
        print("\n❌ Ocorreu um erro. Verifique as mensagens acima.")
        
if __name__ == "__main__":
    print("=== CORREÇÃO DE VIEWS NO BANCO DE DADOS ===\n")
    main()