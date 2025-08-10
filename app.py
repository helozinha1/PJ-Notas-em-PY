# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'chave_super_secreta'
db = SQLAlchemy(app)

# Executa o script SQL para inicializar o banco de dados se ele não existir
def init_database():
    """Initializa o banco de dados a partir do arquivo init_db.sql se ele não existir."""
    if not os.path.exists('database.db'):
        conn = sqlite3.connect('database.db')
        with open('init_db.sql') as f:
            conn.executescript(f.read())
        conn.commit()
        conn.close()

# Cria os modelos para as tabelas
class Turma(db.Model):
    """Modelo de dados para a tabela 'turma'."""
    __tablename__ = 'turma'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    alunos = db.relationship('Aluno', backref='turma', lazy=True)

class Aluno(db.Model):
    """Modelo de dados para a tabela 'aluno'."""
    __tablename__ = 'aluno'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    idade = db.Column(db.Integer, nullable=False)
    turma_id = db.Column(db.Integer, db.ForeignKey('turma.id'))
    projetos = db.relationship('Projeto', backref='aluno', lazy=True, cascade='all, delete-orphan')

class Projeto(db.Model):
    """Modelo de dados para a tabela 'projeto'."""
    __tablename__ = 'projeto'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    nota = db.Column(db.Float, nullable=False)
    aluno_id = db.Column(db.Integer, db.ForeignKey('aluno.id', ondelete='CASCADE'), nullable=False)


with app.app_context():
    init_database()
    db.create_all()

@app.route('/')
def index():
    """Renderiza a página inicial."""
    return render_template('index.html')

# Rotas para Alunos
@app.route('/students')
def students_list():
    """Renderiza a página com a lista de alunos e suas médias."""
    alunos_list = Aluno.query.all()
    alunos_com_medias = []
    for aluno in alunos_list:
        projetos = Projeto.query.filter_by(aluno_id=aluno.id).all()
        media = sum([p.nota for p in projetos]) / len(projetos) if projetos else None
        
        turma_nome = aluno.turma.nome if aluno.turma else None

        alunos_com_medias.append({
            'id': aluno.id,
            'name': aluno.nome,
            'avg_score': media,
            'turma_nome': turma_nome
        })
    turmas_list = Turma.query.all()
    return render_template('students.html', students=alunos_com_medias, turmas=turmas_list)

@app.route('/students/add', methods=['GET', 'POST'])
def add_aluno():
    """Adiciona um novo aluno ao banco de dados."""
    if request.method == 'POST':
        nome = request.form.get('name')
        email = request.form.get('email')
        idade = request.form.get('age')
        turma_id = request.form.get('turma_id') 
        
        if not nome or not email or not idade:
            flash('Todos os campos são obrigatórios.', 'error')
            return redirect(url_for('add_aluno'))
        
        if Aluno.query.filter_by(email=email).first():
            flash('Email já cadastrado.', 'error')
            return redirect(url_for('add_aluno'))
            
        try:
            idade = int(idade)
            if idade <= 0:
                flash('Idade deve ser um número positivo.', 'error')
                return redirect(url_for('add_aluno'))
        except ValueError:
            flash('Idade deve ser um número válido.', 'error')
            return redirect(url_for('add_aluno'))
        
        # AQUI: A coluna turma_id agora é preenchida com o valor do formulário
        novo_aluno = Aluno(nome=nome, email=email, idade=idade, turma_id=turma_id if turma_id else None)
        db.session.add(novo_aluno)
        db.session.commit()
        flash('Aluno adicionado com sucesso!', 'success')
        return redirect(url_for('students_list'))
    
    turmas_list = Turma.query.all()
    return render_template('add_student.html', turmas=turmas_list)


@app.route('/students/edit/<int:id>', methods=['POST'])
def edit_aluno(id):
    """Edita as informações de um aluno."""
    aluno = Aluno.query.get_or_404(id)
    aluno.nome = request.form.get('nome')
    aluno.email = request.form.get('email')
    aluno.idade = request.form.get('idade')
    turma_id_str = request.form.get('turma_id')
    aluno.turma_id = int(turma_id_str) if turma_id_str else None

    if not aluno.nome or not aluno.email or not aluno.idade:
        flash('Todos os campos são obrigatórios.', 'error')
        return redirect(url_for('students_list'))

    if Aluno.query.filter(Aluno.email == aluno.email, Aluno.id != id).first():
        flash('Email já cadastrado.', 'error')
        return redirect(url_for('students_list'))
        
    try:
        aluno.idade = int(aluno.idade)
    except ValueError:
        flash('Idade deve ser um número válido.', 'error')
        return redirect(url_for('students_list'))
    
    db.session.commit()
    flash('Aluno atualizado com sucesso!', 'success')
    return redirect(url_for('students_list'))

@app.route('/students/delete/<int:id>')
def delete_aluno(id):
    """Remove um aluno e seus projetos do banco de dados."""
    aluno = Aluno.query.get_or_404(id)
    db.session.delete(aluno)
    db.session.commit()
    flash('Aluno e seus projetos removidos com sucesso!', 'success')
    return redirect(url_for('students_list'))

@app.route('/student_detail/<int:id>')
def student_detail(id):
    """Renderiza a página de detalhes de um aluno."""
    aluno = Aluno.query.get_or_404(id)
    projetos = Projeto.query.filter_by(aluno_id=aluno.id).all()
    media = sum([p.nota for p in projetos]) / len(projetos) if projetos else 0
    turmas = Turma.query.all()
    return render_template('student_detail.html', aluno=aluno, projetos=projetos, media=media, turmas=turmas)

# Rotas para Projetos
@app.route('/grades/add', methods=['GET', 'POST'])
def grades_add():
    """Adiciona uma nova nota a um projeto de aluno."""
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        nome_projeto = request.form.get('subject')
        nota = request.form.get('score')
        
        if not student_id or not nome_projeto or not nota:
            flash('Todos os campos são obrigatórios.', 'error')
            return redirect(url_for('grades_add'))

        try:
            nota = float(nota)
            student_id = int(student_id)
            if not 0 <= nota <= 10:
                flash('A nota deve ser entre 0 e 10.', 'error')
                return redirect(url_for('grades_add'))
        except (ValueError, TypeError):
            flash('ID do aluno e nota devem ser números válidos.', 'error')
            return redirect(url_for('grades_add'))
        
        novo_projeto = Projeto(nome=nome_projeto, nota=nota, aluno_id=student_id)
        db.session.add(novo_projeto)
        db.session.commit()
        flash('Projeto adicionado com sucesso!', 'success')
        return redirect(url_for('student_detail', id=student_id))
    
    alunos_list = Aluno.query.all()
    students_data = [{'id': aluno.id, 'name': aluno.nome} for aluno in alunos_list]
    return render_template('grades_add.html', students=students_data)

@app.route('/student_detail/<int:aluno_id>/add_projeto', methods=['POST'])
def add_projeto(aluno_id):
    """Adiciona um projeto a um aluno específico."""
    nome = request.form.get('nome')
    nota = request.form.get('nota')

    if not nome or not nota:
        flash('Todos os campos são obrigatórios.', 'error')
        return redirect(url_for('student_detail', id=aluno_id))
    
    try:
        nota = float(nota)
    except ValueError:
        flash('Nota deve ser um número válido.', 'error')
        return redirect(url_for('student_detail', id=aluno_id))
    
    novo_projeto = Projeto(nome=nome, nota=nota, aluno_id=aluno_id)
    db.session.add(novo_projeto)
    db.session.commit()
    flash('Projeto adicionado com sucesso!', 'success')
    return redirect(url_for('student_detail', id=aluno_id))

@app.route('/student_detail/<int:aluno_id>/delete_projeto/<int:id>')
def delete_projeto(id, aluno_id):
    """Remove um projeto específico de um aluno."""
    projeto = Projeto.query.get_or_404(id)
    db.session.delete(projeto)
    db.session.commit()
    flash('Projeto removido com sucesso!', 'success')
    return redirect(url_for('student_detail', id=aluno_id))

@app.route('/student_detail/<int:aluno_id>/edit_projeto/<int:id>', methods=['POST'])
def edit_projeto(id, aluno_id):
    """Edita um projeto específico de um aluno."""
    projeto = Projeto.query.get_or_404(id)
    projeto.nome = request.form.get('nome')
    nota = request.form.get('nota')
    
    if not projeto.nome or not nota:
        flash('Todos os campos são obrigatórios.', 'error')
        return redirect(url_for('student_detail', id=aluno_id))

    try:
        projeto.nota = float(nota)
    except ValueError:
        flash('Nota deve ser um número válido.', 'error')
        return redirect(url_for('student_detail', id=aluno_id))
        
    db.session.commit()
    flash('Projeto atualizado com sucesso!', 'success')
    return redirect(url_for('student_detail', id=aluno_id))

# Rotas para Turmas
@app.route('/turmas')
def turmas():
    """Renderiza a página com a lista de turmas."""
    turmas_list = Turma.query.all()
    turmas_com_alunos = []
    for turma in turmas_list:
        turmas_com_alunos.append({
            'id': turma.id,
            'nome': turma.nome,
            'descricao': turma.descricao,
            'num_alunos': len(turma.alunos)
        })
    return render_template('turmas.html', turmas=turmas_com_alunos)

@app.route('/turma/add', methods=['POST'])
def add_turma():
    """Adiciona uma nova turma ao banco de dados."""
    nome = request.form.get('nome')
    descricao = request.form.get('descricao')

    if not nome:
        flash('O nome da turma é obrigatório.', 'error')
        return redirect(url_for('turmas'))
    
    nova_turma = Turma(nome=nome, descricao=descricao)
    db.session.add(nova_turma)
    db.session.commit()
    flash('Turma adicionada com sucesso!', 'success')
    return redirect(url_for('turmas'))

@app.route('/turma/edit/<int:id>', methods=['POST'])
def edit_turma(id):
    """Edita as informações de uma turma."""
    turma = Turma.query.get_or_404(id)
    turma.nome = request.form.get('nome')
    turma.descricao = request.form.get('descricao')

    if not turma.nome:
        flash('O nome da turma é obrigatório.', 'error')
        return redirect(url_for('turmas'))

    db.session.commit()
    flash('Turma atualizada com sucesso!', 'success')
    return redirect(url_for('turmas'))

@app.route('/turma/delete/<int:id>')
def delete_turma(id):
    """Remove uma turma e desassocia os alunos."""
    turma = Turma.query.get_or_404(id)
    
    for aluno in turma.alunos:
        aluno.turma_id = None
    
    db.session.delete(turma)
    db.session.commit()
    flash('Turma removida com sucesso! Os alunos foram desassociados.', 'success')
    return redirect(url_for('turmas'))

if __name__ == '__main__':
    app.run(debug=True)
