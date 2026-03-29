import tkinter as tk
from tkinter import ttk, messagebox, font
import re
from datetime import datetime
import mysql.connector
from mysql.connector import Error

# --- Configuración de la Base de Datos ---
# Diccionario que contiene los parámetros de conexión a la base de datos MySQL.
# Es importante que estos datos coincidan con tu configuración local de MySQL.
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
        messagebox.showerror("Error de Conexión", f"No se pudo conectar a la base de datos: {e}")
        return None

class GestorAsistenciasApp:
    """
    Clase principal de la aplicación del Gestor de asistencias a asesorias.
    Gestiona la interfaz de usuario, la navegación entre pantallas y la interacción con la base de datos.
    """
    def __init__(self, ventana_principal):
        """
        Constructor de la clase GestorAsistenciasApp.
        Inicializa la ventana principal de Tkinter y configura las propiedades básicas de la aplicación.
        :param ventana_principal: El objeto Tkinter Tk que representa la ventana raíz de la aplicación.
        """
        self.ventana_principal = ventana_principal
        self.ventana_principal.title("Gestor de asistencias y asesorias")  # Establece el título de la ventana
        self.ventana_principal.geometry("1000x700")  # Define el tamaño inicial de la ventana (ancho x alto)
        self.ventana_principal.configure(bg="#009182")  # Configura el color de fondo de la ventana principal
        self.ventana_principal.resizable(False, False)  # Impide que el usuario redimensione la ventana (ancho, alto)

        # Configuración de colores: Define una paleta de colores para usar en toda la aplicación.
        self.color_primario = "#2c3e50"
        self.color_secundario = "#3498db"
        self.color_acento = "#e74c3c"
        self.color_claro = "#ecf0f1"
        self.color_oscuro = "#34495e"
        self.color_resaltado = "#2980b9"

        # Fuentes: Define diferentes estilos de fuente para mantener la coherencia visual.
        self.fuente_titulo = ("Arial", 24, "bold")
        self.fuente_subtitulo = ("Arial", 18, "bold")
        self.fuente_encabezado = ("Arial", 16, "bold")
        self.fuente_cuerpo = ("Arial", 12)
        self.fuente_boton = ("Arial", 12, "bold")
        self.fuente_menu = ("Arial", 11)

        self.configurar_estilos()  # Llama al método para aplicar los estilos a los widgets ttk

        # Estado de la aplicación: Variables para mantener el estado del usuario actual.
        self._tipo_usuario_actual = None  # 'student' o 'teacher'
        self._id_usuario_actual = None    # ID del usuario logueado en la BD
        self._info_usuario_actual = {}    # Diccionario con la información completa del usuario
        self._materia_actual = None       # Materia seleccionada por el estudiante para asesoría
        self._id_estudiante_actual = None # ID del estudiante seleccionado por el profesor para asistencia

        self.mostrar_pantalla_bienvenida()  # Inicia la aplicación mostrando la pantalla de bienvenida

 
    def get_tipo_usuario_actual(self):
        return self._tipo_usuario_actual

    def set_tipo_usuario_actual(self, tipo):
        self._tipo_usuario_actual = tipo

    def get_id_usuario_actual(self):
        return self._id_usuario_actual

    def set_id_usuario_actual(self, id_usuario):
        self._id_usuario_actual = id_usuario

    def get_info_usuario_actual(self):
        return self._info_usuario_actual

    def set_info_usuario_actual(self, info):
        self._info_usuario_actual = info

    def get_materia_actual(self):
        return self._materia_actual

    def set_materia_actual(self, materia):
        self._materia_actual = materia

    def get_id_estudiante_actual(self):
        return self._id_estudiante_actual

    def set_id_estudiante_actual(self, id_estudiante):
        self._id_estudiante_actual = id_estudiante

    def configurar_estilos(self):
        """
        Configura los estilos visuales para los widgets ttk (Themed Tkinter).
        Esto permite una apariencia más moderna y consistente en la aplicación.
        """
        estilo = ttk.Style()
        estilo.theme_use("clam")  

        # Estilos para Frames (contenedores)
        estilo.configure("Main.TFrame", background="#D9D9D9")  # Fondo principal de las pantallas
        estilo.configure("Nav.TFrame", background="#009182")  # Fondo de la barra de navegación/encabezado
        estilo.configure("Sidebar.TFrame", background="#009182")  # Fondo del menú lateral

        # Estilos para Labels (etiquetas de texto)
        estilo.configure("Nav.TLabel", background="#009182", foreground="white", font=self.fuente_encabezado)
        estilo.configure("Sidebar.TLabel", background="#009182", foreground="white", font=self.fuente_cuerpo)
        # Las siguientes etiquetas tienen fondo blanco para asegurar visibilidad sobre el fondo gris principal
        estilo.configure("Title.TLabel", font=self.fuente_titulo, foreground="#000000", background="#d9d9d9")
        estilo.configure("Subtitle.TLabel", font=self.fuente_subtitulo, foreground="#000000", background="#d9d9d9")
        estilo.configure("Header.TLabel", font=self.fuente_encabezado, foreground="#000000", background="#d9d9d9")
        estilo.configure("Body.TLabel", font=self.fuente_cuerpo, foreground="#000000", background="#d9d9d9")
        estilo.configure("Footer.TLabel", font=("Arial", 10), foreground="#d9d9d9", background="#d9d9d9")

        # Estilos para Buttons (botones)
        estilo.configure("TButton", font=self.fuente_boton, padding=8)  # Estilo base para todos los botones
        estilo.configure("Primary.TButton", background="#D9D9D9", foreground="#000000") # Botones principales
        estilo.configure("Accent.TButton", background=self.color_acento, foreground="white") # Botones de acción destacada
        estilo.configure("Success.TButton", background="#27ae60", foreground="white") # Botones de éxito (ej. "Sí asistió")
        estilo.configure("Danger.TButton", background="#e74c3c", foreground="white") # Botones de peligro (ej. "No asistió", "Cerrar Sesión")

        # Mapeo de estilos para botones del menú lateral (cambio de color al pasar el ratón)
        estilo.configure("Sidebar.TButton", background="#009182", foreground="white", font=self.fuente_menu, borderwidth=0, width=15, anchor="w")
        estilo.map("Sidebar.TButton", background=[("active", "#007a6e")]) # Color más oscuro al pasar el ratón

        # Estilos para "Tarjetas" (frames con borde para agrupar contenido)
        estilo.configure("Card.TFrame", background="#d9d9d9", borderwidth=1, relief="solid")
        estilo.configure("SubjectCard.TFrame", background="#d9d9d9", borderwidth=1, relief="solid", padding=20)
        estilo.configure("StudentCard.TFrame", background="#d9d9d9", borderwidth=1, relief="solid", padding=15)

    def limpiar_ventana(self):
        """
        Elimina todos los widgets (elementos de la interfaz) de la ventana principal.
        Esto se usa antes de cargar una nueva pantalla para asegurar que la interfaz esté limpia.
        """
        for widget in self.ventana_principal.winfo_children():
            widget.destroy()

    def cerrar_sesion(self):
        """
        Reinicia el estado de la sesión del usuario y redirige a la pantalla de bienvenida.
        """
        self.set_tipo_usuario_actual(None)
        self.set_id_usuario_actual(None)
        self.set_info_usuario_actual({})
        self.set_materia_actual(None)
        self.set_id_estudiante_actual(None)
        self.mostrar_pantalla_bienvenida()

    def mostrar_pantalla_bienvenida(self):
        """
        Muestra la pantalla inicial de bienvenida de la aplicación.
        """
        self.limpiar_ventana()
        marco_principal = ttk.Frame(self.ventana_principal, style="Main.TFrame")
        marco_principal.pack(fill="both", expand=True, padx=50, pady=50)
        ttk.Label(marco_principal, text="Bienvenido a nuestro", style="Body.TLabel").pack(pady=(80, 0))
        ttk.Label(marco_principal, text="Gestor de asistencias a asesorias", style="Title.TLabel").pack(pady=(0, 60))
        ttk.Button(marco_principal, text="Entrar", command=self.mostrar_opciones_cuenta, style="Primary.TButton").pack(pady=(30, 100), ipadx=30, ipady=10)
        ttk.Label(marco_principal, text="Universidad Tecnológica de Puebla - 2025", style="Footer.TLabel").pack(side="bottom", pady=20)

    def mostrar_opciones_cuenta(self):
        """
        Muestra la pantalla donde el usuario puede elegir entre crear una cuenta o iniciar sesión.
        """
        self.limpiar_ventana()
        marco_principal = ttk.Frame(self.ventana_principal, style="Main.TFrame")
        marco_principal.pack(fill="both", expand=True, padx=50, pady=50)
        ttk.Label(marco_principal, text="¿No tienes cuenta aún?", style="Subtitle.TLabel").pack(pady=(40, 10))
        ttk.Button(marco_principal, text="Crea tu cuenta", command=self.mostrar_seleccion_tipo_usuario, style="TButton").pack(pady=20, ipadx=10, ipady=5)
        ttk.Separator(marco_principal, orient="horizontal").pack(fill="x", pady=20, padx=50)
        ttk.Label(marco_principal, text="¿Tienes una cuenta?", style="Subtitle.TLabel").pack(pady=10)
        marco_botones = ttk.Frame(marco_principal, style="Main.TFrame")
        marco_botones.pack(pady=30)
        ttk.Button(marco_botones, text="Estudiante - Iniciar Sesión", command=lambda: self.mostrar_pantalla_login("student"), style="Primary.TButton").grid(row=0, column=0, padx=15, ipadx=10, ipady=5)
        ttk.Button(marco_botones, text="Profesor - Iniciar Sesión", command=lambda: self.mostrar_pantalla_login("teacher"), style="Primary.TButton").grid(row=0, column=1, padx=15, ipadx=10, ipady=5)

    def mostrar_seleccion_tipo_usuario(self):
        """
        Muestra la pantalla para seleccionar el tipo de usuario al crear una cuenta (solo estudiante).
        """
        self.limpiar_ventana()
        marco_principal = ttk.Frame(self.ventana_principal, style="Main.TFrame")
        marco_principal.pack(fill="both", expand=True, padx=50, pady=50)
        ttk.Label(marco_principal, text="Eres", style="Subtitle.TLabel").pack(pady=(50, 30))
        marco_botones = ttk.Frame(marco_principal, style="Main.TFrame")
        marco_botones.pack(pady=20)
        ttk.Button(marco_botones, text="Estudiante", command=lambda: self.mostrar_pantalla_registro("student"), style="Primary.TButton").grid(row=0, column=0, padx=20, ipadx=20, ipady=10)
        # Eliminado el botón de Profesor para crear cuenta, ya que solo se permite crear cuentas de estudiante.
        ttk.Button(marco_principal, text="Regresar", command=self.mostrar_opciones_cuenta, style="TButton").pack(pady=20, ipadx=10, ipady=5)

    def mostrar_pantalla_registro(self, tipo_usuario):
        """
        Muestra la pantalla de registro de usuario.
        :param tipo_usuario: El tipo de usuario a registrar ('student' o 'teacher').
                             Actualmente, solo se permite el registro de 'student'.
        """
        self.limpiar_ventana()
        self.set_tipo_usuario_actual(tipo_usuario)
        marco_principal = ttk.Frame(self.ventana_principal, style="Main.TFrame")
        marco_principal.pack(fill="both", expand=True, padx=50, pady=30)
        titulo = "Crear Cuenta - Estudiante" # Solo se permite crear cuentas de estudiante
        ttk.Label(marco_principal, text=titulo, style="Subtitle.TLabel").pack(pady=(20, 30))
        marco_formulario = ttk.Frame(marco_principal, style="Card.TFrame", padding=20)
        marco_formulario.pack(pady=10, padx=100, fill="x")

        campos = ["Usuario", "Contraseña", "Nombre", "Apellidos"]
        # Solo campos para estudiante
        campos.extend(["Matrícula", "Correo Inst."])
        
        self.entradas = {}
        for i, campo in enumerate(campos):
            ttk.Label(marco_formulario, text=f"{campo}:", style="Body.TLabel").grid(row=i, column=0, sticky="w", pady=8, padx=(0, 10))
            entrada = ttk.Entry(marco_formulario, width=30, font=self.fuente_cuerpo)
            if "Contraseña" in campo:
                entrada.config(show="*")  # Oculta la contraseña
            entrada.grid(row=i, column=1, sticky="ew", pady=8)
            self.entradas[campo] = entrada
        
        ttk.Button(marco_principal, text="Crear Cuenta", command=self.crear_cuenta, style="Accent.TButton").pack(pady=30, ipadx=20, ipady=8)
        ttk.Button(marco_principal, text="Regresar", command=self.mostrar_opciones_cuenta, style="TButton").pack(pady=10, ipadx=10, ipady=5)

    def crear_cuenta(self):
        """
        Procesa los datos del formulario de registro y crea una nueva cuenta de estudiante en la base de datos.
        Realiza validaciones básicas y muestra mensajes de éxito o error.
        """
        datos = {campo: entrada.get() for campo, entrada in self.entradas.items()}
        if any(not valor for valor in datos.values()):
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        # Lógica simplificada para solo crear cuentas de estudiante
        if not re.match(r"[^@]+@[^@]+\.[^@]+", datos["Correo Inst."]):
            messagebox.showerror("Error", "Formato de correo institucional inválido")
            return
        
        consulta = "INSERT INTO Alumnos (usuario, contrasena, matricula, nombre, apellidos, correo) VALUES (%s, %s, %s, %s, %s, %s)"
        parametros = (datos["Usuario"], datos["Contraseña"], datos["Matrícula"], datos["Nombre"], datos["Apellidos"], datos["Correo Inst."])

        conexion = conectar_bd()
        if not conexion: return
        try:
            cursor = conexion.cursor()
            cursor.execute(consulta, parametros)
            conexion.commit()
            messagebox.showinfo("Éxito", f"Cuenta de estudiante creada exitosamente")
            self.mostrar_pantalla_login(self.get_tipo_usuario_actual()) # Redirige a la pantalla de login
        except Error as e:
            messagebox.showerror("Error", f"No se pudo crear la cuenta: {e}")
        finally:
            if conexion.is_connected():
                conexion.close()

    def mostrar_pantalla_login(self, tipo_usuario):
        """
        Muestra la pantalla de inicio de sesión para un tipo de usuario específico.
        :param tipo_usuario: El tipo de usuario que intenta iniciar sesión ('student' o 'teacher').
        """
        self.limpiar_ventana()
        self.set_tipo_usuario_actual(tipo_usuario)
        marco_principal = ttk.Frame(self.ventana_principal, style="Main.TFrame")
        marco_principal.pack(fill="both", expand=True, padx=50, pady=50)
        titulo = f"Iniciar Sesión - {'Estudiante' if tipo_usuario == 'student' else 'Profesor'}"
        ttk.Label(marco_principal, text=titulo, style="Subtitle.TLabel").pack(pady=(30, 40))
        marco_formulario = ttk.Frame(marco_principal, style="Card.TFrame", padding=20)
        marco_formulario.pack(pady=10, padx=150, fill="x")

        ttk.Label(marco_formulario, text="Usuario:", style="Body.TLabel").grid(row=0, column=0, sticky="w", pady=8, padx=(0, 10))
        self.entrada_usuario = ttk.Entry(marco_formulario, width=25, font=self.fuente_cuerpo)
        self.entrada_usuario.grid(row=0, column=1, sticky="ew", pady=8)
        ttk.Label(marco_formulario, text="Contraseña:", style="Body.TLabel").grid(row=1, column=0, sticky="w", pady=8, padx=(0, 10))
        self.entrada_contrasena = ttk.Entry(marco_formulario, width=25, show="*", font=self.fuente_cuerpo)
        self.entrada_contrasena.grid(row=1, column=1, sticky="ew", pady=8)
        
        ttk.Button(marco_principal, text="Entrar", command=self.autenticar, style="Accent.TButton").pack(pady=40, ipadx=30, ipady=8)
        ttk.Button(marco_principal, text="Regresar", command=self.mostrar_opciones_cuenta, style="TButton").pack(pady=10, ipadx=10, ipady=5)

    def autenticar(self):
        """
        Verifica las credenciales del usuario (estudiante o profesor) contra la base de datos.
        Si las credenciales son correctas, redirige al usuario a su pantalla de inicio correspondiente.
        """
        nombre_usuario = self.entrada_usuario.get()
        contrasena = self.entrada_contrasena.get()
        if not nombre_usuario or not contrasena:
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        tabla = "Alumnos" if self.get_tipo_usuario_actual() == "student" else "Profesores"
        campo_id = "id_alumno" if self.get_tipo_usuario_actual() == "student" else "id_profesor"
        
        conexion = conectar_bd()
        if not conexion: return
        try:
            cursor = conexion.cursor(dictionary=True) # Retorna resultados como diccionarios
            cursor.execute(f"SELECT * FROM {tabla} WHERE usuario = %s AND contrasena = %s", (nombre_usuario, contrasena))
            usuario = cursor.fetchone() # Obtiene la primera fila que coincide

            if usuario:
                self.set_id_usuario_actual(usuario[campo_id])
                self.set_info_usuario_actual(usuario)
                if self.get_tipo_usuario_actual() == "student":
                    self.mostrar_inicio_estudiante()
                else:
                    self.mostrar_inicio_profesor()
            else:
                messagebox.showerror("Error", "Usuario o contraseña incorrectos")
        except Error as e:
            messagebox.showerror("Error", f"Error de autenticación: {e}")
        finally:
            if conexion.is_connected():
                conexion.close()

    # --- VISTAS DE PROFESOR ---
    def mostrar_inicio_profesor(self):
        """
        Muestra la pantalla de inicio para el profesor.
        """
        self.limpiar_ventana()
        self.crear_diseno_profesor("Inicio")

    def crear_diseno_profesor(self, pagina_actual):
        """
        Crea el diseño general de la interfaz del profesor, incluyendo el encabezado,
        el menú lateral y el área de contenido principal.
        :param pagina_actual: La página que se debe mostrar en el área de contenido.
        """
        # Encabezado: Contiene el título de la aplicación y el botón de cerrar sesión.
        marco_encabezado = ttk.Frame(self.ventana_principal, style="Nav.TFrame", padding=10)
        marco_encabezado.pack(fill="x")
        ttk.Label(marco_encabezado, text="Gestor de asistencias a asesorias", style="Nav.TLabel").pack(side="left", padx=20)
        ttk.Button(marco_encabezado, text="Cerrar Sesión", command=self.cerrar_sesion, style="Danger.TButton").pack(side="right", padx=20)
        
        # Contenedor principal: Contiene el menú lateral y el área de contenido.
        marco_principal = ttk.Frame(self.ventana_principal, style="Content.TFrame")
        marco_principal.pack(fill="both", expand=True)

        # Menú lateral (Sidebar): Contiene los botones de navegación para el profesor.
        marco_lateral = ttk.Frame(marco_principal, style="Sidebar.TFrame", width=200)
        marco_lateral.pack(side="left", fill="y")
        
        elementos_menu = ["Inicio", "Alumnos", "Asesoría", "Asistencia", "Gestionar Horarios"]
        for elemento in elementos_menu:
            boton = ttk.Button(marco_lateral, text=elemento, command=lambda i=elemento: self.gestionar_menu_profesor(i), style="Sidebar.TButton")
            boton.pack(fill="x", pady=5, padx=10, ipady=5)

        # Área de contenido: Donde se cargan las diferentes vistas según la selección del menú.
        self.marco_contenido = ttk.Frame(marco_principal, style="Content.TFrame", padding=30)
        self.marco_contenido.pack(side="right", fill="both", expand=True)
        
        self.actualizar_contenido_profesor(pagina_actual) # Carga el contenido inicial de la página

    def gestionar_menu_profesor(self, opcion):
        """
        Maneja la selección de opciones en el menú lateral del profesor.
        :param opcion: La opción de menú seleccionada (ej. "Inicio", "Alumnos").
        """
        self.actualizar_contenido_profesor(opcion)

    def actualizar_contenido_profesor(self, opcion):
        """
        Actualiza el contenido del área principal del profesor según la opción seleccionada.
        :param opcion: La opción de menú que determina qué contenido mostrar.
        """
        for widget in self.marco_contenido.winfo_children():
            widget.destroy() # Limpia el área de contenido actual

        if opcion == "Inicio":
            ttk.Label(self.marco_contenido, text="Bienvenido", style="Subtitle.TLabel").pack(pady=(30, 20))
            ttk.Label(self.marco_contenido, text="La educación es tu mejor herramienta, sigue adelante.", wraplength=500, justify="center", style="Body.TLabel").pack(pady=20)
        elif opcion == "Alumnos":
            self.mostrar_alumnos_profesor()
        elif opcion == "Asesoría":
            self.mostrar_asesoria_profesor()
        elif opcion == "Asistencia":
            self.mostrar_asistencias_profesor()
        elif opcion == "Gestionar Horarios":
            self.mostrar_gestion_horarios_profesor()
        
        ttk.Label(self.marco_contenido, text="Universidad Tecnológica de Puebla - 2025", style="Footer.TLabel").pack(side="bottom", pady=30)

    def mostrar_gestion_horarios_profesor(self):
        """
        Muestra la interfaz para que el profesor gestione los horarios de sus materias.
        Carga las materias asignadas al profesor desde la base de datos.
        """
        ttk.Label(self.marco_contenido, text="Gestionar Horarios de Asesoría", style="Subtitle.TLabel").pack(pady=20)
        conexion = conectar_bd()
        if not conexion: return
        try:
            cursor = conexion.cursor(dictionary=True)
            # Consulta las materias que imparte el profesor actual
            consulta = "SELECT id_materia, nombre_materia, horario FROM Materias WHERE id_profesor = %s"
            cursor.execute(consulta, (self.get_id_usuario_actual(),))
            materias = cursor.fetchall()

            if not materias:
                ttk.Label(self.marco_contenido, text="No tienes materias asignadas.", style="Body.TLabel").pack(pady=20)
                return

            # Muestra cada materia en una "tarjeta" con opción para editar el horario
            for i, materia in enumerate(materias):
                materia_frame = ttk.Frame(self.marco_contenido, style="Card.TFrame", padding=15)
                materia_frame.pack(fill="x", pady=5, padx=20)

                ttk.Label(materia_frame, text=f"Materia: {materia['nombre_materia']}", style="Header.TLabel").pack(anchor="w")
                ttk.Label(materia_frame, text=f"Horario Actual: {materia['horario'] or 'No definido'}", style="Body.TLabel").pack(anchor="w")
                
                ttk.Button(materia_frame, text="Editar Horario", command=lambda m=materia: self.mostrar_editar_horario_materia(m), style="Primary.TButton").pack(pady=5)
        except Error as e:
            messagebox.showerror("Error", f"No se pudieron cargar las materias: {e}")
        finally:
            if conexion.is_connected():
                conexion.close()

    def mostrar_editar_horario_materia(self, materia):
        """
        Muestra la interfaz para editar el horario de una materia específica.
        :param materia: Diccionario con la información de la materia a editar.
        """
        self.limpiar_ventana()
        self.crear_diseno_profesor("Gestionar Horarios") # Mantiene el menú lateral del profesor

        # Limpia solo el área de contenido para cargar el formulario de edición
        for widget in self.marco_contenido.winfo_children():
            widget.destroy()

        ttk.Label(self.marco_contenido, text=f"Editar Horario para: {materia['nombre_materia']}", style="Subtitle.TLabel").pack(pady=20)

        ttk.Label(self.marco_contenido, text="Nuevo Horario:", style="Body.TLabel").pack(pady=5)
        self.entrada_nuevo_horario = ttk.Entry(self.marco_contenido, width=50, font=self.fuente_cuerpo)
        self.entrada_nuevo_horario.insert(0, materia['horario'] or '') # Muestra el horario actual
        self.entrada_nuevo_horario.pack(pady=5)

        ttk.Button(self.marco_contenido, text="Guardar Horario", command=lambda: self.guardar_horario_materia(materia['id_materia'], self.entrada_nuevo_horario.get()), style="Success.TButton").pack(pady=20)
        ttk.Button(self.marco_contenido, text="Cancelar", command=self.mostrar_gestion_horarios_profesor, style="Danger.TButton").pack(pady=5)

    def guardar_horario_materia(self, id_materia, nuevo_horario):
        """
        Actualiza el horario de una materia en la base de datos.
        :param id_materia: ID de la materia a actualizar.
        :param nuevo_horario: El nuevo horario a establecer.
        """
        conexion = conectar_bd()
        if not conexion: return
        try:
            cursor = conexion.cursor()
            consulta = "UPDATE Materias SET horario = %s WHERE id_materia = %s"
            cursor.execute(consulta, (nuevo_horario, id_materia))
            conexion.commit()
            messagebox.showinfo("Éxito", "Horario actualizado correctamente.")
            self.mostrar_gestion_horarios_profesor() # Vuelve a la lista de horarios después de guardar
        except Error as e:
            messagebox.showerror("Error", f"No se pudo actualizar el horario: {e}")
        finally:
            if conexion.is_connected():
                conexion.close()

    def mostrar_asistencias_profesor(self):
        """
        Muestra los registros de asistencia de los alumnos para las materias del profesor actual.
        Los datos se presentan en un Treeview (tabla).
        """
        ttk.Label(self.marco_contenido, text="Registros de Asistencia", style="Subtitle.TLabel").pack(pady=20)
        conexion = conectar_bd()
        if not conexion: return
        try:
            cursor = conexion.cursor(dictionary=True)
            consulta = '''
                SELECT
                    a.nombre, a.apellidos, m.nombre_materia, asi.fecha, asi.presente
                FROM asistencias asi
                JOIN asesorias_registradas ar ON asi.id_registro = ar.id_registro
                JOIN Alumnos a ON ar.id_alumno = a.id_alumno
                JOIN Materias m ON ar.id_materia = m.id_materia
                WHERE m.id_profesor = %s
                ORDER BY asi.fecha DESC
            '''
            cursor.execute(consulta, (self.get_id_usuario_actual(),))
            asistencias = cursor.fetchall()

            if not asistencias:
                ttk.Label(self.marco_contenido, text="No hay registros de asistencia.", style="Body.TLabel").pack(pady=20)
                return

            # Crear Treeview para mostrar asistencias
            marco_tabla = ttk.Frame(self.marco_contenido)
            marco_tabla.pack(fill="both", expand=True, pady=10)

            tabla = ttk.Treeview(marco_tabla, columns=("alumno", "materia", "fecha", "estado"), show="headings")
            tabla.heading("alumno", text="Alumno")
            tabla.heading("materia", text="Materia")
            tabla.heading("fecha", text="Fecha")
            tabla.heading("estado", text="Estado")

            tabla.column("alumno", width=200)
            tabla.column("materia", width=200)
            tabla.column("fecha", width=100)
            tabla.column("estado", width=100)

            for registro in asistencias:
                nombre_completo = f"{registro['nombre']} {registro['apellidos']}"
                estado = "Presente" if registro['presente'] else "Ausente"
                tabla.insert("", "end", values=(nombre_completo, registro['nombre_materia'], registro['fecha'], estado))

            tabla.pack(fill="both", expand=True)

        except Error as e:
            messagebox.showerror("Error", f"No se pudieron cargar las asistencias: {e}")
        finally:
            if conexion.is_connected():
                conexion.close()

    def mostrar_alumnos_profesor(self):
        """
        Muestra una lista de alumnos en riesgo de deserción para el profesor actual.
        """
        ttk.Label(self.marco_contenido, text="Alumnos en riesgo de deserción", style="Subtitle.TLabel").pack(pady=20)
        conexion = conectar_bd()
        if not conexion: return
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT nombre, apellidos, matricula, correo FROM Alumnos WHERE en_riesgo = 1")
            alumnos = cursor.fetchall()
            
            marco_alumnos = ttk.Frame(self.marco_contenido, style="Content.TFrame")
            marco_alumnos.pack(fill="both", expand=True, padx=50, pady=10)

            for i, alumno in enumerate(alumnos):
                tarjeta_alumno = ttk.Frame(marco_alumnos, style="StudentCard.TFrame")
                tarjeta_alumno.grid(row=i, column=0, sticky="ew", pady=10, padx=20)
                ttk.Label(tarjeta_alumno, text=f"{alumno['nombre']} {alumno['apellidos']}", style="Header.TLabel").pack(anchor="w", pady=(0, 5))
                ttk.Label(tarjeta_alumno, text=f"Matrícula: {alumno['matricula']}", style="Body.TLabel").pack(anchor="w")
                ttk.Label(tarjeta_alumno, text=f"Correo: {alumno['correo']}", style="Body.TLabel").pack(anchor="w")
        except Error as e:
            messagebox.showerror("Error", f"No se pudieron cargar los alumnos: {e}")
        finally:
            if conexion.is_connected():
                conexion.close()

    def mostrar_asesoria_profesor(self):
        """
        Muestra una lista de alumnos registrados para asesorías con el profesor actual.
        Permite al profesor marcar la asistencia de estos alumnos.
        """
        ttk.Label(self.marco_contenido, text="Alumnos registrados a la asesoría", style="Subtitle.TLabel").pack(pady=20)
        conexion = conectar_bd()
        if not conexion: return
        try:
            cursor = conexion.cursor(dictionary=True)
            consulta = '''
                SELECT a.id_alumno, a.nombre, a.apellidos, a.matricula, a.correo, ar.id_registro
                FROM Alumnos a
                JOIN asesorias_registradas ar ON a.id_alumno = ar.id_alumno
                JOIN Materias m ON ar.id_materia = m.id_materia
                WHERE m.id_profesor = %s
            '''
            cursor.execute(consulta, (self.get_id_usuario_actual(),))
            alumnos = cursor.fetchall()

            marco_alumnos = ttk.Frame(self.marco_contenido, style="Content.TFrame")
            marco_alumnos.pack(fill="both", expand=True, padx=50, pady=10)

            if not alumnos:
                ttk.Label(marco_alumnos, text="No hay alumnos registrados para tus materias.", style="Body.TLabel").pack(pady=20)
                return

            for i, alumno in enumerate(alumnos):
                tarjeta_alumno = ttk.Frame(marco_alumnos, style="StudentCard.TFrame")
                tarjeta_alumno.grid(row=i, column=0, sticky="ew", pady=10, padx=20)
                ttk.Label(tarjeta_alumno, text=f"{alumno['nombre']} {alumno['apellidos']}", style="Header.TLabel").pack(anchor="w", pady=(0, 5))
                ttk.Label(tarjeta_alumno, text=f"Matrícula: {alumno['matricula']}", style="Body.TLabel").pack(anchor="w")
                
                btn_asistencia = ttk.Button(tarjeta_alumno, text="Marcar Asistencia", command=lambda s=alumno: self.mostrar_pantalla_asistencia(s), style="Primary.TButton")
                btn_asistencia.pack(pady=10, ipadx=10, ipady=3)
        except Error as e:
            messagebox.showerror("Error", f"No se pudieron cargar los alumnos: {e}")
        finally:
            if conexion.is_connected():
                conexion.close()

    def mostrar_pantalla_asistencia(self, info_alumno):
        """
        Muestra la pantalla para marcar la asistencia de un alumno específico.
        :param info_alumno: Diccionario con la información del alumno y el ID de registro de asesoría.
        """
        self.set_id_estudiante_actual(info_alumno['id_alumno'])
        self.limpiar_ventana()
        self.crear_diseno_profesor("Asistencia") # Mantiene el menú lateral del profesor
        
        # Limpia solo el área de contenido para cargar el formulario de asistencia
        for widget in self.marco_contenido.winfo_children():
            widget.destroy()

        ttk.Label(self.marco_contenido, text="Marcar Asistencia", style="Subtitle.TLabel").pack(pady=10)
        ttk.Label(self.marco_contenido, text=f"Alumno: {info_alumno['nombre']} {info_alumno['apellidos']}", style="Header.TLabel").pack(pady=5)
        ttk.Label(self.marco_contenido, text=f"Matrícula: {info_alumno['matricula']}", style="Body.TLabel").pack(pady=5)
        ttk.Label(self.marco_contenido, text="¿El alumno asistió a la asesoría?", style="Body.TLabel").pack(pady=30)

        marco_botones = ttk.Frame(self.marco_contenido, style="Content.TFrame")
        marco_botones.pack(pady=20)
        
        boton_si = ttk.Button(marco_botones, text="Sí asistió", command=lambda: self.marcar_asistencia(info_alumno['id_registro'], 1), style="Success.TButton")
        boton_si.grid(row=0, column=0, padx=20, ipadx=20, ipady=8)
        boton_no = ttk.Button(marco_botones, text="No asistió", command=lambda: self.marcar_asistencia(info_alumno['id_registro'], 0), style="Danger.TButton")
        boton_no.grid(row=0, column=1, padx=20, ipadx=20, ipady=8)

    def marcar_asistencia(self, id_registro, estado):
        """
        Registra la asistencia de un alumno en la base de datos.
        Si el alumno no asiste, envía una alerta.
        :param id_registro: ID del registro de asesoría.
        :param estado: 1 si asistió, 0 si no asistió.
        """
        conexion = conectar_bd()
        if not conexion: return
        try:
            cursor = conexion.cursor()
            consulta = "INSERT INTO asistencias (id_registro, fecha, presente) VALUES (%s, %s, %s)"
            cursor.execute(consulta, (id_registro, datetime.now().date(), estado))
            conexion.commit()
            
            if estado == 1:
                messagebox.showinfo("Éxito", "Asistencia registrada correctamente.")
            else:
                self.enviar_alerta(self.get_id_estudiante_actual()) # Envía alerta si no asistió
            
            self.gestionar_menu_profesor("Asesoría") # Vuelve a la pantalla de asesorías

        except Error as e:
            messagebox.showerror("Error", f"No se pudo marcar la asistencia: {e}")
        finally:
            if conexion.is_connected():
                conexion.close()

    def enviar_alerta(self, id_alumno):
        """
        Envía una alerta a un alumno específico, registrándola en la base de datos.
        :param id_alumno: ID del alumno al que se enviará la alerta.
        """
        conexion = conectar_bd()
        if not conexion: return
        try:
            cursor = conexion.cursor()
            mensaje = "El alumno no asistió a la asesoría programada. Se recomienda seguimiento."
            consulta = "INSERT INTO alertas (id_alumno, id_profesor, mensaje, fecha_envio) VALUES (%s, %s, %s, %s)"
            cursor.execute(consulta, (id_alumno, self.get_id_usuario_actual(), mensaje, datetime.now()))
            conexion.commit()
            messagebox.showinfo("Alerta Enviada", "Se ha enviado una alerta por la inasistencia del alumno.")
        except Error as e:
            messagebox.showerror("Error", f"No se pudo enviar la alerta: {e}")
        finally:
            if conexion.is_connected():
                conexion.close()

    # --- VISTAS DE ESTUDIANTE ---
    def obtener_alertas_estudiante(self):
        """
        Consulta y retorna las alertas enviadas al estudiante actual desde la base de datos.
        :return: Una lista de diccionarios, donde cada diccionario representa una alerta.
        """
        conexion = conectar_bd()
        if not conexion: return []
        try:
            cursor = conexion.cursor(dictionary=True)
            consulta = '''
                SELECT a.mensaje, a.fecha_envio, p.nombre, p.apellidos
                FROM alertas a
                JOIN Profesores p ON a.id_profesor = p.id_profesor
                WHERE a.id_alumno = %s
                ORDER BY a.fecha_envio DESC
            '''
            cursor.execute(consulta, (self.get_id_usuario_actual(),))
            alertas = cursor.fetchall()
            return alertas
        except Error as e:
            messagebox.showerror("Error", f"No se pudieron cargar las alertas: {e}")
            return []
        finally:
            if conexion.is_connected():
                conexion.close()

    def mostrar_inicio_estudiante(self):
        """
        Muestra la pantalla de inicio para el estudiante.
        """
        self.limpiar_ventana()
        self.crear_diseno_estudiante("Inicio")

    def crear_diseno_estudiante(self, pagina_actual):
        """
        Crea el diseño general de la interfaz del estudiante, incluyendo el encabezado,
        el menú lateral y el área de contenido principal.
        :param pagina_actual: La página que se debe mostrar en el área de contenido.
        """
        # Encabezado: Contiene el título de la aplicación y el botón de cerrar sesión.
        marco_encabezado = ttk.Frame(self.ventana_principal, style="Nav.TFrame", padding=10)
        marco_encabezado.pack(fill="x")
        ttk.Label(marco_encabezado, text="Gestor de asistencias a asesorias", style="Nav.TLabel").pack(side="left", padx=20)
        ttk.Button(marco_encabezado, text="Cerrar Sesión", command=self.cerrar_sesion, style="Danger.TButton").pack(side="right", padx=20)

        # Contenedor principal: Contiene el menú lateral y el área de contenido.
        marco_principal = ttk.Frame(self.ventana_principal, style="Content.TFrame")
        marco_principal.pack(fill="both", expand=True)

        # Menú lateral (Sidebar): Contiene los botones de navegación para el estudiante.
        marco_lateral = ttk.Frame(marco_principal, style="Sidebar.TFrame", width=200)
        marco_lateral.pack(side="left", fill="y")
        
        ttk.Label(marco_lateral, text="Menú", style="Sidebar.TLabel", padding=10).pack(fill="x")
        elementos_menu = ["Inicio", "Profesores", "Asesoría", "Mis Asesorías"]
        for elemento in elementos_menu:
            boton = ttk.Button(marco_lateral, text=elemento, command=lambda i=elemento: self.gestionar_menu_estudiante(i), style="Sidebar.TButton")
            boton.pack(fill="x", pady=5, padx=10)

        # Área de contenido: Donde se cargan las diferentes vistas según la selección del menú.
        self.marco_contenido = ttk.Frame(marco_principal, style="Content.TFrame", padding=20)
        self.marco_contenido.pack(side="right", fill="both", expand=True)
        
        self.actualizar_contenido_estudiante(pagina_actual) # Carga el contenido inicial de la página

    def gestionar_menu_estudiante(self, opcion):
        """
        Maneja la selección de opciones en el menú lateral del estudiante.
        :param opcion: La opción de menú seleccionada (ej. "Inicio", "Profesores").
        """
        self.actualizar_contenido_estudiante(opcion)

    def actualizar_contenido_estudiante(self, opcion):
        """
        Actualiza el contenido del área principal del estudiante según la opción seleccionada.
        :param opcion: La opción de menú que determina qué contenido mostrar.
        """
        for widget in self.marco_contenido.winfo_children():
            widget.destroy() # Limpia el área de contenido actual

        if opcion == "Inicio":
            self.mostrar_panel_estudiante()
        elif opcion == "Profesores":
            self.mostrar_profesores_estudiante()
        elif opcion == "Asesoría":
            self.mostrar_asesoria_estudiante()
        elif opcion == "Mis Asesorías":
            self.mostrar_mis_asesorias()

    def mostrar_panel_estudiante(self):
        """
        Muestra el panel principal del estudiante, incluyendo un mensaje de bienvenida
        y la sección de notificaciones (alertas).
        """
        ttk.Label(self.marco_contenido, text=f"Bienvenido, {self.get_info_usuario_actual()['nombre']}", style="Header.TLabel").pack(pady=(20, 10))
        
        # --- Sección de Alertas ---
        ttk.Label(self.marco_contenido, text="Notificaciones", style="Subtitle.TLabel").pack(pady=(20, 10))
        
        alertas = self.obtener_alertas_estudiante() # Obtiene las alertas del estudiante
        
        marco_alertas = ttk.Frame(self.marco_contenido, style="Content.TFrame")
        marco_alertas.pack(fill="both", expand=True, padx=30, pady=10)

        if not alertas:
            ttk.Label(marco_alertas, text="No tienes notificaciones nuevas.", style="Body.TLabel").pack(pady=20)
        else:
            # Muestra cada alerta en una "tarjeta"
            for i, alerta in enumerate(alertas):
                tarjeta_alerta = ttk.Frame(marco_alertas, style="Card.TFrame", padding=15)
                tarjeta_alerta.pack(fill="x", pady=5)
                
                mensaje = f"Alerta del profesor {alerta['nombre']} {alerta['apellidos']}:"
                fecha = alerta['fecha_envio'].strftime("%d/%m/%Y %H:%M") # Formatea la fecha
                
                ttk.Label(tarjeta_alerta, text=mensaje, style="Header.TLabel", wraplength=600).pack(anchor="w")
                ttk.Label(tarjeta_alerta, text=alerta['mensaje'], style="Body.TLabel", wraplength=600).pack(anchor="w", pady=(5, 0))
                ttk.Label(tarjeta_alerta, text=f"Enviado: {fecha}", style="Footer.TLabel", wraplength=600).pack(anchor="e", pady=(5, 0))

        ttk.Label(self.marco_contenido, text="Universidad Tecnológica de Puebla - 2025", style="Footer.TLabel").pack(side="bottom", pady=30)

    def mostrar_profesores_estudiante(self):
        """
        Muestra una lista de todos los profesores y las materias que imparten.
        """
        ttk.Label(self.marco_contenido, text="Profesores", style="Header.TLabel").pack(pady=20)
        conexion = conectar_bd()
        if not conexion: return
        try:
            cursor = conexion.cursor(dictionary=True)
            consulta = '''
                SELECT p.nombre, p.apellidos, m.nombre_materia
                FROM Profesores p
                LEFT JOIN Materias m ON p.id_profesor = m.id_profesor
            '''
            cursor.execute(consulta)
            profesores = cursor.fetchall()
            
            marco_profesores = ttk.Frame(self.marco_contenido, style="Content.TFrame")
            marco_profesores.pack(fill="both", expand=True, padx=20, pady=10)

            for i, profesor in enumerate(profesores):
                tarjeta_profesor = ttk.Frame(marco_profesores, style="Card.TFrame", padding=15)
                tarjeta_profesor.grid(row=i, column=0, sticky="ew", pady=10, padx=20)
                ttk.Label(tarjeta_profesor, text=f"{profesor['nombre']} {profesor['apellidos']}", style="Body.TLabel", font=self.fuente_encabezado).pack(anchor="w")
                ttk.Label(tarjeta_profesor, text=f"Materia: {profesor['nombre_materia'] or 'No asignada'}", style="Body.TLabel").pack(anchor="w")
        except Error as e:
            messagebox.showerror("Error", f"No se pudieron cargar los profesores: {e}")
        finally:
            if conexion.is_connected():
                conexion.close()

    def mostrar_asesoria_estudiante(self):
        """
        Muestra una lista de materias disponibles para que el estudiante se registre para asesorías.
        """
        ttk.Label(self.marco_contenido, text="Asesoría", style="Header.TLabel").pack(pady=20)
        conexion = conectar_bd()
        if not conexion: return
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT id_materia, nombre_materia FROM Materias")
            materias = cursor.fetchall()
            
            marco_materias = ttk.Frame(self.marco_contenido, style="Content.TFrame")
            marco_materias.pack(fill="both", expand=True, padx=20, pady=10)

            for i, materia in enumerate(materias):
                tarjeta_materia = ttk.Frame(marco_materias, style="SubjectCard.TFrame")
                tarjeta_materia.grid(row=i, column=0, sticky="ew", pady=15, padx=50)
                ttk.Label(tarjeta_materia, text=materia['nombre_materia'], style="Subtitle.TLabel").pack(pady=10)
                boton_seleccionar = ttk.Button(tarjeta_materia, text="Seleccionar", command=lambda s=materia: self.mostrar_detalle_materia(s), style="Primary.TButton")
                boton_seleccionar.pack(pady=10, ipadx=10, ipady=5)
        except Error as e:
            messagebox.showerror("Error", f"No se pudieron cargar las materias: {e}")
        finally:
            if conexion.is_connected():
                conexion.close()

    def mostrar_mis_asesorias(self):
        """
        Muestra las asesorías a las que el estudiante se ha registrado.
        """
        ttk.Label(self.marco_contenido, text="Mis Asesorías Registradas", style="Header.TLabel").pack(pady=20)
        conexion = conectar_bd()
        if not conexion: return
        try:
            cursor = conexion.cursor(dictionary=True)
            consulta = '''
                SELECT ar.id_registro, m.nombre_materia, p.nombre, p.apellidos, m.horario
                FROM asesorias_registradas ar
                JOIN Materias m ON ar.id_materia = m.id_materia
                JOIN Profesores p ON m.id_profesor = p.id_profesor
                WHERE ar.id_alumno = %s
            '''
            cursor.execute(consulta, (self.get_id_usuario_actual(),))
            asesorias = cursor.fetchall()
            
            marco_asesorias = ttk.Frame(self.marco_contenido, style="Content.TFrame")
            marco_asesorias.pack(fill="both", expand=True, padx=20, pady=10)

            if not asesorias:
                ttk.Label(marco_asesorias, text="No te has registrado a ninguna asesoría.", style="Body.TLabel").pack(pady=20)
            else:
                for i, asesoria in enumerate(asesorias):
                    tarjeta_asesoria = ttk.Frame(marco_asesorias, style="Card.TFrame", padding=15)
                    tarjeta_asesoria.grid(row=i, column=0, sticky="ew", pady=10, padx=20)
                    
                    info_materia = f"{asesoria['nombre_materia']}\nProfesor: {asesoria['nombre']} {asesoria['apellidos']}\nHorario: {asesoria['horario']}"
                    ttk.Label(tarjeta_asesoria, text=info_materia, style="Body.TLabel").pack(anchor="w")
                    
                    boton_cancelar = ttk.Button(tarjeta_asesoria, text="Cancelar Registro", command=lambda r=asesoria['id_registro']: self.cancelar_asesoria(r), style="Danger.TButton")
                    boton_cancelar.pack(pady=10, ipadx=10, ipady=5)

        except Error as e:
            messagebox.showerror("Error", f"No se pudieron cargar tus asesorías: {e}")
        finally:
            if conexion.is_connected():
                conexion.close()

    def cancelar_asesoria(self, id_registro):
        """
        Cancela el registro de un estudiante a una asesoría.
        """
        if messagebox.askyesno("Confirmar Cancelación", "¿Estás seguro de que quieres cancelar tu registro a esta asesoría?"):
            conexion = conectar_bd()
            if not conexion: return
            try:
                cursor = conexion.cursor()
                # Primero, eliminamos las asistencias asociadas para mantener la integridad referencial
                cursor.execute("DELETE FROM asistencias WHERE id_registro = %s", (id_registro,))
                # Luego, eliminamos el registro de la asesoría
                cursor.execute("DELETE FROM asesorias_registradas WHERE id_registro = %s", (id_registro,))
                conexion.commit()
                messagebox.showinfo("Éxito", "Tu registro a la asesoría ha sido cancelado.")
                self.gestionar_menu_estudiante("Mis Asesorías") # Recargamos la pantalla
            except Error as e:
                messagebox.showerror("Error", f"No se pudo cancelar la asesoría: {e}")
            finally:
                if conexion.is_connected():
                    conexion.close()

    def mostrar_detalle_materia(self, materia):
        """
        Muestra los detalles de una materia seleccionada, incluyendo su horario,
        y permite al estudiante confirmar su asistencia a la asesoría.
        :param materia: Diccionario con la información de la materia seleccionada.
        """
        self.set_materia_actual(materia)
        self.limpiar_ventana()
        self.crear_diseno_estudiante("Asesoría") # Mantiene el menú lateral del estudiante
        
        # Limpia solo el área de contenido para cargar los detalles de la materia
        for widget in self.marco_contenido.winfo_children():
            widget.destroy()

        conexion = conectar_bd()
        if not conexion: return
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT horario FROM Materias WHERE id_materia = %s", (materia['id_materia'],))
            horario = cursor.fetchone()

            ttk.Label(self.marco_contenido, text=materia['nombre_materia'], style="Header.TLabel").pack(pady=20)
            ttk.Label(self.marco_contenido, text="Horario:", style="Subtitle.TLabel").pack(pady=10)
            ttk.Label(self.marco_contenido, text=horario['horario'] if horario else "No disponible", style="Body.TLabel").pack(pady=5)
            
            ttk.Button(self.marco_contenido, text="Asistiré a la asesoría", command=self.confirmar_asesoria, style="Accent.TButton").pack(pady=30, ipadx=20, ipady=8)
        except Error as e:
            messagebox.showerror("Error", f"No se pudo cargar el detalle de la materia: {e}")
        finally:
            if conexion.is_connected():
                conexion.close()

    def confirmar_asesoria(self):
        """
        Registra la asistencia del estudiante a una asesoría en la base de datos.
        Verifica si el estudiante ya está registrado para evitar duplicados.
        """
        conexion = conectar_bd()
        if not conexion: return
        try:
            cursor = conexion.cursor()
            # Verifica si el estudiante ya está registrado para esta asesoría
            consulta_verificacion = "SELECT * FROM asesorias_registradas WHERE id_alumno = %s AND id_materia = %s"
            cursor.execute(consulta_verificacion, (self.get_id_usuario_actual(), self.get_materia_actual()['id_materia']))
            if cursor.fetchone():
                messagebox.showinfo("Información", "Ya estás registrado en esta asesoría.")
                return

            # Si no está registrado, procede con la inserción
            consulta = "INSERT INTO asesorias_registradas (id_alumno, id_materia) VALUES (%s, %s)"
            cursor.execute(consulta, (self.get_id_usuario_actual(), self.get_materia_actual()['id_materia']))
            conexion.commit()
            self.mostrar_pantalla_confirmacion() # Muestra la pantalla de confirmación
        except Error as e:
            messagebox.showerror("Error", f"No se pudo confirmar la asistencia: {e}")
        finally:
            if conexion.is_connected():
                conexion.close()

    def mostrar_pantalla_confirmacion(self):
        """
        Muestra una pantalla de confirmación después de que el estudiante se registra para una asesoría.
        """
        self.limpiar_ventana()
        marco_principal = ttk.Frame(self.ventana_principal, style="Content.TFrame", padding=50)
        marco_principal.pack(fill="both", expand=True)
        ttk.Label(marco_principal, text="¡Tu asistencia está confirmada!", style="Subtitle.TLabel").pack(pady=50)
        ttk.Label(marco_principal, text=f"Se ha registrado tu interés en la asesoría de {self.get_materia_actual()['nombre_materia']}.", style="Body.TLabel").pack(pady=10)
        ttk.Button(marco_principal, text="Inicio", command=self.mostrar_inicio_estudiante, style="Primary.TButton").pack(pady=50, ipadx=30, ipady=8)
        ttk.Label(marco_principal, text="Universidad Tecnológica de Puebla - 2025", style="Footer.TLabel").pack(side="bottom", pady=20)

# Punto de entrada de la aplicación
if __name__ == "__main__":
    ventana_principal = tk.Tk() # Crea la ventana principal de Tkinter
    aplicacion = GestorAsistenciasApp(ventana_principal) # Instancia la aplicación
    ventana_principal.mainloop() # Inicia el bucle principal de eventos de Tkinter, manteniendo la ventana abierta