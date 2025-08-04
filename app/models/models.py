from datetime import datetime, timedelta
import calendar
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
    
    def calcular_dias_validos(self, inicio, fim):
        """Calcula os dias válidos entre as datas, considerando apenas os dias da semana permitidos"""
        dias_validos = 0
        dias_semana_permitidos = [int(d) for d in self.diassemanasvalidos] if self.diassemanasvalidos else []
        
        # Ajuste para formato de dia da semana do Python (0=Segunda, 6=Domingo)
        dias_ajustados = [(d % 7) for d in dias_semana_permitidos]
        
        data_atual = inicio
        while data_atual <= fim:
            # Na semana do Python, 0 é segunda-feira e 6 é domingo
            dia_semana = data_atual.weekday()
            if dia_semana in dias_ajustados:
                dias_validos += 1
            data_atual += timedelta(days=1)
            
        return dias_validos
    
    def atualizar_contagem_dias(self):
        """Atualiza a contagem total de dias com base nos eventos associados"""
        if not self.habilitacaocontagem:
            return 0
            
        total_dias = 0
        dias_contados = set()  # Para evitar contar o mesmo dia duas vezes
        
        for evento in self.eventos:
            data_atual = evento.datainicio
            while data_atual <= evento.datafim:
                # Verificar se o dia da semana é válido
                if self.diassemanasvalidos and str(data_atual.isoweekday()) in self.diassemanasvalidos:
                    dias_contados.add(data_atual.strftime('%Y-%m-%d'))
                data_atual += timedelta(days=1)
                
        total_dias = len(dias_contados)
        return total_dias

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