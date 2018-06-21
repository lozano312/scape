# Developed by Alvaro Hurtado
# a.hurtado.bo@gmail.com
# Oruro, Bolivia

import sys
import time
import multiprocessing
from PyQt4 import QtGui, QtCore
from time import sleep, strftime
from gpio import MembraneMatrix

class GUIParalela():
    """
    La presente clase representa una interfaz visual de alarma Activada/Desactivada
    Su función principal es la de gestionar la activación y desactivación de la alarma.
    Al Desactivar la alarma Identifica a la persona ingresando
    Al Activar la alarma se regresa al estado inicial
    Presionar ESC para cerrar el GUI
    """
    myQueue = multiprocessing.Queue()
    miTeclado = MembraneMatrix()
    valorActual = ''
    
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
        interfaz = InterfazVideo(GUIParalela.myQueue,pantallaTotal=fullScreen)
        sys.exit(app.exec_())

class InterfazVideo(QtGui.QWidget):         #QWidget #QMainWindow
    """
    Interfaz gráfica visual
    """

    def __init__(self,fila,pantallaTotal = True,parent=None):
        #super(InterfazVideo, self).__init__(parent)
        QtGui.QWidget.__init__(self, None, QtCore.Qt.WindowStaysOnTopHint)
        # Parámetros constantes:
        self.titulo = 'Scape Room 2'
        self.thread = ThreadClass(fila)

        self.listaPreguntas =[] #id,pregunta,respuesta
        with open('./database/quest', 'r') as f:
            readData = f.read()
        for pregunta in readData.split('\n'):
            valores = pregunta.split(';')
            if len(valores) ==3:
                self.listaPreguntas.append(valores)
                #print('Agregado: ',self.listaPreguntas[-1])
        #print('Total: ',self.listaPreguntas)
        self.estadoActual = 1
        self.maximoNuemeroPreguntas = len(self.listaPreguntas)
        
        self.thread.start()
        self.connect(self.thread,QtCore.SIGNAL("INTRODUCI_CARACTER"),self.actualizarTexto)
        self.connect(self.thread,QtCore.SIGNAL("BORRAR"),self.borrarTexto)
        self.connect(self.thread,QtCore.SIGNAL("REVISAR"),self.revisarRespuesta)

        # Clases auxiliares: 
        self.initUI()
        # Al inicializarse la clase se muestra:
        if pantallaTotal:
            self.showFullScreen()
        else:
            self.show()
        #self.displayOverlay()


    def initUI(self):
        """
        Inicialización de sus parámetros
        """
        # Parte visual
        self.imagen = QtGui.QLabel(self)
        self.respuestaLabel = QtGui.QLabel('Respuesta:')
        self.intro = QtGui.QLineEdit('')
        self.intro.setMaximumWidth(400)
        self.intro.setPointSize(24)
        self.pregunta = QtGui.QLabel()
        self.pregunta.setFont(QtGui.QFont('SansSerif', 36))
        self.layoutTotalHorizontal = QtGui.QHBoxLayout()
        self.layoutGanador = QtGui.QHBoxLayout()
        
        self.imagenIzquierdaLayout = QtGui.QVBoxLayout()
        self.preguntasDerechaLayout = QtGui.QVBoxLayout()
        self.smallLayout = QtGui.QHBoxLayout()
        
        self.smallLayout.addWidget(self.respuestaLabel)
        self.smallLayout.addWidget(self.intro)

        self.preguntasDerechaLayout.addWidget(self.pregunta)
        self.preguntasDerechaLayout.addLayout(self.smallLayout)

        self.imagenIzquierdaLayout.addWidget(self.imagen)

        self.layoutTotalHorizontal.addLayout(self.imagenIzquierdaLayout)
        self.layoutTotalHorizontal.addLayout(self.preguntasDerechaLayout)

        self.actualizarLayout(self.estadoActual)
        
        self.setMinimumHeight(450)
        
        #self.setGeometry(300, 300, 300, 150)
        # Algunas visualizaciones:
        self.setWindowIcon(QtGui.QIcon('./imagenes/logo.png')) 
        
        self.setWindowTitle(self.titulo)
        
    def actualizarLayout(self,estado):
        self.pixmapAct = QtGui.QPixmap('./database/{}.png'.format(self.listaPreguntas[estado-1][0]))
        self.imagen.setPixmap(self.pixmapAct)
        self.pregunta.setText(self.listaPreguntas[estado-1][1])
        self.setLayout(self.layoutTotalHorizontal)
        if estado == 0:
            self.pregunta.setText('GANASTE!')
        
    def displayOverlay(self):
        self.popup = QtGui.QDialog(self,QtCore.Qt.WindowStaysOnTopHint)
        self.popup.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        
        self.pregunta = QtGui.QLabel('Respuesta')
        #self.pregunta.setMinimumWidth(500)
        self.intro = QtGui.QLineEdit('')
        
        f = self.intro.font()
        f.setPointSize(27)
        self.intro.setFont(f)
        self.intro.setMinimumWidth(500)
        #self.intro.setEchoMode(QtGui.QLineEdit.Password)
        self.intro.updateGeometry()
        self.miMensaje = QtGui.QHBoxLayout()
        #self.miMensaje.addWidget(self.pregunta)
        self.miMensaje.addWidget(self.intro)
        self.popup.setLayout(self.miMensaje)
        #position_x = (self.frameGeometry().width()-self.popup.frameGeometry().width())/2
        #position_y = (self.frameGeometry().height()-self.popup.frameGeometry().height())/2
        resolution = QtGui.QDesktopWidget().screenGeometry()
        position_x = (resolution.width() / 2) - (self.popup.frameGeometry().width() / 2)
        position_y = 7/8*((resolution.height()) - (self.popup.frameGeometry().height()))

        self.popup.move(position_x, position_y)
        #event.accept()
        self.popup.show()

    def keyPressEvent(self, e):
        """
        Se redefine la interacción con el teclado para que la tecla ESC cierre el GUI
        """
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()
    
    def actualizarTexto(self,valor):
        self.intro.setText(self.intro.text()+str(valor))

    def revisarRespuesta(self):
        #print('Intro: ',self.intro.text(),type(self.intro.text()))
        #print('Corr: ',self.listaPreguntas[self.estadoActual][2],type(self.listaPreguntas[self.estadoActual][1]))
        if self.intro.text() == self.listaPreguntas[self.estadoActual][2]:
            print(' Correcta')
            self.estadoActual += 1
            if self.estadoActual == self.maximoNuemeroPreguntas:
                self.actualizarLayout(0)
                time.sleep(10)
                self.estadoActual = 1
                self.actualizarLayout(self.estadoActual)
            else:
                self.actualizarLayout(self.estadoActual)
        else:
            print(' Incorrecta')

    def borrarTexto(self):
        self.intro.setText('')

class ThreadClass(QtCore.QThread):
    """
    Thread para revisión continua de la fila de registros
    """
    def __init__(self,fila,parent = None):
        """
        Constructor
        """
        super(ThreadClass,self).__init__(parent)
        

    def run(self):
        """
        Re implementación del método
        """
        while True:
            if not GUIParalela.miTeclado.teclas.empty():
                valor = GUIParalela.miTeclado.teclas.get() # valor = (estado, id, nombre)
                
                if valor == '*':
                    print('Introducido: ',GUIParalela.valorActual)
                    print('Y la respuesta es.... ')
                    self.emit(QtCore.SIGNAL('REVISAR'))
                    """
                    if GUIParalela.valorActual in self.listaPreguntas:
                        print(' Correcta')
                    else:
                        print(' Incorrecta')
                    """
                    GUIParalela.valorActual = ''
                    self.emit(QtCore.SIGNAL('BORRAR'))
                    #self.intro.setText(GUIParalela.valorActual)
                else:
                    if valor == '#':
                        GUIParalela.valorActual = ''
                        self.emit(QtCore.SIGNAL('BORRAR'))
                    else:
                        GUIParalela.valorActual+= str(valor)
                        self.emit(QtCore.SIGNAL('INTRODUCI_CARACTER'),valor)
                    #self.intro.setText(GUIParalela.valorActual)
                
                
if __name__ == '__main__':
    """
    Preguntas
    """
    pantalla = False
    for input in sys.argv:
        if input == 'Full':
            pantalla = True
    p = GUIParalela(fullScreen=pantalla)
    
    p.process.join() 

