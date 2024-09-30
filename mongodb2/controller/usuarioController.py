from appWeb import app, usuarios
from flask import render_template, request, redirect, session
import yagmail
import threading

# Función para enviar correo electrónico
def enviarCorreo(email, destinatario, asunto, mensaje):
    try:
        email.send(to=destinatario, subject=asunto, contents=mensaje)
        print("Correo enviado exitosamente.")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")

# Ruta para el login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("frmLogin.html")
    else:
        # Obtener los datos del formulario
        username = request.form['txtUsername']
        password = request.form['txtPassword']
        
        # Crear diccionario con las credenciales ingresadas
        usuario = {
            "username": username,
            "password": password
        }
        
        # Verificar si el usuario existe en la base de datos
        userExiste = usuarios.find_one({"username": username})  # Asegúrate de que la búsqueda sea correcta

        if userExiste and check_password(userExiste['password'], password):  # Verifica la contraseña correctamente
            # Si el usuario existe, crear una sesión
            session['user'] = usuario
            
            # Configurar el envío de correo con yagmail
            try:
                email = yagmail.SMTP("ffelipeandres24@gmail.com", open(".password", "r", encoding="UTF-8").read())
                
                # Crear asunto y mensaje
                asunto = "Reporte ingreso al sistema de usuario"
                mensaje = f"Se informa que el usuario {username} ha ingresado al sistema"
                destinatario = "ffelipeandres24@gmail.com"  # Dirección de correo válida
                
                # Iniciar un hilo para enviar el correo de forma asíncrona
                thread = threading.Thread(target=enviarCorreo, args=(email, destinatario, asunto, mensaje))
                thread.start()
                
                # Redirigir a la lista de productos
                return redirect('/listarProductos')
            except Exception as e:
                print(f"Error al configurar el correo: {e}")
                mensaje = "Error al enviar el correo de notificación"
                return render_template("frmLogin.html", mensaje=mensaje)
        else:
            # Si las credenciales no son válidas, mostrar un mensaje de error
            mensaje = "Credenciales de ingreso no válidas"
            return render_template("frmLogin.html", mensaje=mensaje)

# Ruta para cerrar la sesión
@app.route("/salir")
def salir():
    # Eliminar la variable de sesión 'user'
    session.pop('user', None)
    session.clear()  # Limpiar todas las variables de sesión
    # Redirigir al formulario de login con mensaje de confirmación
    return render_template("frmLogin.html", mensaje="Ha cerrado la sesión")

# Función para verificar la contraseña (suponiendo que uses bcrypt o similar)
def check_password(stored_password, provided_password):
    from werkzeug.security import check_password_hash
    return check_password_hash(stored_password, provided_password)