import os

from dotenv import load_dotenv
from flask import Flask
from service import usuarios_bp
from service import mensajes_bp

load_dotenv()

app = Flask(__name__)

# Registrar los microservicios como Blueprints
app.register_blueprint(usuarios_bp, url_prefix="/usuarios")
app.register_blueprint(mensajes_bp, url_prefix="/mensajes")

@app.route("/")
def main_route():
    return f"<a href='http://127.0.0.1:{os.getenv('SERVICE_PORT')}/usuarios'>Ver usuarios</a>"

# Ejecutar la aplicación Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.getenv("SERVICE_PORT"))