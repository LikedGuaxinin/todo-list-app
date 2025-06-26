from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from src.extensions import db
from src.models import User, Task

# Blueprints
auth_routes = Blueprint('auth', __name__)
task_routes = Blueprint('task', __name__)

# ROTAS DE AUTENTICAÇÃO
@auth_routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('Usuário já existe.')
            return redirect(url_for('auth.register'))

        new_user = User(
            username=username,
            password=generate_password_hash(password, method='pbkdf2:sha256')
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Conta criada com sucesso!')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('task.tasks'))
        else:
            flash('Login inválido')

    return render_template('login.html')


@auth_routes.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


# ROTAS DE TAREFAS
@task_routes.route('/')
@login_required
def tasks():
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.id.desc()).all()
    return render_template('tasks.html', tasks=tasks)


@task_routes.route('/add', methods=['POST'])
@login_required
def add():
    content = request.form['content']
    if not content.strip():
        flash("A tarefa não pode estar vazia.")
        return redirect(url_for('task.tasks'))
    
    new_task = Task(content=content.strip(), user_id=current_user.id)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('task.tasks'))


@task_routes.route('/update/<int:task_id>')
@login_required
def update(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        return 'Acesso não autorizado.', 403

    task.completed = not task.completed
    db.session.commit()
    return redirect(url_for('task.tasks'))


@task_routes.route('/delete/<int:task_id>')
@login_required
def delete(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        return 'Acesso não autorizado.', 403

    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('task.tasks'))


@task_routes.route('/toggle/<int:task_id>')
@login_required
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        return 'Acesso não autorizado.', 403

    task.completed = not task.completed
    db.session.commit()
    return redirect(url_for('task.tasks'))
