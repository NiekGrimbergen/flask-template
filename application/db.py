from flask_sqlalchemy import SQLAlchemy
from application.models.base import Base

db = SQLAlchemy(model_class=Base)