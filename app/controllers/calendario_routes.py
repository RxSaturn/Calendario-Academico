from flask import Blueprint, render_template, redirect, url_for, flash, request
from app import db
from app.models.models import Calendario, TipoCalendario, CategoriaCalendario
from app.forms import CalendarioForm
from datetime import datetime

calendario_bp = Blueprint('calendario', __name__, url_prefix='/calendarios')

@calendario_bp.route('/')
def listar():
    calendarios = Calendario.query.order_by(Calendario.ano.desc(), Calendario.nome).all()
    return render_template('calendarios/listar.html', calendarios=calendarios)

@calendario_bp.route('/novo', methods=['GET', 'POST'])
def novo():
    form = CalendarioForm()
    form.id_tipo.choices = [(t.id_tipo, f"{t.sigla} - {t.nome}") for t in TipoCalendario.query.all()]
    
    if form.validate_on_submit():
        calendario = Calendario(
            id_tipo=form.id_tipo.data,
            nome=form.nome.data,
            ano=form.ano.data,
            datainicio=form.datainicio.data,
            datafim=form.datafim.data,
            ativo=form.ativo.data
        )
        
        db.session.add(calendario)
        db.session.commit()
        flash('Calendário criado com sucesso!', 'success')
        return redirect(url_for('calendario.listar'))
        
    return render_template('calendarios/form.html', form=form, titulo='Novo Calendário')

@calendario_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    calendario = Calendario.query.get_or_404(id)
    form = CalendarioForm(obj=calendario)
    form.id_tipo.choices = [(t.id_tipo, f"{t.sigla} - {t.nome}") for t in TipoCalendario.query.all()]
    
    if form.validate_on_submit():
        form.populate_obj(calendario)
        db.session.commit()
        flash('Calendário atualizado com sucesso!', 'success')
        return redirect(url_for('calendario.listar'))
        
    return render_template('calendarios/form.html', form=form, titulo='Editar Calendário')

@calendario_bp.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    calendario = Calendario.query.get_or_404(id)
    
    # Verificar se há categorias associadas
    if calendario.categorias:
        flash('Não é possível excluir um calendário com categorias associadas.', 'danger')
        return redirect(url_for('calendario.listar'))
    
    db.session.delete(calendario)
    db.session.commit()
    flash('Calendário excluído com sucesso!', 'success')
    
    return redirect(url_for('calendario.listar'))

@calendario_bp.route('/visualizar/<int:id>')
def visualizar(id):
    calendario = Calendario.query.get_or_404(id)
    return render_template('calendarios/visualizar.html', calendario=calendario)

@calendario_bp.route('/alternar-status/<int:id>', methods=['POST'])
def alternar_status(id):
    calendario = Calendario.query.get_or_404(id)
    calendario.ativo = not calendario.ativo
    db.session.commit()
    
    status = "ativado" if calendario.ativo else "desativado"
    flash(f'Calendário {status} com sucesso!', 'success')
    
    return redirect(url_for('calendario.listar'))

@calendario_bp.route('/copiar/<int:id>', methods=['GET', 'POST'])
def copiar(id):
    calendario_original = Calendario.query.get_or_404(id)
    
    if request.method == 'POST':
        novo_nome = request.form.get('novo_nome')
        novo_ano = int(request.form.get('novo_ano'))
        
        # Criar novo calendário com base no original
        novo_calendario = Calendario(
            id_tipo=calendario_original.id_tipo,
            nome=novo_nome,
            ano=novo_ano,
            datainicio=datetime(novo_ano, calendario_original.datainicio.month, calendario_original.datainicio.day),
            datafim=datetime(novo_ano, calendario_original.datafim.month, calendario_original.datafim.day),
            ativo=True
        )
        
        db.session.add(novo_calendario)
        db.session.commit()
        
        # Copiar categorias - usando relação do modelo
        for categoria_original in calendario_original.categorias:
            nova_categoria = CategoriaCalendario(
                id_calendario=novo_calendario.id_calendario,
                id_periodo=categoria_original.id_periodo,
                nome=categoria_original.nome,
                corassociada=categoria_original.corassociada,
                totaldias=categoria_original.totaldias,
                diassemanasvalidos=categoria_original.diassemanasvalidos,
                habilitacaocontagem=categoria_original.habilitacaocontagem
            )
            db.session.add(nova_categoria)
        
        db.session.commit()
        flash(f'Calendário copiado com sucesso para o ano {novo_ano}!', 'success')
        return redirect(url_for('calendario.visualizar', id=novo_calendario.id_calendario))
    
    return render_template('calendarios/copiar.html', calendario=calendario_original)