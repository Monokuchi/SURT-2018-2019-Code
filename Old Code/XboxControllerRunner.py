import pygame
import serial
import sys
import os
import sys
import math
from pygame.locals import *
from serial.tools.list_ports import comports
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class GUI(QWidget):
    def __init__(self, *args, **kwargs):
        super(GUI, self).__init__(*args, **kwargs)

        self.comm = Communications()

        pygame.init()

        # Set up the joystick
        pygame.joystick.init()

        self.my_joystick = None
        self.joystick_names = []

        self.g_keys = None

        # Enumerate joysticks
        for i in range(0, pygame.joystick.get_count()):
            self.joystick_names.append(pygame.joystick.Joystick(i).get_name())
        print(self.joystick_names)

        # By default, load the first available joystick.
        if len(self.joystick_names) > 0:
            self.my_joystick = pygame.joystick.Joystick(0)
            self.my_joystick.init()

        max_joy = max(self.my_joystick.get_numaxes(),
                      self.my_joystick.get_numbuttons(),
                      self.my_joystick.get_numhats())

        ## I ADDED THIS
        # start here
        # Start timer for controller polling
        self.__timer_init = QTimer()
        self.__timer_init.timeout.connect(self.pollController)
        self.__timer_init.setSingleShot(False)
        self.__timer_init.start(10)

        self.button_array = []
        self.axes_array = []
        self.hat_array = []
        self.plot_array = []
        self.axes1 = None
        self.initUI()

        ## I ADDED THIS

    def initUI(self):
        # Layout for axes display
        vbox_axes = QVBoxLayout()
        vbox_axes.addStretch(1)
        label_axes = QLabel(self)
        label_axes.setText('Axes')
        vbox_axes.addWidget(label_axes)
        self.axes1 = AxesWidget()
        self.axes2 = AxesWidget()
        # Assume 4 axes are on controller
        # for i in range(0, self.my_joystick.get_numaxes()):
        for name in ['Movement', 'Camera']:
            slider = QSlider(Qt.Horizontal, self)
            slider.setRange(-100.0, 100.0)
            self.axes_array.append(slider)
            label = QLabel(self)
            label.setText(name + '-X')
            vbox_axes.addWidget(label)
            vbox_axes.addWidget(slider)

            slider = QSlider(Qt.Horizontal, self)
            slider.setRange(-100.0, 100.0)
            self.axes_array.append(slider)
            label = QLabel(self)
            label.setText(name + '-Y')
            vbox_axes.addWidget(label)
            vbox_axes.addWidget(slider)

        hbox_axesplot = QHBoxLayout()

        vbox = QVBoxLayout()
        axesTitle = QLabel(self)
        axesTitle.setText("Movement Axes")
        vbox.addWidget(axesTitle)
        self.axes_array[0].valueChanged[int].connect(self.axes1.set_x_value)
        self.axes_array[1].valueChanged[int].connect(self.axes1.set_y_value)
        vbox.addWidget(self.axes1)
        hbox_axesplot.addLayout(vbox)

        vbox = QVBoxLayout()
        axesTitle = QLabel(self)
        axesTitle.setText("Camera Axes")
        vbox.addWidget(axesTitle)
        self.axes_array[2].valueChanged[int].connect(self.axes2.set_x_value)
        self.axes_array[3].valueChanged[int].connect(self.axes2.set_y_value)
        vbox.addWidget(self.axes2)
        hbox_axesplot.addLayout(vbox)

        vbox_axes.addLayout(hbox_axesplot)

        # Layout for button checkboxes
        hbox_buttons = QHBoxLayout()
        hbox_buttons.addStretch(1)
        label_buttons = QLabel(self)
        label_buttons.setText('Buttons')
        for i in range(0, self.my_joystick.get_numbuttons()):
            cb = QCheckBox(str(i), self)
            self.button_array.append(cb)
            cb.setEnabled(False)
            cb.setChecked(False)
            hbox_buttons.addWidget(cb)

        # Layout for D-pad
        hbox_dpad = QHBoxLayout()
        label_dpad = QLabel(self)
        label_dpad.setText('D-Pad')
        for i in range(0, self.my_joystick.get_numhats()):
            lbl_2 = QLabel(self)
            self.hat_array.append(lbl_2)
            lbl_2.setText(str(self.my_joystick.get_hat(i)))
            hbox_dpad.addWidget(lbl_2)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(vbox_axes)
        vbox.addWidget(label_buttons)
        vbox.addLayout(hbox_buttons)
        vbox.addWidget(label_dpad)
        vbox.addLayout(hbox_dpad)

        # self.setGeometry(300, 300, 300, 150)
        self.setLayout(vbox)

        # Qt show window
        self.show()

        ## I ADDED THIS

    def pollController(self):
        toSend = []
        # 0: Left Stick Y, 0-100
        # 1: Left Stick X, 0-100
        # 2: Right Stick Y, 0-100
        # 3: Right Stick X, 0-100
        # 4: Triggers, 0-100
        # 5-8: A, B, X, Y
        # 9-10: Bumpers
        # 11-12: Back, Start
        # 13: Left Stick Button
        # 14: Right Stick Button
        # 15: Hat Switch, 0-8
        # For Hat, 0 is resting, 1:NW, 2:N, continues clockwise
        g_keys = pygame.event.get()
        for event in g_keys:
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                self.quit()
                return

            elif event.type == QUIT:
                self.quit()
                return

        values = list()
        for i in range(0, self.my_joystick.get_numaxes()):
            ax_value = self.my_joystick.get_axis(i)
            values.append(ax_value)
            self.axes_array[i].setValue(ax_value * 100)
            self.axes1.repaint()
            self.axes2.repaint()




        for i in range(0, self.my_joystick.get_numbuttons()):
            state = self.my_joystick.get_button(i) == 1
            values.append(state)
            self.button_array[i].setChecked(state)




        for i in range(0, self.my_joystick.get_numhats()):
            state = self.my_joystick.get_hat(i)
            values.append(state)
            self.hat_array[i].setText(str(state))



        #this is for seeing the controller data
        #print (values)


        toSend = [0 for x in range(16)]
        toSend[1] = int(getAxisValueInPercentage(self.my_joystick.get_axis(0))) #Left Stick X
        toSend[0] = int(getAxisValueInPercentage(self.my_joystick.get_axis(1))) #Left Stick Y
        toSend[3] = int(getAxisValueInPercentage(self.my_joystick.get_axis(2))) #Right Stick X
        toSend[2] = int(getAxisValueInPercentage(self.my_joystick.get_axis(3))) #Right Stick Y
        toSend[7] = (self.my_joystick.get_button(0)) #X or Square
        toSend[5] = (self.my_joystick.get_button(1)) #A or Cross
        toSend[6] = (self.my_joystick.get_button(2)) #B or Circle
        toSend[8] = (self.my_joystick.get_button(3)) #Y or Triangle
        toSend[9] = (self.my_joystick.get_button(4)) #Left Bumper
        toSend[10] = (self.my_joystick.get_button(5)) #Right Bumper
        toSend[4] = (self.my_joystick.get_button(6)) #Left Trigger
        toSend[4] = (self.my_joystick.get_button(7)) #Right Trigger
        toSend[11] = (self.my_joystick.get_button(8)) #Back or Select
        toSend[12] = (self.my_joystick.get_button(9)) #Start
        toSend[13] = (self.my_joystick.get_button(10)) #Left Stick Button
        toSend[14] = (self.my_joystick.get_button(11)) #Right Stick Buttpn
        toSend[15] = 0 #(self.my_joystick.get_hat(0)) #D-Pad

        print(toSend)
        #This is the flag in the array
        toSend.insert(0, 250)
        self.comm.sendData(toSend)

    def quit(self):
        pass


def getAxisValueInPercentage(axisValue:float)->int:
    return (((2 - (1 - axisValue)) * 100) / 2)



    # Assumes range on axes is -100 to 100
class AxesWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.value = (0, 0)

    def initUI(self):
        self.setMinimumSize(120, 120)
        self.setMaximumSize(120, 120)

    def set_x_value(self, x):
        self.value = (x, self.value[1])

    def set_y_value(self, y):
        self.value = (self.value[0], y)

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()

    def drawWidget(self, qp):
        size = self.size()
        h = size.height()
        # step = int(round(h / 200))
        qp.setPen(QColor(255, 0, 0))
        qp.setBrush(QColor(0, 0, 0))
        x = self.value[0] / 2 + 60
        y = self.value[1] / 2 + 60
        qp.drawEllipse(x, y, 7, 7)
        qp.setPen(QColor(0, 0, 0))
        qp.setBrush(QColor(0, 0, 0, 0))
        qp.drawRect(9, 9, h - 11, h - 11)

class Communications:
    def __init__(self):
        self.SerialPort = serial.Serial()
        self.SerialPort.baudrate = 115200
        self.getListofPorts()
        self.openPort()

    def __del__(self):
        if self.SerialPort.is_open:
            self.SerialPort.close()

    def getListofPorts(self):
        ports = comports()
        for portname in ports:
            print(portname)
        return ports

    def openPort(self, portname="COM3"):
        self.SerialPort.port = portname
        self.SerialPort.open()

    def sendData(self, bytelist):
        for byte in bytelist:
            self.SerialPort.write(byte)




if __name__== "__main__":
    gui = QApplication(sys.argv)
    gui.setApplicationName("ControllerGUI")
    window = GUI()
    gui.exec_()