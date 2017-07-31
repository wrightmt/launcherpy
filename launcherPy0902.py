import sys, time, re, os
from PySide.QtGui import *
from PySide.QtCore import *
import subprocess

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
                    MainWindow.statusBar.showMessage("Online - Getting info...")
                    MainWindow.computerCPU.start()

                self.exiting=True
                self.signal.sig.emit('OK')


class computerCPUThread(QThread):
        def __init__(self, parent=None):
                QThread.__init__(self, parent)
                self.exiting = False

        def run(self):
                hostname = readHostThread.currentHost
                while self.exiting == False:
                        print "start cpu thread"
                        cpuload = subprocess.Popen(["wmic", "/node:", hostname, "cpu", "get", "loadpercentage"], shell=True, stdout=subprocess.PIPE)
                        cpuload.wait()
                        response = cpuload.returncode
                        print response
                        if response == 0:
                                MainWindow.computerCPULabel.setFont(MainWindow.labelFont)
                        else:
                                MainWindow.computerCPULabel.setFont(MainWindow.hostFont)
                        cpuresult = cpuload.stdout.read()
                        print cpuresult
                        cpuInt = re.findall('\d+', cpuresult)
                        cpuInt = str(cpuInt)
                        MainWindow.computerCPUResult.setText(cpuInt)
                self.exiting = True
                self.signal.sig.emit('OK')

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
                resultFont = QFont('Serif', 12, QFont.Light)
                MainWindow.statusFont = QFont('Serif', 8, QFont.Light)
                hostFont = QFont('Serif', 11, QFont.Light)
                hostFont.setCapitalization(QFont.AllUppercase)
                # Set widgets - labels and edit boxes
                # Host widgets
                self.hostLabel = QLabel('Hostname')
                self.hostLabel.setFont(MainWindow.labelFont)
                MainWindow.hostCombo = QComboBox()
                self.hostCombo.setFont(hostFont)
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
                self.userButton.clicked.connect(self.readUser)
                self.userEdit = QLineEdit()
                self.userEdit.setFont(resultFont)
                #self.readUser = readUserThread()
                #
                self.fullNameButton = QPushButton('Name')
                self.fullNameButton.clicked.connect(self.readFullName)
                self.fullNameEdit = QLineEdit()
                self.fullNameEdit.setFont(resultFont)
                #
                # Computer widgets
                self.computerModelLabel = QLabel('Model')
                self.computerModelLabel.setFont(MainWindow.labelFont)
                self.computerModelResult = QLineEdit()
                self.computerModelResult.setFont(resultFont)
                #
                self.computerSerialLabel = QLabel('Serial')
                self.computerSerialLabel.setFont(MainWindow.labelFont)
                self.computerSerialResult = QLineEdit()
                self.computerSerialResult.setFont(resultFont)
                #
                self.computerIPAddressLabel = QLabel('IP')
                self.computerIPAddressLabel.setFont(MainWindow.labelFont)
                self.computerIPAddressResult = QLineEdit()
                self.computerIPAddressResult.setFont(resultFont)
                #
                self.computerMACAddressLabel = QLabel('MAC')
                self.computerMACAddressLabel.setFont(MainWindow.labelFont)
                self.computerMACAddressResult = QLineEdit()
                self.computerMACAddressResult.setFont(resultFont)
                #
                self.computerOSVersionLabel = QLabel('OS')
                self.computerOSVersionLabel.setFont(MainWindow.labelFont)
                self.computerOSVersionResult = QLineEdit()
                self.computerOSVersionResult.setFont(resultFont)
                #
                self.computerUpTimeLabel = QLabel('UpTime')
                self.computerUpTimeLabel.setFont(MainWindow.labelFont)
                self.computerUpTimeResult = QLineEdit()
                self.computerUpTimeResult.setFont(resultFont)
                #
                MainWindow.computerCPU = computerCPUThread()
                MainWindow.computerCPULabel = QLabel('CPU')
                MainWindow.computerCPULabel.setFont(statusFont)
                MainWindow.computerCPULabel.setAlignment(Qt.AlignRight)
                MainWindow.computerCPUResult = QLabel('00%')
                MainWindow.computerCPUResult.setFont(MainWindow.statusFont)
                MainWindow.computerCPUResult.setAlignment(Qt.AlignRight)
                #
                self.computerMEMLabel = QLabel('MEM')
                self.computerMEMLabel.setFont(statusFont)
                self.computerMEMLabel.setAlignment(Qt.AlignRight)
                self.computerMEMResult = QLabel('0/0MB')
                self.computerMEMResult.setFont(statusFont)
                self.computerMEMResult.setAlignment(Qt.AlignRight)
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
                # Set layout
                #
                grid = QGridLayout()
                self.setLayout(grid)
                #
                grid.addWidget(self.hostCombo, 0, 0, 1, 3)
                grid.addWidget(self.readHostButton, 0, 3)
                grid.addWidget(self.readHostHistoryButton, 1, 3)
                grid.addWidget(self.userButton, 2, 0)
                grid.addWidget(self.userEdit, 2, 1, 1, 3)
                grid.addWidget(self.fullNameButton, 3, 0)
                grid.addWidget(self.fullNameEdit, 3, 1, 1, 3)
                grid.addWidget(self.computerModelLabel, 4, 0)
                grid.addWidget(self.computerModelResult, 4, 1, 1, 3)
                grid.addWidget(self.computerSerialLabel, 5, 0)
                grid.addWidget(self.computerSerialResult, 5, 1, 1, 3)
                grid.addWidget(self.computerIPAddressLabel, 6, 0)
                grid.addWidget(self.computerIPAddressResult, 6, 1, 1, 3)
                grid.addWidget(self.computerMACAddressLabel, 7, 0)
                grid.addWidget(self.computerMACAddressResult, 7, 1, 1, 3)
                grid.addWidget(self.computerOSVersionLabel, 8, 0)
                grid.addWidget(self.computerOSVersionResult, 8, 1, 1, 3)
                grid.addWidget(self.computerUpTimeLabel, 9, 0)
                grid.addWidget(self.computerUpTimeResult, 9, 1, 1, 3)
                grid.addWidget(self.computerCPULabel, 10, 2)
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

        def readHostComplete(self):
            #self.statusBar.showMessage('Complete')
            self.readHostButton.setEnabled(True)

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
