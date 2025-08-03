from datetime import datetime
from app import db

class Periodo(db.Model):
    __tablename__ = 'periodo'
    
    id_periodo = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(30))
    datainicial = db.Column(db.Date, nullable=False)
    datafinal = db.Column(db.Date, nullable=False)
    
    # Relacionamentos
    categorias = db.relationship('CategoriaCalendario', backref='periodo', lazy=True)
    
    def __repr__(self):
        return f'<Periodo {self.descricao}>'

class TipoCalendario(db.Model):
    __tablename__ = 'tipocalendario'
    
    id_tipo = db.Column(db.Integer, primary_key=True)
    sigla = db.Column(db.String(4), nullable=False)
    nome = db.Column(db.String(30), nullable=False)
    
    # Relacionamentos
    calendarios = db.relationship('Calendario', backref='tipo_calendario', lazy=True)
    
    def __repr__(self):
        return f'<TipoCalendario {self.sigla} - {self.nome}>'

class Calendario(db.Model):
    __tablename__ = 'calendario'
    
    id_calendario = db.Column(db.Integer, primary_key=True)
    id_tipo = db.Column(db.Integer, db.ForeignKey('tipocalendario.id_tipo'), nullable=False)
    nome = db.Column(db.String(30), nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    datainicio = db.Column(db.Date, nullable=False)
    datafim = db.Column(db.Date, nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    categorias = db.relationship('CategoriaCalendario', backref='calendario', lazy=True)
    
    def __repr__(self):
        return f'<Calendario {self.nome} ({self.ano})>'

class CategoriaCalendario(db.Model):
    __tablename__ = 'categoriacalendario'
    
    id_categoria = db.Column(db.Integer, primary_key=True)
    id_calendario = db.Column(db.Integer, db.ForeignKey('calendario.id_calendario'), nullable=False)
    id_periodo = db.Column(db.Integer, db.ForeignKey('periodo.id_periodo'), nullable=False)
    nome = db.Column(db.String(30), nullable=False)
    corassociada = db.Column(db.String(30))
    totaldias = db.Column(db.Integer)
    diassemanasvalidos = db.Column(db.String(30))
    habilitacaocontagem = db.Column(db.Boolean)
    
    # Relacionamentos
    eventos = db.relationship('Eventos', backref='categoria', lazy=True)
    
    def __repr__(self):
        return f'<CategoriaCalendario {self.nome}>'

class Eventos(db.Model):
    __tablename__ = 'eventos'
    
    id_evento = db.Column(db.Integer, primary_key=True)
    id_categoria = db.Column(db.Integer, db.ForeignKey('categoriacalendario.id_categoria'), nullable=False)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(255))
    datainicio = db.Column(db.Date, nullable=False)
    datafim = db.Column(db.Date, nullable=False)
    dia_todo = db.Column(db.Boolean, default=False)
    local = db.Column(db.String(100))
    
    def __repr__(self):
        return f'<Evento {self.titulo}>'