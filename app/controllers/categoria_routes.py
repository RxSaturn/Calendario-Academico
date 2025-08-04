from flask import Blueprint, render_template, redirect, url_for, flash, request
from app import db
from app.models.models import CategoriaCalendario, Calendario, Periodo
from app.forms import CategoriaForm

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