import re
from flask import Blueprint, Flask, render_template

def camel_to_kebab(name: str) -> str:
    """
    Converts a CamelCase string to kebab-case.
    
    :param name: The CamelCase string to convert
    :return: The resulting kebab-case string
    """
    # Insert a hyphen before each uppercase letter, except the first one, and convert to lowercase
    return re.sub(r'(?<!^)(?=[A-Z])', '-', name).lower()

def route(rule, methods=None):
    """
    Decorator to mark a method as a route.
    
    :param rule: URL rule as string
    :param methods: List of HTTP methods allowed for this route
    """
    def decorator(func):
        func.route_rule = rule
        func.route_methods = methods or ['GET']
        return func
    return decorator

class BaseController:
    blueprint: Blueprint = None

    def __init__(self):
        """
        Initialize the BaseController with a Flask Blueprint dynamically based on the subclass name.
        """
        # Use the name of the subclass for the blueprint name
        self.name = camel_to_kebab(self.__class__.__name__)
        blueprint_name = self.name
        url_prefix = f"/{self.name}"  # Default to the subclass name as the URL prefix

        # Create a blueprint for the controller
        self.blueprint = Blueprint(blueprint_name, __name__, url_prefix=url_prefix, template_folder=f"views/{self.name}/")

        # Automatically bind route methods to the blueprint
        self.register_routes()

    def register_routes(self):
        """
        Automatically register routes to the blueprint by looking for methods decorated with @route.
        """
        # Iterate over all methods of the class
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            # Check if the attribute has a route attribute
            if callable(attr) and hasattr(attr, 'route_rule'):
                route_rule = getattr(attr, 'route_rule')
                route_methods = getattr(attr, 'route_methods', ['GET'])

                # Register the route with the blueprint
                self.blueprint.route(route_rule, methods=route_methods)(attr)

    def register(self, app: Flask):
        """
        Register the controller's blueprint with the Flask app.
        
        :param app: The Flask app instance
        """
        if self.blueprint:
            app.register_blueprint(self.blueprint)
        else:
            raise ValueError("Blueprint not defined for the controller.")
        
    def render_template(self, rel_path: str, **kwargs):
        return render_template(f"{self.name}/{rel_path}", **kwargs)
