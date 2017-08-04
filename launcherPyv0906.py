import sys, re
from PySide.QtGui import *
from PySide.QtCore import *
from dateutil.parser import parse
from time import time, sleep, localtime
from datetime import datetime, timedelta
import subprocess
import socket


class MySignal(QObject):
        sig = Signal(str)

class readHostThread(QThread):
        def __init__(self, parent = None):
                QThread.__init__(self, parent)
                self.exiting = False
                self.signal = MySignal()

        def run(self):
                readHostThread.currentHost = str(MainWindow.hostCombo.currentText())
                print readHostThread.currentHost
                # add to history
                process = subprocess.Popen(["ping", "-n", "1", readHostThread.currentHost], shell=True, stdout=subprocess.PIPE)
                process.wait()
                response = process.returncode
                result_str = process.stdout.read()
                r = re.compile('Destination host unreachable')
                m = r.search(result_str)
                if m or response == 1:
                    MainWindow.statusBar.showMessage("Offline")

                else:
                    # Set initial labels
                    MainWindow.statusBar.showMessage("Online - Getting info...")
                    MainWindow.userEdit.setText('######################################################')
                    sleep(.03)
                    MainWindow.fullNameEdit.setText('######################################################')
                    sleep(.01)
                    MainWindow.userEdit.setText(' ')
                    sleep(.01)
                    MainWindow.computerModelResult.setText('####################################')
                    sleep(.01)
                    MainWindow.fullNameEdit.setText(' ')
                    sleep(.01)
                    MainWindow.computerSerialResult.setText('####################################')
                    sleep(.01)
                    MainWindow.computerModelResult.setText(' ')
                    sleep(.01)
                    MainWindow.computerIPAddressResult.setText('####################################')
                    sleep(.01)
                    MainWindow.computerSerialResult.setText(' ')
                    sleep(.01)
                    MainWindow.computerMACResult.setText('####################################')
                    sleep(.01)
                    MainWindow.computerIPAddressResult.setText(' ')
                    sleep(.01)
                    MainWindow.computerOSVersionResult.setText('####################################')
                    sleep(.01)
                    MainWindow.computerMACResult.setText(' ')
                    sleep(.01)
                    MainWindow.computerUpTimeResult.setText('####################################')
                    sleep(.01)
                    MainWindow.computerOSVersionResult.setText(' ')
                    sleep(.01)
                    MainWindow.computerUpTimeResult.setText(' ')
                    # Start threads
                    MainWindow.readUser.start()
                    MainWindow.computerModel.start()
                    MainWindow.computerCPU.start()
                    MainWindow.computerMEM.start()
                self.exiting=True
                self.signal.sig.emit('OK')


class readUserThread(QThread):
    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.exiting = False
        self.signal = MySignal()

    def run(self):
        hostname = readHostThread.currentHost
        while self.exiting == False:
            currentUser = subprocess.Popen(["wmic", "/node:", hostname, "ComputerSystem", "get", "Username"], shell=True,stdout=subprocess.PIPE)
            currentUser.wait()
            #response = currentUser.returncode
            currentUserData = currentUser.stdout.read()
            print currentUserData
            currentUserData = currentUserData.rpartition('\\')[-1]
            currentUserData = currentUserData.rstrip()
            print currentUserData
            MainWindow.userEdit.setText(currentUserData)
            getFullName = subprocess.Popen(["net", "user", currentUserData, "/domain"], shell=True,stdout=subprocess.PIPE)
            getFullName.wait()
            getFullName = getFullName.stdout.read()
            print getFullName
            string = re.findall(r'Name\s*(.*?)\r\nComment', getFullName)
            string = str(string)

            plainName = re.findall('\S+', string)
            print string

            plainName = ' '.join(plainName)
            plainName = plainName.strip("['']")
            print plainName
            MainWindow.fullNameEdit.setText(plainName)
            #plainName = str(plainName)
            #print plainName

            #MainWindow.userDetail.appendPlainText(getFullName)
            #MainWindow.userDetail.setText(getFullName)



            self.signal.sig.emit('OK')
            self.exiting = True
        self.exiting = False

class userDetailThread(QThread):
    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.exiting = False
        self.signal = MySignal()

    def run(self):
        while self.exiting == False:
            MainWindow.userDetailWindow.clear()
            #print "user detail thread started"
            currentUsername = MainWindow.userEdit.text()
            #print currentUsername
            getFullName = subprocess.Popen(["net", "user", currentUsername, "/domain"], shell=True, stdout=subprocess.PIPE)
            getFullName.wait()
            getFullName = getFullName.stdout.read()
            MainWindow.userDetailData = getFullName
            #print getFullName
            #MainWindow.userDetailWindow.appendPlainText(getFullName)
            self.signal.sig.emit('OK')
            self.exiting = True


class computerCPUThread(QThread):
        def __init__(self, parent=None):
                QThread.__init__(self, parent)
                self.exiting = False
                self.signal = MySignal()

        def run(self):
                hostname = readHostThread.currentHost
                while self.exiting == False:
                        print "start cpu thread"
                        cpuload = subprocess.Popen(["wmic", "/node:", hostname, "cpu", "get", "loadpercentage"], shell=True, stdout=subprocess.PIPE)
                        cpuload.wait()
                        response = cpuload.returncode
                        print response
                        if response == 0:
                                MainWindow.computerCPULabel.setFont(MainWindow.statusFontBold)
                        else:
                                MainWindow.computerCPULabel.setFont(MainWindow.hostFont)
                        cpuresult = cpuload.stdout.read()
                        print cpuresult
                        cpuInt = re.findall('\d+', cpuresult)
                        cpuInt = " ".join (cpuInt)
                        cpuInt = str(cpuInt)
                        MainWindow.computerCPUResult.setText(cpuInt)
                        if MainWindow.computerCPUCheckbox.isChecked() == True:
                            self.exiting = False
                        else:
                            self.exiting = True
                self.signal.sig.emit('OK')
                self.exiting = False


class computerModelThread(QThread):
    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.exiting = False
        self.signal = MySignal()

    def run(self):
        hostname = readHostThread.currentHost
        while self.exiting == False:
            print "start model thread"
            getModel = subprocess.Popen(["wmic", "/node:", hostname, "csproduct", "get", "name"], shell=True,stdout=subprocess.PIPE)
            getModel.wait()
            getModel = getModel.stdout.read()
            getModel = re.findall(r'Name\s*(.*?)\r\r\n', getModel)
            getModel = str(getModel)
            getModel = getModel.strip("['']")
            MainWindow.computerModelResult.setText(getModel)
            getSerial = subprocess.Popen(["wmic", "/node:", hostname, "bios", "get", "serialnumber"], shell=True,stdout=subprocess.PIPE)
            getSerial.wait()
            getSerial = getSerial.stdout.read()
            getSerial = re.findall(r'SerialNumber\s*(.*?)\r\r\n', getSerial)
            getSerial = str(getSerial)
            getSerial = getSerial.strip("['']")
            MainWindow.computerSerialResult.setText(getSerial)
            ###WMIC BLOCK####
            getMAC = subprocess.Popen(["getmac", "/s", hostname, "/NH", "/FO", "table"], shell=True,stdout=subprocess.PIPE)
            getMAC.wait()
            getMAC = getMAC.stdout.read()
            getMAC = str(getMAC)
            getMAC = getMAC.split(' ', 1)[0]
            getMAC = getMAC.strip()
            MainWindow.computerMACResult.setText(getMAC)
            ###WMIC BLOCK####
            getIP = socket.gethostbyname(hostname)
            getIP = str(getIP)
            MainWindow.computerIPAddressResult.setText(getIP)
            ###WMIC BLOCK####
            getOSCaption = subprocess.Popen(["wmic", "/node:", hostname, "os", "get", "Caption"], shell=True,stdout=subprocess.PIPE)
            getOSCaption.wait()
            getOSCaption = getOSCaption.stdout.read()
            getOSCaption = str(getOSCaption)
            getOSCaption = getOSCaption.split(' ', 1)[1]
            getOSCaption = getOSCaption.strip()
            getOSArch = subprocess.Popen(["wmic", "/node:", hostname, "os", "get", "OSArchitecture"], shell=True,stdout=subprocess.PIPE)
            getOSArch.wait()
            getOSArch = getOSArch.stdout.read()
            getOSArch = str(getOSArch)
            getOSArch = getOSArch.split(' ', 1)[1]
            getOSArch = getOSArch.strip()
            getOSBuildNumber = subprocess.Popen(["wmic", "/node:", hostname, "os", "get", "BuildNumber"], shell=True,stdout=subprocess.PIPE)
            getOSBuildNumber.wait()
            getOSBuildNumber = getOSBuildNumber.stdout.read()
            getOSBuildNumber = str(getOSBuildNumber)
            getOSBuildNumber = getOSBuildNumber.split(' ', 1)[1]
            getOSBuildNumber = getOSBuildNumber.strip()
            computerOSString = getOSCaption +' '+ getOSArch +' '+ getOSBuildNumber
            print computerOSString
            MainWindow.computerOSVersionResult.setText(computerOSString)
            #http://www.lfd.uci.edu/~gohlke/pythonlibs/#python-dateutil
            getUpTime = subprocess.Popen(["wmic", "/node:", hostname, "os", "get", "LastBootUpTime"], shell=True,stdout=subprocess.PIPE)
            getUpTime.wait()
            getUpTime = getUpTime.stdout.read()
            now = datetime.now()
            boot = getUpTime
            boot = str(boot)
            boot = boot.split('.')[0]
            boot = parse(boot, fuzzy=True)
            totuptime = str(now - boot)
            totuptime = totuptime.split('.')[0]
            MainWindow.computerUpTimeResult.setText(totuptime)
            ###WMIC BLOCK####
            #self.signal.sig.emit('OK')
            self.exiting = True
        self.exiting = False

class computerMEMThread(QThread):
    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.exiting = False
        self.signal = MySignal()

    def run(self):
        hostname = readHostThread.currentHost
        while self.exiting == False:
            totalmem = subprocess.Popen(["wmic", "/node:", hostname, "ComputerSystem", "get", "TotalPhysicalMemory"], shell=True,stdout=subprocess.PIPE)
            totalmem.wait()
            response = totalmem.returncode
            print response
            if response == 0:
                MainWindow.computerMEMLabel.setFont(MainWindow.statusFont)
            else:
                MainWindow.computerMEMLabel.setFont(MainWindow.hostFont)
            totalmemresult = totalmem.stdout.read()
            totalmemInt = re.findall('\d+', totalmemresult)
            totalmemInt = " ".join (totalmemInt)
            totalmemInt = int(totalmemInt)
            totalmemInt = totalmemInt/1024/1024
            totalmemInt = str(totalmemInt)
            print totalmemInt
            availmem = subprocess.Popen(["wmic", "/node:", hostname, "OS", "get", "FreePhysicalMemory"],
                                        shell=True, stdout=subprocess.PIPE)
            availmem.wait()
            response = availmem.returncode
            if response == 0:
                MainWindow.computerMEMLabel.setFont(MainWindow.statusFontBold)
            else:
                #MainWindow.computerMEMLabel.setBackground(QColor(6,253,60))
                self.exiting = True
            availmemresult = availmem.stdout.read()
            availmemInt = re.findall('\d+', availmemresult)
            availmemInt = " ".join(availmemInt)
            availmemInt = int(availmemInt)
            availmemInt = availmemInt / 1024
            availmemInt = str(availmemInt)
            MainWindow.computerMEMResult.setText(availmemInt + '/' + totalmemInt+'MB')
            self.exiting = True
        self.signal.sig.emit('OK')
        self.exiting = False


class MainWindow(QWidget):
        def __init__(self, parent=None):
                QWidget.__init__(self,parent)
                # Set the size, alignment, and title
                self.resize(380, 550)
                self.setFixedSize(self.size())
                self.setWindowTitle('LauncherPy v1.0')
                # Fonts
                statusFont = QFont('Serif', 11, QFont.Light)
                MainWindow.labelFont = QFont('Serif', 12, QFont.Light)
                MainWindow.resultFont = QFont('Serif', 12, QFont.Light)
                MainWindow.smallresultFont = QFont('Serif', 8, QFont.Light)
                MainWindow.statusFont = QFont('Serif', 8, QFont.Light)
                MainWindow.statusFontBold = QFont('Serif', 8, QFont.Bold)
                MainWindow.hostFont = QFont('Serif', 11, QFont.Light)
                MainWindow.hostFont.setCapitalization(QFont.AllUppercase)
                # Set widgets - labels and edit boxes
                # Host widgets
                self.hostLabel = QLabel('Hostname')
                self.hostLabel.setFont(MainWindow.labelFont)
                MainWindow.hostCombo = QComboBox()
                self.hostCombo.setFont(MainWindow.hostFont)
                self.hostCombo.setEditable(True)
                self.readHostButton = QPushButton('Go')
                self.readHostButton.clicked.connect(self.readHostOperation)
                self.readHostButton.setAutoDefault(True)
                self.readHost = readHostThread()
                self.readHost.signal.sig.connect(self.readHostComplete)
                #
                self.readHostHistoryButton = QPushButton('>')
                self.readHostHistoryButton.clicked.connect(self.readHostHistory)
                #
                # User widgets
                self.userButton = QPushButton('User')
                #self.userButton.clicked.connect(MainWindow.readUser()
                MainWindow.userEdit = QLineEdit()
                MainWindow.userEdit.setFont(MainWindow.resultFont)
                MainWindow.readUser = readUserThread()
                #self.userDetailButton = QPushButton('Details')
                #self.userDetailButton.clicked.connect(self.readFullNameOperation)
                #self.readUser = readUserThread()
                #####################READ FULL NAME###################################
                MainWindow.userDetailWindow = QPlainTextEdit()
                MainWindow.userDetailWindow.setReadOnly(True)
                #MainWindow.userDetailWindow.setOverwriteMode(True)
                MainWindow.userDetailWindow.setWindowTitle('User Details')
                MainWindow.userDetailWindow.resize(350, 550)
                MainWindow.userDetailButton = QPushButton('Details')
                MainWindow.userDetailButton.clicked.connect(self.userDetailOperation)
                self.userDetail = userDetailThread()
                self.userDetail.signal.sig.connect(self.userDetailComplete)
                ######################################################################
                self.fullNameButton = QPushButton('Name')
                self.fullNameButton.clicked.connect(self.readFullName)
                MainWindow.fullNameEdit = QLineEdit()
                MainWindow.fullNameEdit.setFont(MainWindow.resultFont)
                #
                # Computer widgets
                self.computerModelLabel = QLabel('Model')
                self.computerModelLabel.setFont(MainWindow.labelFont)
                MainWindow.computerModelResult = QLineEdit()
                MainWindow.computerModelResult.setFont(MainWindow.resultFont)
                MainWindow.computerModel = computerModelThread()
                #self.computerModel.signal.sig.connect(self.computerModelComplete)
                #
                self.computerSerialLabel = QLabel('Serial')
                self.computerSerialLabel.setFont(MainWindow.labelFont)
                MainWindow.computerSerialResult = QLineEdit()
                MainWindow.computerSerialResult.setFont(MainWindow.resultFont)
                #
                self.computerIPAddressLabel = QLabel('IP')
                self.computerIPAddressLabel.setFont(MainWindow.labelFont)
                MainWindow.computerIPAddressResult = QLineEdit()
                self.computerIPAddressResult.setFont(MainWindow.resultFont)
                #
                self.computerMACAddressLabel = QLabel('MAC')
                self.computerMACAddressLabel.setFont(MainWindow.labelFont)
                MainWindow.computerMACResult = QLineEdit()
                self.computerMACResult.setFont(MainWindow.resultFont)
                #
                self.computerOSVersionLabel = QLabel('OS')
                self.computerOSVersionLabel.setFont(MainWindow.labelFont)
                MainWindow.computerOSVersionResult = QLineEdit()
                self.computerOSVersionResult.setFont(MainWindow.smallresultFont)
                #
                self.computerUpTimeLabel = QLabel('UpTime')
                self.computerUpTimeLabel.setFont(MainWindow.labelFont)
                MainWindow.computerUpTimeResult = QLineEdit()
                self.computerUpTimeResult.setFont(MainWindow.resultFont)
                #
                MainWindow.computerCPU = computerCPUThread()
                MainWindow.computerCPU.signal.sig.connect(self.computerCPUComplete)
                MainWindow.computerCPULabel = QLabel('CPU')
                MainWindow.computerCPULabel.setFont(MainWindow.statusFont)
                MainWindow.computerCPULabel.setAlignment(Qt.AlignRight)
                MainWindow.computerCPUResult = QLabel('00%')
                MainWindow.computerCPUResult.setFont(MainWindow.statusFont)
                MainWindow.computerCPUResult.setAlignment(Qt.AlignRight)
                MainWindow.computerCPUCheckbox = QCheckBox()
                #
                MainWindow.computerMEM = computerMEMThread()
                MainWindow.computerMEM.signal.sig.connect(self.computerCPUComplete)
                MainWindow.computerMEMLabel = QLabel('MEM')
                MainWindow.computerMEMLabel.setFont(MainWindow.statusFont)
                MainWindow.computerMEMLabel.setAlignment(Qt.AlignRight)
                MainWindow.computerMEMResult = QLabel('0/0MB')
                MainWindow.computerMEMResult.setFont(MainWindow.statusFont)
                MainWindow.computerMEMResult.setAlignment(Qt.AlignRight)
                #
                # Command widgets
                #
                self.commandCDriveButton = QPushButton('C Drive')
                self.commandCDriveButton.clicked.connect(self.commandCDrive)
                #
                self.commandHDriveButton = QPushButton('H Drive')
                self.commandHDriveButton.clicked.connect(self.commandHDrive)
                #
                self.commandDesktopButton = QPushButton('Desktop')
                self.commandDesktopButton.clicked.connect(self.commandDesktop)
                #
                self.commandRebootButton = QPushButton('Reboot')
                self.commandRebootButton.clicked.connect(self.commandReboot)
                #
                self.commandRemoteButton = QPushButton('Remote')
                self.commandRemoteButton.clicked.connect(self.commandRemote)
                #
                self.commandRDPButton = QPushButton('RDP')
                self.commandRDPButton.clicked.connect(self.commandRDP)
                #
                self.commandCMDButton = QPushButton('CMD')
                self.commandCMDButton.clicked.connect(self.commandCMD)
                #
                self.commandGPUpdateButton = QPushButton('GPUpdate')
                self.commandGPUpdateButton.clicked.connect(self.commandGPUpdate)
                #
                self.commandMessageButton = QPushButton('Message')
                self.commandMessageButton.clicked.connect(self.commandMessage)
                #
                self.commandPingWindow = QLineEdit()
                self.commandPingWindow.setMaximumHeight(70)
                self.commandPingButton = QPushButton('Ping')
                self.commandPingButton.clicked.connect(self.commandPing)
                self.commandPingCheckboxLabel = QLabel('Continual')
                self.commandPingCheckboxLabel.setAlignment(Qt.AlignCenter)
                self.commandPingCheckbox = QCheckBox()
                # self.commandPingCheckbox.setAlignment(Qt.AlignRight)
                #
                # Extras
                #
                MainWindow.statusBar = QStatusBar()
                MainWindow.statusBar.setFont(statusFont)
                #
                # Host history window
                #
                self.history = QTableWidget()
                self.history.setRowCount(200)
                self.history.setColumnCount(3)
                self.history.setWindowTitle('Host History')
                self.history.resize(350, 550)
                #
                # User details window
                #
                # Set layout
                #
                grid = QGridLayout()
                self.setLayout(grid)
                #
                grid.addWidget(self.hostCombo, 0, 0, 1, 3)
                grid.addWidget(self.readHostButton, 0, 3)
                grid.addWidget(self.readHostHistoryButton, 1, 3)
                grid.addWidget(self.userButton, 2, 0)
                grid.addWidget(MainWindow.userEdit, 2, 1, 1, 2)
                grid.addWidget(self.userDetailButton, 2, 3, 1, 1)
                grid.addWidget(self.fullNameButton, 3, 0)
                grid.addWidget(MainWindow.fullNameEdit, 3, 1, 1, 3)
                grid.addWidget(self.computerModelLabel, 4, 0)
                grid.addWidget(MainWindow.computerModelResult, 4, 1, 1, 3)
                grid.addWidget(self.computerSerialLabel, 5, 0)
                grid.addWidget(MainWindow.computerSerialResult, 5, 1, 1, 3)
                grid.addWidget(self.computerIPAddressLabel, 6, 0)
                grid.addWidget(MainWindow.computerIPAddressResult, 6, 1, 1, 3)
                grid.addWidget(self.computerMACAddressLabel, 7, 0)
                grid.addWidget(MainWindow.computerMACResult, 7, 1, 1, 3)
                grid.addWidget(self.computerOSVersionLabel, 8, 0)
                grid.addWidget(MainWindow.computerOSVersionResult, 8, 1, 1, 3)
                grid.addWidget(self.computerUpTimeLabel, 9, 0)
                grid.addWidget(MainWindow.computerUpTimeResult, 9, 1, 1, 3)
                grid.addWidget(self.computerCPULabel, 10, 2)
                grid.addWidget(MainWindow.computerCPUCheckbox, 10,2)
                grid.addWidget(self.computerCPUResult, 11, 2)
                grid.addWidget(self.computerMEMLabel, 10, 3)
                grid.addWidget(self.computerMEMResult, 11, 3)
                grid.addWidget(self.commandRemoteButton, 12, 0)
                grid.addWidget(self.commandRDPButton, 12, 1)
                grid.addWidget(self.commandRebootButton, 12, 2)
                grid.addWidget(self.commandCMDButton, 12, 3)
                grid.addWidget(self.commandGPUpdateButton, 13, 0)
                grid.addWidget(self.commandMessageButton, 13, 1)
                grid.addWidget(self.commandCDriveButton, 13, 2)
                grid.addWidget(self.commandHDriveButton, 13, 3)
                # grid.addWidget(self.commandDesktopButton,14,2)
                grid.addWidget(self.commandPingWindow, 16, 0, 7, 4)
                grid.addWidget(self.commandPingButton, 15, 3)
                grid.addWidget(self.commandPingCheckboxLabel, 15, 2)
                grid.addWidget(self.commandPingCheckbox, 15, 2)
                grid.addWidget(self.statusBar, 23, 0, 1, 4)
                #
                # Setup initial state
                #checkTextPresent = str(MainWindow.userEdit.text())
                #if checkTextPresent:
                #    self.userDetailButton.setEnabled(True)
                #else:
                #    self.userDetailButton.setEnabled(False)

                self.statusBar.showMessage('Ready')
                #
                #
        def readHostOperation(self):
            if not self.readHost.isRunning():
                self.readHost.exiting = False
                self.readHost.start()
                #self.computerCPU.start()
                self.statusBar.showMessage('Pinging...')
                self.readHostButton.setEnabled(False)

        def userDetailOperation(self):
            checkTextPresent = str(MainWindow.userEdit.text())
            if MainWindow.userDetailWindow.isVisible():
                print "it's visible"
                self.userDetail.quit()
                MainWindow.userDetailWindow.clear()
                MainWindow.userDetailWindow.hide()
            elif checkTextPresent:

                print "it's not but has text so show and start thread"

                # OMG such a hack job to move the window
                newstring = str(self.pos())
                x, y = newstring.split(",", 1)
                x = x[21:]
                y = y.lstrip()
                y = y.strip(')')
                x = int(x) + 381
                y = int(y)
                MainWindow.userDetailWindow.move(x, y)
                if not self.userDetail.isRunning():
                    self.userDetail.exiting = False
                    #MainWindow.userDetailWindow.clear()
                    self.userDetail.start()
                    MainWindow.userDetailWindow.show()
                    #print userDetailThread.getFullName



        def userDetailComplete(self):
            MainWindow.userDetailWindow.appendPlainText(MainWindow.userDetailData)
            MainWindow.userDetailWindow.moveCursor(QTextCursor.Start)

        #def computerModelComplete(self):
        #    print "end model"
        #    print computerModelThread.getModel
        #    MainWindow.computerModelResult.setText(computerModelThread.getModel.text())

        def readHostComplete(self):
            self.statusBar.showMessage('Complete')
            self.readHostButton.setEnabled(True)

        def computerCPUComplete(self):
            #self.statusBar.showMessage('Complete')
            MainWindow.computerCPUResult.setText('00')

        @Slot()
        def readHostHistory(self):
            if self.history.isVisible():
                self.history.hide()
            else:
                self.history.move(self.pos())
                # OMG such a hack job to move the window
                newstring = str(self.pos())
                x, y = newstring.split(",", 1)
                x = x[21:]
                y = y.lstrip()
                y = y.strip(')')
                x = int(x) + 381
                y = int(y)
                self.history.move(x, y)
                self.history.show()

        @Slot()
        def readUser(self):
            ()

        @Slot()
        def readFullName(self):
            ()

        @Slot()
        def commandCDrive(self):
            ()

        @Slot()
        def commandHDrive(self):
            ()

        @Slot()
        def commandDesktop(self):
            ()

        @Slot()
        def commandReboot(self):
            ()

        @Slot()
        def commandRemote(self):
            ()

        @Slot()
        def commandRDP(self):
            ()

        @Slot()
        def commandCMD(self):
            ()

        @Slot()
        def commandGPUpdate(self):
            ()

        @Slot()
        def commandMessage(self):
            ()

        @Slot()
        def commandPing(self):
            print(self.pos())


if __name__=='__main__':
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
