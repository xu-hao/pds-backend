import connexion
from flask_cors import CORS

def create_app():
    app = connexion.FlaskApp(__name__, specification_dir='openapi/')
    app.add_api('my_api.yaml')
    CORS(app.app)
    return app
