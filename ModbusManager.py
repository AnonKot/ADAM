import struct
import serial
import time
from threading import Thread
import sys


HIBYTE = b'\
\x00\xC0\xC1\x01\xC3\x03\x02\xC2\xC6\x06\x07\xC7\x05\xC5\xC4\x04\
\xCC\x0C\x0D\xCD\x0F\xCF\xCE\x0E\x0A\xCA\xCB\x0B\xC9\x09\x08\xC8\
\xD8\x18\x19\xD9\x1B\xDB\xDA\x1A\x1E\xDE\xDF\x1F\xDD\x1D\x1C\xDC\
\x14\xD4\xD5\x15\xD7\x17\x16\xD6\xD2\x12\x13\xD3\x11\xD1\xD0\x10\
\xF0\x30\x31\xF1\x33\xF3\xF2\x32\x36\xF6\xF7\x37\xF5\x35\x34\xF4\
\x3C\xFC\xFD\x3D\xFF\x3F\x3E\xFE\xFA\x3A\x3B\xFB\x39\xF9\xF8\x38\
\x28\xE8\xE9\x29\xEB\x2B\x2A\xEA\xEE\x2E\x2F\xEF\x2D\xED\xEC\x2C\
\xE4\x24\x25\xE5\x27\xE7\xE6\x26\x22\xE2\xE3\x23\xE1\x21\x20\xE0\
\xA0\x60\x61\xA1\x63\xA3\xA2\x62\x66\xA6\xA7\x67\xA5\x65\x64\xA4\
\x6C\xAC\xAD\x6D\xAF\x6F\x6E\xAE\xAA\x6A\x6B\xAB\x69\xA9\xA8\x68\
\x78\xB8\xB9\x79\xBB\x7B\x7A\xBA\xBE\x7E\x7F\xBF\x7D\xBD\xBC\x7C\
\xB4\x74\x75\xB5\x77\xB7\xB6\x76\x72\xB2\xB3\x73\xB1\x71\x70\xB0\
\x50\x90\x91\x51\x93\x53\x52\x92\x96\x56\x57\x97\x55\x95\x94\x54\
\x9C\x5C\x5D\x9D\x5F\x9F\x9E\x5E\x5A\x9A\x9B\x5B\x99\x59\x58\x98\
\x88\x48\x49\x89\x4B\x8B\x8A\x4A\x4E\x8E\x8F\x4F\x8D\x4D\x4C\x8C\
\x44\x84\x85\x45\x87\x47\x46\x86\x82\x42\x43\x83\x41\x81\x80\x40'
 
LOBYTE = b'\
\x00\xC1\x81\x40\x01\xC0\x80\x41\x01\xC0\x80\x41\x00\xC1\x81\x40\
\x01\xC0\x80\x41\x00\xC1\x81\x40\x00\xC1\x81\x40\x01\xC0\x80\x41\
\x01\xC0\x80\x41\x00\xC1\x81\x40\x00\xC1\x81\x40\x01\xC0\x80\x41\
\x00\xC1\x81\x40\x01\xC0\x80\x41\x01\xC0\x80\x41\x00\xC1\x81\x40\
\x01\xC0\x80\x41\x00\xC1\x81\x40\x00\xC1\x81\x40\x01\xC0\x80\x41\
\x00\xC1\x81\x40\x01\xC0\x80\x41\x01\xC0\x80\x41\x00\xC1\x81\x40\
\x00\xC1\x81\x40\x01\xC0\x80\x41\x01\xC0\x80\x41\x00\xC1\x81\x40\
\x01\xC0\x80\x41\x00\xC1\x81\x40\x00\xC1\x81\x40\x01\xC0\x80\x41\
\x01\xC0\x80\x41\x00\xC1\x81\x40\x00\xC1\x81\x40\x01\xC0\x80\x41\
\x00\xC1\x81\x40\x01\xC0\x80\x41\x01\xC0\x80\x41\x00\xC1\x81\x40\
\x00\xC1\x81\x40\x01\xC0\x80\x41\x01\xC0\x80\x41\x00\xC1\x81\x40\
\x01\xC0\x80\x41\x00\xC1\x81\x40\x00\xC1\x81\x40\x01\xC0\x80\x41\
\x00\xC1\x81\x40\x01\xC0\x80\x41\x01\xC0\x80\x41\x00\xC1\x81\x40\
\x01\xC0\x80\x41\x00\xC1\x81\x40\x00\xC1\x81\x40\x01\xC0\x80\x41\
\x01\xC0\x80\x41\x00\xC1\x81\x40\x00\xC1\x81\x40\x01\xC0\x80\x41\
\x00\xC1\x81\x40\x01\xC0\x80\x41\x01\xC0\x80\x41\x00\xC1\x81\x40'

class ModBus():
    def __init__(self,UI):
        self.port = "/dev/ttyAP6"
        self.baudrate = 9600
        self.stopBits = 1
        self.bytesize = 8
        self.parity = 'None'
        self.timeOut = 1
        self.isConnect =False
        self.toListen = False
        self.window = UI

    def connect(self):
        parityDic ={
            'None' : 'N',
            'Even' : 'E',
            'Mark' : 'M',
            'Odd'  : 'O',
            'Space': 'S'}
        parityValue = parityDic[self.parity]
        self.ser = serial.Serial(self.port, self.baudrate, stopbits = self.stopBits, bytesize = self.bytesize, parity = parityValue, timeout = self.timeOut)
        self.isConnect = True
 
    def encode(self, read_address, command, write_byte_count, write_count):
        if command =='Read Holding Registers':
                commandValue=3
        elif command =='Read Input Registers':
            commandValue = 4
        elif command =='Read Discrete Inputs':
            commandValue = 2
        elif command == 'Read Coil Status':
            commandValue = 1
        result = struct.pack('>BBHH',
                    read_address, commandValue,  write_count,\
                     write_byte_count)
        return result
    
    def crc16(self,data):
        crchi = 0xFF
        crclo = 0xFF
        index = 0
    
        for byte in data :
            index = crchi ^ int(byte)
            crchi = crclo ^ LOBYTE[index]
            crclo = HIBYTE[index]
        
        return struct.pack('>BB', crchi, crclo)

    def createCommand(self, addres, baudrate, dataFormat, checksum, timeI):
        dataFormatDic = {'Modbus':4, 'Advantech':0}
        FormatValue = dataFormatDic[dataFormat]
        baudDic = {'1200':'3', '2400':'4', '4800':'5', '9600':'6', '19200':'7', '38400':'8', '57600':'9', '115200':'A'}
        baudCount = baudDic[baudrate]
        checksumWithTime = (hex(checksum * 4 + (timeI == '60') * 0 + (timeI == '50') * 8)[2:]).upper()
        hexaddres = hex(int(addres))[2:]
        if len(hexaddres) == 1:
            hexaddres= '0' + hexaddres
        command = f"%00{hexaddres}080{baudCount}{checksumWithTime}{FormatValue}\r"
        return command.encode("ASCII")

    def editConfig(self,command):
        self.connect()
        self.ser.write(command)
        res = self.ser.readline()
        par = self.getParameters()
        if b'!' in res :
            print(f'Success {par}')
        else:
            print(f"Fail {par}")
        self.ser.close()
    
    def sendCommand(self,data):
        self.connect()
        encodeData = (data+'\r').encode("ASCII")
        self.ser.write(encodeData)
        self.window.label_17.setText(str(self.ser.readline())[3:-3])
        self.ser.close()

    def sendModBusCommand(self, read_address, write_address, write_byte_count,mode):
        self.connect()
        while self.toListen:
            time.sleep(0.1)
            command=self.encode(int(read_address), mode, int(write_byte_count),int(write_address))
            
            cr = self.crc16(command)
            self.ser.write(command + cr)
            res = self.ser.read(22)

            decodeData = self.decode(res)
            sys.stdout.write(decodeData)
            #self.window.textEdit.insertPlainText(str(datetime.datetime.now())[10:-7]+' '+str(decodeData) + "\n")
            # if self.toListen:
            #     self.window.WriteData(decodeData)
        time.sleep(0.1)
        self.ser.close()



    def startListen(self, read_address = 21, write_address = 0, write_byte_count = 8,mode = 'Read Holding Registers'):
        self.toListen = True
        self.th = Thread(target=self.sendModBusCommand,args=(read_address, write_address, write_byte_count, mode),daemon=True)
        self.th.start()
        
    def stopListen(self):
        self.toListen = False
        

    def getParameters(self):
        self.ser.write('$002\r'.encode("ASCII"))
        return self.ser.readline()

    def editComSettings(self,port,baudrate,stopBits,bytesize,parity,timeOut):
        self.port = port
        self.baudrate = int(baudrate)
        self.stopBits =int (stopBits)
        self.bytesize = int(bytesize)
        self.parity = parity
        self.timeOut =int( timeOut)
        print(self.port, self.baudrate, self.stopBits, self.bytesize,  self.parity,self.timeOut)


    def decode(self, data):
        write_registers =[]
        for i in range(3, data[2] + 3, 2):
            reg = struct.unpack('>H',data[i:i + 2])[0]
            register = 0-(10-reg * 0.00030517578125)
            write_registers.append(f'{register:.2f}')
        return write_registers

    def modbusSettings(self):
        self.connect()
        data =  self.getParameters()
        data=str(data)[2:]
        self.ser.close()
        baudDic = {'3':'1200', '4':'2400', '5':'4800', '6':'9600', '7':'19200', '8':'38400', '9':'57600','A': '115200'}
        dataFormatDic = {'4':'Modbus','0': 'Advantech'}
        self.window.textEdit_6.setText(str(int(data[1:3],16))) 
        self.window.textEdit_7.setText(baudDic[data[6]])
        decTimeWithCheck = int(data[7],16)
        if decTimeWithCheck ==12:
            check = 'True'
            timeI = '50'
        elif decTimeWithCheck==8:
            check = 'False'
            timeI = '50'
        elif decTimeWithCheck == 4:
            check = 'True'
            timeI = '60'
        elif decTimeWithCheck == 0:
            check = 'False'
            timeI = '60'
        self.window.textEdit_10.setText(check)
        self.window.textEdit_8.setText(timeI)
        self.window.textEdit_9.setText(dataFormatDic[data[8]])




        

