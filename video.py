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

    def __init__(self,fullScreen=True):
        """
        Constructor de la clase tiene dos opciones a activar o desactivar:
        bool simulation = Falso por defecto, corre una simulación de la activación y desactivación de la alarma por un minuto con datos simulados en forma de variable de clase
        bool fullScreen = True por defecto, corre la GUI en modo de pantalla total, lo que se espera en su funcionamiento normal
        """
        self.process = multiprocessing.Process(target=self._correrGui,args=(fullScreen,))
        self.process.start()

    def _correrGui(self,fullScreen):
        """
        Metodo auxiliar para paralelizar la interfaz
        """
        app = QtGui.QApplication(sys.argv)
        interfaz = AlarmaGUI(GUIParalela.myQueue,pantallaTotal=fullScreen)
        sys.exit(app.exec_())
        



class AlarmaGUI(QtGui.QWidget):         #QWidget #QMainWindow
    """
    Interfaz gráfica visual
    """
    def __init__(self,fila,pantallaTotal = True,parent=None):
        #super(AlarmaGUI, self).__init__(parent)
        QtGui.QWidget.__init__(self, None, QtCore.Qt.WindowStaysOnTopHint)
        # Parámetros constantes:
        self.titulo = 'Scape Room'
        self.thread = ThreadClass(fila)
        self.thread.start()
        self.connect(self.thread,QtCore.SIGNAL('MOSTRAR_VIDEO_1'),self._mostrarVideo1)
        self.connect(self.thread,QtCore.SIGNAL('MOSTRAR_VIDEO_2'),self._mostrarVideo2)

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
        self.media0 = Phonon.MediaSource('./imagenes/logoWeb.png')
        self.media1 = Phonon.MediaSource('./videos/1.avi')
        self.video = Phonon.VideoPlayer(self)
        self.video.load(self.media1)

        self.media2 = Phonon.MediaSource('./videos/2.avi')

        self.fechaYHora = QtGui.QLabel('Fecha')
        self.estadoAlarma = QtGui.QLabel('Alarma Activada')
        self.fechaYHora.setGeometry(25, 25, 250, 250)
        self.pixmapAct = QtGui.QPixmap('./imagenes/alarmaActivada.png')
        self.imagen.setPixmap(self.pixmapAct)


        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self._time)
        self.timer.start(1000)

        # Layouts:
        self.layoutVideo1 = QtGui.QVBoxLayout()
        
        self.layoutVideo1.addWidget(self.video)
        #self.layoutVideo1.setAlignment(self.imagen, QtCore.Qt.AlignHCenter)

        self.setLayout(self.layoutVideo1)
        self.video.load(self.media0)
        self.video.play()
        self.setMinimumHeight(450)
        
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
        #self.lcd.display(strftime("%Y"+"-"+"%m"+"-"+"%d"+" "+"%H"+":"+"%M"+":"+"%S"))
        #self.layoutVideo1.removeWidget(self.video)
        #self.layoutVideo1.addWidget(self.video)
        pass
    
    def _mostrarVideo1(self):
        """
        Despliega el video 1
        """
        print('reproduciendo video 1')
        self.video.load(self.media1)
        self.video.play()
        
    def _mostrarVideo2(self):
        """
        Despliega el video 2
        """
        print('reproduciendo video 2')
        self.video.load(self.media2)
        self.video.play()

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
        self.passwords = []
        with open('./database/key', 'r') as f:
            readData = f.read()
        for password in readData.split('\n'):
            if len(password)>4:
                self.passwords.append(password) 

    def run(self):
        """
        Re implementación del método
        """
        while True:
            if not self.queue.empty():
                valor = self.queue.get() # valor = (estado, id, nombre)
                if valor in self.passwords:
                    self.emit(QtCore.SIGNAL('MOSTRAR_VIDEO_1'))
                else:
                    self.emit(QtCore.SIGNAL('MOSTRAR_VIDEO_2'))

if __name__ == '__main__':
    """
    Este pequeno script demostrativo muestra que la interfaz puede ser creada sin interferir con el programa principal
    """
    p = GUIParalela(fullScreen=False)
    enviandoValores = True
    while enviandoValores:
        sleep(1)
        myInput = str(input('Ingrese Contraseña: '))
        GUIParalela.myQueue.put(myInput)
        if myInput == '0':
            enviandoValores = False
    
    p.process.join() 

