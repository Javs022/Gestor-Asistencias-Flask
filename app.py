from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import re

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui' # Necesario para manejar sesiones y flash messages

# --- Configuración de la Base de Datos ---
CONFIG_BD = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  
    'database': 'desercion_db'
}

# Función para establecer la conexión con la base de datos.
def conectar_bd():
    """
    Crea y retorna una conexión a la base de datos utilizando los parámetros definidos en CONFIG_BD.
    Maneja posibles errores de conexión y muestra un mensaje al usuario si la conexión falla.
    :return: Objeto de conexión a la base de datos (mysql.connector.connection) si es exitosa, None en caso contrario.
    """
    try:
        conexion = mysql.connector.connect(**CONFIG_BD)
        return conexion
    except Error as e:
        print(f"Error de Conexión: {e}")
        return None

@app.route('/')
def index():
    """
    Ruta principal de la aplicación.
    Muestra la página de inicio (landing page).
    """
    return render_template('index.html')

@app.route('/opciones')
def opciones_cuenta():
    """
    Muestra la página con las opciones para iniciar sesión o registrarse.
    Si el usuario ya tiene una sesión activa, lo redirige automáticamente a su panel correspondiente.
    """
    # Si ya hay sesión, redirigir al dashboard correspondiente
    if 'user_id' in session:
        if session['user_type'] == 'student':
            return redirect(url_for('estudiante_dashboard'))
        else:
            return redirect(url_for('profesor_dashboard'))
    return render_template('opciones_cuenta.html')

@app.route('/logout')
def logout():
    """
    Cierra la sesión del usuario actual eliminando los datos de la sesión
    y lo redirige a la página principal.
    """
    session.clear()
    return redirect(url_for('index'))

# --- REGISTRO (Solo Estudiantes) ---
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    """
    Maneja el registro de nuevos estudiantes.
    Por GET: Muestra el formulario de registro.
    Por POST: Recibe los datos, los valida y crea un nuevo registro en la base de datos.
    """
    if request.method == 'POST':
        usuario = request.form['username']
        contrasena = request.form['password']
        nombre = request.form['nombre']
        apellidos = request.form['apellidos']
        matricula = request.form['matricula']
        correo = request.form['correo']

        if not all([usuario, contrasena, nombre, apellidos, matricula, correo]):
            flash("Todos los campos son obligatorios", "error")
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", correo):
            flash("Formato de correo institucional inválido", "error")
        else:
            conexion = conectar_bd()
            if conexion:
                try:
                    cursor = conexion.cursor()
                    consulta = "INSERT INTO Alumnos (usuario, contrasena, matricula, nombre, apellidos, correo) VALUES (%s, %s, %s, %s, %s, %s)"
                    cursor.execute(consulta, (usuario, contrasena, matricula, nombre, apellidos, correo))
                    conexion.commit()
                    flash("Cuenta creada exitosamente. Por favor inicia sesión.", "success")
                    return redirect(url_for('login', user_type='student'))
                except Error as e:
                    flash(f"Error al crear cuenta: {e}", "error")
                finally:
                    conexion.close()
            else:
                flash("Error: No se pudo conectar a la base de datos.", "error")
    return render_template('registro.html')

@app.route('/login/<user_type>', methods=['GET', 'POST'])
def login(user_type):
    """
    Maneja el inicio de sesión para estudiantes o profesores.
    :param user_type: Tipo de usuario que intenta ingresar ('student' o 'teacher').
    Valida las credenciales contra la base de datos y, si son correctas,
    inicia la sesión y redirige al panel correspondiente.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        tabla = "Alumnos" if user_type == "student" else "Profesores"
        campo_id = "id_alumno" if user_type == "student" else "id_profesor"

        conexion = conectar_bd()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                cursor.execute(f"SELECT * FROM {tabla} WHERE usuario = %s AND contrasena = %s", (username, password))
                usuario = cursor.fetchone()

                if usuario:
                    session['user_id'] = usuario[campo_id]
                    session['user_type'] = user_type
                    session['nombre'] = usuario['nombre']
                    session['apellidos'] = usuario['apellidos']
                    
                    if user_type == 'student':
                        return redirect(url_for('estudiante_dashboard'))
                    else:
                        return redirect(url_for('profesor_dashboard'))
                else:
                    flash("Usuario o contraseña incorrectos", "error")
            except Error as e:
                flash(f"Error de conexión: {e}", "error")
            finally:
                conexion.close()
        else:
            flash("Error: No se pudo conectar a la base de datos.", "error")

    return render_template('login.html', user_type=user_type)

# --- RUTAS DE PROFESOR ---

@app.route('/profesor/inicio')
def profesor_dashboard():
    """
    Muestra el panel principal (dashboard) del profesor.
    Requiere que el usuario tenga sesión iniciada como 'teacher'.
    """
    if 'user_id' not in session or session['user_type'] != 'teacher':
        return redirect(url_for('index'))
    return render_template('profesor/inicio.html')

@app.route('/profesor/alumnos')
def profesor_alumnos():
    """
    Muestra una lista de todos los alumnos que están marcados con riesgo de deserción
    (en_riesgo = 1) en la base de datos.
    """
    if 'user_id' not in session or session['user_type'] != 'teacher': return redirect(url_for('index'))
    conexion = conectar_bd()
    alumnos = []
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT nombre, apellidos, matricula, correo FROM Alumnos WHERE en_riesgo = 1")
        alumnos = cursor.fetchall()
        conexion.close()
    return render_template('profesor/alumnos_riesgo.html', alumnos=alumnos)

@app.route('/profesor/horarios', methods=['GET', 'POST'])
def profesor_horarios():
    """
    Permite al profesor ver y gestionar los horarios de las materias que imparte.
    Por POST: Actualiza el horario de una materia específica en la base de datos.
    Por GET: Muestra las materias asignadas al profesor logueado.
    """
    if 'user_id' not in session or session['user_type'] != 'teacher': return redirect(url_for('index'))
    conexion = conectar_bd()
    if request.method == 'POST':
        id_materia = request.form['id_materia']
        nuevo_horario = request.form['horario']
        try:
            cursor = conexion.cursor()
            cursor.execute("UPDATE Materias SET horario = %s WHERE id_materia = %s", (nuevo_horario, id_materia))
            conexion.commit()
            flash("Horario actualizado correctamente", "success")
        except Error as e:
            flash(f"Error al actualizar: {e}", "error")
    
    materias = []
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id_materia, nombre_materia, horario FROM Materias WHERE id_profesor = %s", (session['user_id'],))
        materias = cursor.fetchall()
        conexion.close()
    return render_template('profesor/gestionar_horarios.html', materias=materias)

@app.route('/profesor/asesorias')
def profesor_asesorias():
    """
    Muestra la lista de alumnos que se han registrado para recibir asesorías
    en cualquiera de las materias que imparte el profesor actual.
    """
    if 'user_id' not in session or session['user_type'] != 'teacher': return redirect(url_for('index'))
    conexion = conectar_bd()
    alumnos = []
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        consulta = '''
            SELECT a.id_alumno, a.nombre, a.apellidos, a.matricula, m.nombre_materia, ar.id_registro
            FROM Alumnos a
            JOIN asesorias_registradas ar ON a.id_alumno = ar.id_alumno
            JOIN Materias m ON ar.id_materia = m.id_materia
            WHERE m.id_profesor = %s
        '''
        cursor.execute(consulta, (session['user_id'],))
        alumnos = cursor.fetchall()
        conexion.close()
    return render_template('profesor/asesorias.html', alumnos=alumnos)

@app.route('/profesor/asistencia/<int:id_registro>/<int:estado>')
def marcar_asistencia(id_registro, estado):
    """
    Registra la asistencia (o falta) de un alumno a una asesoría.
    :param id_registro: ID de la asesoría registrada.
    :param estado: 1 si asistió, 0 si faltó.
    Si el alumno falta (estado 0), genera automáticamente una alerta para seguimiento.
    """
    if 'user_id' not in session or session['user_type'] != 'teacher': return redirect(url_for('index'))
    conexion = conectar_bd()
    if conexion:
        try:
            cursor = conexion.cursor()
            # Registrar asistencia
            cursor.execute("INSERT INTO asistencias (id_registro, fecha, presente) VALUES (%s, %s, %s)", 
                           (id_registro, datetime.now().date(), estado))
            
            # Si no asistió (estado 0), enviar alerta
            if estado == 0:
                # Necesitamos el id_alumno para la alerta
                cursor.execute("SELECT id_alumno FROM asesorias_registradas WHERE id_registro = %s", (id_registro,))
                res = cursor.fetchone()
                if res:
                    id_alumno = res[0]
                    mensaje = "El alumno no asistió a la asesoría programada. Se recomienda seguimiento."
                    cursor.execute("INSERT INTO alertas (id_alumno, id_profesor, mensaje, fecha_envio) VALUES (%s, %s, %s, %s)",
                                   (id_alumno, session['user_id'], mensaje, datetime.now()))
                    flash("Asistencia marcada como FALTA. Alerta enviada.", "warning")
            else:
                flash("Asistencia marcada como PRESENTE.", "success")
            
            conexion.commit()
        except Error as e:
            flash(f"Error al marcar asistencia: {e}", "error")
        finally:
            conexion.close()
    return redirect(url_for('profesor_asesorias'))

@app.route('/profesor/historial_asistencias')
def profesor_historial():
    """
    Muestra el historial completo de las asistencias registradas por el profesor
    para todas sus materias.
    """
    if 'user_id' not in session or session['user_type'] != 'teacher': return redirect(url_for('index'))
    conexion = conectar_bd()
    asistencias = []
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        consulta = '''
            SELECT a.nombre, a.apellidos, m.nombre_materia, asi.fecha, asi.presente
            FROM asistencias asi
            JOIN asesorias_registradas ar ON asi.id_registro = ar.id_registro
            JOIN Alumnos a ON ar.id_alumno = a.id_alumno
            JOIN Materias m ON ar.id_materia = m.id_materia
            WHERE m.id_profesor = %s
            ORDER BY asi.fecha DESC
        '''
        cursor.execute(consulta, (session['user_id'],))
        asistencias = cursor.fetchall()
        conexion.close()
    return render_template('profesor/historial.html', asistencias=asistencias)

# --- RUTAS DE ESTUDIANTE ---

@app.route('/estudiante/inicio')
def estudiante_dashboard():
    """
    Muestra el panel principal del estudiante, incluyendo un listado de las alertas
    o notificaciones que los profesores le han enviado (por inasistencias, etc.).
    """
    if 'user_id' not in session or session['user_type'] != 'student': return redirect(url_for('index'))
    conexion = conectar_bd()
    alertas = []
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        consulta = '''
            SELECT a.mensaje, a.fecha_envio, p.nombre, p.apellidos
            FROM alertas a
            JOIN Profesores p ON a.id_profesor = p.id_profesor
            WHERE a.id_alumno = %s
            ORDER BY a.fecha_envio DESC
        '''
        cursor.execute(consulta, (session['user_id'],))
        alertas = cursor.fetchall()
        conexion.close()
    return render_template('estudiante/inicio.html', alertas=alertas)

@app.route('/estudiante/materias')
def estudiante_materias():
    """
    Muestra la lista de todas las materias disponibles para solicitar asesorías,
    junto con el profesor que imparte cada materia y sus horarios.
    """
    if 'user_id' not in session or session['user_type'] != 'student': return redirect(url_for('index'))
    conexion = conectar_bd()
    materias = []
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT m.id_materia, m.nombre_materia, m.horario, p.nombre, p.apellidos FROM Materias m JOIN Profesores p ON m.id_profesor = p.id_profesor")
        materias = cursor.fetchall()
        conexion.close()
    return render_template('estudiante/materias.html', materias=materias)

@app.route('/estudiante/registrar/<int:id_materia>')
def registrar_asesoria(id_materia):
    """
    Permite a un estudiante registrarse para recibir asesoría de una materia.
    :param id_materia: El ID de la materia a la que desea inscribirse.
    Verifica primero que el alumno no esté ya registrado para evitar duplicados.
    """
    if 'user_id' not in session or session['user_type'] != 'student': return redirect(url_for('index'))
    conexion = conectar_bd()
    if conexion:
        try:
            cursor = conexion.cursor()
            # Verificar duplicados
            cursor.execute("SELECT * FROM asesorias_registradas WHERE id_alumno = %s AND id_materia = %s", (session['user_id'], id_materia))
            if cursor.fetchone():
                flash("Ya estás registrado en esta asesoría.", "warning")
            else:
                cursor.execute("INSERT INTO asesorias_registradas (id_alumno, id_materia) VALUES (%s, %s)", (session['user_id'], id_materia))
                conexion.commit()
                flash("Registro exitoso a la asesoría.", "success")
        except Error as e:
            flash(f"Error al registrar: {e}", "error")
        finally:
            conexion.close()
    return redirect(url_for('estudiante_mis_asesorias'))

@app.route('/estudiante/mis_asesorias')
def estudiante_mis_asesorias():
    """
    Muestra un listado con las asesorías a las cuales el estudiante actual se ha registrado.
    """
    if 'user_id' not in session or session['user_type'] != 'student': return redirect(url_for('index'))
    conexion = conectar_bd()
    asesorias = []
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        consulta = '''
            SELECT ar.id_registro, m.nombre_materia, p.nombre, p.apellidos, m.horario
            FROM asesorias_registradas ar
            JOIN Materias m ON ar.id_materia = m.id_materia
            JOIN Profesores p ON m.id_profesor = p.id_profesor
            WHERE ar.id_alumno = %s
        '''
        cursor.execute(consulta, (session['user_id'],))
        asesorias = cursor.fetchall()
        conexion.close()
    return render_template('estudiante/mis_asesorias.html', asesorias=asesorias)

@app.route('/estudiante/cancelar/<int:id_registro>')
def cancelar_asesoria(id_registro):
    """
    Permite a un estudiante cancelar su registro a una asesoría.
    :param id_registro: ID del registro de asesoría que se va a eliminar.
    """
    if 'user_id' not in session or session['user_type'] != 'student': return redirect(url_for('index'))
    conexion = conectar_bd()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM asistencias WHERE id_registro = %s", (id_registro,))
            cursor.execute("DELETE FROM asesorias_registradas WHERE id_registro = %s", (id_registro,))
            conexion.commit()
            flash("Registro cancelado correctamente.", "success")
        except Error as e:
            flash(f"Error al cancelar: {e}", "error")
        finally:
            conexion.close()
    return redirect(url_for('estudiante_mis_asesorias'))

if __name__ == '__main__':
    app.run(debug=True)

