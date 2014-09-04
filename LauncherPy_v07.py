#LauncherPy v0.7
#Qt PySide implementation
import sys
sys.stderr = sys.stdout
from PySide.QtGui import *
from PySide.QtCore import *
import re
import active_directory
import wmi
import datetime
from datetime import *
from dateutil.parser import parse
import os
import win32net
import win32api
import subprocess
import socket

qt_app = QApplication(sys.argv)

class LauncherPySide(QWidget):
	
	def __init__(self,parent):		
		QWidget.__init__(self)
		self.process = QProcess(self)
		self.setWindowTitle("LauncherPy v0.7")
		self.resize(325,400)
		self.setFixedSize(self.size())
		font = QFont('Serif', 12, QFont.Light)
		font1 = QFont('Serif', 11, QFont.Light)
		font2 = QFont('Serif', 11, QFont.Light)
		font2.setCapitalization(QFont.AllUppercase)
		grid = QGridLayout()
		self.sb = QStatusBar()
		self.sb.setFont(font)
		self.sb.setFixedHeight(18)
		host_l = QLabel('<b>Hostname</b>')
		host_l.setFont(font1)
		logon_l = QLabel('<b>Logon</b>')
		logon_l.setFont(font1)
		name_l = QLabel('<b>Name</b>')
		name_l.setFont(font1)
		model_l = QLabel('<b>Model</b>')
		model_l.setFont(font1)
		serial_l = QLabel('<b>Serial</b>')
		serial_l.setFont(font1)
		uptime_l = QLabel('<b>Uptime</b>')
		uptime_l.setFont(font1)
		os_l = QLabel('<b>OS</b>')
		os_l.setFont(font1)
		ip_l = QLabel('<b>IP</b>')
		ip_l.setFont(font1)
		self.pingcheck_l = QLabel('Continual')
		
		
		verticalLine = QFrame()
		verticalLine.setFrameStyle(QFrame.VLine)
		verticalLine.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Expanding)
		
		self.host_e = QComboBox()
		self.host_e.setEditable(True)
		
		self.host_e.setFont(font2)
		self.logon_e = QLineEdit()
		self.name_e = QLineEdit()
		self.model_e = QLineEdit()
		self.serial_e = QLineEdit()
		self.uptime_e = QLineEdit()
		self.os_e = QLineEdit()
		self.ip_e = QLineEdit()
		self.ping_box = QTextEdit()
		self.ping_box.setMaximumHeight(70)
		self.pingcheck = QCheckBox()
		self.pingcheck.setText("Continual")
		go_butt = QPushButton('Go')
		go_butt.clicked.connect(self.gethost)
		go_butt.setAutoDefault(True)
		remote_butt = QPushButton('Remote')
		remote_butt.clicked.connect(self.remote)
		rdp_butt = QPushButton('RDP')
		rdp_butt.clicked.connect(self.rdp)
		reboot_butt = QPushButton('Reboot')
		reboot_butt.clicked.connect(self.reboot)
		self.ping_butt = QPushButton('Ping')
		self.ping_butt.clicked.connect(self.ping)
		self.profile_butt = QPushButton('Profile')
		self.profile_butt.clicked.connect(self.profile)
		self.hdrive_butt = QPushButton('H Drive')
		self.hdrive_butt.clicked.connect(self.hdrive)
		self.cdrive_butt = QPushButton('C Drive')
		self.cdrive_butt.clicked.connect(self.cdrive)
		
		
		grid.addWidget(host_l,0,0)
		grid.addWidget(self.host_e,0,1)
		grid.addWidget(go_butt,0,2)
		grid.addWidget(logon_l,1,0)
		grid.addWidget(self.logon_e,1,1,1,2)
		grid.addWidget(name_l,2,0)
		grid.addWidget(self.name_e,2,1,1,2)
		grid.addWidget(model_l,3,0)
		grid.addWidget(self.model_e,3,1,1,2)
		grid.addWidget(serial_l,4,0)
		grid.addWidget(self.serial_e,4,1,1,2)
		grid.addWidget(uptime_l,5,0)
		grid.addWidget(self.uptime_e,5,1,1,2)
		grid.addWidget(os_l,6,0)
		grid.addWidget(self.os_e,6,1,1,2)
		grid.addWidget(ip_l,7,0)
		grid.addWidget(self.ip_e,7,1,1,2)
		grid.addWidget(self.profile_butt,9,0)
		grid.addWidget(self.hdrive_butt,9,1)
		grid.addWidget(self.cdrive_butt,9,2)
		grid.addWidget(remote_butt,8,0)
		grid.addWidget(reboot_butt,8,2)
		grid.addWidget(rdp_butt,8,1)
		grid.addWidget(self.ping_butt,11,1)
		grid.addWidget(self.ping_box,10,0,1,3)
		grid.addWidget(self.sb,12,0,1,3)
		grid.addWidget(self.pingcheck,11,2)
		self.sb.showMessage("Ready")
		self.process.readyRead.connect(self.dataReady)
		self.setLayout(grid)
		
	
	def paintEvent(self, event):
		self.tile = QPixmap("bg_uxc.png")
		painter = QPainter(self)
		painter.drawTiledPixmap(self.rect(), self.tile)
		#paintEvent(event)
		
	def dataReady(self):
		#updates ping box with data from ping process
		cursor = self.ping_box.textCursor()
		cursor.movePosition(cursor.End)
		cursor.insertText(str(self.process.readAll()))
		self.ping_box.ensureCursorVisible()
		
	def getwmi(self):
		try:
			
			self.sb.showMessage("Online")
			hostname = str(self.host_e.currentText())
			#resolve ip from hostname and update label
			data = socket.gethostbyname(hostname)
			ip = repr(data)
			rip = re.compile("\'(.*?)\'")
			mip = rip.search(ip)
			ipstrip = mip.group(1)    
			self.ip_e.setText(ipstrip)
			#get os version
			c = wmi.WMI(hostname)
			for os in c.Win32_OperatingSystem():
				self.os_e.setText(os.caption)
			#convert wmi timestamp and calc uptime
				now = datetime.now()
				boot = os.LastBootUpTime
				boot = boot.split('.')[0]
				boot = parse(boot, fuzzy=True)
				totuptime = str(now - boot)
				totuptime = totuptime.split('.')[0]
				self.uptime_e.setText(totuptime)
			#set serial
			for bios in c.Win32_BIOS():
				self.serial_e.setText(bios.SerialNumber)
			#set model
			for sys in c.Win32_ComputerSystem():
					self.model_e.setText(sys.Model)
			
			#set logon and fullname
			if sys.Username > " ":
				usersplit = str(sys.UserName)
				domain,login=usersplit.split("\\")
				self.login = login
				self.logon_e.setText(self.login)
				fullname = str(active_directory.find_user(login))
				r = re.compile('CN=(.*?),OU')
				m = r.search(fullname)
				if m:
					fullnamedisplay = m.group(1)
					self.name_e.setText(fullnamedisplay)
				else:
					self.logon_e.setText("No user login")
		
		except Exception:
                    self.sb.showMessage("WMI Failed")
	
	@Slot()
	def gethost(self):
		#Init all labels
		self.sb.showMessage('Trying...')
		self.name_e.setText('')
		self.os_e.setText('')
		self.serial_e.setText('')
		self.model_e.setText('')
		self.uptime_e.setText('')
		self.logon_e.setText('')
		self.ip_e.setText('')
		self.ping_box.setText('')
		#Check/add current hostname to combobox
		hostname = str(self.host_e.currentText())
		checklist = self.host_e.findText(hostname, Qt.MatchFixedString)
		if checklist == -1:
			self.host_e.addItem(hostname)
		else:
			pass
		
		#ping host and set status
		process = subprocess.Popen(["ping", "-n", "1", hostname], shell=True, stdout=subprocess.PIPE)
		process.wait()
		response = process.returncode
		result_str = process.stdout.read()
		r = re.compile('Destination host unreachable')
		m = r.search(result_str)
		if m or response == 1:
			self.sb.showMessage("Offline")
	
		else:
			self.getwmi()
	
	@Slot()
	def remote(self):
		#SCCM remote control
		hostname = str(self.host_e.currentText())
		hostname = str(hostname.upper())
		cmd = 'C:\\Program Files\\Microsoft Configuration Manager\\AdminConsole\\bin\\i386\\CmRcViewer.exe "%s"' % hostname
		win32api.WinExec(cmd)
	
	@Slot()
	def reboot(self):
		#reboot control and dialog box
		hostname = str(self.host_e.currentText())
		c = wmi.WMI(computer=hostname, privileges=["RemoteShutdown"])
		os = c.Win32_OperatingSystem (Primary=1)[0]
		reply = QMessageBox.question(self, 'Are you sure Jen?',"Really reboot %s?" % hostname, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
		if reply == QMessageBox.Yes:
			os.Reboot()
		else:
			pass
	
	@Slot()
	def rdp(self):
		#rdp control
		hostname = str(self.host_e.currentText())
		hostname = str(hostname.upper())
		cmd = 'mstsc /v:"%s"' % hostname
		win32api.WinExec(cmd)
	
	@Slot()
	def ping(self):
		#start ping process one time or continual, kill process on start. Not sure if this is working correctly
		hostname = str(self.host_e.currentText())
		self.process.kill()
		if self.pingcheck.isChecked() == True:
			self.process.start("ping",["-t",hostname])
		else:
			self.process.start("ping",[hostname])

	
	@Slot()
	def profile(self):
		try:
			profilepath = "\\tacfil02\profiles$\%s.v2" % self.login
			subprocess.Popen(r"explorer /open,\%s" % profilepath)
		except Exception:
			pass
	
	@Slot()
	def hdrive(self):
		try:
			hdrivepath = "\\tacfil02\users\%s" % self.login
			subprocess.Popen(r"explorer /open,\%s" % hdrivepath)
		except Exception:
			pass
	
	@Slot()
	def cdrive(self):
		hostname = str(self.host_e.currentText())
		try:
			cdrivepath = "\\\%s\c$" % hostname
			subprocess.Popen(r"explorer /open,%s" % cdrivepath)
		except Exception:
			pass
			
	def run(self):
		
		self.show()
		qt_app.exec_()

app = LauncherPySide(False)
app.run()