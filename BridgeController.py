# Bridge_Controller.py
# coding=utf-8
import sys
import os

from PyQt5.QtWidgets import QMainWindow, QApplication,QPushButton,QGridLayout,QLabel,QWidget,QDialog,QComboBox,QCheckBox,QLineEdit,QInputDialog,QMessageBox,QTabWidget,QAction,QGraphicsView,QGraphicsScene
from PyQt5 import QtGui
from PyQt5.QtCore import QThread, pyqtSignal
import pyqtgraph as pg

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QSizePolicy

import serial
import serial.tools.list_ports
import time
import math
import logging
import threading
import random


BridgeSerial = serial.Serial()  # open serial port
#time.sleep(0.5)
#LARGE_FONT= ("Verdana", 12)

Resistances = {'1':'2.0 m'+u'\u03A9','01':'2.0 m'+u'\u03A9','2':'6.32 m'+u'\u03A9','02':'6.32 m'+u'\u03A9','3':'20.0 m'+u'\u03A9','03':'20.0 m'+u'\u03A9','4':'63.2 m'+u'\u03A9','04':'63.2 m'+u'\u03A9','5':'200 m'+u'\u03A9','05':'200 m'+u'\u03A9','6':'632 m'+u'\u03A9','06':'632 m'+u'\u03A9','7':'2'+u'\u03A9','07':'2'+u'\u03A9','8':'6.32'+u'\u03A9','08':'6.32'+u'\u03A9','9':'20.0'+u'\u03A9','09':'20.0'+u'\u03A9','10':'63.2'+u'\u03A9','11':'200'+u'\u03A9','12':'632'+u'\u03A9','13':'2.00 k'+u'\u03A9','14':'6.32 k'+u'\u03A9','15':'20.0 k'+u'\u03A9','16':'63.2 k'+u'\u03A9','17':'200 k'+u'\u03A9','18':'632 k'+u'\u03A9','19':'2.00 M'+u'\u03A9','20':'6.32 M'+u'\u03A9','21':'20.0 M'+u'\u03A9','22':'63.2 M'+u'\u03A9'}
Voltages = {'01':'2.00 uV','1':'2.00 uV','02':'6.32 uV','2':'6.32 uV','03':'20.0 uV','3':'20.0 uV','04':'63.2 uV','4':'63.2 uV','05':'200 uV','5':'200 uV','06':'532uV','6':'532uV','07':'2.0 mV','7':'2.0 mV','08':'6.32 mV','8':'6.32 mV','09':'20.0 mV','9':'20.0 mV','10':'63.2 mV','11':'200 mV','12':'632 mV'}

def find_n_sub_str(src, sub, pos, start):
    index = src.find(sub, start)
    if index != -1 and pos > 0:
        return find_n_sub_str(src, sub, pos - 1, index + 1)
    return index



class BridgeController(QMainWindow):

    def __init__(self):
        super().__init__()
        
        self.widget = QWidget()
        self.setCentralWidget(self.widget)
        self.grid = QGridLayout()
        self.widget.setLayout(self.grid)
        self.grid.setSpacing(20)
        
        self.serial_ports_available = []
        self.serial_ports_available = self.SerialPorts()
        if len(self.serial_ports_available) == 0:
            self.var_serial_port = ""
        else:
            self.var_serial_port = self.serial_ports_available[0]
        self.menu_port = QComboBox(self)
        self.PortMenu()
        self.initUI()

    def initUI(self):

        self.statusBar().showMessage('Ready')
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('BridgeController')

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
        
        if BridgeSerial.is_open:
            self.hide()
            self.next_page = Second(self)
            self.next_page.show()
        else:
            self.statusBar().showMessage('Port is not opened')

    def PortMenu(self):
        self.menu_port.addItem(str(self.var_serial_port))
        self.menu_port.activated.connect(self.SetPort)

    def SetPort(self):
        BridgeSerial.port = str(self.var_serial_port)
        BridgeSerial.baudrate = 9600
        BridgeSerial.timeout = 1
        BridgeSerial.parity = serial.PARITY_ODD
        BridgeSerial.bytesize = serial.SEVENBITS
        BridgeSerial.stopbits = serial.STOPBITS_ONE

        try:
            BridgeSerial.open()
        except Exception as e:
            self.statusBar().showMessage("error open serial port: "+str(e))
        else:
            self.statusBar().showMessage("Open port: "+BridgeSerial.port)


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
        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result

    def RollCall(self):
        if BridgeSerial.is_open:
            BridgeSerial.write(str.encode('*IDN?\n'))
            try:
                self.lineinput=BridgeSerial.readline()
            except serial.SerialException as e:
                self.label_rollcall.setText("Minion not recognized")
            except Exception as e:
                print ("error doing roll-call: "+str(e))
            else:
                if self.lineinput == "":
                    self.label_rollcall.setText("Minion did not respond to roll call")
                else:
                    
                    self.label_rollcall.setText(self.lineinput.decode('utf-8').strip())

        else:
            self.statusBar().showMessage('Port is not opened')
            pass
                
class Second(QMainWindow):
     def __init__(self,first_page):
        super().__init__()
        self.statusBar().showMessage("Ready")
        self.first_page = first_page
        self.setWindowTitle('Performance')
        self.setGeometry(300, 300, 290, 150)
        self.table_widget = TableWidget(self,self.first_page)
        self.setCentralWidget(self.table_widget)
        
        self.show()



class TableWidget(QWidget):
    def __init__(self,parent,first_page):
        super(QWidget, self).__init__(parent)
        self.parent=parent
        self.statusBar = parent.statusBar()
        self.layout = QGridLayout(self)
        
        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tabs.resize(300,200)
        
        # Add tabs
        self.tabs.addTab(self.tab1,"Scan")
        self.tabs.addTab(self.tab2,"Plot")
        
        # Create first tab
        self.grid = QGridLayout()
        self.tab1.setLayout(self.grid)
        self.grid.setColumnStretch(1, 1)


        self.grid_tab2 = QGridLayout()
        self.tab2.setLayout(self.grid_tab2)
        self.grid_tab2_btn = QGridLayout()
        self.grid_tab2.addLayout(self.grid_tab2_btn,1,1)
        
        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        
        self.first_page = first_page

        self.grid.setSpacing(20)
        self.readings = 4
        self.logpath = os.path.abspath('.')

        
         
        self.initUI()
        
        
    def initUI(self):
        
        self.setWindowTitle('Performance')
        
        self.label_measurement = QLabel(self)
        self.grid.addWidget(self.label_measurement,1,1)
        self.label_measurement.setText("Measurement")
        self.label_measurement.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))

        
          
        self.label_channel = QLabel(self)
        self.grid.addWidget(self.label_channel,1,2)
        self.label_channel.setText("Channel")
        self.label_channel.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))

        self.label_on = QLabel(self)
        self.grid.addWidget(self.label_on,1,3)
        self.label_on.setText("On?")
        self.label_on.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))

        self.label_temperature = QLabel(self)
        self.grid.addWidget(self.label_temperature,1,4)
        self.label_temperature.setText("Temperature")
        self.label_temperature.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))
        
        self.label_resistance = QLabel(self)
        self.grid.addWidget(self.label_resistance,1,5)
        self.label_resistance.setText("Resistance Range")
        self.label_resistance.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))

        self.label_excitation = QLabel(self)
        self.grid.addWidget(self.label_excitation,1,6)
        self.label_excitation.setText("Excitation")
        self.label_excitation.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))

        self.label_range = QLabel(self)
        self.grid.addWidget(self.label_range,1,7)
        self.label_range.setText("Range")
        self.label_range.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))

        self.label_thermometer = QLabel(self)
        self.grid.addWidget(self.label_thermometer,1,8)
        self.label_thermometer.setText("Thermometer")
        self.label_thermometer.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))

        self.label_method = QLabel(self)
        self.grid.addWidget(self.label_method,1,9)
        self.label_method.setText("Method")
        self.label_method.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))

        self.channels = []
        for i in range(0,16):
            self.channels.append(self.Channel(self,i+1))

        self.btn_begin = QPushButton("Begin",self)
        self.grid.addWidget(self.btn_begin,0,2)
        self.btn_begin.clicked.connect(self.BeginDAQ)


        self.btn_pause = QPushButton("Stop",self)
        self.grid.addWidget(self.btn_pause,0,3)
        self.btn_pause.clicked.connect(self.Pause)

        self.btn_back = QPushButton("Back",self)
        self.grid.addWidget(self.btn_back,0,1)
        self.btn_back.clicked.connect(self.Back)

        self.btn_seconds = QPushButton("Seconds Between Readings: "+ str(self.readings),self)
        self.grid.addWidget(self.btn_seconds,18,1)
        self.btn_seconds.clicked.connect(self.ReadSeconds)

        self.label_logpath = QLabel("Log File Path: ",self)
        self.grid.addWidget(self.label_logpath,19,1)

        self.line_logpath = QLineEdit(self)
        self.grid.addWidget(self.line_logpath,19,2,1,3)
        self.line_logpath.setText(self.logpath)

        self.btn_readme = QPushButton("Read Me",self)
        self.grid.addWidget(self.btn_readme,0,8)
        self.btn_readme.clicked.connect(self.ReadMe)
        self.btn_readme.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))

        try:
            self.file_conversion = open('thermometer.txt',"r")
        except:
            print("Conversion File Lost")
        else: 
            self.lines = self.file_conversion.readlines()
            self.file_conversion.close()


        self.plot = Plot(width=8, height=6, dpi=100)
        self.grid_tab2.addWidget(self.plot,1,2,2,2)
        self.plot.axes.plot()
        self.plotupdate = self.PlotUpdate(2,self)
        plt.autoscale(enable=True)
        plt.ylabel("temperature/K")

        self.btn_length = QPushButton("Plot Length: "+ str(self.plotupdate.length),self)
        self.grid_tab2_btn.addWidget(self.btn_length,18,1)
        self.btn_length.clicked.connect(self.PlotLength)

        self.btn_refresh = QPushButton("Refresh Status")
        self.grid.addWidget(self.btn_refresh,0,4)
        self.btn_refresh.clicked.connect(self.RefreshStatus)
        
        self.statusBar.showMessage("Ready")


    def RefreshStatus(self):
        for i in range(0,16):
            self.channels[i].menu_range.currentIndexChanged.disconnect(self.channels[i].ChangeRange)
            self.channels[i].menu_excitation.currentIndexChanged.disconnect(self.channels[i].ChangeExcitation)
            self.channels[i].Status(self)
            self.channels[i].menu_range.currentIndexChanged.connect(self.channels[i].ChangeRange)
            self.channels[i].menu_excitation.currentIndexChanged.connect(self.channels[i].ChangeExcitation)
        self.statusBar.showMessage("Refreshed")

    def PlotLength(self):
        seconds, ok = QInputDialog.getInt(self, 'Plot Length',"Enter the data points to plot (enter 0 for whole data):", 100, 0, 1000, 1 )
        if ok:
            self.plotupdate.length = seconds
        self.btn_length.setText("Plot Length: "+ str(self.plotupdate.length))
        self.statusBar.showMessage("Plot Length changed to "+str(self.plotupdate.length))

            



    def ReadMe(self):
        readme = QMessageBox.information(self,"Read Me","To avoid crash down, please do any operation after status bar gives you feedback!\n Without stop scan, data will not be logged!!!",QMessageBox.Yes )
        

    def ReadSeconds(self):
        seconds, ok = QInputDialog.getInt(self, 'Seconds Between Readings',"Enter the seconds between readings", 4, 1, 20, 1 )
        if ok:
            self.readings = seconds
        self.btn_seconds.setText("Seconds Between Readings: "+ str(self.readings))
        self.statusBar.showMessage("Seconds Between Readings Changed to "+str(self.readings))
    

    def Back(self):
        self.parent.hide()
        self.first_page.show()

    def BeginDAQ(self):
        self.thread_scan = self.Scan(1,self)
        self.thread_scan.start()

    def Pause(self):
        try:
            self.thread_scan
        except AttributeError:
            pass
        else:
            self.thread_scan.stop()
            del self.thread_scan


        

    class Scan(QThread):
        signal_pause = pyqtSignal(str)

        def __init__(self,rest,window,parent=None):
            super().__init__(parent)
            self._rest = rest
            self.window = window
            self.working = True
            self.times = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            
#            open(self.window.line_logpath.text() +'\\'+'Temperature_' + time.strftime('%Y%m%d',time.localtime(int(round(time.time()*1000))/1000)) + '.txt','a' )
            print((self.window.line_logpath.text() + '\\'+time.strftime('%Y%m%d%H%M%S',time.localtime(int(round(time.time()*1000))/1000)) + '.txt'))
            self.window.statusBar.showMessage("Log File Created")

        def stop(self):
            self.window.statusBar.showMessage("Log File Saved")
            self.logfile.close()
            self.working = False
            self.wait()
            self.window.statusBar.showMessage("Scan Stopped")
            

        def run(self):
            while self.working:
                for i in range(0,16):
                    if self.working:
                        if self.window.channels[i].checkbox_channel.isChecked():
                            self.window.channels[i].DAQ()
                            self.times[i] += 1
                            print("Scanning CH"+str(i+1))
                            self.log(i)
                            self.window.statusBar.showMessage("Scaned CH "+str(i+1)+'  '+str(self.times[i]))
                            time.sleep(self.window.readings)
                        else:
                            time.sleep(0.1)
                            continue
                    else:
                        break

        def log(self,i):
            now = time.strftime('%Y%m%d%H%M%S',time.localtime(int(round(time.time()*1000))/1000))
            measurement = self.window.channels[i].line_measurement.text()
            try:
                self.window.channels[i].temperature
            except:
                temperature = "N/A"
            else:
                temperature = self.window.channels[i].temperature
            resistance = self.window.channels[i].resistance
            with open(self.window.line_logpath.text() +'\\'+'Temperature_' + time.strftime('%Y%m%d',time.localtime(int(round(time.time()*1000))/1000)) + '.txt','a' ) as self.logfile:
                if type(temperature) is float:
                    self.logfile.write(str(now)+'\t'+'CH'+str(i+1)+'\t'+str("%.6f" % temperature)+' K '+'\n')
                else:
                    self.logfile.write(str(now)+'\t'+'CH'+str(i+1)+'\t'+str(temperature)+' K '+'\n')


    class PlotUpdate(QThread):
        signal_pause = pyqtSignal(str)

        def __init__(self,rest,window,parent=None):
            super().__init__(parent)
            self._rest = rest
            self.window = window
            self.working = False
            self.channel = 1
            self.length = 100
            self.window.statusBar.showMessage("Begin to plot")

        def stop(self):
            self.window.statusBar.showMessage("Log File Saved")
            self.logfile.close()
            self.working = False
            self.wait()
            self.window.statusBar.showMessage("Scan Stopped")
            

        def run(self):
            while True:
                if self.working:
                    self.window.plot.axes.cla()
                    self.window.plot.axes.grid()
                    self.window.plot.axes.title.set_text("temperature of CH "+str(self.channel))
                    if len(self.window.channels[self.channel-1].array_temperature) == 0:
                        pass
                    elif self.length == 0:
                        self.window.plot.axes.scatter(range(0,len(self.window.channels[self.channel-1].array_temperature)),self.window.channels[self.channel-1].array_temperature,c='k')
                    elif len(self.window.channels[self.channel-1].array_temperature) < self.length:
                        self.window.plot.axes.scatter(range(0,len(self.window.channels[self.channel-1].array_temperature)),self.window.channels[self.channel-1].array_temperature,c='k')
                    else :
                        self.window.plot.axes.scatter(range(0,len(self.window.channels[self.channel-1].array_temperature[-(self.length+1):-1])),self.window.channels[self.channel-1].array_temperature[-(self.length+1):-1],c='k')                        
                    self.window.plot.draw()
                time.sleep(1)



    class Channel():
        def __init__(self,window,channel):
            self.channel = channel
            self.window = window
            self.name = "CH "+str(channel)
            self.resistance = float(0)
            self.temperature = "Out of Range"
            self.array_resistance = []
            self.array_temperature = []
            self.line_measurement = QLineEdit(window)
            window.grid.addWidget(self.line_measurement,channel+1,1,1,1)
            
            self.btn_channel = QPushButton(window)
            window.grid.addWidget(self.btn_channel,channel+1,2)
            self.btn_channel.setText("CH "+str(channel))
            self.btn_channel.clicked.connect(self.Click)

            self.label_temperature = QLabel(window)
            window.grid.addWidget(self.label_temperature,channel+1,4)
            self.label_temperature.setText("N/A")
            
            self.label_resistance = QLabel(window)
            window.grid.addWidget(self.label_resistance,channel+1,5)
            self.label_resistance.setText("N/A")

            self.checkbox_channel = QCheckBox("CH "+str(self.channel),window)
            window.grid.addWidget(self.checkbox_channel,channel+1,3)
            self.checkbox_channel.stateChanged.connect(self.StateChange)


            self.menu_excitation = QComboBox(window)
            window.grid.addWidget(self.menu_excitation,self.channel+1,6)
            self.ExcitationMenu()

            self.menu_range = QComboBox(window)
            window.grid.addWidget(self.menu_range,self.channel+1,7)
            self.RangeMenu()

            self.menu_thermometer = QComboBox(window)
            window.grid.addWidget(self.menu_thermometer,self.channel+1,8)
            self.ThermometerMenu()
            self.menu_thermometer.currentIndexChanged.connect(self.ChangeThermometer)

            self.menu_method = QComboBox(window)
            window.grid.addWidget(self.menu_method,self.channel+1,9,1,3)
            self.menu_method.currentIndexChanged.connect(self.ChangeMethod)

            self.status = ""
            self.Status(window)
            self.menu_excitation.currentIndexChanged.connect(self.ChangeExcitation)
            self.menu_range.currentIndexChanged.connect(self.ChangeRange)

            self.btn_plot = QPushButton()
            self.btn_plot.setText("CH "+str(self.channel))
            self.window.grid_tab2_btn.addWidget(self.btn_plot,channel,1)
            self.btn_plot.clicked.connect(self.PlotChannel)


           

        def PlotChannel(self):
            self.window.plotupdate.working = True
            self.window.plotupdate.channel = self.channel
            self.window.plotupdate.start()

        
        def StateChange(self):
            if self.checkbox_channel.isChecked():
                self.window.statusBar.showMessage("Set CH "+str(self.channel)+" To On")
            else:
                self.window.statusBar.showMessage("Set CH "+str(self.channel)+" To Off")

        def ExcitationMenu(self):
            
            for i in range(1,13):
                self.menu_excitation.addItem(Voltages[str(i)])


        def RangeMenu(self):

            for i in range(1,23):
                self.menu_range.addItem(Resistances[str(i)])
            
        def ChangeExcitation(self):
            self.voltage = self.menu_excitation.currentIndex() + 1        
            BridgeSerial.write(str.encode('RDGRNG '+str(self.channel)+',0,'+str(self.voltage)+','+str(self.range)+',0'+',0'+'\n'))
            self.window.statusBar.showMessage("Change CH"+str(self.channel)+" Excitation Voltage to "+Voltages[str(self.voltage)])
                       

        def ChangeRange(self):
            self.range = self.menu_range.currentIndex() + 1        
            BridgeSerial.write(str.encode('RDGRNG '+str(self.channel)+',0,'+str(self.voltage)+','+str(self.range)+',0'+',0'+'\n'))
            self.window.statusBar.showMessage("Change CH"+str(self.channel)+" Resistance Range to "+Resistances[str(self.range)])

        def ChangeMethod(self):
            self.window.statusBar.showMessage("Set CH "+str(self.channel)+" Method To " +self.menu_method.currentText() )
        
        def Click(self):
#            while True:
#                random_resistance = random.uniform(5530,69999)
#                self.resistance = random_resistance
#                self.RtoT()
#                print(self.temperature)
#                if not str(self.temperature).startswith('Out'):
#                    break
#            self.label_resistance.setText(str(self.resistance)+u'\u03A9')
#            self.array_temperature.append(self.temperature)
#            self.RtoT()
            self.DAQ()
            self.window.statusBar.showMessage("Scaned CH "+str(self.channel))

        def DAQ(self):
            BridgeSerial.write(str.encode('RDGST?'+str(self.channel)+'\n'))
            self.work_or_not = BridgeSerial.readline()
            if self.work_or_not != b'000\r\n':
                self.indicator = self.StatusIndicator(self.work_or_not)
                self.label_resistance.setText(self.indicator)
            else:
                BridgeSerial.write(str.encode('RDGR?'+str(self.channel)+'\n'))
                try:
                    self.lineinput=BridgeSerial.readline()
                except Exception as e:
                    self.label_resistance.setText("error doing DAQ: "+str(e))
                else:
                    if self.lineinput == "":
                        self.label_resistance.setText("Read Resistance Error")
                    else:
                        self.lineinput = self.lineinput.decode('utf-8').strip()
                        self.resistance = float(self.lineinput[0:self.lineinput.find('E',0)]) * pow(10,int(self.lineinput[self.lineinput.find('E',0)+1:]))
                        
                        self.label_resistance.setText(str("%.6f" % self.resistance)+u'\u03A9')
                        self.RtoT()
                        if type(self.temperature) is float:
                            self.array_temperature.append(self.temperature)

        def StatusIndicator(self,weight):
            status = ['CS OVL ','VCM OVL ','VMIX OVL ','VDIF OVL ','R. OVER ','R. UNDER ','T. OVER ','T. UNDER ']
            for i in range(0,8):
                if bin(int(weight.strip().decode('utf-8')))[-(i+1)] == '1':
                    return status[i]
                else:
                    continue
                    

        def Status(self,window):
            BridgeSerial.write(str.encode('RDGST?'+str(self.channel)+'\n'))
            self.work_or_not = BridgeSerial.readline()
            if ( self.work_or_not == b'000\r\n'):
                BridgeSerial.write(str.encode('RDGRNG?'+str(self.channel)+'\n'))
                try:
                    self.lineinput=BridgeSerial.readline()
                except Exception as e:
                    self.label_resistance.setText("error : "+str(e))
                else:
                    if self.lineinput == "":
                        self.label_resistance.setText("Read Error")
                    else:
                        self.lineinput = str(self.lineinput)
                        self.status = self.lineinput
                        self.range = (self.lineinput[find_n_sub_str(self.lineinput,',',1,0)+1:find_n_sub_str(self.lineinput,',',2,0)])
                        if (int(self.range) <= 22):
                            self.menu_range.setCurrentIndex(int(self.range)-1)
                            self.range = int(self.range)
                        else:
                            pass

                        self.voltage = self.lineinput[find_n_sub_str(self.lineinput,',',0,0)+1:find_n_sub_str(self.lineinput,',',1,0)]
                        if(int(self.voltage) <= 12):
                            self.menu_excitation.setCurrentIndex(int(self.voltage)-1)
                            self.voltage = int(self.voltage)
                        else:
                            pass
            else:
                pass

        def ChangeThermometer(self):
            self.menu_method.clear()
            if self.menu_thermometer.currentText() == ' ':
                self.menu_method.addItem(' ')
            elif self.menu_thermometer.currentText() == 'ca04':
                self.menu_method.addItem('linear interpolation')
            elif self.menu_thermometer.currentText() == '501':
                self.menu_method.addItem('linear interpolation')
            elif self.menu_thermometer.currentText() == '541':
                self.menu_method.addItem('chebychev')
            elif self.menu_thermometer.currentText() == 'x94607':
                self.menu_method.addItem('chebychev')
            elif self.menu_thermometer.currentText() == 'x94606':
                self.menu_method.addItem('chebychev')
            elif self.menu_thermometer.currentText() == 'x30259':
                self.menu_method.addItem('chebychev')
            elif self.menu_thermometer.currentText() == 'x30314':
                self.menu_method.addItem('chebychev')
            elif self.menu_thermometer.currentText() == 'x46547':
                self.menu_method.addItem('linear interpolation')
                self.menu_method.addItem('chebychev')
            elif self.menu_thermometer.currentText() == 'p14271':
                self.menu_method.addItem('linear interpolation')
                self.menu_method.addItem('chebychev')
            elif self.menu_thermometer.currentText() == '30256':
                self.menu_method.addItem('linear interpolation')
                self.menu_method.addItem('chebychev')
            elif self.menu_thermometer.currentText() == 'sf15':
                self.menu_method.addItem('linear interpolation')
            elif self.menu_thermometer.currentText() == 'sf05':
                self.menu_method.addItem('linear interpolation')
            elif self.menu_thermometer.currentText() == 'sf25':
                self.menu_method.addItem('linear interpolation')
            elif self.menu_thermometer.currentText() == 'pt100':
                self.menu_method.addItem('linear interpolation')
            elif self.menu_thermometer.currentText() == 'x46545':
                self.menu_method.addItem('linear interpolation')
            elif self.menu_thermometer.currentText() == 'x48597':
                self.menu_method.addItem('linear interpolation')
            elif self.menu_thermometer.currentText() == 'x48759':
                self.menu_method.addItem('linear interpolation')


        def ThermometerMenu(self):
            thermometer = [' ','ca04','501','541','x94607','x94606','x30259','x30314','x46547','p14271','30256','sf15','sf05','sf25','pt100','x46545','x48597','x48759']
            for i in range(0,18):
                self.menu_thermometer.addItem(thermometer[i])
            

        def RtoT(self):
            if self.menu_method.currentText() == 'linear interpolation':
                start = 0
                end = 0
                i = -1
                for line in self.window.lines:
                    i+=1
                    if line.startswith('begin-look '+self.menu_thermometer.currentText()):
                        start = i
                    if line.startswith('end-look '+self.menu_thermometer.currentText()):
                        end = i
                array_resistance = []
                array_temperature = []
                for i in range(start+1,end):
                    array_resistance.append(float(self.window.lines[i].split('\t')[0]))
                    array_temperature.append(float(self.window.lines[i].split('\t')[1]))
                if self.resistance < array_resistance[0] or self.resistance > array_resistance[-1]:
                    self.temperature = "Out of Range"
                    self.label_temperature.setText(str(self.temperature))
                    return
                for i in range(0,len(array_resistance)-1):
                    if self.resistance > array_resistance[i] and self.resistance < array_resistance[i+1]:
                        self.temperature = float(array_temperature[i] + ( array_temperature[i+1] - array_temperature[i] ) * (self.resistance - array_resistance[i]) / (array_resistance[i+1] - array_resistance[i]))
                        self.label_temperature.setText(str("%.6f" % self.temperature)+" K")
            elif self.menu_method.currentText() == 'chebychev':
                start = []
                end = []
                i = -1
                for line in self.window.lines:
                    i+=1
                    if line.startswith('begin-cheb '+self.menu_thermometer.currentText()):
                        start.append(i)
                    if line.startswith('end-cheb '+self.menu_thermometer.currentText()):
                        end.append(i)
                coe = []
                z = 0
                zu = 0
                zl = 0
                for i in range(0,len(start)):
                    if self.window.lines[start[i]+1].startswith('log'):
                        z = math.log(self.resistance)/math.log(10)
                    elif self.window.lines[start[i]+1].startswith('lin'):
                        z = self.resistance
                    zl = float(self.window.lines[start[i]+2])
                    zu = float(self.window.lines[start[i]+3])
                    if z < zu and z > zl:
                        break
                if z > zu or z < zl:
                    self.temperature = "Out of Range"
                    self.label_temperature.setText(str(self.temperature))
                    return
                x = ((z - zl) - (zu - z))/(zu - zl)
                for i in range(start[i]+4,end[i]):
                    coe.append(float(self.window.lines[i].split('\t')[1]))
                    print(float(self.window.lines[i].split('\t')[1]))
                T = 0
                for i in range(0,len(coe)):
                    T = T + coe[i]*math.cos(i*math.acos(x))
                    print (T)
                self.temperature = T
                self.label_temperature.setText(str("%.6f" % self.temperature)+" K")


class Plot(FigureCanvas):
 
    def __init__(self, parent=None, width=10, height=8, dpi=100):

        self.length = 100
 
        self.fig = Figure(figsize=(width, height), dpi=dpi) 
 
        self.axes = self.fig.add_subplot(1, 1, 1)
        self.axes.title.set_text("temperature")
        self.axes.grid()
 
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
 
 
        FigureCanvas.setSizePolicy(self, 
                                        QSizePolicy.Expanding, 
                                        QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        


                
            
if __name__ == '__main__':

    app = QApplication(sys.argv)

    Controller = BridgeController()

    Controller.show()
    
    
    sys.exit(app.exec_())
