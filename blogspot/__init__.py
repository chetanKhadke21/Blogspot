import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # Load config from environment variables
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    app.config['REQUIRE_APPROVAL'] = True  # Set to True if posts need admin approval

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Ensure the uploads directory exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    with app.app_context():
        # Import models
        from .models import User

        # Import routes
        from .auth.routes import auth
        from .main.routes import main
        from .admin.routes import admin

        # Register blueprints
        app.register_blueprint(auth)
        app.register_blueprint(main)
        app.register_blueprint(admin)

        # Create database tables
        db.create_all()

        # Create admin user if not exists
        create_admin()

        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

    return app

def create_admin():
    from .models import User
    from werkzeug.security import generate_password_hash

    admin = User.query.filter_by(email='admin@gmail.com').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@gmail.com',
            password=generate_password_hash('admin'),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
