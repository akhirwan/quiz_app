import os

class BaseConfig:
  SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-secret')
  SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///quiz_app.db')
  SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(BaseConfig):
  DEBUG = True
  ENV = 'development'

class ProductionConfig(BaseConfig):
  DEBUG = False
  ENV = 'production'