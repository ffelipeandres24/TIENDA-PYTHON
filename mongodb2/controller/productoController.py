from flask import Flask, request, render_template, redirect, session
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
import pymongo
import pymongo.errors
import os

# Crear un objeto de tipo Flask
app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = "./static/img"
app.secret_key = 'clave_secreta2'  # Necesario para las sesiones

# Conectar a la base de datos
miConexion = pymongo.MongoClient("mongodb+srv://AAndres:contrasena@cluster0.ihn0soq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
baseDatos = miConexion['TIENDA']
productos = baseDatos['productos']

@app.route('/')
def inicio():
    mensaje = ""
    listaProductos = []
    try:
        listaProductos = list(productos.find())  # Convertimos el cursor a una lista
        if len(listaProductos) == 0:
            mensaje = "No hay productos"
    except pymongo.errors.PyMongoError as error:
        mensaje = str(error)
    return render_template('index.html', productos=listaProductos, mensaje=mensaje)

@app.route('/agregar', methods=['POST', 'GET'])
def agregar():
    mensaje = ""  # Inicializar la variable
    producto = {}
    
    if request.method == 'POST':
        try:
            codigo = int(request.form['txtCodigo'])
            nombre = request.form['txtNombre']
            precio = int(request.form['txtPrecio'])
            categoria = request.form['cbCategoria']
            foto = request.files['fileFoto']
            nombreArchivo = secure_filename(foto.filename)
            
            # Verificar si la extensión es válida
            if '.' in nombreArchivo:
                extension = nombreArchivo.rsplit(".", 1)[1].lower()
                if extension not in ['jpg', 'jpeg', 'png']:
                    mensaje = "Extensión de archivo no permitida"
                    return render_template("frmAgregarProducto.html", mensaje=mensaje)
            else:
                mensaje = "Archivo sin extensión válida"
                return render_template("frmAgregarProducto.html", mensaje=mensaje)

            # Nombre de la foto se compone del código y la extensión
            nombreFoto = f"{codigo}.{extension}"
            producto = {
                "codigo": codigo,
                "nombre": nombre,
                "precio": precio,
                "categoria": categoria,
                "foto": nombreFoto
            }
            # Verificar si ya existe un producto con ese código
            existe = existeProducto(codigo)
            if not existe:
                resultado = productos.insert_one(producto)
                if resultado.acknowledged:
                    mensaje = "Producto agregado correctamente"
                    foto.save(os.path.join(app.config['UPLOAD_FOLDER'], nombreFoto))
                    return redirect('/listarProductos')
                else:
                    mensaje = "Error al agregar producto"
            else:
                mensaje = "El producto ya existe con ese código"
        except pymongo.errors.PyMongoError as error:
            mensaje = str(error)
    
    return render_template("frmAgregarProducto.html", mensaje=mensaje, producto=producto)

def existeProducto(codigo):
    try:
        consulta = {"codigo": codigo}
        producto = productos.find_one(consulta)
        return producto is not None
    except pymongo.errors.PyMongoError as error:
        print(str(error))
        return False

@app.route("/consultar/<string:id>", methods=["GET"])
def consultar(id):
    try:
        id = ObjectId(id)
        consulta = {"_id": id}
        producto = productos.find_one(consulta)
        return render_template("frmActualizarProducto.html", producto=producto)
    except pymongo.errors.PyMongoError as error:
        mensaje = str(error)
    return redirect("/listarProductos")

@app.route('/listarProductos')
def listarProductos():
    mensaje = ""
    listaProductos = []
    try:
        # Obtener todos los productos de la colección
        listaProductos = list(productos.find())
        if len(listaProductos) == 0:
            mensaje = "No hay productos disponibles"
    except pymongo.errors.PyMongoError as error:
        mensaje = str(error)

    # Renderizar la plantilla con la lista de productos y cualquier mensaje
    return render_template("listarProductos.html", productos=listaProductos, mensaje=mensaje)

@app.route("/actualizar", methods=["POST"])
def actualizarProducto():
    try:
        if request.method == "POST":
            # Recibir los valores de la vista en variables locales
            codigo = int(request.form["txtCodigo"])
            nombre = request.form["txtNombre"]
            precio = float(request.form["txtPrecio"])  # Cambiar a float por posibles precios decimales
            categoria = request.form["cbCategoria"]
            id = ObjectId(request.form["id"])
            
            # Verificar si se sube una nueva foto
            foto = request.files["fileFoto"]
            if foto and foto.filename != "":
                # Asegurar el nombre del archivo y procesar su extensión
                nombreArchivo = secure_filename(foto.filename)
                extension = nombreArchivo.rsplit(".", 1)[1].lower()  # Obtener la extensión del archivo
                nombreFoto = f"{codigo}.{extension}"
                producto = {
                    "codigo": codigo,
                    "nombre": nombre,
                    "precio": precio,
                    "categoria": categoria,
                    "foto": nombreFoto
                }
            else:
                # Si no hay nueva foto, no modificar ese campo
                producto = {
                    "codigo": codigo,
                    "nombre": nombre,
                    "precio": precio,
                    "categoria": categoria
                }
            
            # Verificar si el código ya existe en otro producto
            existe = productos.find_one({"codigo": codigo, "_id": {"$ne": id}})
            if existe:
                mensaje = "Ya existe un producto con ese código"
                return render_template("frmActualizarProducto.html", producto=producto, mensaje=mensaje)
            
            # Si no hay conflicto de código, actualizar el producto
            criterio = {"_id": id}
            consulta = {"$set": producto}
            resultado = productos.update_one(criterio, consulta)

            if resultado.acknowledged:
                if foto and foto.filename != "":
                    # Guardar la nueva foto si se subió
                    foto.save(os.path.join(app.config["UPLOAD_FOLDER"], nombreFoto))
                mensaje = "Producto actualizado correctamente"
                return redirect("/listarProductos")
    
    except pymongo.errors.PyMongoError as error:
        mensaje = f"Error al actualizar producto: {str(error)}"
        return render_template("frmActualizarProducto.html", producto=producto, mensaje=mensaje)
    
    return redirect("/listarProductos")

@app.route("/eliminar/<string:id>", methods=["GET"])
def eliminarProducto(id):
    try:
        id = ObjectId(id)  # Convertir el id a ObjectId
        criterio = {"_id": id}
        # Buscar el producto antes de eliminar
        producto = productos.find_one(criterio)
        if producto:
            # Eliminar el producto de la base de datos
            resultado = productos.delete_one(criterio)
            if resultado.deleted_count > 0:
                mensaje = "Producto eliminado correctamente"
                # Intentar eliminar la imagen del sistema de archivos
                if "foto" in producto:  # Verificar que haya una imagen asociada
                    foto_path = os.path.join(app.config['UPLOAD_FOLDER'], producto['foto'])
                    try:
                        os.remove(foto_path)  # Intentar eliminar la foto
                    except FileNotFoundError:
                        mensaje += ", pero la imagen no fue encontrada en el sistema"
            else:
                mensaje = "No se pudo eliminar el producto"
        else:
            mensaje = "Producto no encontrado"
    except pymongo.errors.PyMongoError as error:
        mensaje = f"Error al eliminar producto: {str(error)}"
    return redirect('/listarProductos')

if __name__ == "__main__":
    app.run(port=8000, debug=True)