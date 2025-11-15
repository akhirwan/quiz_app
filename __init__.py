from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

db = SQLAlchemy()

def create_app():
  load_dotenv()  # baca .env
    
  app = Flask(__name__)

  # pilih config
  if os.getenv('FLASK_ENV') == 'production':
    app.config.from_object('config.ProductionConfig')
  else:
    app.config.from_object('config.DevelopmentConfig')

  db.init_app(app)

  # register blueprint kalau ada
  from .app import main_bp
  app.register_blueprint(main_bp)
  
  return app
