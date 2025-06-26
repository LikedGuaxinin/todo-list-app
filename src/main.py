import os
from flask import Flask
from src.extensions import db, login_manager
from src.routes import auth_routes, task_routes

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'sua_chave_secreta'

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(BASE_DIR, 'database')
    db_file = os.path.join(db_path, 'app.db')

    # Garante que a pasta 'database' existe
    if not os.path.exists(db_path):
        os.makedirs(db_path)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_file
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)

    # Registra os blueprints com prefixos apropriados
    app.register_blueprint(auth_routes, url_prefix='/auth')
    app.register_blueprint(task_routes, url_prefix='/')

    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
