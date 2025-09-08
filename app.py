from flask import Flask
from config import Config
from models import init_db
from routes.auth import auth_bp
from routes.images import image_bp
import os

app = Flask(__name__)
app.config.from_object(Config)

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Init database
init_db(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(image_bp)

if __name__ == '__main__':
    app.run(debug=True)
