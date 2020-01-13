import matplotlib.pyplot as plt
from PyQt5 import QtWidgets
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from packet import Packet
import csv
import time
import calendar
import datetime
import sys

class Plotter(QtWidgets.QDialog):
	def __init__(self, parent=None):
		super(Plotter, self).__init__(parent)

		self.t_stmp_day,self.t_stmp, self.bat_volt, self.ai, self.eventsrc, self.sf, self.lte_connect_time = [],[],[],[],[],[],[]
		self.figure = Figure()
		self.ax = self.figure.add_subplot(111)
		self.ax.set_xlabel("Time")
		self.canvas = FigureCanvas(self.figure)
		self.toolbar = NavigationToolbar(self.canvas, self)
		self.button = QtWidgets.QPushButton('Clear Plot')
		self.button.clicked.connect(self.clearplot)
		self.loadfilebtn = QtWidgets.QPushButton("Select File to plot")
		self.loadfilebtn.clicked.connect(self.file_open)
		self.cbox_list, self.ax_list = [],[]

		check_boxes = ['BAT', 'LTE time', 'AI', 'EventSrc', 'SF']
		colors = ['b', 'g', 'r', 'y', 'm']

		for i, box in enumerate(check_boxes):
			ax = self.ax.twinx()
			cbox = QtWidgets.QCheckBox(box)
			cbox.stateChanged.connect(self.plot(cbox, box, colors[i], i, ax))
			self.cbox_list.append(cbox)
			self.ax_list.append(ax)

		self.filenamelabel = QtWidgets.QLabel()

		# set the layout
		widgets = [self.toolbar, self.canvas, self.button,self.loadfilebtn, self.filenamelabel]
		layout = QtWidgets.QVBoxLayout()
		for item in widgets:
			layout.addWidget(item)

		for item in self.cbox_list:
			layout.addWidget(item)

		self.setLayout(layout)

		try:
			self.filename = sys.argv[1]
		except:
			self.filename = None
			print ("Select a file")

		if self.filename != None:
			self.file_data(self.filename)
			self.filenamelabel.setText(self.filename)

	def file_data(self,device_file):
		print ("Device file:" + device_file)
		device_id = device_file.split("_")[1].split(".")[0]
		prev_packet_num, packet_num, SFum = -1, -1, 0
		packet_list = []
		cur_packet = Packet()
		SFcolum = True

		with open(device_file) as csv_file:
			csv_reader = csv.reader(csv_file, delimiter=',')
			for line in csv_reader:
				if not line[17] in (None, ""):
					try:
	   					SFum += float(line[17]) +3
					except:
						continue
		if SFum == 0:
			SFcolum=False

		print ("SFcoulm exist: " + str(SFcolum))

		with open(device_file) as csv_file:
			csv_reader = csv.reader(csv_file, delimiter=',')
			for indx, row in enumerate(csv_reader):
				if row[19] in (None, "") or indx == 0:
					continue
				packet_num = int(row[19])

				# Check if new packet
				if packet_num != prev_packet_num:
					prev_packet = cur_packet
					prev_packet_num = packet_num

					#if packet is complete, append to list
					if prev_packet.is_packet_complete(SFcolum) == True:
						print ("Packet Complete")
						packet_list.append(prev_packet)

					cur_packet = Packet()
					cur_packet.number = packet_num

				try:
					if not(row[3] in (None, "")):
						cur_packet.battery_voltage = (float(row[3]))
						cur_packet.local_time = (float(row[0]))
					if not(row[7] in (None, "")):
						cur_packet.lte_time = (float(row[7]))
					if not(row[2] in (None, "")):
						cur_packet.ai = (float(row[2]))
					if not(row[8] in (None, "")):
						cur_packet.event_source = (float(row[8]))
					if not(row[17] in (None, "")):
						cur_packet.sf = (float(row[17]))
				except:
					print("error reading row")
					continue

		for packet in packet_list:
			print (packet)
			self.bat_volt.append(packet.battery_voltage)
			self.t_stmp.append(packet.local_time)
			self.t_stmp_day.append(packet.local_time/(3600*24))
			self.lte_connect_time.append(packet.lte_time)
			self.ai.append(packet.ai)
			self.eventsrc.append(packet.event_source)
			self.sf.append(packet.sf)

	def file_open(self):
		self.name = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File')[0]

		#Get data from file
		if self.name:
			print (self.name)
			self.file_data(self.name)
		else:
			self.filenamelabel.setText("Select a file to plot")

		#set the file name as label in GUI
		self.filenamelabel.setText(self.name)

	def plot(self, button, label, color, ydata, twinax):
		def subplot():
			data_list = [self.bat_volt, self.lte_connect_time, self.ai, self.eventsrc, self.sf]
			position = 0
			if button.isChecked() == True:
				twinax.set_ylim(min(data_list[ydata]), max(data_list[ydata]))
				twinax.set_ylabel(label)
				style = '%s-' %color

				# plot data
				p1 = self.ax.plot(self.t_stmp_day, data_list[ydata], style, label=label)

				if ydata > 0:
					position += 20
					twinax.spines['right'].set_position(('outward', position))
					twinax.yaxis.set_ticks_position('right')
					twinax.tick_params(axis='y', colors=color)

				# refresh canvas
				self.canvas.draw()
			else:
				twinax.clear()
				self.canvas.draw()
		return subplot

	def clearplot(self):
		#Clear plot
		self.ax.clear()
		for ax in self.ax_list:
			ax.clear()

		#define x-axis limits
		xlimit = self.t_stmp_day[-1]
		xmin =min(self.t_stmp_day)

		#Set x-axis limits and label
		self.ax.set_xlim(xmin, xlimit)
		self.ax.set_xlabel("Time (days)")
		self.canvas.draw()

		#Uncheck checkbuttons
		for box in self.cbox_list:
			box.setChecked(False)
			box.isChecked() == False

if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	main = Plotter()
	main.show()
	sys.exit(app.exec_())
