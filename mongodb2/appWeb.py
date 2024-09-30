from flask import Flask
import pymongo
# Crear un objeto de tipo Flask
app = Flask(__name__)

# Secret Key
app.secret_key = 'clave_secreta2'  # Clave secreta para las sesiones

app.config["UPLOAD_FOLDER"]="./static/img"

miConexion = pymongo.MongoClient("mongodb+srv://AAndres:contrasena@cluster0.ihn0soq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

# Crear una base de datos
baseDatos = miConexion['TIENDA']
#  Crear una colección Productos
productos = baseDatos['productos']
# Crear una colección Usuarios
usuarios = baseDatos['Usuarios']

if __name__=="__main__":
    from controller.productoController import *
    from controller.usuarioController import *
    app.run(port=8000, debug=True)