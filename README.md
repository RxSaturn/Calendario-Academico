# Sistema de Calendário Acadêmico

Sistema completo para gerenciamento de calendários acadêmicos, desenvolvido em Flask e SQLAlchemy. Esta aplicação permite o controle de períodos letivos, tipos de calendários, eventos acadêmicos e visualização em formato de calendário.

## Funcionalidades

- Gerenciamento de períodos acadêmicos
- Criação e edição de calendários por ano e tipo
- Categorização de eventos com cores personalizadas
- Visualização interativa de calendários
- Detecção de conflitos de eventos
- Relatórios de calendários

## Requisitos

- Python 3.8 ou superior
- PostgreSQL (recomendado) ou SQLite
- Sistema operacional: Windows, Linux ou macOS

## Preparação do ambiente

### 1. Clone o repositório

```bash
git clone https://github.com/RxSaturn/Calendario-Academico.git
cd Calendario-Academico
```

### 2. Crie e ative o ambiente virtual

#### No Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

#### No Linux/macOS:
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

## Configuração do banco de dados

### Opção 1: Usar SQLite (para desenvolvimento)

Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:

```
SECRET_KEY=sua-chave-secreta
USE_SQLITE=True
```

### Opção 2: Usar PostgreSQL (recomendado para produção)

1. Crie um banco de dados PostgreSQL:
```bash
createdb calendario_academico
```

2. Configure as variáveis de ambiente no arquivo `.env`:
```
SECRET_KEY=sua-chave-secreta
DATABASE_URL=postgresql://seu_usuario:sua_senha@localhost/calendario_academico
```

## Inicialização do banco de dados

```bash
# Inicializar as migrações
flask db upgrade

# Criar tabelas e popular com dados iniciais
flask create-tables
flask seed-db
```

## Executando a aplicação

```bash
flask run
```

A aplicação estará disponível em http://127.0.0.1:5000/

## Acesso à aplicação

1. Abra seu navegador e acesse: http://127.0.0.1:5000/
2. Na primeira execução, o sistema já estará populado com dados de exemplo para o ano de 2025
3. Navegue pelo menu superior para acessar as diferentes funcionalidades:
   - Tipos de Calendário
   - Períodos
   - Calendários
   - Categorias
   - Eventos

## Desenvolvimento

Este projeto segue a arquitetura MVC (Model-View-Controller):
- Models: `app/models/`
- Views: `app/templates/`
- Controllers: `app/controllers/`
