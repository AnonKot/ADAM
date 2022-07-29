import sys 
from PyQt5 import QtWidgets 
from PyQt5.QtCore import  QObject
import des  
from ModbusManager import ModBus
import datetime



from PyQt5.QtCore import pyqtSignal as Signal


class EmittingStream(QObject):  
        textWritten = Signal(str)  # Определите сигнал, который отправляет ул.
        def write(self, text):
            self.textWritten.emit(str(text))






class ExampleApp(QtWidgets.QMainWindow, des.Ui_MainWindow):
    def __init__(self):
        self.MB = ModBus(self)
        super().__init__()
        self.setupUi(self) 

        sys.stdout = EmittingStream(textWritten=self.outputWritten)
        sys.stderr = EmittingStream(textWritten=self.outputWritten)

        self.pushButton_4.clicked.connect(self.ApplyModbusSettings) 
        self.pushButton.clicked.connect(self.SendModBusCommand) 
        self.pushButton_2.clicked.connect(self.StopSend)
        self.pushButton_3.clicked.connect(self.ApplyComPortSettings)
        self.pushButton_6.clicked.connect(self.MB.modbusSettings)
        self.pushButton_5.clicked.connect(self.Send)
        self.pushButton_2.setEnabled(False)

    def ApplyModbusSettings(self):
        command = self.MB.createCommand(self.spinBox.text(),self.comboBox.currentText(),self.comboBox_3.currentText(),self.checkBox.isChecked(),self.comboBox_2.currentText())
        self.MB.editConfig(command)


    def Send(self):
        self.MB.sendCommand(self.lineEdit_2.text())


    def StopSend(self):
        self.MB.stopListen()
        self.pushButton.setEnabled(True)
        self.pushButton_2.setEnabled(False)

    def SendModBusCommand(self):
        self.pushButton.setEnabled(False)
        self.pushButton_2.setEnabled(True)
        self.MB.startListen(self.lineEdit.text(),self.lineEdit_4.text(),self.lineEdit_5.text(),self.comboBox_6.currentText())

    def ApplyComPortSettings(self):
       self.MB.editComSettings(self.lineEdit_6.text(),self.comboBox_5.currentText(),self.lineEdit_7.text(),self.lineEdit_8.text(),self.comboBox_4.currentText(),self.lineEdit_9.text())
    

    def outputWritten(self, text):
        self.textBrowser.append(str(datetime.datetime.now())[10:-7]+' '+str(text))    




def main():
    app = QtWidgets.QApplication(sys.argv)  
    window = ExampleApp()
    window.setWindowTitle('ADAM')
    window.show()
    app.exec()

if __name__ == '__main__':
    main() 
