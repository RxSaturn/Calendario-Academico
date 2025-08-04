from flask_wtf import FlaskForm
from wtforms import StringField, DateField, IntegerField, BooleanField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

class PeriodoForm(FlaskForm):
    descricao = StringField('Descrição', validators=[DataRequired(), Length(max=30)])
    datainicial = DateField('Data Inicial', format='%Y-%m-%d', validators=[DataRequired()])
    datafinal = DateField('Data Final', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Salvar')

class TipoCalendarioForm(FlaskForm):
    sigla = StringField('Sigla', validators=[DataRequired(), Length(min=2, max=4)])
    nome = StringField('Nome', validators=[DataRequired(), Length(max=30)])
    submit = SubmitField('Salvar')

class CalendarioForm(FlaskForm):
    id_tipo = SelectField('Tipo de Calendário', coerce=int, validators=[DataRequired()])
    nome = StringField('Nome', validators=[DataRequired(), Length(max=30)])
    ano = IntegerField('Ano', validators=[DataRequired(), NumberRange(min=2000)])
    datainicio = DateField('Data Inicial', format='%Y-%m-%d', validators=[DataRequired()])
    datafim = DateField('Data Final', format='%Y-%m-%d', validators=[DataRequired()])
    ativo = BooleanField('Ativo', default=True)
    submit = SubmitField('Salvar')

class CategoriaForm(FlaskForm):
    id_calendario = SelectField('Calendário', coerce=int, validators=[DataRequired()])
    id_periodo = SelectField('Período', coerce=int, validators=[DataRequired()])
    nome = StringField('Nome', validators=[DataRequired(), Length(max=30)])
    corassociada = StringField('Cor Associada', validators=[Length(max=30)])
    totaldias = IntegerField('Total de Dias', validators=[Optional()])
    diassemanasvalidos = StringField('Dias da Semana Válidos', validators=[Length(max=30)])
    habilitacaocontagem = BooleanField('Habilitar Contagem', default=True)
    submit = SubmitField('Salvar')

class EventoForm(FlaskForm):
    id_categoria = SelectField('Categoria', coerce=int, validators=[DataRequired()])
    titulo = StringField('Título', validators=[DataRequired(), Length(max=100)])
    descricao = TextAreaField('Descrição', validators=[Length(max=255)])
    datainicio = DateField('Data Inicial', format='%Y-%m-%d', validators=[DataRequired()])
    datafim = DateField('Data Final', format='%Y-%m-%d', validators=[DataRequired()])
    dia_todo = BooleanField('Dia Todo', default=False)
    local = StringField('Local', validators=[Length(max=100)])
    submit = SubmitField('Salvar')