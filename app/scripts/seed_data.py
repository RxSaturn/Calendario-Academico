from app import create_app, db
from app.models.models import Periodo, TipoCalendario, Calendario, CategoriaCalendario, Eventos
from datetime import datetime, timedelta

def seed_database():
    app = create_app()
    with app.app_context():
        # Limpar dados existentes
        Eventos.query.delete()
        CategoriaCalendario.query.delete()
        Calendario.query.delete()
        TipoCalendario.query.delete()
        Periodo.query.delete()
        
        print("🔄 Iniciando população do banco de dados...")
        
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
        
        # Inserir tipos de calendário (cada um com uma sigla única)
        tipos = [
            TipoCalendario(sigla='GRAD', nome='Graduação'),
            TipoCalendario(sigla='POS', nome='Pós-Graduação'),
            TipoCalendario(sigla='INST', nome='Institucional'),
            TipoCalendario(sigla='EVEN', nome='Eventos Acadêmicos')
        ]
        db.session.add_all(tipos)
        db.session.commit()
        print("✅ Tipos de calendário inseridos")
        
        # Inserir calendários
        calendarios = [
            Calendario(id_tipo=1, nome='Calendário Graduação', ano=2025, datainicio=datetime(2025, 1, 1), datafim=datetime(2025, 12, 31), ativo=True),
            Calendario(id_tipo=2, nome='Calendário Pós-Graduação', ano=2025, datainicio=datetime(2025, 1, 1), datafim=datetime(2025, 12, 31), ativo=True),
            Calendario(id_tipo=3, nome='Calendário Institucional', ano=2025, datainicio=datetime(2025, 1, 1), datafim=datetime(2025, 12, 31), ativo=True),
            Calendario(id_tipo=4, nome='Eventos Acadêmicos', ano=2025, datainicio=datetime(2025, 1, 1), datafim=datetime(2025, 12, 31), ativo=False) # Deixamos um inativo para exemplo
        ]
        db.session.add_all(calendarios)
        db.session.commit()
        print("✅ Calendários inseridos")
        
        # Inserir categorias de calendário
        categorias = [
            # Graduação - 1º Semestre
            CategoriaCalendario(id_calendario=1, id_periodo=1, nome='Aulas Regulares', corassociada='#3788d8', totaldias=100, diassemanasvalidos='12345', habilitacaocontagem=True),
            CategoriaCalendario(id_calendario=1, id_periodo=1, nome='Provas', corassociada='#d81b60', totaldias=10, diassemanasvalidos='12345', habilitacaocontagem=True),
            CategoriaCalendario(id_calendario=1, id_periodo=1, nome='Feriados', corassociada='#8e24aa', diassemanasvalidos='1234567', habilitacaocontagem=False),
            
            # Graduação - 2º Semestre
            CategoriaCalendario(id_calendario=1, id_periodo=2, nome='Aulas Regulares', corassociada='#4285F4', totaldias=100, diassemanasvalidos='12345', habilitacaocontagem=True),
            CategoriaCalendario(id_calendario=1, id_periodo=2, nome='Provas', corassociada='#DB4437', totaldias=10, diassemanasvalidos='12345', habilitacaocontagem=True),
            CategoriaCalendario(id_calendario=1, id_periodo=2, nome='Feriados', corassociada='#AB47BC', diassemanasvalidos='1234567', habilitacaocontagem=False),
            
            # Pós-Graduação - 1º Semestre
            CategoriaCalendario(id_calendario=2, id_periodo=1, nome='Aulas Pós', corassociada='#4caf50', totaldias=90, diassemanasvalidos='12345', habilitacaocontagem=True),
            CategoriaCalendario(id_calendario=2, id_periodo=1, nome='Defesas e Seminários', corassociada='#ff9800', totaldias=None, diassemanasvalidos='12345', habilitacaocontagem=False),
            
            # Pós-Graduação - 2º Semestre
            CategoriaCalendario(id_calendario=2, id_periodo=2, nome='Aulas Pós', corassociada='#00897B', totaldias=90, diassemanasvalidos='12345', habilitacaocontagem=True),
            CategoriaCalendario(id_calendario=2, id_periodo=2, nome='Defesas e Seminários', corassociada='#FF8F00', totaldias=None, diassemanasvalidos='12345', habilitacaocontagem=False),
            
            # Institucional - Ano todo
            CategoriaCalendario(id_calendario=3, id_periodo=1, nome='Reuniões', corassociada='#795548', totaldias=None, diassemanasvalidos='12345', habilitacaocontagem=False),
            CategoriaCalendario(id_calendario=3, id_periodo=2, nome='Reuniões', corassociada='#5D4037', totaldias=None, diassemanasvalidos='12345', habilitacaocontagem=False),
            
            # Eventos - Ano todo
            CategoriaCalendario(id_calendario=4, id_periodo=1, nome='Palestras', corassociada='#607d8b', totaldias=None, diassemanasvalidos='12345', habilitacaocontagem=False),
            CategoriaCalendario(id_calendario=4, id_periodo=2, nome='Congressos', corassociada='#455A64', totaldias=None, diassemanasvalidos='12345', habilitacaocontagem=False)
        ]
        db.session.add_all(categorias)
        db.session.commit()
        print("✅ Categorias inseridas")
        
        # ======= GRADUAÇÃO =======
        
        # Graduação - Aulas Regulares (1º Semestre)
        eventos_aulas_1s = [
            Eventos(
                id_categoria=1,  # Aulas Regulares 1º semestre
                titulo='Período Letivo - 1º Semestre',
                descricao='Aulas regulares do 1º semestre de graduação',
                datainicio=datetime(2025, 2, 3),  # Segunda-feira
                datafim=datetime(2025, 7, 4),     # Sexta-feira (respeitando o limite de 100 dias)
                dia_todo=False,
                local='Todos os campi'
            )
        ]
        
        # Graduação - Provas (1º Semestre)
        eventos_provas_1s = [
            Eventos(
                id_categoria=2,
                titulo='Avaliação P1',
                descricao='Primeira avaliação parcial',
                datainicio=datetime(2025, 4, 7),  # Segunda
                datafim=datetime(2025, 4, 11),    # Sexta (5 dias)
                dia_todo=False,
                local='Salas de aula'
            ),
            Eventos(
                id_categoria=2,
                titulo='Avaliação P2',
                descricao='Segunda avaliação parcial',
                datainicio=datetime(2025, 6, 23),  # Segunda
                datafim=datetime(2025, 6, 27),     # Sexta (5 dias)
                dia_todo=False,
                local='Salas de aula'
            )
        ]
        
        # Graduação - Feriados (1º Semestre)
        eventos_feriados_1s = [
            Eventos(
                id_categoria=3,
                titulo='Carnaval',
                descricao='Feriado nacional',
                datainicio=datetime(2025, 3, 4),
                datafim=datetime(2025, 3, 4),
                dia_todo=True,
                local=None
            ),
            Eventos(
                id_categoria=3,
                titulo='Tiradentes',
                descricao='Feriado nacional',
                datainicio=datetime(2025, 4, 21),
                datafim=datetime(2025, 4, 21),
                dia_todo=True,
                local=None
            ),
            Eventos(
                id_categoria=3,
                titulo='Dia do Trabalho',
                descricao='Feriado nacional',
                datainicio=datetime(2025, 5, 1),
                datafim=datetime(2025, 5, 1),
                dia_todo=True,
                local=None
            )
        ]
        
        # Graduação - Aulas Regulares (2º Semestre)
        eventos_aulas_2s = [
            Eventos(
                id_categoria=4,  # Aulas Regulares 2º semestre
                titulo='Período Letivo - 2º Semestre',
                descricao='Aulas regulares do 2º semestre de graduação',
                datainicio=datetime(2025, 8, 4),   # Segunda-feira
                datafim=datetime(2025, 12, 12),    # Sexta-feira
                dia_todo=False,
                local='Todos os campi'
            )
        ]
        
        # Graduação - Provas (2º Semestre)
        eventos_provas_2s = [
            Eventos(
                id_categoria=5,
                titulo='Avaliação P1',
                descricao='Primeira avaliação parcial',
                datainicio=datetime(2025, 9, 29),  # Segunda
                datafim=datetime(2025, 10, 3),     # Sexta (5 dias)
                dia_todo=False,
                local='Salas de aula'
            ),
            Eventos(
                id_categoria=5,
                titulo='Avaliação P2',
                descricao='Segunda avaliação parcial',
                datainicio=datetime(2025, 11, 24), # Segunda
                datafim=datetime(2025, 11, 28),    # Sexta (5 dias)
                dia_todo=False,
                local='Salas de aula'
            )
        ]
        
        # Graduação - Feriados (2º Semestre)
        eventos_feriados_2s = [
            Eventos(
                id_categoria=6,
                titulo='Independência do Brasil',
                descricao='Feriado nacional',
                datainicio=datetime(2025, 9, 7),
                datafim=datetime(2025, 9, 7),
                dia_todo=True,
                local=None
            ),
            Eventos(
                id_categoria=6,
                titulo='Nossa Senhora Aparecida',
                descricao='Feriado nacional',
                datainicio=datetime(2025, 10, 12),
                datafim=datetime(2025, 10, 12),
                dia_todo=True,
                local=None
            ),
            Eventos(
                id_categoria=6,
                titulo='Finados',
                descricao='Feriado nacional',
                datainicio=datetime(2025, 11, 2),
                datafim=datetime(2025, 11, 2),
                dia_todo=True,
                local=None
            ),
            Eventos(
                id_categoria=6,
                titulo='Proclamação da República',
                descricao='Feriado nacional',
                datainicio=datetime(2025, 11, 15),
                datafim=datetime(2025, 11, 15),
                dia_todo=True,
                local=None
            ),
            Eventos(
                id_categoria=6,
                titulo='Natal',
                descricao='Feriado nacional',
                datainicio=datetime(2025, 12, 25),
                datafim=datetime(2025, 12, 25),
                dia_todo=True,
                local=None
            )
        ]
        
        # ======= PÓS-GRADUAÇÃO =======
        
        # Pós-Graduação - Aulas (1º Semestre)
        eventos_pos_1s = [
            Eventos(
                id_categoria=7,
                titulo='Período de Aulas - Pós-Graduação 1º Semestre',
                descricao='Período de aulas do 1º semestre de pós-graduação',
                datainicio=datetime(2025, 2, 10),  # Segunda
                datafim=datetime(2025, 7, 5),      # Sábado (mas vai contar só dias úteis)
                dia_todo=False,
                local='Bloco de Pós-Graduação'
            )
        ]
        
        # Pós-Graduação - Defesas e Seminários (1º Semestre)
        eventos_defesas_1s = [
            Eventos(
                id_categoria=8,
                titulo='Seminário de Pesquisa',
                descricao='Apresentação de projetos de pesquisa',
                datainicio=datetime(2025, 3, 20),
                datafim=datetime(2025, 3, 20),
                dia_todo=False,
                local='Auditório Central'
            ),
            Eventos(
                id_categoria=8,
                titulo='Defesa de Dissertação: Maria Silva',
                descricao='Inteligência Artificial aplicada à Educação',
                datainicio=datetime(2025, 5, 15),
                datafim=datetime(2025, 5, 15),
                dia_todo=False,
                local='Sala de Defesas 1'
            ),
            Eventos(
                id_categoria=8,
                titulo='Defesa de Tese: João Santos',
                descricao='Algoritmos evolucionários em problemas de otimização',
                datainicio=datetime(2025, 6, 12),
                datafim=datetime(2025, 6, 12),
                dia_todo=False,
                local='Sala de Defesas 2'
            )
        ]
        
        # Pós-Graduação - Aulas (2º Semestre)
        eventos_pos_2s = [
            Eventos(
                id_categoria=9,
                titulo='Período de Aulas - Pós-Graduação 2º Semestre',
                descricao='Período de aulas do 2º semestre de pós-graduação',
                datainicio=datetime(2025, 8, 4),   # Segunda
                datafim=datetime(2025, 12, 15),    # Segunda
                dia_todo=False,
                local='Bloco de Pós-Graduação'
            )
        ]
        
        # Pós-Graduação - Defesas e Seminários (2º Semestre)
        eventos_defesas_2s = [
            Eventos(
                id_categoria=10,
                titulo='Seminário de Pesquisa - 2º Semestre',
                descricao='Apresentação de projetos de pesquisa',
                datainicio=datetime(2025, 9, 18),
                datafim=datetime(2025, 9, 18),
                dia_todo=False,
                local='Auditório Central'
            ),
            Eventos(
                id_categoria=10,
                titulo='Defesa de Dissertação: Carlos Pereira',
                descricao='Computação em Nuvem para Sistemas Embarcados',
                datainicio=datetime(2025, 10, 23),
                datafim=datetime(2025, 10, 23),
                dia_todo=False,
                local='Sala de Defesas 1'
            ),
            Eventos(
                id_categoria=10,
                titulo='Defesa de Tese: Ana Oliveira',
                descricao='Sistemas de Recomendação baseados em Aprendizado Profundo',
                datainicio=datetime(2025, 11, 27),
                datafim=datetime(2025, 11, 27),
                dia_todo=False,
                local='Sala de Defesas 2'
            )
        ]
        
        # ======= INSTITUCIONAL =======
        
        # Institucional - Reuniões (1º Semestre)
        eventos_reunioes_1s = [
            Eventos(
                id_categoria=11,
                titulo='Reunião do Conselho Universitário',
                descricao='Pauta: Orçamento anual',
                datainicio=datetime(2025, 2, 15),
                datafim=datetime(2025, 2, 15),
                dia_todo=False,
                local='Sala do Conselho'
            ),
            Eventos(
                id_categoria=11,
                titulo='Reunião de Coordenadores',
                descricao='Avaliação do início do semestre',
                datainicio=datetime(2025, 3, 10),
                datafim=datetime(2025, 3, 10),
                dia_todo=False,
                local='Sala de Reuniões A'
            ),
            Eventos(
                id_categoria=11,
                titulo='Colegiado de Graduação',
                descricao='Discussão de casos discentes',
                datainicio=datetime(2025, 5, 5),
                datafim=datetime(2025, 5, 5),
                dia_todo=False,
                local='Sala de Reuniões B'
            )
        ]
        
        # Institucional - Reuniões (2º Semestre)
        eventos_reunioes_2s = [
            Eventos(
                id_categoria=12,
                titulo='Reunião do Conselho Universitário - 2º Semestre',
                descricao='Pauta: Planejamento do próximo ano',
                datainicio=datetime(2025, 8, 15),
                datafim=datetime(2025, 8, 15),
                dia_todo=False,
                local='Sala do Conselho'
            ),
            Eventos(
                id_categoria=12,
                titulo='Reunião de Coordenadores - 2º Semestre',
                descricao='Avaliação do segundo semestre',
                datainicio=datetime(2025, 9, 10),
                datafim=datetime(2025, 9, 10),
                dia_todo=False,
                local='Sala de Reuniões A'
            ),
            Eventos(
                id_categoria=12,
                titulo='Colegiado de Pós-Graduação',
                descricao='Planejamento de disciplinas para o próximo ano',
                datainicio=datetime(2025, 11, 5),
                datafim=datetime(2025, 11, 5),
                dia_todo=False,
                local='Sala de Reuniões B'
            )
        ]
        
        # ======= EVENTOS =======
        
        # Eventos - Palestras (1º Semestre)
        eventos_palestras = [
            Eventos(
                id_categoria=13,
                titulo='Palestra de Boas-vindas',
                descricao='Orientações aos calouros',
                datainicio=datetime(2025, 2, 5),
                datafim=datetime(2025, 2, 5),
                dia_todo=False,
                local='Auditório Principal'
            ),
            Eventos(
                id_categoria=13,
                titulo='Palestra: Mercado de Trabalho em TI',
                descricao='Palestrante: Empresa BigTech',
                datainicio=datetime(2025, 4, 17),
                datafim=datetime(2025, 4, 17),
                dia_todo=False,
                local='Auditório Principal'
            ),
            Eventos(
                id_categoria=13,
                titulo='Palestra: Sustentabilidade Ambiental',
                descricao='Palestrante: Dr. Silva Costa',
                datainicio=datetime(2025, 6, 5),
                datafim=datetime(2025, 6, 5),
                dia_todo=False,
                local='Auditório Secundário'
            )
        ]
        
        # Eventos - Congressos (2º Semestre)
        eventos_congressos = [
            Eventos(
                id_categoria=14,
                titulo='Congresso de Iniciação Científica',
                descricao='Apresentação de trabalhos de IC',
                datainicio=datetime(2025, 10, 15),
                datafim=datetime(2025, 10, 17),
                dia_todo=True,
                local='Centro de Convenções'
            ),
            Eventos(
                id_categoria=14,
                titulo='Simpósio de Tecnologia e Inovação',
                descricao='Apresentações e workshops',
                datainicio=datetime(2025, 11, 10),
                datafim=datetime(2025, 11, 12),
                dia_todo=True,
                local='Auditório Principal e Salas Anexas'
            )
        ]
        
        # Juntar todos os eventos
        todos_eventos = (
            eventos_aulas_1s +
            eventos_provas_1s +
            eventos_feriados_1s +
            eventos_aulas_2s +
            eventos_provas_2s +
            eventos_feriados_2s +
            eventos_pos_1s +
            eventos_defesas_1s +
            eventos_pos_2s +
            eventos_defesas_2s +
            eventos_reunioes_1s +
            eventos_reunioes_2s +
            eventos_palestras +
            eventos_congressos
        )
        
        # Inserir todos os eventos
        db.session.add_all(todos_eventos)
        db.session.commit()
        print(f"✅ {len(todos_eventos)} eventos inseridos")
        
        print("✅✅✅ Banco de dados populado com sucesso!")

if __name__ == '__main__':
    seed_database()