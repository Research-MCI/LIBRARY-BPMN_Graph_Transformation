from flask import Flask
from .post_controller import bp as post_bp
from .check_controller import bp as check_bp
from .bpmn_controller import bp as bpmn_bp  
from .query_controller import bp as query_bp  
from .health_controller import bp as health_bp

def register_routes(app: Flask):
    API_PREFIX = "/api/graph"
    app.register_blueprint(post_bp, url_prefix=f"{API_PREFIX}/posts")
    app.register_blueprint(check_bp, url_prefix=f"{API_PREFIX}/check")
    app.register_blueprint(bpmn_bp, url_prefix=f"{API_PREFIX}/processes")  
    app.register_blueprint(query_bp, url_prefix=f"{API_PREFIX}/query")  
    app.register_blueprint(health_bp, url_prefix=f"{API_PREFIX}")
