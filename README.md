# Scape Room
Interfaz gráfica construida en PyQt4 para una genial experiencia de usuario

Para correr el programa actual en un Raspberry pi necesitamos primeramente instalar todas las librerías requeridas por el mismo:

```
sudo apt-get update
sudo apt-get install python3-pyqt4
sudo apt-get install python3-pyqt4.phonon-dbg
```

Para correr el programa ejecute los siguientes comandos desde una terminal


```
python3 questions.py Full
python3 videos.py Full
```

El parámetro Full ingresa el programa en modo pantalla completa y es opcional

En caso de desear que el programa se ejecute al prender la raspberry pi siga los siguientes pasos:

Creamos un auto ejecutable de inicio para terminal
```
nano /home/pi/.config/autostart/lxterm-autostart.desktop
```

E introducimos el siguiente código:

```
[Desktop Entry]
Encoding=UTF-8
Name=Terminal autostart
Comment=Start a terminal and list directory
Exec=lxterminal
```

Por otro lado configuramos el terminal para que lance el programa al inicio

```
nano /home/pi/.bashrc 
```

E introducimos al final el siguiente código para el programa de preguntas:

```
echo "Running at Boot"
sleep 1
cd /home/pi/trafficFlow/scape/
python3 questions.py Full
```

O el siguiente para el programa de video:

```
echo "Running at Boot"
cd /home/pi/trafficFlow/scape/
python3 video.py Full
```

Todas las imagenes y preguntas son intercambiables y agregables

El programa asume que el teclado matricial está conectado en los pines

ROW = [29,31,33,35]
COL = [37,36,38,40]

Y el relé está en el pin 7, con la numeración de tablero de la raspberry pi como se muestra en la imagen:

![alt text](https://github.com/alvarohurtadobo/scape/blob/master/pinout.png)