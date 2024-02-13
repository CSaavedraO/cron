import mysql.connector

#CLASE CONTROLADORA DE LA CONEXION A LA BD
class clsConexionDB:
    def __init__(self):
        self.config = {
            "host": "localhost",
            "user": "root",
            "password": "", 
            "database": "dbcronproyect",
            "raise_on_warnings": True
        }
        self.conexion = None
        self.cursor = None

    def conectar(self):
        try:
            self.conexion = mysql.connector.connect(**self.config)
            if self.conexion.is_connected():
                print("Conexión exitosa a la base de datos")
                self.cursor = self.conexion.cursor()
        except mysql.connector.Error as Error:
            print(f"Error al conectarse a la base de datos: {Error}")
    
    def cerrar_conexion(self):
        try:
            if self.conexion.is_connected():
                self.cursor.close()
                self.conexion.close()
                print("Conexión cerrada")
        except mysql.connector.Error as error:
            print(f"Error al cerrar la conexión: {error}")

    def Signup_usuario(self, nombre, apellido, contrasena, correo):
        try:
            query = "INSERT INTO usuarios (Nombre_users, Apellido_users, Contraseña_users, Correo_users) VALUES (%s, %s, %s, %s)"
            valores = (nombre, apellido, contrasena, correo)
            self.cursor.execute(query, valores)
            self.conexion.commit()
            print("Usuario registrado exitosamente")
            return True
        except mysql.connector.Error as Error:
            print(f"Error al registrar el usuario: {Error}")
            self.conexion.rollback()
            return False

    def login_usuario(self, correo, contraseña):
        try:
            query = "SELECT * FROM usuarios WHERE correo_users = %s AND contraseña_users = %s"
            valores = (correo, contraseña)
            self.cursor.execute(query, valores)
            usuario = self.cursor.fetchone()
            if usuario:
                print("Inicio de sesión exitoso")
                return True
            else:
                print("Credenciales incorrectas")
                return False
        except mysql.connector.Error as Error:
            print(f"Error al realizar el login: {Error}")
            return False
    
    def obtener_id_usuario(self, correo):
        try:
            query = "SELECT ID_users FROM usuarios WHERE Correo_users = %s"
            valores = (correo,)
            self.cursor.execute(query, valores)
            resultado = self.cursor.fetchone()
            if resultado:
                return resultado[0]
            else:
                print("El usuario no existe en la base de datos")
                return None
        except mysql.connector.Error as error:
            print(f"Error al obtener ID de usuario: {error}")
            return None
    
    def obtener_clasificaciones(self):
        try:
            query = "SELECT clasificacion FROM clasificaciones;"
            self.cursor.execute(query)
            clasificaciones = self.cursor.fetchall()
            return [clasificacion[0] for clasificacion in clasificaciones]
        except mysql.connector.Error as error:
            print(f"Error al obtener las clasificaciones: {error}")
            return []
    
    def obtener_id_clasificacion(self, clasificacion):
        try:
            query = "SELECT ID_clas FROM clasificaciones WHERE clasificacion = %s"
            valores = (clasificacion,)
            self.cursor.execute(query, valores)
            resultado = self.cursor.fetchone()
            if resultado:
                id_clasificacion = resultado[0]
                return id_clasificacion
            else:
                print("La clasificación no existe en la base de datos")
                return None
        except mysql.connector.Error as error:
            print(f"Error al obtener ID de clasificación: {error}")
            return None

    def insertar_tarea(self, nombre_tarea, descripcion_tarea, clasificacion, usuario_id):
        try:
            id_clasificacion = self.obtener_id_clasificacion(clasificacion)
            if id_clasificacion is None:
                return False
            
            query = "INSERT INTO tareas (Nombre_tasks, Descripcion_tasks, Clasificacion_ID, Usuarios_ID) VALUES (%s, %s, %s, %s)"
            valores = (nombre_tarea, descripcion_tarea, id_clasificacion, usuario_id)
            self.cursor.execute(query, valores)
            self.conexion.commit()
            print("Tarea registrada exitosamente")
            return True
        except mysql.connector.Error as error:
            print(f"Error al registrar la tarea: {error}")
            self.conexion.rollback()
            return False
            
    def obtener_tareas_usuario(self, usuario_id):
        try:
            query = "SELECT tareas.Nombre_tasks, tareas.Descripcion_tasks, tareas.Tiempo_tasks, clasificaciones.clasificacion, tareas.Estado_tasks FROM tareas INNER JOIN clasificaciones ON tareas.Clasificacion_ID = clasificaciones.ID_clas WHERE tareas.Usuarios_ID = %s"
            valores = (usuario_id,)
            self.cursor.execute(query, valores)
            tareas_usuario = self.cursor.fetchall()
            return tareas_usuario
        except mysql.connector.Error as error:
            print(f"Error al obtener las tareas del usuario: {error}")
            return []
    
    def eliminar_tarea(self, nombre_tarea):
        try:
            query = "DELETE FROM tareas WHERE Nombre_tasks = %s"
            valores = (nombre_tarea,)
            self.cursor.execute(query, valores)
            self.conexion.commit()
            print("Tarea eliminada exitosamente")
            return True
        except mysql.connector.Error as error:
            print(f"Error al eliminar la tarea: {error}")
            self.conexion.rollback()
            return False
    
    def actualizar_estado_tarea(self, nombre_tarea, estado):
        try:
            query = "UPDATE tareas SET Estado_tasks = %s WHERE Nombre_tasks = %s"
            valores = (estado, nombre_tarea)
            self.cursor.execute(query, valores)
            self.conexion.commit()
            print(f"Estado de la tarea '{nombre_tarea}' actualizado a '{estado}'")
            return True
        except mysql.connector.Error as error:
            print(f"Error al actualizar estado de la tarea: {error}")
            self.conexion.rollback()
            return False

    def actualizar_tiempo_tarea(self, nombre_tarea, tiempo_transcurrido):
        try:
            query = "UPDATE tareas SET Tiempo_tasks = %s WHERE Nombre_tasks = %s"
            valores = (tiempo_transcurrido, nombre_tarea)
            self.cursor.execute(query, valores)
            self.conexion.commit()
            print(f"Tiempo de la tarea '{nombre_tarea}' actualizado a '{tiempo_transcurrido}'")
            return True
        except mysql.connector.Error as error:
            print(f"Error al actualizar tiempo de la tarea: {error}")
            self.conexion.rollback()
            return False
        
    def obtener_tiempo_tarea(self, nombre_tarea):
        try:
            query = "SELECT Tiempo_tasks FROM tareas WHERE Nombre_tasks = %s"
            valores = (nombre_tarea,)
            self.cursor.execute(query, valores)
            tiempo_tarea = self.cursor.fetchone()
            return tiempo_tarea[0] if tiempo_tarea else None
        except mysql.connector.Error as error:
            print(f"Error al obtener el tiempo de la tarea: {error}")
            return None