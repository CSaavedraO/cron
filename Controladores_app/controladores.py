from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QTimer, QTime
from ui.ui_login import Ui_Login
from ui.ui_signup import Ui_Signup
from ui.ui_main import Ui_MainWindow
from ui.ui_nuevatarea import Ui_NuevaTarea
from Conexion.conexion import clsConexionDB
import sys


#CLASE CONTROLADOR VENTANA MAIN 
class clsMainWindowController:
    def __init__(self, usuario_id):
        self.usuario_id = usuario_id
        self.main_window = QtWidgets.QMainWindow()
        self.ui_main = Ui_MainWindow()
        self.ui_main.setupUi(self.main_window)
        self.ui_main.btnNuevaTarea.clicked.connect(self.abrir_nueva_tarea)
        self.ui_main.btnCerrarSesion.clicked.connect(self.cerrar_sesion)
        self.ui_main.btnEliminar.clicked.connect(self.eliminar_tarea_desde_tabla)
        self.login_controller = login_controller
        self.nueva_tarea_controller = None 
        self.db = clsConexionDB()
        self.db.conectar()
        self.tiempo_transcurrido = QTime(0, 0) 
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_cron)
        self.ui_main.btnIniciar.clicked.connect(self.iniciar_tarea)
        self.ui_main.btnPausar.clicked.connect(self.pausar_tarea)
        self.ui_main.btnReanudar.clicked.connect(self.reanudar_tarea)
        self.ui_main.btnDetener.clicked.connect(self.detener_tarea)
        self.comboBox_actualizado = False
        
    def iniciar_tarea(self):
        self.ui_main.lblTiempo.setText('00:00:00') 
        self.ui_main.lblTiempo.show() 
        self.timer.start(1000)
        row = 0
        self.ui_main.qtwTabla.setItem(row, 4, QtWidgets.QTableWidgetItem("Activo"))  

    def pausar_tarea(self):
        self.timer.stop()
        row = 0
        self.ui_main.qtwTabla.setItem(row, 4, QtWidgets.QTableWidgetItem("Inactivo"))

    def reanudar_tarea(self):
        self.timer.start(1000)
        row = 0
        self.ui_main.qtwTabla.setItem(row, 4, QtWidgets.QTableWidgetItem("Activo"))

    
    def detener_tarea(self):
        self.timer.stop()
        tiempo_detenido = self.ui_main.lblTiempo.text()
        row = self.ui_main.qtwTabla.currentRow()

        if row >= 0: 
            tarea_seleccionada = self.ui_main.qtwTabla.item(row, 0).text()
            self.actualizar_y_detener_tarea(tarea_seleccionada, tiempo_detenido)
        else: 
            tarea_seleccionada = self.ui_main.cmbSeleccionartarea.currentText()
            if tarea_seleccionada:  
                self.actualizar_y_detener_tarea(tarea_seleccionada, tiempo_detenido)
            else:
                QtWidgets.QMessageBox.warning(self.main_window, "Error", "Selecciona una tarea para detener el tiempo")
    
    def actualizar_y_detener_tarea(self, tarea_seleccionada, tiempo_detenido):
        row = self.ui_main.qtwTabla.findItems(tarea_seleccionada, QtCore.Qt.MatchExactly)[0].row()
        self.ui_main.qtwTabla.setItem(row, 2, QtWidgets.QTableWidgetItem(tiempo_detenido))
        self.ui_main.qtwTabla.setItem(row, 4, QtWidgets.QTableWidgetItem("Inactivo"))

        self.db.actualizar_tiempo_tarea(tarea_seleccionada, tiempo_detenido)


    def actualizar_cron(self):
        self.tiempo_transcurrido = self.tiempo_transcurrido.addSecs(1)
        cron_texto = self.tiempo_transcurrido.toString('hh:mm:ss')
        self.ui_main.lblTiempo.setText(cron_texto)
    
    def eliminar_tarea_desde_tabla(self):
        fila_seleccionada = self.ui_main.qtwTabla.currentRow()
        if fila_seleccionada >= 0:  
            tarea_seleccionada = self.ui_main.qtwTabla.item(fila_seleccionada, 0).text()
            self.eliminar_tarea(tarea_seleccionada)
        else: 
            tarea_seleccionada = self.ui_main.cmbSeleccionartarea.currentText()
            if tarea_seleccionada:  
                self.eliminar_tarea(tarea_seleccionada)
            else:
                QtWidgets.QMessageBox.warning(self.main_window, "Error", "Selecciona una tarea para eliminar")


    def eliminar_tarea(self, nombre_tarea):
        if self.db.eliminar_tarea(nombre_tarea):
            self.llenar_tabla_tareas()
            if not self.comboBox_actualizado:  
                self.llenar_combo_box_tareas()  
                self.comboBox_actualizado = True  

    def abrir_nueva_tarea(self):
        self.nueva_tarea_controller = clsNuevaTareaController(self.main_window, self.usuario_id) 
        self.nueva_tarea_controller.nueva_tarea_window.show()
        self.main_window.hide()
    
    def cerrar_sesion(self):
        self.main_window.close() 
        self.login_controller.login_window.show() 
    
    @staticmethod
    def estado_activo_inactivo(bit_value):
        return "Activo" if bit_value else "Inactivo"
    
    def llenar_tabla_tareas(self):
        tareas_usuario = self.db.obtener_tareas_usuario(self.usuario_id)
        self.ui_main.qtwTabla.setRowCount(len(tareas_usuario))
        for row, tarea in enumerate(tareas_usuario):
            nombre = tarea[0] 
            descripcion = tarea[1]  
            tiempo = str(tarea[2])
            clasificacion = tarea[3]
            estado = self.estado_activo_inactivo(tarea[4])
            self.ui_main.qtwTabla.setItem(row, 0, QtWidgets.QTableWidgetItem(nombre))
            self.ui_main.qtwTabla.setItem(row, 1, QtWidgets.QTableWidgetItem(descripcion))
            self.ui_main.qtwTabla.setItem(row, 2, QtWidgets.QTableWidgetItem(tiempo))
            self.ui_main.qtwTabla.setItem(row, 3, QtWidgets.QTableWidgetItem(clasificacion))
            self.ui_main.qtwTabla.setItem(row, 4, QtWidgets.QTableWidgetItem(estado))
    
    def obtener_tareas_usuario(self):
        return self.db.obtener_tareas_usuario(self.usuario_id)
    
    def llenar_combo_box_tareas(self):
        tareas_usuario = self.obtener_tareas_usuario()
        for tarea in tareas_usuario:
            self.ui_main.cmbSeleccionartarea.addItem(tarea[0])

#CLASE COTROLADOR DE VENTANA LOG IN 
class clsLoginController:
    def __init__(self):
        self.app = QtWidgets.QApplication([]) 
        self.login_window = QtWidgets.QMainWindow()
        self.ui_login = Ui_Login()
        self.ui_login.setupUi(self.login_window)
        self.ui_login.txtcontrasena_login.setEchoMode(QtWidgets.QLineEdit.Password)
        self.ui_login.btnRegistarse.clicked.connect(self.mostrar_ventana_registro)
        self.ui_login.btnIngresar_login.clicked.connect(self.iniciar_sesion)
        self.db = clsConexionDB()
        self.db.conectar()

    def mostrar_ventana_registro(self):
        self.login_window.close()
        self.signup_controller = clsSignupController()
        self.signup_controller.registro_window.show()
   
    def iniciar_sesion(self):
        correo = self.ui_login.txtcorreo_login.text()
        contraseña = self.ui_login.txtcontrasena_login.text()

        if self.db.login_usuario(correo, contraseña):
            usuario_id = self.db.obtener_id_usuario(correo)
            self.abrir_ventana_principal(usuario_id)
        else:
            self.mostrar_error_login()
        
        self.ui_login.txtcorreo_login.clear()
        self.ui_login.txtcontrasena_login.clear()

    def abrir_ventana_principal(self, usuario_id):
        self.main_controller = clsMainWindowController(usuario_id) 
        self.main_controller.llenar_tabla_tareas()
        self.main_controller.main_window.show()
        self.login_window.close()
        self.main_controller.llenar_combo_box_tareas()

    def mostrar_error_login(self):
        mensaje = "Credenciales inválidas. Inténtalo de nuevo."
        self.mostrar_mensaje_error(mensaje)

    def mostrar_mensaje_error(self, mensaje):
        QtWidgets.QMessageBox.warning(self.login_window, "Error", mensaje)

#CLASE CONTROLADOR DE VENTANA SIGN UP 
class clsSignupController:
    def __init__(self):
        self.registro_window = QtWidgets.QMainWindow()
        self.ui_registro = Ui_Signup()
        self.ui_registro.setupUi(self.registro_window)
        self.ui_registro.txtconstrasena_regis.setEchoMode(QtWidgets.QLineEdit.Password)
        self.ui_registro.txtcontrasenaconfir_regis.setEchoMode(QtWidgets.QLineEdit.Password)
        self.ui_registro.btnIngresar_regis.clicked.connect(self.registrar_usuario)
        self.ui_registro.btnCancelar.clicked.connect(self.cancelar_registro)
        self.login_controller = login_controller
        self.db = clsConexionDB()
        self.db.conectar()
        
    def registrar_usuario(self):
        nombre = self.ui_registro.txtnombre_regis.text()
        apellido = self.ui_registro.txtapellido_regis.text()
        correo = self.ui_registro.txtcorreo_regis.text()
        contrasena = self.ui_registro.txtconstrasena_regis.text()
        confirmacion_contra = self.ui_registro.txtcontrasenaconfir_regis.text()

        if self.campos_incompletos(nombre, apellido, correo, contrasena, confirmacion_contra):
            self.mostrar_error("Por favor, completa todos los campos.")
        elif contrasena != confirmacion_contra:
            self.mostrar_error("Las contraseñas no coinciden")
        else:
            self.procesar_registro(nombre, apellido, correo, contrasena)

    def campos_incompletos(self, *campos):
        return any(not campo for campo in campos)

    def procesar_registro(self, nombre, apellido, correo, contrasena):
        if self.db.Signup_usuario(nombre, apellido, contrasena, correo):
            self.mostrar_exito("Usuario registrado con éxito")
            usuario_id = self.db.obtener_id_usuario(correo)
            self.registro_window.close()
            self.login_controller.abrir_ventana_principal(usuario_id)
        else:
            self.mostrar_error("Hubo un problema al registrar el usuario")

    def mostrar_exito(self, mensaje):
        QtWidgets.QMessageBox.information(self.registro_window, "Éxito", mensaje)

    def mostrar_error(self, mensaje):
        QtWidgets.QMessageBox.warning(self.registro_window, "Error", mensaje)
        
    def cancelar_registro(self):
        self.registro_window.close()
        self.login_controller.login_window.show()    

#CLASE CONTROLADOR DE VENTANA NUEVA TAREA   
class clsNuevaTareaController:
    def __init__(self, main_window, usuario_id):
        self.nueva_tarea_window = QtWidgets.QMainWindow()
        self.ui_nueva_tarea = Ui_NuevaTarea()
        self.ui_nueva_tarea.setupUi(self.nueva_tarea_window)
        self.usuario_id = usuario_id 
        self.db = clsConexionDB()
        self.db.conectar()
        self.llenar_combo_box()
        self.ui_nueva_tarea.btnGuardar.clicked.connect(self.guardar_tarea)
        self.ui_nueva_tarea.btnCancelar.clicked.connect(self.cancelar_tarea)
        self.main_window = main_window
        self.main_controller = None

    def llenar_combo_box(self):
        clasificaciones = self.db.obtener_clasificaciones() 
        self.ui_nueva_tarea.cmbClasificacion.addItems(clasificaciones)
        
    def guardar_tarea(self):
        nombre_tarea = self.ui_nueva_tarea.txtNuevatarea.text()
        descripcion_tarea = self.ui_nueva_tarea.txtDescripcion.toPlainText()
        clasificacion_seleccionada = self.ui_nueva_tarea.cmbClasificacion.currentText()

        if not nombre_tarea or not descripcion_tarea or clasificacion_seleccionada == "Clasificación":
            QtWidgets.QMessageBox.warning(self.nueva_tarea_window, "Error", "Completa todos los campos")
            return

        if len(nombre_tarea) > 50:
            QtWidgets.QMessageBox.warning(self.nueva_tarea_window, "Error", "El nombre de la tarea debe tener menos de 50 caracteres")
            return

        if len(descripcion_tarea) > 200:
            QtWidgets.QMessageBox.warning(self.nueva_tarea_window, "Error", "La descripción de la tarea debe tener menos de 255 caracteres")
            return
        
        if self.db.insertar_tarea(nombre_tarea, descripcion_tarea, clasificacion_seleccionada, self.usuario_id):
            QtWidgets.QMessageBox.information(self.nueva_tarea_window, "Éxito", "Tarea registrada con éxito")
            self.nueva_tarea_window.close()
            self.main_controller = clsMainWindowController(self.usuario_id)
            self.main_controller.llenar_tabla_tareas()
            self.main_controller.llenar_combo_box_tareas() 
            self.main_controller.main_window.show()
        else:
            QtWidgets.QMessageBox.warning(self.nueva_tarea_window, "Error", "Hubo un problema al registrar la tarea")

    def cancelar_tarea(self):
        self.nueva_tarea_window.close()
        self.main_window.show()
    

if __name__ == "__main__":
    login_controller = clsLoginController()
    login_controller.login_window.show()
    sys.exit(login_controller.app.exec_())