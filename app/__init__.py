from flask import Flask
from flask_cors import CORS
from app.models import db
import os

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///voltonic.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'voltonic-secret-key-2026'
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        print("✅ Database tables created")
    
    return app