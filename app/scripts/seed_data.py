from app import create_app, db
from app.models.models import Periodo, TipoCalendario, Calendario, CategoriaCalendario, Eventos
from datetime import datetime

def seed_database():
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
        print("✅ Períodos acadêmicos inseridos")
        
        # Inserir tipos de calendário
        tipos = [
            TipoCalendario(sigla='GRAD', nome='Graduação'),
            TipoCalendario(sigla='POS', nome='Pós-Graduação'),
            TipoCalendario(sigla='INST', nome='Institucional'),
            TipoCalendario(sigla='EVEN', nome='Eventos Especiais')
        ]
        db.session.add_all(tipos)
        db.session.commit()
        print("✅ Tipos de calendário inseridos")
        
        # Inserir calendários
        calendarios = [
            Calendario(id_tipo=1, nome='Calendário Graduação', ano=2025, datainicio=datetime(2025, 1, 1), datafim=datetime(2025, 12, 31), ativo=True),
            Calendario(id_tipo=2, nome='Calendário Pós-Graduação', ano=2025, datainicio=datetime(2025, 1, 1), datafim=datetime(2025, 12, 31), ativo=True),
            Calendario(id_tipo=3, nome='Calendário Institucional', ano=2025, datainicio=datetime(2025, 1, 1), datafim=datetime(2025, 12, 31), ativo=True),
            Calendario(id_tipo=4, nome='Eventos Acadêmicos', ano=2025, datainicio=datetime(2025, 1, 1), datafim=datetime(2025, 12, 31), ativo=True)
        ]
        db.session.add_all(calendarios)
        db.session.commit()
        print("✅ Calendários inseridos")
        
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
            
            # Pós-Graduação - 1º Semestre
            CategoriaCalendario(id_calendario=2, id_periodo=1, nome='Aulas Pós', corassociada='#4caf50', totaldias=90, diassemanasvalidos='12345', habilitacaocontagem=True),
            CategoriaCalendario(id_calendario=2, id_periodo=1, nome='Defesas e Seminários', corassociada='#ff9800', diassemanasvalidos='12345', habilitacaocontagem=False),
            
            # Institucional - Ano todo
            CategoriaCalendario(id_calendario=3, id_periodo=1, nome='Reuniões', corassociada='#795548', diassemanasvalidos='12345', habilitacaocontagem=False),
            CategoriaCalendario(id_calendario=3, id_periodo=2, nome='Reuniões', corassociada='#795548', diassemanasvalidos='12345', habilitacaocontagem=False),
            
            # Eventos - Ano todo
            CategoriaCalendario(id_calendario=4, id_periodo=1, nome='Palestras', corassociada='#607d8b', diassemanasvalidos='12345', habilitacaocontagem=False),
            CategoriaCalendario(id_calendario=4, id_periodo=2, nome='Congressos', corassociada='#607d8b', diassemanasvalidos='12345', habilitacaocontagem=False)
        ]
        db.session.add_all(categorias)
        db.session.commit()
        print("✅ Categorias inseridas")
        
        # Inserir eventos
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
            Eventos(id_categoria=2, titulo='Exames Finais', descricao='Exames de recuperação final', 
                   datainicio=datetime(2025, 7, 7), datafim=datetime(2025, 7, 11), dia_todo=False, local='Conforme grade de horários'),
            
            # Feriados - 1º Semestre
            Eventos(id_categoria=3, titulo='Carnaval', descricao='Feriado nacional', 
                   datainicio=datetime(2025, 3, 4), datafim=datetime(2025, 3, 4), dia_todo=True, local=None),
            Eventos(id_categoria=3, titulo='Tiradentes', descricao='Feriado nacional', 
                   datainicio=datetime(2025, 4, 21), datafim=datetime(2025, 4, 21), dia_todo=True, local=None),
            Eventos(id_categoria=3, titulo='Dia do Trabalho', descricao='Feriado nacional', 
                   datainicio=datetime(2025, 5, 1), datafim=datetime(2025, 5, 1), dia_todo=True, local=None),
            
            # Aulas Regulares - 2º Semestre
            Eventos(id_categoria=4, titulo='Início do 2º Semestre', descricao='Início oficial das aulas do 2º semestre', 
                   datainicio=datetime(2025, 8, 4), datafim=datetime(2025, 8, 4), dia_todo=True, local='Todos os campi'),
            Eventos(id_categoria=4, titulo='Encerramento do Ano Letivo', descricao='Último dia de aulas do ano letivo', 
                   datainicio=datetime(2025, 12, 13), datafim=datetime(2025, 12, 13), dia_todo=True, local='Todos os campi'),
            
            # Provas - 2º Semestre
            Eventos(id_categoria=5, titulo='Semana de Provas P1', descricao='Primeira avaliação do semestre', 
                   datainicio=datetime(2025, 9, 29), datafim=datetime(2025, 10, 3), dia_todo=False, local='Conforme grade de horários'),
            Eventos(id_categoria=5, titulo='Semana de Provas P2', descricao='Segunda avaliação do semestre', 
                   datainicio=datetime(2025, 11, 24), datafim=datetime(2025, 11, 28), dia_todo=False, local='Conforme grade de horários'),
            
            # Feriados - 2º Semestre
            Eventos(id_categoria=6, titulo='Independência do Brasil', descricao='Feriado nacional', 
                   datainicio=datetime(2025, 9, 7), datafim=datetime(2025, 9, 7), dia_todo=True, local=None),
            Eventos(id_categoria=6, titulo='Nossa Senhora Aparecida', descricao='Feriado nacional', 
                   datainicio=datetime(2025, 10, 12), datafim=datetime(2025, 10, 12), dia_todo=True, local=None),
            Eventos(id_categoria=6, titulo='Finados', descricao='Feriado nacional', 
                   datainicio=datetime(2025, 11, 2), datafim=datetime(2025, 11, 2), dia_todo=True, local=None),
            Eventos(id_categoria=6, titulo='Proclamação da República', descricao='Feriado nacional', 
                   datainicio=datetime(2025, 11, 15), datafim=datetime(2025, 11, 15), dia_todo=True, local=None),
            Eventos(id_categoria=6, titulo='Natal', descricao='Feriado nacional', 
                   datainicio=datetime(2025, 12, 25), datafim=datetime(2025, 12, 25), dia_todo=True, local=None),
            
            # Aulas Pós-Graduação - 1º Semestre
            Eventos(id_categoria=7, titulo='Início das Aulas de Pós-Graduação', descricao='Início das disciplinas de pós', 
                   datainicio=datetime(2025, 2, 10), datafim=datetime(2025, 2, 10), dia_todo=False, local='Bloco P'),
            Eventos(id_categoria=7, titulo='Encerramento das Aulas de Pós', descricao='Último dia de aulas do semestre', 
                   datainicio=datetime(2025, 7, 5), datafim=datetime(2025, 7, 5), dia_todo=False, local='Bloco P'),
            
            # Defesas e Seminários
            Eventos(id_categoria=8, titulo='Seminário de Pesquisa', descricao='Apresentação de projetos de pesquisa', 
                   datainicio=datetime(2025, 3, 20), datafim=datetime(2025, 3, 20), dia_todo=False, local='Auditório Central'),
            Eventos(id_categoria=8, titulo='Defesa de Dissertação: Maria Silva', descricao='Inteligência Artificial aplicada à Educação', 
                   datainicio=datetime(2025, 5, 15), datafim=datetime(2025, 5, 15), dia_todo=False, local='Sala de Defesas 1'),
            Eventos(id_categoria=8, titulo='Defesa de Tese: João Santos', descricao='Algoritmos evolucionários em problemas de otimização', 
                   datainicio=datetime(2025, 6, 12), datafim=datetime(2025, 6, 12), dia_todo=False, local='Sala de Defesas 2'),
            
            # Reuniões Institucionais - 1º Semestre
            Eventos(id_categoria=9, titulo='Reunião do Conselho Universitário', descricao='Pauta: Orçamento anual', 
                   datainicio=datetime(2025, 2, 15), datafim=datetime(2025, 2, 15), dia_todo=False, local='Sala do Conselho'),
            Eventos(id_categoria=9, titulo='Reunião de Coordenadores', descricao='Avaliação do início do semestre', 
                   datainicio=datetime(2025, 3, 10), datafim=datetime(2025, 3, 10), dia_todo=False, local='Sala de Reuniões A'),
            Eventos(id_categoria=9, titulo='Colegiado de Graduação', descricao='Discussão de casos discentes', 
                   datainicio=datetime(2025, 5, 5), datafim=datetime(2025, 5, 5), dia_todo=False, local='Sala de Reuniões B'),
            
            # Palestras - 1º Semestre
            Eventos(id_categoria=11, titulo='Palestra de Boas-vindas', descricao='Orientações aos calouros', 
                   datainicio=datetime(2025, 2, 5), datafim=datetime(2025, 2, 5), dia_todo=False, local='Auditório Principal'),
            Eventos(id_categoria=11, titulo='Palestra: Mercado de Trabalho em TI', descricao='Palestrante: Empresa BigTech', 
                   datainicio=datetime(2025, 4, 17), datafim=datetime(2025, 4, 17), dia_todo=False, local='Auditório Principal'),
            Eventos(id_categoria=11, titulo='Palestra: Sustentabilidade Ambiental', descricao='Palestrante: Dr. Silva Costa', 
                   datainicio=datetime(2025, 6, 5), datafim=datetime(2025, 6, 5), dia_todo=False, local='Auditório Secundário'),
            
            # Evento com sobreposição para testar a detecção de conflitos
            Eventos(id_categoria=11, titulo='Palestra Especial: Inovação Tecnológica', descricao='Palestrante convidado internacional', 
                   datainicio=datetime(2025, 6, 5), datafim=datetime(2025, 6, 5), dia_todo=False, local='Auditório Secundário')
        ]
        db.session.add_all(eventos)
        db.session.commit()
        print("✅ Eventos inseridos")
        
        print("✅✅✅ Banco de dados populado com sucesso!")

if __name__ == '__main__':
    seed_database()