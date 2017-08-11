#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, re, thread
from PySide.QtGui import *
from PySide.QtCore import *
from dateutil.parser import parse
from time import time, sleep, localtime
from datetime import datetime, timedelta
import subprocess
from subprocess import call
import socket
import csv
import wmi
import pythoncom
import win32net
import win32api


class MySignal(QObject):
        sig = Signal(str)

class readHostThread(QThread):
        def __init__(self, parent = None):
                QThread.__init__(self, parent)
                self.exiting = False
                self.signal = MySignal()

        def run(self):
                readHostThread.currentHost = str(MainWindow.hostCombo.currentText())
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
                    #MainWindow.statusBar.showMessage("Online - Getting info...")
                    clearWindowDown = u'▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼'
                    MainWindow.userEdit.setText(clearWindowDown)
                    sleep(.03)
                    MainWindow.fullNameEdit.setText(clearWindowDown)
                    sleep(.01)
                    MainWindow.userEdit.setText(' ')
                    sleep(.01)
                    MainWindow.computerModelResult.setText(clearWindowDown)
                    sleep(.01)
                    MainWindow.fullNameEdit.setText(' ')
                    sleep(.01)
                    MainWindow.computerSerialResult.setText(clearWindowDown)
                    sleep(.01)
                    MainWindow.computerModelResult.setText(' ')
                    sleep(.01)
                    MainWindow.computerIPAddressResult.setText(clearWindowDown)
                    sleep(.01)
                    MainWindow.computerSerialResult.setText(' ')
                    sleep(.01)
                    MainWindow.computerMACResult.setText(clearWindowDown)
                    sleep(.01)
                    MainWindow.computerIPAddressResult.setText(' ')
                    sleep(.01)
                    MainWindow.computerOSVersionResult.setText(clearWindowDown)
                    sleep(.01)
                    MainWindow.computerMACResult.setText(' ')
                    sleep(.01)
                    MainWindow.computerUpTimeResult.setText(clearWindowDown)
                    sleep(.01)
                    MainWindow.computerOSVersionResult.setText(' ')
                    sleep(.01)
                    MainWindow.computerUpTimeResult.setText(' ')
                    # Start threads
                    MainWindow.readUser.start()
                    MainWindow.computerModel.start()
                    MainWindow.computerCPU.start()
                    MainWindow.computerMEM.start()
                    MainWindow.checkLogon.start()

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
            #MainWindow.statusBar.showMessage('Getting info...')
            currentUser = subprocess.Popen(["wmic", "/node:", hostname, "ComputerSystem", "get", "Username"], shell=True,stdout=subprocess.PIPE)
            currentUser.wait()
            currentUserData = currentUser.stdout.read()
            currentUserData = currentUserData.rpartition('\\')[-1]
            currentUserData = currentUserData.rstrip()
            MainWindow.userEdit.setText(currentUserData)
            readUserThread.currentUserData = currentUserData
            getFullName = subprocess.Popen(["net", "user", currentUserData, "/domain"], shell=True,stdout=subprocess.PIPE)
            getFullName.wait()
            getFullName = getFullName.stdout.read()
            string = re.findall(r'Name\s*(.*?)\r\nComment', getFullName)
            string = str(string)
            plainName = re.findall('\S+', string)
            plainName = ' '.join(plainName)
            plainName = plainName.strip("['']")
            readUserThread.plainName = plainName
            MainWindow.fullNameEdit.setText(readUserThread.plainName)
            #print readUserThread.plainName
            self.signal.sig.emit('OK')
            self.exiting = True
        self.exiting = False

class quickFullnameThread(QThread):
    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.exiting = False
        self.signal = MySignal()
    def run(self):
        self.exiting = False
        while self.exiting == False:
            userName = MainWindow.userEdit.text()
            getFullName = subprocess.Popen(["net", "user", userName, "/domain"], shell=True, stdout=subprocess.PIPE)
            getFullName.wait()
            getFullName = getFullName.stdout.read()
            string = re.findall(r'Name\s*(.*?)\r\nComment', getFullName)
            string = str(string)
            plainName = re.findall('\S+', string)
            plainName = ' '.join(plainName)
            plainName = plainName.strip("['']")
            readUserThread.plainName = plainName
            MainWindow.fullNameEdit.setText(readUserThread.plainName)
            self.signal.sig.emit('OK')
            self.exiting = True
        self.exiting = False


class checkLogonThread(QThread):
    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.exiting = False
        self.signal = MySignal()

    def run(self):
        self.exiting = False
        while self.exiting == False:
            pythoncom.CoInitialize()
            procList = list()
            hostLogonCheck = wmi.WMI(readHostThread.currentHost)
            for process in hostLogonCheck.Win32_Process():
                checkProcessName = process.Name
                procList.append(checkProcessName)
            newProcList = str(procList)
            logonProc = "LogonUI.exe"
            if logonProc in newProcList:
                MainWindow.statusBar.showMessage("Online - Locked")
            else:
                MainWindow.statusBar.showMessage("Online - Unlocked")
            self.signal.sig.emit('OK')
            self.exiting = True

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
            self.signal.sig.emit('OK')
        self.exiting = True

class commandMessageThread(QThread):
    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.exiting = False
        self.signal = MySignal()

    def run(self):
        while self.exiting == False:

            print "command thread started"
            MainWindow.commandMessageData = str(MainWindow.commandMessageData)
            sendMessage = subprocess.Popen(["powershell", "-ExecutionPolicy", "Unrestricted", "\\\ISDNASBKUP\Desktop\messages\message.ps1", "-Message", '"' + MainWindow.commandMessageData + '"', "-TargetPC", MainWindow.hostCombo.currentText()], shell=True, stdout=subprocess.PIPE)
            sendMessage.wait()
            self.signal.sig.emit('OK')
            self.exiting = True
        self.exiting = False

class commandRDPThread(QThread):
    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.exiting = False
        self.signal = MySignal()

    def run(self):
        while self.exiting == False:
            print "command RDP started"
            subprocess.Popen(["mstsc", "/v:", MainWindow.hostCombo.currentText()], shell=True, stdout=subprocess.PIPE)
            self.signal.sig.emit('OK')
            self.exiting = True
        self.exiting = False

class commandCMDThread(QThread):
    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.exiting = False
        self.signal = MySignal()

    def run(self):
        while self.exiting == False:
            hostValue = MainWindow.hostCombo.currentText()
            hostHack = "\\" + "\\" + hostValue
            cmdline = "psexec %s cmd" % hostHack
            call("start cmd /K" + cmdline, shell=True)
            self.exiting = True
        self.exiting = False

class commandGPThread(QThread):
    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.exiting = False
        self.signal = MySignal()

    def run(self):
        while self.exiting == False:
            hostValue = MainWindow.hostCombo.currentText()
            hostHack = "\\" + "\\" + hostValue
            cmdline = "psexec %s gpupdate /force" % hostHack
            call("start cmd /K" + cmdline, shell=True)
            self.exiting = True
        self.exiting = False



class commandRemoteThread(QThread):
    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.exiting = False
        self.signal = MySignal()

    def run(self):
        while self.exiting == False:
            print "command remote started"
            pythoncom.CoInitialize()
            procList = list()
            hostLogonCheck = wmi.WMI(readHostThread.currentHost)
            for process in hostLogonCheck.Win32_Process():
                checkProcessName = process.Name
                procList.append(checkProcessName)
            newProcList = str(procList)
            logonProc = "cmrcservice.exe"
            if logonProc in newProcList:
                print "service running"
                runRemote = subprocess.Popen(["cmrcviewer", MainWindow.hostCombo.currentText()], shell=True, stdout=subprocess.PIPE)
            else:
                hostValue = MainWindow.hostCombo.currentText()
                hostHack = "\\" + "\\"  + hostValue
                print hostHack
                MainWindow.statusBar.showMessage('Starting service')
                subprocess.Popen(["psexec", hostHack, "net", "start", "cmrcservice"], shell=True,stdout=subprocess.PIPE)
                #checkService.wait()
                subprocess.Popen(["cmrcviewer", MainWindow.hostCombo.currentText()], shell=True,stdout=subprocess.PIPE)
                #runRemote.wait()
                self.signal.sig.emit('OK')
                self.exiting = True
        self.exiting = False

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
                        #MainWindow.hostLogonCheck()
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
            MainWindow.computerOSVersionResult.setText(computerOSString)
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
            # Check/add current hostname to combobox
            checklist = MainWindow.hostCombo.findText(readHostThread.currentHost, Qt.MatchFixedString)
            if checklist == -1:
                MainWindow.hostCombo.addItem(readHostThread.currentHost)
            else:
                pass
            ###HISTORY###
            historyNameItem = QTableWidgetItem(readUserThread.currentUserData)
            timeStamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            historyHostItem = QTableWidgetItem(readHostThread.currentHost)
            historyTimeStampItem = QTableWidgetItem(timeStamp)
            MainWindow.history.insertRow(0)
            MainWindow.history.setItem(0, 0, historyTimeStampItem)
            MainWindow.history.setItem(0, 1, historyHostItem)
            MainWindow.history.setItem(0, 2, historyNameItem)
            # write to csv
            #print readUserThread.currentUserData
            historyUpdateString = timeStamp+","+readHostThread.currentHost+","+readUserThread.currentUserData+","+ '\n'
            #
            # update the history file
            fd = open('history.csv', 'a')
            fd.write(historyUpdateString)
            fd.close()
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
                self.exiting = True
            availmemresult = availmem.stdout.read()
            availmemInt = re.findall('\d+', availmemresult)
            availmemInt = " ".join(availmemInt)
            availmemInt = int(availmemInt)
            availmemInt = availmemInt / 1024
            availmemInt = str(availmemInt)
            MainWindow.computerMEMResult.setText(availmemInt + '/' + totalmemInt+'MB')
            self.exiting = True
            #MainWindow.hostLogonCheck()
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
                # set always on top
                self.alwaysOnTop = QPushButton('Top')
                self.alwaysOnTop.clicked.connect(self.alwaysOnTopSet)
                # logon check
                MainWindow.checkLogon = checkLogonThread()
                #self.checkLogon.signal.sig.connect(self.checkLogon)
                # dumb ping process
                #
                self.process = QProcess(self)
                self.process.readyRead.connect(self.dataReady)
                #MainWindow.systemLocked = systemLockedThread()
                #MainWindow.systemLocked.signal.sig.connect(MainWindow.systemLocked)
                #
                self.readHostHistoryButton = QPushButton('History')
                self.readHostHistoryButton.clicked.connect(self.readHostHistory)
                #
                # User widgets
                self.userButton = QPushButton('User')
                self.quickFullnameThread = quickFullnameThread()
                self.userButton.clicked.connect(self.quickFullname)
                MainWindow.userEdit = QLineEdit()
                MainWindow.userEdit.setFont(MainWindow.resultFont)
                MainWindow.readUser = readUserThread()
                #####################READ FULL NAME###################################
                MainWindow.userDetailWindow = QPlainTextEdit()
                MainWindow.userDetailWindow.setReadOnly(True)
                MainWindow.userDetailWindow.setWindowTitle('User Details')
                MainWindow.userDetailWindow.resize(400, 550)
                MainWindow.userDetailButton = QPushButton('Details')
                MainWindow.userDetailButton.clicked.connect(self.userDetailOperation)
                self.userDetail = userDetailThread()
                self.userDetail.signal.sig.connect(self.userDetailComplete)
                ######################################################################
                self.fullNameButton = QLabel('Name')
                #self.fullNameButton.clicked.connect(self.readFullName)
                MainWindow.fullNameEdit = QLineEdit()
                MainWindow.fullNameEdit.setFont(MainWindow.resultFont)
                self.fullNameButton.setFont(MainWindow.labelFont)
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
                MainWindow.computerCPUCheckboxLabel = QLabel('Monitor')
                MainWindow.computerCPUCheckboxLabel.setAlignment(Qt.AlignCenter)
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
                MainWindow.hostLogonCheck = self.hostLogonCheck
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
                self.commandRemoteThread = commandRemoteThread()
                self.commandRemoteButton = QPushButton('Remote')
                self.commandRemoteButton.clicked.connect(self.commandRemote)

                #
                self.commandRDPButton = QPushButton('RDP')
                self.commandRDPButton.clicked.connect(self.commandRDP)
                self.commandRDPThread = commandRDPThread()
                #
                self.commandCMDButton = QPushButton('CMD')
                self.commandCMDButton.clicked.connect(self.commandCMD)
                self.commandCMDThread = commandCMDThread()
                #
                self.commandGPUpdateButton = QPushButton('GPUpdate')
                self.commandGPUpdateButton.clicked.connect(self.commandGP)
                self.commandGPThread = commandGPThread()
                #
                self.commandMessageThread = commandMessageThread()
                self.commandMessageButton = QPushButton('Message', self)
                self.commandMessageButton.clicked.connect(self.commandMessage)
                #MainWindow.commandMessageData = QLineEdit(self)
                #
                self.commandPingWindow = QTextEdit()
                self.commandPingWindow.setMaximumHeight(70)
                self.commandPingButton = QPushButton('Ping')
                #self.pingThread = pingThread()
                self.commandPingButton.clicked.connect(self.ping)
                self.commandPingCheckboxLabel = QLabel('Continual')
                self.commandPingCheckboxLabel.setAlignment(Qt.AlignCenter)
                self.commandPingCheckbox = QCheckBox()
                #
                # Extras
                #
                MainWindow.statusBar = QStatusBar()
                MainWindow.statusBar.setFont(statusFont)
                #
                # Host history window
                #
                MainWindow.history = QTableWidget()
                MainWindow.history.itemClicked.connect(self.historyHost)
                self.history.setRowCount(200)
                self.history.setColumnCount(3)
                self.history.setWindowTitle('Host History')
                self.history.resize(400, 550)
                self.historyColumnLabels = ["Viewed","Hostname","User"]
                self.history.setHorizontalHeaderLabels(self.historyColumnLabels)

                # import history.csv into table
                # hacky bullshit to make it read in reverse
                historyFile = "history.csv"
                readHistoryFile = open(historyFile, "r")
                lines = readHistoryFile.readlines()
                MainWindow.history.tableRow = len(lines)
                newRowNumber = 0
                readHistoryFile.close()
                with open('history.csv', 'r') as textfile:
                    for row in reversed(list(csv.reader(textfile))):
                        myList = [i.split(',')[0] for i in row]
                        viewed = myList[0]
                        host = myList[1]
                        user = myList[2]
                        viewedItem = QTableWidgetItem(viewed)
                        hostItem = QTableWidgetItem(host)
                        userItem = QTableWidgetItem(user)
                        MainWindow.history.setItem(newRowNumber,0,viewedItem)
                        MainWindow.history.setItem(newRowNumber, 1, hostItem)
                        MainWindow.history.setItem(newRowNumber, 2, userItem)
                        newRowNumber += 1
                self.history.horizontalHeader().setResizeMode(QHeaderView.Stretch)
                # User details window
                #
                # Set layout
                #
                grid = QGridLayout()
                self.setLayout(grid)
                #
                grid.addWidget(self.hostCombo, 0, 0, 1, 3)
                grid.addWidget(self.readHostButton, 0, 3)
                grid.addWidget(self.alwaysOnTop, 1, 0)
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
                grid.addWidget(MainWindow.computerCPUCheckboxLabel, 10,1)
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
                #Set always on top
                self.ontopflag = 0
                #

        def readHostOperation(self):
            if not self.readHost.isRunning():
                self.readHost.exiting = False
                self.readHost.start()
                self.statusBar.showMessage('Getting info...')
                self.readHostButton.setEnabled(False)

        def userDetailOperation(self):
            checkTextPresent = str(MainWindow.userEdit.text())
            if MainWindow.userDetailWindow.isVisible():
                print "it's visible"
                self.userDetail.quit()
                MainWindow.userDetailWindow.clear()
                MainWindow.userDetailWindow.hide()
            elif checkTextPresent:
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
                    self.userDetail.start()


        def userDetailComplete(self):
            MainWindow.userDetailWindow.show()
            MainWindow.userDetailWindow.appendPlainText(MainWindow.userDetailData)
            #MainWindow.userDetailWindow.moveCursor(QTextCursor.Start)


        def readHostComplete(self):
            #self.statusBar.showMessage('Complete')
            self.readHostButton.setEnabled(True)
            #self.hostLogonCheck()

        #@Slot()
        def hostLogonCheck(self):
            pythoncom.CoInitialize()
            hostLogonCheck = wmi.WMI(self.hostCombo.currentText())
            procList = list()
            for process in hostLogonCheck.Win32_Process():
                checkProcessName = process.Name
                procList.append(checkProcessName)
            newProcList = str(procList)
            logonProc = "LogonUI.exe"
            if logonProc in newProcList:
                MainWindow.statusBar.showMessage("Online - Locked")
            else:
                MainWindow.statusBar.showMessage("Online - Unlocked")

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
                self.history.setSortingEnabled(False)
                #self.history.sortItems(0, Qt.AscendingOrder)
                #self.history.sortItems(1, Qt.AscendingOrder)
                #self.history.sortItems(2, Qt.AscendingOrder)
                #self.history.sortItems(0[, order=AscendingOrder])

        def historyHost(self, item):
            # Takes the item from the history and sets it as host
            updateHost = item.text()
            #print MainWindow.hostCombo.currentIndex
            #MainWindow.hostCombo.InsertPolicy.InsertAtTop
            #MainWindow.hostCombo.insertItem(0, updateHost)
            #MainWindow.hostCombo.itemData(0)
            MainWindow.hostCombo.setEditText(updateHost)



        @Slot()
        def commandCDrive(self):
            hostname = str(self.hostCombo.currentText())
            try:
                cdrivepath = "\\\%s\c$" % hostname
                subprocess.Popen(r"explorer /open,%s" % cdrivepath)
            except Exception:
                pass

        @Slot()
        def commandHDrive(self):
            try:
                hdrivepath = "\\tacfil02\users\%s" % MainWindow.userEdit.text()
                subprocess.Popen(r"explorer /open,\%s" % hdrivepath)
            except Exception:
                pass

        @Slot()
        def commandDesktop(self):
            ()

        @Slot()
        def commandReboot(self):
            hostname = str(self.hostCombo.currentText())
            c = wmi.WMI(computer=hostname, privileges=["RemoteShutdown"])
            os = c.Win32_OperatingSystem(Primary=1)[0]
            reply = QMessageBox.question(self, 'Are you sure?', "Really reboot %s?" % hostname,QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                os.Reboot()
            else:
                pass

        @Slot()
        def commandRemote(self):
            if not self.commandRemoteThread.isRunning():
                self.commandRemoteThread.exiting = False
                self.commandRemoteThread.start()
                self.statusBar.showMessage('Starting remote')
                #self.readHostButton.setEnabled(False)

        @Slot()
        def commandRDP(self):
            print "RDP start"
            if not self.commandRDPThread.isRunning():
                self.commandRDPThread.exiting = False
                self.commandRDPThread.start()

        @Slot()
        def commandCMD(self):
            print "CMD start"
            if not self.commandCMDThread.isRunning():
                self.commandCMDThread.exiting = False
                self.commandCMDThread.start()

        @Slot()
        def commandGP(self):
            print "GP start"
            if not self.commandGPThread.isRunning():
                self.commandGPThread.exiting = False
                self.commandGPThread.start()
        @Slot()
        def commandMessage(self):
            self.exiting = False
            text, ok = QInputDialog.getText(self, 'Display Message', 'Message:')
            if ok:
                MainWindow.commandMessageData=(str(text))
                print MainWindow.commandMessageData
                self.commandMessageThread.start()

        def ping(self):
            # start ping process one time or continual, kill process on start. Not sure if this is working correctly
            hostname = str(self.hostCombo.currentText())
            self.commandPingWindow.clear()
            self.process.kill()
            if self.commandPingCheckbox.isChecked() == True:
                self.process.start("ping", ["-t", hostname])
            else:
                self.process.start("ping", [hostname])

        def dataReady(self):
            cursor = self.commandPingWindow.textCursor()
            cursor.movePosition(cursor.End)
            cursor.insertText(str(self.process.readAll()))
            self.commandPingWindow.ensureCursorVisible()
            if self.commandPingCheckbox.isChecked() == False:
                self.process.kill()

        @Slot()
        def commandPing(self):
            if not self.pingThread.isRunning():
                self.pingThread.exiting = False
                self.pingThread.start()

        @Slot()
        def quickFullname(self):
            if not self.quickFullnameThread.isRunning():
                self.quickFullnameThread.exiting = False
                self.quickFullnameThread.start()

        @Slot()
        def alwaysOnTopSet(self):
            self.setWindowFlags(self.windowFlags() ^ Qt.WindowStaysOnTopHint)
            window.show()

if __name__=='__main__':
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
