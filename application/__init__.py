import importlib
import os
from flask import Flask
from dotenv import load_dotenv
import sqlalchemy

from application.app import app
from application.db import db

load_dotenv()

def create_app():
    # Configure as needed
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    db.init_app(app)

    register_controllers(app)
    register_models(app)

    return app

from application.controllers.base import BaseController

def register_controllers(app: Flask) -> None:
    # Directory of the current file
    current_dir = os.path.dirname(__file__)
    controller_dir = os.path.join(current_dir, 'controllers')
    
    # Verify that the controller directory exists
    if not os.path.exists(controller_dir):
        raise FileNotFoundError(f"The controllers directory {controller_dir} does not exist.")

    controllers = set()

    # Loop through the files in the controller directory
    for controller_file in os.listdir(controller_dir):
        if controller_file.endswith(".py"):
            module_name = os.path.basename(controller_file)[:-3]  # Strip .py from filename
            module_path = os.path.join(controller_dir, controller_file)  # Full path to the module

            controller_spec = importlib.util.spec_from_file_location(module_name, module_path)
            controller_module = importlib.util.module_from_spec(controller_spec)
            controller_spec.loader.exec_module(controller_module)

            # Check all items in the module
            for name, obj in controller_module.__dict__.items():
                if isinstance(obj, type) and issubclass(obj, BaseController) and obj is not BaseController:
                    controllers.add(obj())  # Instantiate the controller

    # Register each controller with the Flask app
    for controller in controllers:
        controller.register(app)

def register_models(app: Flask) -> None:
    with app.app_context():
        # Directory of the current file
        current_dir = os.path.dirname(__file__)
        models_dir = os.path.join(current_dir, 'models')
        
        # Verify that the models directory exists
        if not os.path.exists(models_dir):
            raise FileNotFoundError(f"The modelss directory {models_dir} does not exist.")

        # Loop through the files in the models directory
        for models_file in os.listdir(models_dir):
            if models_file.endswith(".py"):
                try:
                    module_name = os.path.basename(models_file)[:-3]  # Strip .py from filename
                    module_path = os.path.join(models_dir, models_file)  # Full path to the module

                    models_spec = importlib.util.spec_from_file_location(module_name, module_path)
                    models_module = importlib.util.module_from_spec(models_spec)
                    models_spec.loader.exec_module(models_module)
                except sqlalchemy.exc.InvalidRequestError:
                    continue
                except Exception as e:
                    print(e)
                    continue