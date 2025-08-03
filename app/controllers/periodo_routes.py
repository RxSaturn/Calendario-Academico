from flask import Blueprint, render_template, redirect, url_for, flash, request
from app import db
from app.models.models import Periodo
from app.forms import PeriodoForm

periodo_bp = Blueprint('periodo', __name__, url_prefix='/periodos')

@periodo_bp.route('/')
def listar():
    periodos = Periodo.query.all()
    return render_template('periodos/listar.html', periodos=periodos)

@periodo_bp.route('/novo', methods=['GET', 'POST'])
def novo():
    form = PeriodoForm()
    
    if form.validate_on_submit():
        periodo = Periodo(
            descricao=form.descricao.data,
            datainicial=form.datainicial.data,
            datafinal=form.datafinal.data
        )
        
        db.session.add(periodo)
        db.session.commit()
        flash('Período criado com sucesso!', 'success')
        return redirect(url_for('periodo.listar'))
        
    return render_template('periodos/form.html', form=form, titulo='Novo Período')

@periodo_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    periodo = Periodo.query.get_or_404(id)
    form = PeriodoForm(obj=periodo)
    
    if form.validate_on_submit():
        form.populate_obj(periodo)
        db.session.commit()
        flash('Período atualizado com sucesso!', 'success')
        return redirect(url_for('periodo.listar'))
        
    return render_template('periodos/form.html', form=form, titulo='Editar Período')

@periodo_bp.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    periodo = Periodo.query.get_or_404(id)
    
    try:
        db.session.delete(periodo)
        db.session.commit()
        flash('Período excluído com sucesso!', 'success')
    except Exception:
        db.session.rollback()
        flash('Não foi possível excluir este período. Verifique se há registros associados.', 'danger')
    
    return redirect(url_for('periodo.listar'))