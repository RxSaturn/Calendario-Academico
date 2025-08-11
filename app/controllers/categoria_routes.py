from flask import Blueprint, render_template, redirect, url_for, flash, request
from sqlalchemy import text
from app import db
from app.models.models import CategoriaCalendario, Calendario, Periodo, Eventos
from app.forms import CategoriaForm
from datetime import datetime

categoria_bp = Blueprint('categoria', __name__, url_prefix='/categorias')

@categoria_bp.route('/')
def listar():
    categorias = CategoriaCalendario.query.all()
    return render_template('categorias/listar.html', categorias=categorias)

@categoria_bp.route('/novo', methods=['GET', 'POST'])
def novo():
    form = CategoriaForm()
    form.id_calendario.choices = [(c.id_calendario, f"{c.nome} ({c.ano})") for c in Calendario.query.all()]
    form.id_periodo.choices = [(p.id_periodo, p.descricao) for p in Periodo.query.all()]
    
    if form.validate_on_submit():
        # Verificar cores duplicadas no mesmo calendário
        cor_existente = CategoriaCalendario.query.filter_by(
            id_calendario=form.id_calendario.data,
            corassociada=form.corassociada.data
        ).first()
        
        if cor_existente:
            flash(f'A cor {form.corassociada.data} já está sendo usada em outra categoria deste calendário.', 'danger')
            return render_template('categorias/form.html', form=form, titulo='Nova Categoria')
        
        categoria = CategoriaCalendario(
            id_calendario=form.id_calendario.data,
            id_periodo=form.id_periodo.data,
            nome=form.nome.data,
            corassociada=form.corassociada.data,
            totaldias=form.totaldias.data,
            diassemanasvalidos=form.diassemanasvalidos.data,
            habilitacaocontagem=form.habilitacaocontagem.data
        )
        
        db.session.add(categoria)
        db.session.commit()
        flash('Categoria criada com sucesso!', 'success')
        return redirect(url_for('categoria.listar'))
        
    return render_template('categorias/form.html', form=form, titulo='Nova Categoria')

@categoria_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    categoria = CategoriaCalendario.query.get_or_404(id)
    form = CategoriaForm(obj=categoria)
    form.id_calendario.choices = [(c.id_calendario, f"{c.nome} ({c.ano})") for c in Calendario.query.all()]
    form.id_periodo.choices = [(p.id_periodo, p.descricao) for p in Periodo.query.all()]
    
    if form.validate_on_submit():
        # Verificar cores duplicadas no mesmo calendário
        cor_existente = CategoriaCalendario.query.filter_by(
            id_calendario=form.id_calendario.data,
            corassociada=form.corassociada.data
        ).filter(CategoriaCalendario.id_categoria != id).first()
        
        if cor_existente:
            flash(f'A cor {form.corassociada.data} já está sendo usada em outra categoria deste calendário.', 'danger')
            return render_template('categorias/form.html', form=form, titulo='Editar Categoria')
        
        form.populate_obj(categoria)
        db.session.commit()
        flash('Categoria atualizada com sucesso!', 'success')
        return redirect(url_for('categoria.listar'))
        
    return render_template('categorias/form.html', form=form, titulo='Editar Categoria')

@categoria_bp.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    categoria = CategoriaCalendario.query.get_or_404(id)
    
    try:
        db.session.delete(categoria)
        db.session.commit()
        flash('Categoria excluída com sucesso!', 'success')
    except Exception:
        db.session.rollback()
        flash('Não foi possível excluir esta categoria. Verifique se há eventos associados.', 'danger')
    
    return redirect(url_for('categoria.listar'))

@categoria_bp.route('/remover/<int:id>', methods=['POST'])
def remover(id):
    """
    Remove uma categoria e todos seus eventos associados, 
    redirecionando para a visualização do calendário.
    """
    categoria = CategoriaCalendario.query.get_or_404(id)
    id_calendario = categoria.id_calendario
    
    # Primeiro, remover eventos associados
    eventos = Eventos.query.filter_by(id_categoria=id).all()
    for evento in eventos:
        db.session.delete(evento)
    
    # Depois, remover a categoria
    db.session.delete(categoria)
    db.session.commit()
    
    flash(f'Categoria "{categoria.nome}" e seus {len(eventos)} eventos foram removidos com sucesso!', 'success')
    
    # Redireciona para a página de visualização do calendário
    return redirect(url_for('calendario.visualizar', id=id_calendario))

@categoria_bp.route('/nova/<int:id_calendario>', methods=['GET', 'POST'])
def nova_para_calendario(id_calendario):
    """
    Adiciona uma categoria para um calendário específico,
    já preenchendo o campo do calendário.
    """
    calendario = Calendario.query.get_or_404(id_calendario)
    form = CategoriaForm()
    form.id_calendario.choices = [(c.id_calendario, f"{c.nome} ({c.ano})") for c in Calendario.query.all()]
    form.id_calendario.data = id_calendario  # Pré-seleciona o calendário
    form.id_periodo.choices = [(p.id_periodo, p.descricao) for p in Periodo.query.all()]
    
    if form.validate_on_submit():
        # Verificar cores duplicadas no mesmo calendário
        cor_existente = CategoriaCalendario.query.filter_by(
            id_calendario=id_calendario,
            corassociada=form.corassociada.data
        ).first()
        
        if cor_existente:
            flash(f'A cor {form.corassociada.data} já está sendo usada em outra categoria deste calendário.', 'danger')
            return render_template('categorias/form.html', form=form, titulo=f'Nova Categoria para {calendario.nome}')
        
        categoria = CategoriaCalendario(
            id_calendario=id_calendario,
            id_periodo=form.id_periodo.data,
            nome=form.nome.data,
            corassociada=form.corassociada.data,
            totaldias=form.totaldias.data,
            diassemanasvalidos=form.diassemanasvalidos.data,
            habilitacaocontagem=form.habilitacaocontagem.data
        )
        
        db.session.add(categoria)
        db.session.commit()
        flash('Categoria criada com sucesso!', 'success')
        return redirect(url_for('calendario.visualizar', id=id_calendario))
        
    return render_template('categorias/form.html', form=form, titulo=f'Nova Categoria para {calendario.nome}')

@categoria_bp.route('/visualizar/<int:id>')
def visualizar(id):
    """
    Visualiza detalhes de uma categoria específica e seus eventos associados.
    Também demonstra o uso da função PostgreSQL contar_eventos_por_categoria.
    """
    categoria = CategoriaCalendario.query.get_or_404(id)
    
    # Usar a função PostgreSQL para contar eventos
    try:
        total_eventos_func = db.session.execute(
            text("SELECT contar_eventos_por_categoria(:id_categoria)"),
            {"id_categoria": id}
        ).scalar()
    except Exception as e:
        # Caso a função não esteja disponível
        total_eventos_func = None
        flash(f"Função PostgreSQL não disponível: {str(e)}", "warning")
    
    # Buscar eventos associados a esta categoria
    eventos = Eventos.query.filter_by(id_categoria=id).order_by(Eventos.datainicio).all()
    
    # Calcular total de dias (para categorias com habilitacaocontagem)
    if categoria.habilitacaocontagem:
        dias_letivos = len(set([evento.datainicio for evento in eventos]))
    else:
        dias_letivos = None
    
    # Calcular duração do período associado usando função PostgreSQL
    try:
        duracao_periodo = db.session.execute(
            text("SELECT calcular_duracao_periodo(:id_periodo)"),
            {"id_periodo": categoria.id_periodo}
        ).scalar()
    except Exception:
        duracao_periodo = None
    
    return render_template(
        'categorias/visualizar.html', 
        categoria=categoria,
        eventos=eventos,
        total_eventos=len(eventos),
        total_eventos_func=total_eventos_func,
        dias_letivos=dias_letivos,
        duracao_periodo=duracao_periodo
    )