from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app import db
from app.models.models import Eventos, CategoriaCalendario, Calendario
from app.forms import EventoForm
from sqlalchemy import or_, and_
from datetime import datetime, timedelta

evento_bp = Blueprint('evento', __name__, url_prefix='/eventos')

@evento_bp.route('/')
def listar():
    eventos = Eventos.query.all()
    return render_template('eventos/listar.html', eventos=eventos)

@evento_bp.route('/novo', methods=['GET', 'POST'])
def novo():
    form = EventoForm()
    form.id_categoria.choices = [(c.id_categoria, f"{c.nome} - {c.calendario.nome}") 
                                for c in CategoriaCalendario.query.all()]
    
    if form.validate_on_submit():
        # Buscar a categoria e o calendário associado
        categoria = CategoriaCalendario.query.get(form.id_categoria.data)
        calendario = categoria.calendario
        
        # Verificar se as datas do evento estão dentro do período do calendário
        if form.datainicio.data < calendario.datainicio or form.datafim.data > calendario.datafim:
            flash('As datas do evento devem estar dentro do período do calendário.', 'danger')
            return render_template('eventos/form.html', form=form, titulo='Novo Evento')
        
        # Verificar se as datas estão dentro do período da categoria
        periodo = categoria.periodo
        if form.datainicio.data < periodo.datainicial or form.datafim.data > periodo.datafinal:
            flash('As datas do evento devem estar dentro do período da categoria.', 'warning')
            # Não bloqueia, apenas avisa
        
        evento = Eventos(
            id_categoria=form.id_categoria.data,
            titulo=form.titulo.data,
            descricao=form.descricao.data,
            datainicio=form.datainicio.data,
            datafim=form.datafim.data,
            dia_todo=form.dia_todo.data,
            local=form.local.data
        )
        
        # Verificar conflitos de eventos
        conflitos = verificar_conflitos(evento)
        if conflitos:
            flash(f'Atenção! Existem {len(conflitos)} eventos conflitantes no mesmo período.', 'warning')
        
        db.session.add(evento)
        db.session.commit()
        
        # Se a categoria tem habilitação de contagem, atualizar o total de dias
        if categoria.habilitacaocontagem:
            dias_validos = categoria.atualizar_contagem_dias()
            if categoria.totaldias and dias_validos > categoria.totaldias:
                flash(f'Atenção! A categoria agora tem {dias_validos} dias registrados, ultrapassando o limite de {categoria.totaldias} dias.', 'warning')
        
        flash('Evento criado com sucesso!', 'success')
        return redirect(url_for('evento.listar'))
        
    return render_template('eventos/form.html', form=form, titulo='Novo Evento')

@evento_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    evento = Eventos.query.get_or_404(id)
    form = EventoForm(obj=evento)
    form.id_categoria.choices = [(c.id_categoria, f"{c.nome} - {c.calendario.nome}") 
                                for c in CategoriaCalendario.query.all()]
    
    if form.validate_on_submit():
        # Buscar a categoria e o calendário associado
        categoria = CategoriaCalendario.query.get(form.id_categoria.data)
        calendario = categoria.calendario
        
        # Verificar se as datas do evento estão dentro do período do calendário
        if form.datainicio.data < calendario.datainicio or form.datafim.data > calendario.datafim:
            flash('As datas do evento devem estar dentro do período do calendário.', 'danger')
            return render_template('eventos/form.html', form=form, titulo='Editar Evento')
        
        # Verificar se as datas estão dentro do período da categoria
        periodo = categoria.periodo
        if form.datainicio.data < periodo.datainicial or form.datafim.data > periodo.datafinal:
            flash('As datas do evento devem estar dentro do período da categoria.', 'warning')
            # Não bloqueia, apenas avisa
        
        # Guardar a categoria antiga se foi alterada
        categoria_antiga = None
        if evento.id_categoria != form.id_categoria.data:
            categoria_antiga = evento.categoria
        
        # Atualizar os dados do evento
        form.populate_obj(evento)
        
        # Verificar conflitos de eventos
        conflitos = verificar_conflitos(evento, evento.id_evento)
        if conflitos:
            flash(f'Atenção! Existem {len(conflitos)} eventos conflitantes no mesmo período.', 'warning')
        
        db.session.commit()
        
        # Se a categoria tem habilitação de contagem, atualizar o total de dias
        if categoria.habilitacaocontagem:
            dias_validos = categoria.atualizar_contagem_dias()
            if categoria.totaldias and dias_validos > categoria.totaldias:
                flash(f'Atenção! A categoria agora tem {dias_validos} dias registrados, ultrapassando o limite de {categoria.totaldias} dias.', 'warning')
        
        # Se a categoria foi alterada, atualizar a contagem na categoria antiga também
        if categoria_antiga and categoria_antiga.habilitacaocontagem:
            categoria_antiga.atualizar_contagem_dias()
        
        flash('Evento atualizado com sucesso!', 'success')
        return redirect(url_for('evento.listar'))
        
    return render_template('eventos/form.html', form=form, titulo='Editar Evento')

@evento_bp.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    evento = Eventos.query.get_or_404(id)
    
    db.session.delete(evento)
    db.session.commit()
    flash('Evento excluído com sucesso!', 'success')
    
    return redirect(url_for('evento.listar'))

@evento_bp.route('/calendario/<int:id>')
def eventos_calendario(id):
    calendario = Calendario.query.get_or_404(id)
    categorias = CategoriaCalendario.query.filter_by(id_calendario=id).all()
    categoria_ids = [c.id_categoria for c in categorias]
    
    # Mapeamento de categorias para fácil acesso
    categorias_dict = {c.id_categoria: c for c in categorias}
    
    eventos = Eventos.query.filter(Eventos.id_categoria.in_(categoria_ids)).all()
    
    # Formatar eventos para o fullCalendar respeitando dias válidos
    eventos_formatados = []
    contagem_dias_por_categoria = {}
    
    for evento in eventos:
        categoria = categorias_dict.get(evento.id_categoria)
        dias_semana_validos = []
        
        # Verificar se a categoria tem dias da semana válidos definidos
        if categoria.diassemanasvalidos:
            dias_semana_validos = [int(d) for d in categoria.diassemanasvalidos]
        
        # Se existem restrições de dias da semana
        if dias_semana_validos:
            # Criar eventos individuais para cada dia válido
            data_atual = evento.datainicio
            
            # Contador para essa categoria
            if categoria.nome not in contagem_dias_por_categoria:
                contagem_dias_por_categoria[categoria.nome] = 0
            
            while data_atual <= evento.datafim:
                # Verifica se o dia da semana é válido (1=Segunda até 7=Domingo)
                if data_atual.isoweekday() in dias_semana_validos:
                    # Adiciona um evento individual para este dia
                    eventos_formatados.append({
                        'id': evento.id_evento,
                        'title': evento.titulo,
                        'start': data_atual.isoformat(),
                        'end': (data_atual + timedelta(days=1)).isoformat(),  # Importante para visualização correta
                        'allDay': True,  # Garante que o evento ocupa o dia todo
                        'backgroundColor': categoria.corassociada,
                        'borderColor': categoria.corassociada,
                        'textColor': '#ffffff',  # Texto branco para melhor contraste
                        'description': evento.descricao or '',
                        'location': evento.local or '',
                        'categoria_nome': categoria.nome,
                        'evento_original_id': evento.id_evento
                    })
                    
                    # Incrementa a contagem de dias válidos
                    contagem_dias_por_categoria[categoria.nome] += 1
                
                data_atual += timedelta(days=1)
        else:
            # Se não há restrição de dias, adiciona o evento normalmente
            eventos_formatados.append({
                'id': evento.id_evento,
                'title': evento.titulo,
                'start': evento.datainicio.isoformat(),
                'end': evento.datafim.isoformat(),
                'allDay': evento.dia_todo,
                'backgroundColor': categoria.corassociada,
                'borderColor': categoria.corassociada,
                'textColor': '#ffffff',
                'description': evento.descricao or '',
                'location': evento.local or '',
                'categoria_nome': categoria.nome
            })
            
            # Para eventos sem restrição de dias, conta todos os dias
            if categoria.nome not in contagem_dias_por_categoria:
                contagem_dias_por_categoria[categoria.nome] = 0
                
            contagem_dias_por_categoria[categoria.nome] += (evento.datafim - evento.datainicio).days + 1
    
    # Inicializa contadores para categorias sem eventos
    for categoria in categorias:
        if categoria.nome not in contagem_dias_por_categoria:
            contagem_dias_por_categoria[categoria.nome] = 0
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(eventos_formatados)
    
    return render_template('eventos/calendario.html', 
                           calendario=calendario, 
                           eventos=eventos_formatados,
                           contagem_dias_por_categoria=contagem_dias_por_categoria)

@evento_bp.route('/relatorio/<int:id>')
def relatorio_calendario(id):
    calendario = Calendario.query.get_or_404(id)
    categorias = CategoriaCalendario.query.filter_by(id_calendario=id).all()
    
    # Preparar dados para o relatório
    dados_categorias = []
    for categoria in categorias:
        eventos = Eventos.query.filter_by(id_categoria=categoria.id_categoria).order_by(Eventos.datainicio).all()
        
        # Atualizar contagem de dias válidos, se necessário
        dias_validos = None
        if categoria.habilitacaocontagem:
            dias_validos = categoria.atualizar_contagem_dias()
        
        dados_categorias.append({
            'categoria': categoria,
            'eventos': eventos,
            'dias_validos': dias_validos
        })
    
    return render_template('eventos/relatorio.html', 
                          calendario=calendario, 
                          dados_categorias=dados_categorias)

def verificar_conflitos(evento, evento_id=None):
    """Verifica se há conflitos com outros eventos na mesma categoria e período"""
    query = Eventos.query.filter(
        Eventos.id_categoria == evento.id_categoria,
        and_(
            Eventos.datainicio <= evento.datafim,
            Eventos.datafim >= evento.datainicio
        )
    )
    
    if evento_id:
        query = query.filter(Eventos.id_evento != evento_id)
        
    return query.all()