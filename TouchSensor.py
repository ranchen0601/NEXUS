# Touch_Sensor.py
# coding=utf-8
import sys
import os

from PyQt5.QtWidgets import QMainWindow, QApplication,QPushButton,QGridLayout,QLabel,QWidget,QDialog,QComboBox,QCheckBox,QLineEdit,QInputDialog,QMessageBox,QTabWidget,QAction,QGraphicsView,QGraphicsScene
from PyQt5 import QtGui
from PyQt5.Qt import QMutex,QObject
from PyQt5.QtCore import QThread, pyqtSignal
import pyqtgraph as pg
import glob

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from PyQt5.QtWidgets import QSizePolicy

from datetime import datetime
import serial
import serial.tools.list_ports
import time
import math
import logging
import threading
import random

SensorSerial = serial.Serial()  # open serial port
#time.sleep(0.5)
#LARGE_FONT= ("Verdana", 12)

mutex = QMutex()



class Write(QObject):
    signal_begin = pyqtSignal(str)
    
    def __init__(self,rest):
#        QObject().__init__(self)
        self.mutex = QMutex()
        
    def WriteCMD(self,command):
        self.mutex.lock()
        SensorSerial.write(str.encode(str(command)))
        readline = SensorSerial.readline().decode('utf-8').strip()
        self.mutex.unlock()
        return readline

#command = pyqtSignal(str)


class TouchSensor(QMainWindow):

    def __init__(self):
        super().__init__()

        self.widget = QWidget()
        self.setCentralWidget(self.widget)
        self.grid = QGridLayout()
        self.widget.setLayout(self.grid)
        self.grid.setSpacing(20)

        self.serial_ports_available = []
        self.serial_ports_available = self.SerialPorts()
        self.menu_port = QComboBox(self)
        self.menu_port.addItems(self.serial_ports_available)
        # if len(self.serial_ports_available) == 0:
        #     self.var_serial_port = ""
        # else:
        #     self.var_serial_port = self.serial_ports_available[0]
        self.PortMenu()
        self.initUI()

    def initUI(self):

        self.statusBar().showMessage('Ready')
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Touch Sensor')

        self.label_config = QLabel(self)
        self.label_config.setText('Configuration')
        self.label_config.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))
        self.grid.addWidget(self.label_config,1,1)

        self.grid.addWidget(self.menu_port,2,1)

        self.btn_rollcall = QPushButton('Roll Call',self)
        self.grid.addWidget(self.btn_rollcall,3,1)
        self.btn_rollcall.clicked.connect(self.RollCall)

        self.label_rollcall = QLabel(self)
        self.label_rollcall.setText('N/A')
        self.label_rollcall.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))
        self.grid.addWidget(self.label_rollcall,4,1)

        self.btn_performance = QPushButton('Performance Page', self)
        self.grid.addWidget(self.btn_performance,5,1)
        self.btn_performance.clicked.connect(self.PerformancePage)




    def PerformancePage(self):
        try:
            self.next_page
        except:
            pass
        else:
            self.hide()
            self.next_page.show()
            return

        if SensorSerial.is_open:
            self.hide()
            self.next_page = Second(self)
            self.next_page.show()
        else:
            self.statusBar().showMessage('Port is not opened')

    def PortMenu(self):
#         self.menu_port.addItem(str(self.var_serial_port))
         self.menu_port.activated.connect(self.SetPort)

    def SetPort(self):
        if (SensorSerial.is_open):
            SensorSerial.close()
        SensorSerial.port = str(self.menu_port.currentText())
        SensorSerial.baudrate = 9600
        SensorSerial.timeout = 0.5
#        SensorSerial.parity = serial.PARITY_ODD
#        SensorSerial.bytesize = serial.SEVENBITS
#        SensorSerial.stopbits = serial.STOPBITS_ONE

        try:
            SensorSerial.open()
        except Exception as e:
            self.statusBar().showMessage("error open serial port: "+str(e))
        else:
            self.statusBar().showMessage("Open port: "+SensorSerial.port)


    def SerialPorts(self):
        """ Lists serial port names
        :raises EnvironmentError:
        On unsupported or unknown platforms
        :returns:
        A list of the serial ports available on the system
        """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')
        result = ['']
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result

    def RollCall(self):
        

        
        if SensorSerial.is_open:
            try:
                self.lineinput = write.WriteCMD('R')
            except serial.SerialException as e:
                self.label_rollcall.setText("Minion not recognized")
            except Exception as e:
                print ("error doing roll-call: "+str(e))
            else:
                if self.lineinput == "":
                    self.label_rollcall.setText("Minion did not respond to roll call")
                else:

                    self.label_rollcall.setText(self.lineinput)

        else:
            self.statusBar().showMessage('Port is not opened')
            pass

class Second(QMainWindow):
    def __init__(self,first_page):
        super().__init__()
#        self.statusBar().showMessage("Ready")
#        self.first_page = first_page
#        self.setWindowTitle('Performance')
#        self.setGeometry(300, 300, 290, 150)

        self.widget = QWidget()
        self.setCentralWidget(self.widget)
        self.grid = QGridLayout()
        self.widget.setLayout(self.grid)
        self.grid.setSpacing(20)

        self.grid.setSpacing(20)
        self.readings = 4
        self.logpath = os.path.abspath('.')

        self.initUI()


    def initUI(self):

        self.statusBar().showMessage('Ready')
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('BridgeController')

        self.label_measurement = QLabel(self)
        self.grid.addWidget(self.label_measurement,1,1)
        self.label_measurement.setText("Input")
        self.label_measurement.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))

        self.label_measurement2 = QLabel(self)
        self.grid.addWidget(self.label_measurement2,1,2)
        self.label_measurement2.setText("Touch")
        self.label_measurement2.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))



        self.btn_begin = QPushButton("Begin",self)
        self.grid.addWidget(self.btn_begin,0,1)
        self.btn_begin.clicked.connect(self.BeginDAQ)


        self.btn_pause = QPushButton("Stop",self)
        self.grid.addWidget(self.btn_pause,0,2)
        self.btn_pause.clicked.connect(self.Pause)

        self.label_pin = QLabel(self)
        self.grid.addWidget(self.label_pin,2,1)
        self.label_pin.setText('NA')
        self.label_pin.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))

        self.label_touch = QLabel(self)
        self.grid.addWidget(self.label_touch,2,2)
        self.label_touch.setText('NA')
        self.label_touch.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))

        self.btn_seconds = QPushButton("Freq: "+ str(self.readings),self)
        self.grid.addWidget(self.btn_seconds,4,1)
        self.btn_seconds.clicked.connect(self.ReadSeconds)

        self.label_logpath = QLabel("Log File Path: ",self)
        self.grid.addWidget(self.label_logpath,3,1)

        self.line_logpath = QLineEdit(self)
        self.grid.addWidget(self.line_logpath,3,2,1,3)
        self.line_logpath.setText(self.logpath)

        self.pin=0
        self.touch=""

    def ReadSeconds(self):
        seconds, ok = QInputDialog.getDouble(self, 'Seconds Between Readings',"Enter the seconds between readings", 4, 0.1, 20, 1 )
        if ok:
            self.readings = seconds
        self.btn_seconds.setText("Seconds Between Readings: "+ str(self.readings))
        self.statusBar().showMessage("Seconds Between Readings Changed to "+str(self.readings))


    def Back(self):
        self.parent.hide()
        self.first_page.show()

    def BeginDAQ(self):
        try:
            self.thread_scan
        except:
            self.thread_scan = self.Scan(1,self)
            self.thread_scan.start()
        else:
            self.thread_scan.resume()

    def Pause(self):
        try:
            self.thread_scan
        except AttributeError:
            pass
        else:
            self.thread_scan.stop()

    def DAQ(self):
        lineinput = write.WriteCMD('Q')
        self.lineinput = lineinput
        self.touch = str(self.lineinput[0:self.lineinput.find(":")])
        self.pin = int(self.lineinput[self.lineinput.find(":")+1:])


    class Scan(QThread):
        signal_pause = pyqtSignal(str)

        def __init__(self,rest,window,parent=None):
            super().__init__(parent)
            self._rest = rest
            self.window = window
            self.working = True

            print((self.window.line_logpath.text() + '/'+time.strftime('%Y%m%d%H%M%S',time.localtime(int(round(time.time()*1000))/1000)) + '.txt'))
            self.window.statusBar().showMessage("Log File Created")

        def stop(self):
            self.window.statusBar().showMessage("Log File Saved")
            self.working = False
            self.window.statusBar().showMessage("Scan Stopped")

        def resume(self):
            self.window.statusBar().showMessage("Resume Scan")
            self.working = True


        def run(self):
            while self.working:
                self.window.DAQ()
                self.window.label_pin.setText(str(self.window.pin))
                self.window.label_touch.setText(str(self.window.touch))
                self.log()
                time.sleep(self.window.readings)
                time.sleep(0.1)

        def log(self):
            now = time.strftime('%Y%m%d%H%M%S',time.localtime(int(round(time.time()*1000))/1000))
            Pin = self.window.pin
            Touch = self.window.touch
            with open(self.window.line_logpath.text() +'//'+'TouchSensor_' + time.strftime('%Y%m%d',time.localtime(int(round(time.time()*1000))/1000)) + '.txt','a' ) as self.logfile:
                if os.stat(self.logfile.name).st_size == 0:
                    self.logfile.write("Input\tTouch\tTime\n")
                if type(Pin) is float:
                    Pin = "%.6f" % Pin
                self.logfile.write( str(Pin) + '\t' + str(Touch) + datetime.now().isoformat(sep=' ', timespec='milliseconds') + '\n')








if __name__ == '__main__':

    app = QApplication(sys.argv)

    write = Write(1)    

    Controller = TouchSensor()

    Controller.show()


    sys.exit(app.exec_())
