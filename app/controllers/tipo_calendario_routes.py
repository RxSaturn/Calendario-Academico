from flask import Blueprint, render_template, redirect, url_for, flash, request
from app import db
from app.models.models import TipoCalendario
from app.forms import TipoCalendarioForm

tipo_calendario_bp = Blueprint('tipo_calendario', __name__, url_prefix='/tipos')

@tipo_calendario_bp.route('/')
def listar():
    tipos = TipoCalendario.query.all()
    return render_template('tipos/listar.html', tipos=tipos)

@tipo_calendario_bp.route('/novo', methods=['GET', 'POST'])
def novo():
    form = TipoCalendarioForm()
    
    if form.validate_on_submit():
        # Verificar se a sigla já existe
        if TipoCalendario.query.filter_by(sigla=form.sigla.data).first():
            flash('Esta sigla já está em uso.', 'danger')
            return render_template('tipos/form.html', form=form, titulo='Novo Tipo de Calendário')
            
        tipo = TipoCalendario(
            sigla=form.sigla.data,
            nome=form.nome.data
        )
        
        db.session.add(tipo)
        db.session.commit()
        flash('Tipo de calendário criado com sucesso!', 'success')
        return redirect(url_for('tipo_calendario.listar'))
        
    return render_template('tipos/form.html', form=form, titulo='Novo Tipo de Calendário')

@tipo_calendario_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    tipo = TipoCalendario.query.get_or_404(id)
    form = TipoCalendarioForm(obj=tipo)
    
    if form.validate_on_submit():
        # Verificar se a sigla já existe em outro registro
        existente = TipoCalendario.query.filter_by(sigla=form.sigla.data).first()
        if existente and existente.id_tipo != tipo.id_tipo:
            flash('Esta sigla já está em uso.', 'danger')
            return render_template('tipos/form.html', form=form, titulo='Editar Tipo de Calendário')
            
        form.populate_obj(tipo)
        db.session.commit()
        flash('Tipo de calendário atualizado com sucesso!', 'success')
        return redirect(url_for('tipo_calendario.listar'))
        
    return render_template('tipos/form.html', form=form, titulo='Editar Tipo de Calendário')

@tipo_calendario_bp.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    tipo = TipoCalendario.query.get_or_404(id)
    
    try:
        db.session.delete(tipo)
        db.session.commit()
        flash('Tipo de calendário excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Não foi possível excluir este tipo de calendário. Verifique se há calendários associados.', 'danger')
    
    return redirect(url_for('tipo_calendario.listar'))