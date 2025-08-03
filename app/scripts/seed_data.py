from app import create_app, db
from app.models.models import Periodo, TipoCalendario, Calendario, CategoriaCalendario, Eventos
from datetime import datetime

def seed_database():
    """Preenche o banco de dados com dados iniciais"""
    app = create_app()
    with app.app_context():
        # Limpar dados existentes
        Eventos.query.delete()
        CategoriaCalendario.query.delete()
        Calendario.query.delete()
        TipoCalendario.query.delete()
        Periodo.query.delete()
        
        # Inserir períodos acadêmicos
        periodos = [
            Periodo(descricao='1º Semestre 2025', datainicial=datetime(2025, 2, 1), datafinal=datetime(2025, 7, 15)),
            Periodo(descricao='2º Semestre 2025', datainicial=datetime(2025, 8, 1), datafinal=datetime(2025, 12, 20)),
            Periodo(descricao='Férias Verão 2025', datainicial=datetime(2025, 12, 21), datafinal=datetime(2026, 1, 31)),
            Periodo(descricao='Recesso Julho 2025', datainicial=datetime(2025, 7, 16), datafinal=datetime(2025, 7, 31))
        ]
        db.session.add_all(periodos)
        db.session.commit()
        
        # Inserir tipos de calendário
        tipos = [
            TipoCalendario(sigla='GRAD', nome='Graduação'),
            TipoCalendario(sigla='POS', nome='Pós-Graduação'),
            TipoCalendario(sigla='INST', nome='Institucional'),
            TipoCalendario(sigla='EVEN', nome='Eventos Especiais')
        ]
        db.session.add_all(tipos)
        db.session.commit()
        
        # Inserir calendários
        calendarios = [
            Calendario(id_tipo=1, nome='Calendário Graduação', ano=2025, datainicio=datetime(2025, 1, 1), datafim=datetime(2025, 12, 31), ativo=True),
            Calendario(id_tipo=2, nome='Calendário Pós-Graduação', ano=2025, datainicio=datetime(2025, 1, 1), datafim=datetime(2025, 12, 31), ativo=True),
            Calendario(id_tipo=3, nome='Calendário Institucional', ano=2025, datainicio=datetime(2025, 1, 1), datafim=datetime(2025, 12, 31), ativo=True),
            Calendario(id_tipo=4, nome='Eventos Acadêmicos', ano=2025, datainicio=datetime(2025, 1, 1), datafim=datetime(2025, 12, 31), ativo=True)
        ]
        db.session.add_all(calendarios)
        db.session.commit()
        
        # Inserir categorias de calendário
        categorias = [
            # Graduação - 1º Semestre
            CategoriaCalendario(id_calendario=1, id_periodo=1, nome='Aulas Regulares', corassociada='#3788d8', totaldias=120, diassemanasvalidos='12345', habilitacaocontagem=True),
            CategoriaCalendario(id_calendario=1, id_periodo=1, nome='Provas', corassociada='#d81b60', totaldias=14, diassemanasvalidos='12345', habilitacaocontagem=True),
            CategoriaCalendario(id_calendario=1, id_periodo=1, nome='Feriados', corassociada='#8e24aa', diassemanasvalidos='1234567', habilitacaocontagem=False),
            
            # Graduação - 2º Semestre
            CategoriaCalendario(id_calendario=1, id_periodo=2, nome='Aulas Regulares', corassociada='#3788d8', totaldias=120, diassemanasvalidos='12345', habilitacaocontagem=True),
            CategoriaCalendario(id_calendario=1, id_periodo=2, nome='Provas', corassociada='#d81b60', totaldias=14, diassemanasvalidos='12345', habilitacaocontagem=True),
            CategoriaCalendario(id_calendario=1, id_periodo=2, nome='Feriados', corassociada='#8e24aa', diassemanasvalidos='1234567', habilitacaocontagem=False),
            
            # Outros...
            CategoriaCalendario(id_calendario=2, id_periodo=1, nome='Aulas Pós', corassociada='#4caf50', totaldias=90, diassemanasvalidos='12345', habilitacaocontagem=True),
            CategoriaCalendario(id_calendario=2, id_periodo=1, nome='Defesas e Seminários', corassociada='#ff9800', diassemanasvalidos='12345', habilitacaocontagem=False),
            CategoriaCalendario(id_calendario=3, id_periodo=1, nome='Reuniões', corassociada='#795548', diassemanasvalidos='12345', habilitacaocontagem=False),
            CategoriaCalendario(id_calendario=3, id_periodo=2, nome='Reuniões', corassociada='#795548', diassemanasvalidos='12345', habilitacaocontagem=False),
            CategoriaCalendario(id_calendario=4, id_periodo=1, nome='Palestras', corassociada='#607d8b', diassemanasvalidos='12345', habilitacaocontagem=False),
            CategoriaCalendario(id_calendario=4, id_periodo=2, nome='Congressos', corassociada='#607d8b', diassemanasvalidos='12345', habilitacaocontagem=False)
        ]
        db.session.add_all(categorias)
        db.session.commit()
        
        # Inserir alguns eventos
        eventos = [
            # Aulas Regulares - 1º Semestre
            Eventos(id_categoria=1, titulo='Início do Período Letivo', descricao='Início oficial das aulas do 1º semestre', 
                   datainicio=datetime(2025, 2, 3), datafim=datetime(2025, 2, 3), dia_todo=True, local='Todos os campi'),
            Eventos(id_categoria=1, titulo='Encerramento do 1º Semestre', descricao='Último dia de aulas regulares', 
                   datainicio=datetime(2025, 7, 12), datafim=datetime(2025, 7, 12), dia_todo=True, local='Todos os campi'),
            
            # Provas - 1º Semestre
            Eventos(id_categoria=2, titulo='Semana de Provas P1', descricao='Primeira avaliação do semestre', 
                   datainicio=datetime(2025, 4, 7), datafim=datetime(2025, 4, 11), dia_todo=False, local='Conforme grade de horários'),
            Eventos(id_categoria=2, titulo='Semana de Provas P2', descricao='Segunda avaliação do semestre', 
                   datainicio=datetime(2025, 6, 23), datafim=datetime(2025, 6, 27), dia_todo=False, local='Conforme grade de horários'),
            
            # Feriados
            Eventos(id_categoria=3, titulo='Carnaval', descricao='Feriado nacional', 
                   datainicio=datetime(2025, 3, 4), datafim=datetime(2025, 3, 4), dia_todo=True, local=None),
            Eventos(id_categoria=3, titulo='Tiradentes', descricao='Feriado nacional', 
                   datainicio=datetime(2025, 4, 21), datafim=datetime(2025, 4, 21), dia_todo=True, local=None)
        ]
        db.session.add_all(eventos)
        db.session.commit()
        
        print("Banco de dados populado com sucesso!")

if __name__ == '__main__':
    seed_database()