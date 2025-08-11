from app import create_app, db
from sqlalchemy import text, inspect
import logging
import sqlite3
import os

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_db_features():
    """
    Configura os recursos avançados do banco de dados,
    detectando se é PostgreSQL ou SQLite e adaptando os comandos.
    """
    app = create_app()
    with app.app_context():
        # Detectar o tipo de banco de dados
        db_engine = db.engine.name
        logger.info(f"Banco de dados detectado: {db_engine}")
        
        if db_engine == 'postgresql':
            setup_postgresql_features()
        elif db_engine == 'sqlite':
            # Limpa views existentes antes de criar novas
            clean_sqlite_views()
            setup_sqlite_features()
        else:
            logger.warning(f"Banco de dados {db_engine} não suportado para recursos avançados.")

def clean_sqlite_views():
    """Remove manualmente as views existentes do SQLite."""
    try:
        # Obter o caminho do arquivo do banco de dados
        db_path = db.engine.url.database
        if db_path.startswith('/'):
            # Caminho absoluto
            file_path = db_path
        else:
            # Caminho relativo
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            file_path = os.path.join(base_dir, db_path)
            
        logger.info(f"Conectando diretamente ao SQLite em: {file_path}")
        
        # Conectar diretamente ao SQLite
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()
        
        # Limpar qualquer view/tabela existente com nome de view
        views_to_remove = [
            'vw_eventos_ativos_hoje',
            'vw_resumo_calendario',
            'vw_eventos_futuros_ativos'
        ]
        
        for view_name in views_to_remove:
            try:
                # Tentar como tabela
                cursor.execute(f"DROP TABLE IF EXISTS {view_name}")
                # Tentar como view
                cursor.execute(f"DROP VIEW IF EXISTS {view_name}")
            except Exception as e:
                logger.warning(f"Aviso ao remover {view_name}: {str(e)}")
                
        conn.commit()
        conn.close()
        logger.info("Limpeza SQLite concluída")
    except Exception as e:
        logger.error(f"Erro na limpeza SQLite: {str(e)}")

def setup_postgresql_features():
    """Implementa recursos avançados específicos do PostgreSQL"""
    try:
        # --- VISÕES ---
        logger.info("Criando visões no PostgreSQL...")
        
        # 1. Eventos Ativos no Período Atual
        db.session.execute(text("""
        CREATE OR REPLACE VIEW vw_eventos_ativos_hoje AS
        SELECT 
            e.id_evento,
            e.titulo,
            e.descricao,
            e.datainicio,
            e.datafim,
            e.local,
            cc.nome AS categoria
        FROM 
            eventos e
        JOIN 
            categoriacalendario cc ON e.id_categoria = cc.id_categoria
        JOIN 
            calendario c ON cc.id_calendario = c.id_calendario
        JOIN 
            periodo p ON cc.id_periodo = p.id_periodo
        WHERE 
            c.ativo = true
            AND CURRENT_DATE BETWEEN p.datainicial AND p.datafinal
            AND e.datainicio >= CURRENT_DATE
        ORDER BY 
            e.datainicio;
        """))
        
        # 2. Total de Dias Letivos
        db.session.execute(text("""
        CREATE OR REPLACE VIEW vw_dias_letivos AS
        SELECT 
            p.descricao AS periodo,
            c.nome AS calendario,
            cc.nome AS categoria,
            cc.totaldias AS dias_planejados,
            COUNT(DISTINCT e.datainicio) AS dias_com_eventos,
            SUM(CASE WHEN e.datainicio BETWEEN CURRENT_DATE - 30 AND CURRENT_DATE THEN 1 ELSE 0 END) AS eventos_ultimos_30_dias
        FROM 
            periodo p
        JOIN 
            categoriacalendario cc ON p.id_periodo = cc.id_periodo
        JOIN 
            calendario c ON cc.id_calendario = c.id_calendario
        LEFT JOIN 
            eventos e ON cc.id_categoria = e.id_categoria
        WHERE 
            cc.habilitacaocontagem = true
            AND cc.nome NOT LIKE '%Feriados%'
            AND cc.nome NOT LIKE '%Recessos%'
        GROUP BY 
            p.descricao, c.nome, cc.nome, cc.totaldias, p.datainicial
        ORDER BY 
            c.nome, p.datainicial;
        """))
        
        # 3. Resumo do Calendário
        db.session.execute(text("""
        CREATE OR REPLACE VIEW vw_resumo_calendario AS
        SELECT 
            c.id_calendario,
            c.nome AS nomecalendario,
            c.ano,
            c.datainicio,
            c.datafim,
            c.ativo,
            tc.nome AS tipocalendario,
            COUNT(DISTINCT cc.id_categoria) AS totalcategorias,
            COUNT(e.id_evento) AS totaleventos
        FROM 
            calendario c
        JOIN 
            tipocalendario tc ON c.id_tipo = tc.id_tipo
        LEFT JOIN 
            categoriacalendario cc ON c.id_calendario = cc.id_calendario
        LEFT JOIN 
            eventos e ON cc.id_categoria = e.id_categoria
        GROUP BY 
            c.id_calendario, c.nome, c.ano, c.datainicio, c.datafim, c.ativo, tc.nome
        ORDER BY 
            c.ano DESC, c.nome;
        """))
        
        # 4. Feriados Em Dias Letivos
        db.session.execute(text("""
        CREATE OR REPLACE VIEW vw_feriados_dias_letivos AS
        SELECT 
            f.titulo AS feriado,
            f.datainicio AS data,
            TO_CHAR(f.datainicio, 'Day') AS dia_semana,
            p.descricao AS periodo,
            cc_aulas.nome AS categoria_afetada
        FROM 
            eventos f
        JOIN 
            categoriacalendario cc_feriados ON f.id_categoria = cc_feriados.id_categoria
        JOIN 
            periodo p ON cc_feriados.id_periodo = p.id_periodo
        JOIN 
            categoriacalendario cc_aulas ON 
            cc_aulas.id_periodo = p.id_periodo 
            AND cc_aulas.nome LIKE '%Aulas%'
        WHERE 
            cc_feriados.nome LIKE '%Feriados%'
            AND EXTRACT(ISODOW FROM f.datainicio) BETWEEN 1 AND 5 -- Segunda a Sexta
            AND EXTRACT(YEAR FROM f.datainicio) = EXTRACT(YEAR FROM CURRENT_DATE)
        ORDER BY 
            f.datainicio;
        """))
        
        # 5. Eventos Futuros Ativos
        db.session.execute(text("""
        CREATE OR REPLACE VIEW vw_eventos_futuros_ativos AS
        SELECT 
            e.id_evento,
            e.titulo,
            e.datainicio,
            e.datafim,
            c.nome AS calendario,
            cc.nome AS categoria
        FROM eventos e
        JOIN categoriacalendario cc ON e.id_categoria = cc.id_categoria
        JOIN calendario c ON cc.id_calendario = c.id_calendario
        WHERE 
            c.ativo = TRUE 
            AND e.datainicio > CURRENT_DATE;
        """))
        
        # 6. Feriados do ano
        db.session.execute(text("""
        CREATE OR REPLACE VIEW vw_feriados_do_ano AS
        SELECT 
            e.id_evento,
            e.titulo AS feriado,
            e.datainicio,
            e.datafim,
            c.nome AS calendario
        FROM eventos e
        JOIN categoriacalendario cc ON e.id_categoria = cc.id_categoria
        JOIN calendario c ON cc.id_calendario = c.id_calendario
        WHERE 
            c.ativo = TRUE
            AND LOWER(cc.nome) LIKE '%feriado%'
            AND EXTRACT(YEAR FROM e.datainicio) = EXTRACT(YEAR FROM CURRENT_DATE);
        """))
        
        # 7. Dias letivos por periodo
        db.session.execute(text("""
        CREATE OR REPLACE VIEW vw_dias_letivos_por_periodo AS
        SELECT 
            p.descricao AS periodo,
            COUNT(DISTINCT e.datainicio) AS total_dias_letivos
        FROM 
            periodo p
        JOIN 
            categoriacalendario cc ON p.id_periodo = cc.id_periodo
        JOIN 
            eventos e ON cc.id_categoria = e.id_categoria
        WHERE 
            cc.habilitacaocontagem = true
            AND cc.nome NOT LIKE '%Feriados%'
            AND cc.nome NOT LIKE '%Recessos%'
        GROUP BY 
            p.descricao
        ORDER BY 
            p.descricao;
        """))
        
        logger.info("Visões criadas com sucesso!")
        
        # --- FUNÇÕES ---
        logger.info("Criando funções...")
        
        # 1. Calcular a Duração Total De Um Período em Dias
        db.session.execute(text("""
        CREATE OR REPLACE FUNCTION calcular_duracao_periodo(id_per INTEGER)
        RETURNS INTEGER AS $$
        DECLARE
            dias INTEGER;
        BEGIN
            SELECT (datafinal - datainicial) INTO dias
            FROM periodo
            WHERE id_periodo = id_per;
            RETURN dias;
        END;
        $$ LANGUAGE plpgsql;
        """))
        
        # 2. Contar Total de Eventos Em Uma Categoria Específica
        db.session.execute(text("""
        CREATE OR REPLACE FUNCTION contar_eventos_por_categoria(id_cat INTEGER)
        RETURNS INTEGER AS $$
        DECLARE
            total INTEGER;
        BEGIN
            SELECT COUNT(*) INTO total
            FROM eventos
            WHERE id_categoria = id_cat;
            RETURN total;
        END;
        $$ LANGUAGE plpgsql;
        """))
        
        # 3. Verificar Se Um Calendário Está Atualmente Ativo
        db.session.execute(text("""
        CREATE OR REPLACE FUNCTION esta_calendario_ativo(id_cal INTEGER)
        RETURNS BOOLEAN AS $$
        DECLARE
            resultado BOOLEAN;
        BEGIN
            SELECT (CURRENT_DATE BETWEEN datainicio AND datafim) AND ativo
            INTO resultado
            FROM calendario
            WHERE id_calendario = id_cal;
            RETURN resultado;
        END;
        $$ LANGUAGE plpgsql;
        """))
        
        logger.info("Funções criadas com sucesso!")
        
        # --- REGRAS ---
        logger.info("Criando regras...")
        
        # 1. Impedir exclusão de períodos que estão sendo usados
        db.session.execute(text("""
        CREATE OR REPLACE RULE impedir_delete_periodo_utilizado AS
        ON DELETE TO periodo
        WHERE EXISTS (
            SELECT 1
            FROM categoriacalendario
            WHERE id_periodo = OLD.id_periodo
        )
        DO INSTEAD NOTHING;
        """))
        
        # 2. Desativar Calendário encerrado
        db.session.execute(text("""
        CREATE OR REPLACE RULE desativar_calendario_encerrado AS
        ON UPDATE TO calendario
        WHERE NEW.ativo = TRUE AND NEW.datafim < CURRENT_DATE
        DO INSTEAD
        UPDATE calendario
        SET ativo = FALSE
        WHERE id_calendario = NEW.id_calendario;
        """))
        
        # 3. Impedir Ativação De Calendários Com Datas Inválidas
        db.session.execute(text("""
        CREATE OR REPLACE RULE bloquear_ativacao_calendario_invalido AS
        ON UPDATE TO calendario
        WHERE NEW.ativo = TRUE AND NEW.datafim < NEW.datainicio
        DO INSTEAD NOTHING;
        """))
        
        logger.info("Regras criadas com sucesso!")
        
        # --- GATILHOS ---
        logger.info("Criando gatilhos...")
        
        # 1. Marcar Evento Como Dia Inteiro
        db.session.execute(text("""
        CREATE OR REPLACE FUNCTION marcar_evento_como_dia_todo()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.datainicio = NEW.datafim THEN
                NEW.dia_todo := TRUE;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        
        DROP TRIGGER IF EXISTS trg_dia_todo_automatico ON eventos;
        CREATE TRIGGER trg_dia_todo_automatico
        BEFORE INSERT OR UPDATE ON eventos
        FOR EACH ROW
        EXECUTE FUNCTION marcar_evento_como_dia_todo();
        """))
        
        # 2. Impedir Cadastro De Eventos Com Título Vazio
        db.session.execute(text("""
        CREATE OR REPLACE FUNCTION validar_titulo_evento()
        RETURNS TRIGGER AS $$
        BEGIN
            IF TRIM(NEW.titulo) = '' THEN
                RAISE EXCEPTION 'O título do evento não pode estar vazio.';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        
        DROP TRIGGER IF EXISTS trg_titulo_obrigatorio ON eventos;
        CREATE TRIGGER trg_titulo_obrigatorio
        BEFORE INSERT OR UPDATE ON eventos
        FOR EACH ROW
        EXECUTE FUNCTION validar_titulo_evento();
        """))
        
        # 3. Impedir inserção de eventos com títulos duplicados na mesma categoria
        db.session.execute(text("""
        CREATE OR REPLACE FUNCTION impedir_evento_duplicado()
        RETURNS TRIGGER AS $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM eventos 
                WHERE titulo = NEW.titulo AND id_categoria = NEW.id_categoria
                AND id_evento <> COALESCE(NEW.id_evento, -1)
            ) THEN
                RAISE EXCEPTION 'Já existe um evento com esse título na mesma categoria.';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        
        DROP TRIGGER IF EXISTS trg_evento_titulo_unico ON eventos;
        CREATE TRIGGER trg_evento_titulo_unico
        BEFORE INSERT OR UPDATE ON eventos
        FOR EACH ROW
        EXECUTE FUNCTION impedir_evento_duplicado();
        """))
        
        # 4. Impedir conflito local eventos
        db.session.execute(text("""
        CREATE OR REPLACE FUNCTION impedir_conflito_local_eventos()
        RETURNS TRIGGER AS $$
        BEGIN
          IF EXISTS (
            SELECT 1
            FROM eventos e
            WHERE 
              e.local IS NOT NULL
              AND e.local = NEW.local
              AND e.id_evento <> COALESCE(NEW.id_evento, -1)
              AND e.datainicio <= NEW.datafim
              AND e.datafim >= NEW.datainicio
          ) THEN
            RAISE EXCEPTION 'Conflito detectado: já existe um evento agendado nesse local e período.';
          END IF;
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        
        DROP TRIGGER IF EXISTS trigger_impedir_conflito_local ON eventos;
        CREATE TRIGGER trigger_impedir_conflito_local
        BEFORE INSERT OR UPDATE ON eventos
        FOR EACH ROW
        EXECUTE FUNCTION impedir_conflito_local_eventos();
        """))
        
        logger.info("Gatilhos criados com sucesso!")
        
        db.session.commit()
        logger.info("✅ Configuração dos recursos avançados do PostgreSQL concluída com sucesso!")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Erro na configuração dos recursos avançados: {str(e)}")
        raise

def setup_sqlite_features():
    """Implementa versões simplificadas dos recursos para SQLite"""
    try:
        # --- VISÕES ---
        logger.info("Criando visões no SQLite (versão simplificada)...")
        
        # 1. Eventos Ativos no Período Atual
        logger.info("Criando view: vw_eventos_ativos_hoje")
        db.session.execute(text("""
        CREATE VIEW vw_eventos_ativos_hoje AS
        SELECT 
            e.id_evento,
            e.titulo,
            e.descricao,
            e.datainicio,
            e.datafim,
            e.local,
            cc.nome AS categoria
        FROM 
            eventos e
        JOIN 
            categoriacalendario cc ON e.id_categoria = cc.id_categoria
        JOIN 
            calendario c ON cc.id_calendario = c.id_calendario
        JOIN 
            periodo p ON cc.id_periodo = p.id_periodo
        WHERE 
            c.ativo = 1
            AND date('now') BETWEEN p.datainicial AND p.datafinal
            AND e.datainicio >= date('now')
        ORDER BY 
            e.datainicio;
        """))
        
        # 2. Resumo do Calendário (versão simplificada)
        logger.info("Criando view: vw_resumo_calendario")
        db.session.execute(text("""
        CREATE VIEW vw_resumo_calendario AS
        SELECT 
            c.id_calendario,
            c.nome AS nomecalendario,
            c.ano,
            c.datainicio,
            c.datafim,
            c.ativo,
            tc.nome AS tipocalendario,
            COUNT(DISTINCT cc.id_categoria) AS totalcategorias,
            COUNT(e.id_evento) AS totaleventos
        FROM 
            calendario c
        JOIN 
            tipocalendario tc ON c.id_tipo = tc.id_tipo
        LEFT JOIN 
            categoriacalendario cc ON c.id_calendario = cc.id_calendario
        LEFT JOIN 
            eventos e ON cc.id_categoria = e.id_categoria
        GROUP BY 
            c.id_calendario
        ORDER BY 
            c.ano DESC, c.nome;
        """))
        
        # 3. Eventos Futuros Ativos
        logger.info("Criando view: vw_eventos_futuros_ativos")
        db.session.execute(text("""
        CREATE VIEW vw_eventos_futuros_ativos AS
        SELECT 
            e.id_evento,
            e.titulo,
            e.datainicio,
            e.datafim,
            c.nome AS calendario,
            cc.nome AS categoria
        FROM eventos e
        JOIN categoriacalendario cc ON e.id_categoria = cc.id_categoria
        JOIN calendario c ON cc.id_calendario = c.id_calendario
        WHERE 
            c.ativo = 1 
            AND e.datainicio > date('now')
        ORDER BY 
            e.datainicio;
        """))
        
        db.session.commit()
        logger.info("Visões SQLite criadas com sucesso!")
        logger.info("Nota: Algumas funcionalidades avançadas não estão disponíveis no SQLite.")
        logger.info("Para utilização completa, recomenda-se usar PostgreSQL.")
        
        logger.info("✅ Recursos básicos do SQLite configurados com sucesso!")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Erro na configuração dos recursos do SQLite: {str(e)}")
        raise

if __name__ == "__main__":
    setup_db_features()