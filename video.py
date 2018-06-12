# Developed by Alvaro Hurtado
# a.hurtado.bo@gmail.com
# Oruro, Bolivia

import sys
import multiprocessing
from time import sleep, strftime
from PyQt4 import QtGui, QtCore
from PyQt4.phonon import Phonon

class GUIParalela():
    """
    La presente clase representa una interfaz visual de alarma Activada/Desactivada
    Su función principal es la de gestionar la activación y desactivación de la alarma.
    Al Desactivar la alarma Identifica a la persona ingresando
    Al Activar la alarma se regresa al estado inicial
    Presionar ESC para cerrar el GUI
    """
    myQueue = multiprocessing.Queue()
    valoresPrueba =     [('01A22AE32F','Alvaro Hurtado'),
                        ('01A22AE330','Ivan Hurtado'),
                        ('01A22AE331','Tatiana Hurtado'),
                        ('01A22AE332','Maria Maldonado'),
                        ('01A22AE333','Stanley Salvatierra'),
                        ('01A22AE334','David Gamon'),
                        ('01A22AE335','Daniel Condori'),
                        ('01A22AE336','Viviana Colque'),
                        ('01A22AE337','Denisse Vargas'),
                        ('01A22AE338','Ramiro Aliendre')]

    def __init__(self,simulation = False,fullScreen=True):
        """
        Constructor de la clase tiene dos opciones a activar o desactivar:
        bool simulation = Falso por defecto, corre una simulación de la activación y desactivación de la alarma por un minuto con datos simulados en forma de variable de clase
        bool fullScreen = True por defecto, corre la GUI en modo de pantalla total, lo que se espera en su funcionamiento normal
        """
        self.process = multiprocessing.Process(target=self._correrGui,args=(fullScreen,))
        self.process.start()
        if simulation:
            self._simularLlegadaDatos()
        

    def _correrGui(self,fullScreen):
        """
        Metodo auxiliar para paralelizar la interfaz
        """
        app = QtGui.QApplication(sys.argv)
        interfaz = AlarmaGUI(GUIParalela.myQueue,pantallaTotal=fullScreen)
        sys.exit(app.exec_())
        
    def _simularLlegadaDatos(self):
        """
        Método Auxiliar para simular el ingreso de datos
        """
        for i in range(10):
            sleep(4)
            self.desactivarAlarma(GUIParalela.valoresPrueba[i][0],GUIParalela.valoresPrueba[i][1])
            sleep(2)
            self.activarAlarma()

    
    def desactivarAlarma(self,id,nombre):
        """
        Desactivación de la alarma con ID de la RFID ingresada y el nombre del usuario en forma de string
        """
        GUIParalela.myQueue.put((True,id,nombre))

    def activarAlarma(self):
        """
        Activación de la alarma
        """
        GUIParalela.myQueue.put((False,"",""))


class AlarmaGUI(QtGui.QWidget):         #QWidget #QMainWindow
    """
    Interfaz gráfica visual
    """
    def __init__(self,fila,pantallaTotal = True,parent=None):
        #super(AlarmaGUI, self).__init__(parent)
        QtGui.QWidget.__init__(self, None, QtCore.Qt.WindowStaysOnTopHint)
        # Parámetros constantes:
        self.titulo = 'Estado de alarma'
        self.estado = 'Activado'
        self.thread = ThreadClass(fila)
        self.thread.start()
        self.connect(self.thread,QtCore.SIGNAL('ACTUALIZAR_ESTADO'),self._actualizarValor)
        # Clases auxiliares:
        self.initUI()
        # Al inicializarse la clase se muestra:
        if pantallaTotal:
            self.showFullScreen()
        else:
            self.show()


    def initUI(self):
        """
        Inicialización de sus parámetros
        """
        # Definición de campos:
        self.stringSolicitudAutentificacion = 'AUTENTIFIQUESE POR FAVOR'
        self.imagen = QtGui.QLabel(self)
        self.imagen.setGeometry(150, 150, 250, 250)
        self.labelAutentificacion = QtGui.QLabel(self.stringSolicitudAutentificacion)
        self.labelAutentificacion.setFont(QtGui.QFont('SansSerif', 36))
        self.labelIdentificado = QtGui.QLabel('')
        self.labelIdentificado.setFont(QtGui.QFont('SansSerif', 24))

        # Parte visual
        self.imagenLogo = QtGui.QLabel(self)
        self.fechaYHora = QtGui.QLabel('Fecha')
        self.estadoAlarma = QtGui.QLabel('Alarma Activada')
        self.fechaYHora.setGeometry(25, 25, 250, 250)
        self.pixmapAct = QtGui.QPixmap('./imagenes/alarmaActivada.png')
        self.pixmapDeact = QtGui.QPixmap('./imagenes/alarmaDesactivada.png')
        self.pixmapLogo = QtGui.QPixmap('./imagenes/logoWeb.png')
        self.imagen.setPixmap(self.pixmapAct)
        self.imagenLogo.setPixmap(self.pixmapLogo)
        self.lcd = QtGui.QLCDNumber(self)
        self.lcd.setDigitCount(19)
        self.lcd.setMaximumHeight(60)
        self.lcd.display(strftime("%Y"+"-"+"%m"+"-"+"%d"+" "+"%H"+":"+"%M"+":"+"%S"))
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self._time)
        self.timer.start(1000)

        # Layouts:
        layoutVertical = QtGui.QVBoxLayout()
        layoutHorizontalSuperior = QtGui.QHBoxLayout()

        # Agregar Widgets
        layoutHorizontalSuperior.addWidget(self.imagenLogo)
        #layoutHorizontalSuperior.addWidget(self.timer)
        layoutHorizontalSuperior.addWidget(self.lcd)
        layoutVertical.addLayout(layoutHorizontalSuperior)
        layoutVertical.addWidget(self.imagen)
        layoutVertical.addWidget(self.labelAutentificacion)
        layoutVertical.addWidget(self.labelIdentificado)
        layoutVertical.setAlignment(self.imagen, QtCore.Qt.AlignHCenter)
        layoutVertical.setAlignment(self.labelAutentificacion, QtCore.Qt.AlignHCenter)
        layoutVertical.setAlignment(self.labelIdentificado, QtCore.Qt.AlignHCenter)

        self.setMinimumHeight(450)
        self.setLayout(layoutVertical)
        self.setGeometry(300, 300, 300, 150)
        # Algunas visualizaciones:
        self.setWindowIcon(QtGui.QIcon('./imagenes/logo.png')) 
        self.setWindowTitle(self.titulo)
        
    def keyPressEvent(self, e):
        """
        Se redefine la interacción con el teclado para que la tecla ESC cierre el GUI
        """
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()

    def _time(self):
        """
        Actualización del tiempo
        """
        self.lcd.display(strftime("%Y"+"-"+"%m"+"-"+"%d"+" "+"%H"+":"+"%M"+":"+"%S"))

    def _actualizarValor(self,valor):
        """
        Actualiza los campos en la GUI
        """
        (estado, id, nombre) = valor
        if estado:
            self._desactivarAlarma(id,nombre)
        else:
            self._activarAlarma()

    def _desactivarAlarma(self,id,nombre):
        """
        Actualiza los campos en la GUI para modo Desactivado
        """
        self.imagen.setPixmap(self.pixmapDeact)
        self.labelAutentificacion.setText(id)
        self.labelIdentificado.setText(nombre)

    def _activarAlarma(self):
        """
        Actualiza los campos en la GUI para modo Activado
        """
        self.imagen.setPixmap(self.pixmapAct)
        self.labelAutentificacion.setText(self.stringSolicitudAutentificacion)
        self.labelIdentificado.setText('')


class ThreadClass(QtCore.QThread):
    """
    Thread para revisión continua de la fila de registros
    """
    def __init__(self,fila,parent = None):
        """
        Constructor
        """
        super(ThreadClass,self).__init__(parent)
        self.queue = fila

    def run(self):
        """
        Re implementación del método
        """
        while True:
            if not self.queue.empty():
                valor = self.queue.get() # valor = (estado, id, nombre)
                self.emit(QtCore.SIGNAL('ACTUALIZAR_ESTADO'),valor)


if __name__ == '__main__':
    """
    Este pequeno script demostrativo muestra que la interfaz puede ser creada sin interferir con el programa principal
    """
    p = GUIParalela(simulation = False,fullScreen=True)
    sleep(2)
    p.desactivarAlarma('13','Raspberry')
    sleep(1)
    p.activarAlarma()
    sleep(2)
    p.desactivarAlarma('12','Orange')
    sleep(1)
    p.activarAlarma()

    p.process.join() 

