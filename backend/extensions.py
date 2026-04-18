"""
Shared Flask extensions - breaks circular imports between app.py and models.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
jwt = JWTManager()
