# -*- coding: utf-8 -*-
import traceback
import matplotlib
import numpy as np
import tkinter as tk
from ast import literal_eval
from funksjoner import customSlicePlot



# Bruker mplcursors-pakken til å velge datapunkter om den er installert (ellers ignoreres dette)
Interactivity = True
try:
	import mplcursors
	#from reliability.Other_functions import crosshairs
except:
	Interactivity = False
#_______________________________________



# Klassen som inneholder data og metoder til visualisering av plott

class PlotObject:

	def __init__(self, Data, Configs, sock=None, gui=True):
		self.Data = Data
		self.sock = sock
		self.DataToPlot = {} # data that will be plottet

		# Plotmethod 1 is a slow consumer of data
		if Configs.Online and Configs.plotMethod == 1:
			sock.setblocking(False)

		self.Configs = Configs
		self.gui = gui
		self.bytesData = b""
		self.validSubplot = {}

		# Interactive variables for marking datapoints
		self.DecimalsX = 2
		self.DecimalsY = 2
		self.CurrentAnnotation = None

	def create(self, nrows, ncols, sharex=False):

		# Qt5Agg/QtAgg er ideelle backends (etter min mening) på mac (veldig rask og responsivt). 
		# TkAgg og macosx er ok backends. (TkAgg ser ut som å være default backend på windows)
		# macosx fungerer ikke med plottemetode 2

		# detekterer plotte-metode 2 og prøver å skifte backend (gir status melding i konsollen)
		print("\n___Status for plotting___",flush=True)
		try:
			matplotlib.use(self.Configs.plotBackend)
			print(f"The student has chosen backend {self.Configs.plotBackend}",flush=True)
		except:
			if  matplotlib.get_backend().lower() == "macosx": #Configs.plotMethod == 2 and
				backends = ["macosx","Qt5Agg","QtAgg","TkAgg"]
				success=0
				for b in backends:
					try:
						matplotlib.use(b)
						print(f"Switching backend from macosx to {b}",flush=True)
						success=1
						break
					except:
						pass
				if not success:
					print("Important: Please choose plot-method 1. read more here: https://matplotlib.org/3.5.0/users/explain/backends.html",flush=True)
					print("Failed to switch backend from macosx",flush=True)
		import matplotlib.pyplot as plt
		from matplotlib.animation import FuncAnimation
		self.plt = plt
		self.FuncAnimation = FuncAnimation
		print(f"Using backend {matplotlib.get_backend().lower()} for plotting",flush=True)
		if matplotlib.get_backend().lower() == "macosx" and self.Configs.plotMethod == 2:
			print("macosx backend does not support plot-method 2!",flush=True)
		print("_________________________\n",flush=True)
		#__________________________________________________________________


		if self.Configs.Online and self.gui:
			self.window = tk.Tk()
		self.nrows = nrows
		self.ncols = ncols
		self.fig, self.ax = plt.subplots(nrows, ncols, sharex=sharex)
		self.counter = 0
		self.Mapping = {}
		self.figure_list = []
		self.x_label_list = []
		self.y_label_list = []
		self.lines = {}

		# keep track of highest/lowest value to manually update limits of y-axis when blitting
		self.y_limits = {}

		# formats the subplots to one dimension list
		if self.nrows*self.ncols > 1:
			iterator = self.ax.flat
		else:
			iterator = [self.ax]

		for subplot in iterator:
			
			if self.Configs.plotMethod == 2:
				subplot.get_xaxis().get_label().set_visible(False)
				subplot.tick_params(axis='x', colors='None') 
				subplot.tick_params(axis='y', colors='None')
				

			# initiates a map/dict to be used to access the artists easier
			self.Mapping[subplot] = {
				"min": None, 
				"max": None,
				"maxX": None,
				"x_label": None,
				"count" : 1
			}
		

	def plot(self, subplot, x,  y, **kwargs):
		lineInfo = {}

		xListName = None
		yListName = None
		
		try:
			xListName, xStart,xEnd = customSlicePlot(self.Data,x)
			yListName, yStart,yEnd = customSlicePlot(self.Data,y)
		except KeyError as e:
			print(flush=True)
			print('_________FEIL VED INNSENDING AV VARIABEL TIL PLOTTING_________',flush=True)
			print(f'Variabelen {e} er ikke definert',flush=True)
			print('Sjekk om navnet er stavet riktig (case sensitive) i Main.py filen',flush=True)
			print('Sjekk om du har sendt inn riktig navn i plt.plot(...) i PLOT DATA seksjonen',flush=True)
			print("Traceback: Sjekk 'PLOT DATA' seksjon i Main.py",flush=True)
			print('____________________________________________________________',flush=True)
			print(flush=True)
			raise SystemExit()
			
		self.DataToPlot[xListName] = xListName
		self.DataToPlot[yListName] = yListName

		# REQUIRED
		lineInfo["lineId"] = self.counter
		lineInfo["subplot"] = subplot
		lineInfo["xListName"] = xListName
		lineInfo["yListName"] = yListName

		lineInfo["xStart"] = xStart
		lineInfo["xEnd"] = xEnd
		lineInfo["yStart"] = yStart
		lineInfo["yEnd"] = yEnd

		# OPTIONAL
		lineInfo["color"] = kwargs.get("color","b") or "b"
		lineInfo["linestyle"] = kwargs.get("linestyle","solid") or "solid"
		lineInfo["linewidth"] = kwargs.get("linewidth",1) or 1
		lineInfo["marker"] = kwargs.get("marker","")

		# FULL BLITTING OPTIONAL
		lineInfo["xname"] =  kwargs.get("xname",xListName) or xListName
		lineInfo["yname"] = kwargs.get("yname",yListName) or yListName
		lineInfo["ycolor"] = kwargs.get("ycolor",lineInfo["color"]) or lineInfo["color"]

		self.lines[self.counter] = lineInfo
		self.counter +=1
		self.validSubplot[subplot] = True

		lineInfo["label_index"] = self.Mapping[subplot]["count"]
		self.Mapping[subplot]["count"] += 1


	
	def plotData(self):
		try:
			if self.Configs.plotMethod == 1:
				for lineInfo in self.lines.values():
					subplot = lineInfo["subplot"]
					for line in subplot.get_lines():
						line.remove()
						
			# Håndtering av plottemetoder
			for line in self.lines.values():
				if self.Configs.plotMethod == 1:
					self.Extended(line)
				elif self.Configs.plotMethod == 2:
					self.Blitting(line)
				else:
					raise Exception("Velg plottemetode 1 eller 2")

		except TypeError:
			print(flush=True)
			print('________TRYING TO PLOT DATA WITH WRONG TYPES_________',flush=True)
			print('Make sure the lists you send into plotting contain actual numbers',flush=True)
			print('Trying to plot a list containing string makes no sense and will cause an error',flush=True)
			print("Traceback: Don't send a list that contain string elements into PLOT DATA in Main.py",flush=True)
			print('____________________________________________________________',flush=True)
			print(flush=True)
			raise SystemExit()
		
		except:
			traceback.print_exc()
			self.stopPlot()



	def live(self,i): # i is required internally (removing this causes bugs when resizing window)
		
		while True:
			if self.Configs.plotMethod == 1:
				try:
					received = self.sock.recv(4096)
					if received == b'':
						break
					self.bytesData += received
				except BlockingIOError:
					if self.bytesData.find(b'?') != -1:
						break
				except OSError:
					print("Something went wrong when reading socket",flush=True)
					print("Check ev3 terminal",flush=True)
					raise SystemExit()
			else:
				try:
					received = self.sock.recv(2048)
					self.bytesData += received
					if received.find(b'?') != -1:
						break
				except OSError:
					print("Something went wrong when reading socket",flush=True)
					print("Check ev3 terminal",flush=True)
					raise SystemExit()
		
		splitData = self.bytesData.split(b"?")
		self.bytesData = b""
		for dataEntry in splitData:
			if dataEntry == b'':
				continue
			elif dataEntry == b"end":
				print("Recieved end signal",flush=True)
				self.stopPlot()
				break
			try:
				strDict = dataEntry.decode("utf-8")
				dataDict = literal_eval(strDict)
				# Insert data into lists on the computer
				for key in dataDict:
					self.Data[key].append(dataDict[key])
					if self.Configs.plotMethod == 2:
						if not key in self.y_limits:
							self.y_limits[key] = [dataDict[key],dataDict[key]]
						elif dataDict[key] < self.y_limits[key][0]:
							self.y_limits[key][0] = dataDict[key]
						elif dataDict[key] > self.y_limits[key][1]:
							self.y_limits[key][1] = dataDict[key]
				#_________________________________
				
			except SyntaxError:
				self.bytesData += dataEntry
				continue
		
		self.plotData()
		return *self.figure_list, *self.x_label_list, *self.y_label_list 


	def stopPlot(self):
		print(flush=True)
		print("______ NOTICE ________",flush=True)
		print("Remember to check ev3 terminal for any possible errors",flush=True)
		print("______________________",flush=True)
		print(flush=True)
		try:
			self.sock.close()
		except:
			pass
		# hide invalid subplots
		if self.nrows*self.ncols > 1:
			iterator = self.ax.flat
		else:
			iterator = [self.ax]
		for subplot in iterator:
			if not subplot in self.validSubplot:
				subplot.axis('off')
		#______________________

		# stop liveplot event
		try:
			self.livePlot.pause()
			self.livePlot.event_source.stop()
			self.livePlot._stop()
		except Exception as e:
			if self.Configs.Online:
				print(f"Error when trying to stop plot event: {e}",flush=True)
				

		# clear old lines before redrawing
		if self.Configs.plotMethod == 1:
			try:
				for lineInfo in self.lines.values():
					subplot = lineInfo["subplot"]
					for line in subplot.get_lines():
						line.remove()
			except Exception as e:
				print(f'stopping plot status: {e}',flush=True)
		
		# Remove labels and lines from our custom storage
		for line in self.figure_list:
			try:
				line.remove()
			except:
				pass
			
		for xlabel in self.x_label_list:
			xlabel.remove()

		for ylabel in self.y_label_list:
			ylabel.remove()
		#_______________________________________________

		line2DList = []

		for lineInfo in self.lines.values():
			subplot         = lineInfo["subplot"]    
			xListName       = lineInfo["xListName"]       
			yListName       = lineInfo["yListName"]
			
			xStart			= lineInfo["xStart"]
			xEnd 			= lineInfo["xEnd"]
			yStart 			= lineInfo["yStart"]
			yEnd 			= lineInfo["yEnd"]

			color           = lineInfo["color"] 
			linestyle       = lineInfo["linestyle"]
			linewidth       = lineInfo["linewidth"]
			marker          = lineInfo["marker"]
			yname			= lineInfo["yname"]

			xEnd = len(self.Data[xListName]) if xEnd is None else xEnd
			yEnd = len(self.Data[yListName]) if yEnd is None else yEnd

			line, = subplot.plot(
				self.Data[xListName][xStart:xEnd], 
				self.Data[yListName][yStart:yEnd], 
				color=color,
				linestyle=linestyle, 
				linewidth=linewidth, 
				marker=marker,
				label= str(yname),
			)

			line2DList.append(line)
			
			subplot.legend(loc='upper right')
			if self.Configs.plotMethod == 2:
				subplot.tick_params(axis='x', colors='black') 
				subplot.tick_params(axis='y', colors='black')
				subplot.get_xaxis().get_label().set_visible(True)

		# simulating interactive markings of points 
		if Interactivity:

			# Render updates on keypress
			def update_annotation(annotation,decimalsX,decimalsY):
				if annotation is None:
					return
				xval = f"{annotation.xy[0]:.{decimalsX}f}"
				yval = f"{annotation.xy[1]:.{decimalsY}f}"
				annotation.set_text("X: " + xval + "\nY: " + yval)
				annotation.get_bbox_patch().set(fc="white")


			# responsible for changing decimal places with keybinds
			def on_keypress(event):
				if event.key == '.':
					self.DecimalsY += 1
					update_annotation(self.CurrentAnnotation,self.DecimalsX,self.DecimalsY)
					event.canvas.draw()
					
				elif event.key == ',': 
					if self.DecimalsY > 0:
						self.DecimalsY -= 1
						update_annotation(self.CurrentAnnotation,self.DecimalsX,self.DecimalsY)
						event.canvas.draw()

				elif event.key == 'up':
					self.DecimalsX += 1
					update_annotation(self.CurrentAnnotation,self.DecimalsX,self.DecimalsY)
					event.canvas.draw()
				elif event.key == 'down':
					if self.DecimalsX > 0:
						self.DecimalsX -= 1
						update_annotation(self.CurrentAnnotation,self.DecimalsX,self.DecimalsY)
						event.canvas.draw()


			# event handling hover rendering (with search O(n) for closest point to mouse cursor)		
			def on_hover(sel):
				self.CurrentAnnotation = sel.annotation
				data = sel.artist.get_xydata()
				x = sel.target[0]
				y = sel.target[1]
				index = None

				# BINARY SEARCH O(log n) for closest point to mouse cursor
				xdata = data[:,0]
				index = np.searchsorted(xdata, x, side='left', sorter=None)
				
				if index is None:
					return
				
				x = data[-1][0] if index >= len(data) else data[index][0]
				y = data[-1][1] if index >= len(data) else data[index][1]


				# LINEAR SEARCH O(n) for closest point to mouse cursor
				# smallest = None
				# for i,v in enumerate(data):
				# 	if smallest is None or abs(v[0]-x) + abs(v[1]-y) < smallest:
				# 		smallest = abs(v[0]-x) + abs(v[1]-y)
				# 		index = i
				# if index is None:
				# 	return
				# x = data[index][0]
				# y = data[index][1]
				
				xval = f"{x:.{self.DecimalsX}f}"
				yval = f"{y:.{self.DecimalsY}f}"
				
				sel.annotation.arrow_patch.set(arrowstyle="-")
				sel.annotation.get_bbox_patch().set(fc="white")
				sel.annotation.set_text("X: " + xval + "\nY: " + yval)
				sel.annotation.xy = (x,y)

			# event handling data marking select
			def on_add(sel):
				data = sel.artist.get_xydata()
				x = sel.target[0]
				y = sel.target[1]
				index = None

				# BINARY SEARCH O(log n) for closest point to mouse cursor
				xdata = data[:,0]
				index = np.searchsorted(xdata, x, side='left', sorter=None)
				if index is None:
					return
				
				x = data[-1][0] if index >= len(data) else data[index][0]
				y = data[-1][1] if index >= len(data) else data[index][1]

				# LINEAR SEARCH O(n) for closest point to mouse cursor
				# smallest = None
				# for i,v in enumerate(data):
				# 	if smallest is None or abs(v[0]-x) + abs(v[1]-y) < smallest:
				# 		smallest = abs(v[0]-x) + abs(v[1]-y)
				# 		index = i
				# if index is None:
				# 	return
				# x = data[index][0]
				# y = data[index][1]
				
				xval = f"{x:.{self.DecimalsX}f}"
				yval = f"{y:.{self.DecimalsY}f}"

				if not hasattr(sel.annotation, "IndexMarker"):
					dot, = sel.artist.axes.plot(x,y,marker=".",color="k",  ) 
					setattr(sel.annotation, "IndexMarker", dot)

				sel.annotation.arrow_patch.set(arrowstyle="-")
				sel.annotation.get_bbox_patch().set(fc="white")
				sel.annotation.set_text("X: " + xval + "\nY: " + yval)
				sel.annotation.xy = (x,y)

			# Removing dotted marked point
			def on_remove(sel):
				if hasattr(sel.annotation, "IndexMarker"):
					sel.annotation.IndexMarker.remove()
							

			# responsible for creating the events and connecting them to the markers
			mplcursors.cursor(line2DList, hover=2).connect("add", on_hover)
			cursor = mplcursors.cursor(line2DList, multiple=True)
			cursor.connect("add", on_add)
			cursor.connect("remove", on_remove)
			self.fig.canvas.mpl_connect('key_press_event',on_keypress)

			# Previously used library
			#crosshairs(xlabel="x",ylabel="y",decimals=self.Configs.desimaler)

		if self.Configs.plotMethod == 2:
			self.plt.tight_layout()
		if self.Configs.Online and self.gui:
			self.window.withdraw()
		
		
		self.plt.pause(0) # blokkerer programmet så vi unngår at alt lukkes
	

		

	# plotte-metode 2: Veldig rask, men ulempen er at akseverdier ikke vises
	# har lagt til labels for å få et bedre inntrykk av x og y verdier 
	def Blitting(self, lineInfo):
		lineId          = lineInfo["lineId"]
		subplot         = lineInfo["subplot"]    
		xListName       = lineInfo["xListName"]       
		yListName       = lineInfo["yListName"]

		xStart			= lineInfo["xStart"]
		xEnd 			= lineInfo["xEnd"]
		yStart 			= lineInfo["yStart"]
		yEnd 			= lineInfo["yEnd"]

		color           = lineInfo["color"]
		linestyle       = lineInfo["linestyle"]
		linewidth       = lineInfo["linewidth"]
		marker          = lineInfo["marker"]
		xname			= lineInfo["xname"]
		yname			= lineInfo["yname"]
		ycolor			= lineInfo["ycolor"]

		
		if yListName in self.Data and len(self.Data[yListName]) == 0:
			return

		line = None
		y_label = None
		x_label = None

		if subplot in self.Mapping:
			

			if not self.Mapping[subplot]["x_label"]:
				x_label = subplot.text(
					x=0.5,
					y=0, 
					s="x-value", 
					transform=subplot.transAxes, 
					bbox={'facecolor':'w', 'alpha':1, 'pad':0, 'edgecolor':'none'},
					ha="center", 
					va = "bottom"
				)

				self.Mapping[subplot]["x_label"] = x_label
				self.x_label_list.append(x_label,)
			else:
				x_label = self.Mapping[subplot]["x_label"]

			if lineId in self.Mapping[subplot]:
				line = self.Mapping[subplot][lineId]["line"]
				y_label = self.Mapping[subplot][lineId]["y_label"]
			else:
				line, = subplot.plot([], [], color= color, linewidth = linewidth, linestyle=linestyle, marker = marker)

				index = lineInfo["label_index"]
				offset = 0.1
				y_label = subplot.text(
					x=0.05,y=1-index*offset, 
					s="x-value", 
					transform=subplot.transAxes, 
					bbox={'facecolor':'w', 'alpha':1, 'pad':0, 'edgecolor':'none'},
					ha="left",
					va = "top"
				)
				self.Mapping[subplot][lineId] = {"line": line, "y_label": y_label}
				self.figure_list.append(line)
				self.y_label_list.append(y_label,)

		if line:

			
			
			if yListName in self.Data and len(self.Data[yListName]) == 0:
				return
		
			xEnd = len(self.Data[xListName]) if xEnd is None else xEnd
			yEnd = len(self.Data[yListName]) if yEnd is None else yEnd

			XSlice = self.Data[xListName][xStart:xEnd]
			YSlice = self.Data[yListName][yStart:yEnd]

			if len(XSlice) != len(YSlice):
				dif = len(XSlice) - len(YSlice)
				print("_____FEIL VED PLOTTING!___",flush=True)
				print(f"Kan ikke plotte {xListName} mot {yListName} (ulike lengder): len({xListName})={len(XSlice)} != len({yListName})={len(YSlice)}",flush=True)
				if dif > 0:
					print(f"Forslag: Spesifiser x={xListName}[:{-dif}] og y={yListName} i plottingen i Main.py")
				elif dif < 0:
					print(f"Forslag: Spesifiser y={yListName}[:{-dif}] og x={xListName} i plottingen i Main.py")
				print("Traceback: Sjekk 'PLOT DATA' seksjon i Main.py",flush=True)
				print("__________________________",flush=True)
				print(flush=True)
				raise SystemExit()

		
			scale_X = 1.02
			max_x = self.Data[xListName][xEnd-1] or 0.1
			
			min_y = self.y_limits[yListName][0]
			max_y = self.y_limits[yListName][1]
			
			# limits min and max doesn't exist, then assign them
			if self.Mapping[subplot]["min"] is None:
				self.Mapping[subplot]["min"] = min_y

			if self.Mapping[subplot]["max"] is None:
				self.Mapping[subplot]["max"] = max_y
			
			if self.Mapping[subplot]["maxX"] is None:
				self.Mapping[subplot]["maxX"] = max_x
			#______________________________________

			

			# Handle axes limits for animation
			if min_y < self.Mapping[subplot]["min"]:
				self.Mapping[subplot]["min"] = min_y
			else:
				min_y = self.Mapping[subplot]["min"]

			if max_y > self.Mapping[subplot]["max"]:
				self.Mapping[subplot]["max"] = max_y
			else:
				max_y = self.Mapping[subplot]["max"]
			#__________________________________



			# Handle scaling for the text when blitting
			try:
				boundingBox = subplot.get_window_extent().transformed(self.fig.dpi_scale_trans.inverted())
				width = boundingBox.width * self.fig.dpi
				height = boundingBox.height * self.fig.dpi
				fontSize = min(16, 0.5*min(height,width)/len(self.Mapping[subplot]))
				x_label.set_fontsize(fontSize)
				y_label.set_fontsize(fontSize)
			except:
				pass
			#_________________________________________


			# Make sure there are some leeway for the line so it doesn't hit the figure box
			if (max_y - min_y) == 0:
				max_y += 1e-10
				min_y -= 1e-10
			dy = 0.1*(max_y-min_y)
			
			subplot.set_xlim(self.Data[xListName][0],scale_X*max_x) #set x limit of axis    
			subplot.set_ylim(min_y-dy,max_y+dy)
		
			line.set_data(
						XSlice, 
						YSlice
						)
			
			x_label.set_text(f"{xname}: {round(self.Data[xListName][xEnd-1],1)}") 
			y_label.set_color(ycolor)
			y_label.set_text(f"{yname}: {round(self.Data[yListName][yEnd-1],2)}")
			

	# Litt tregere plottemetode, men vi får vist frem akseverdier
	def Extended(self, lineInfo):
		
		subplot         = lineInfo["subplot"]    
		xListName       = lineInfo["xListName"]       
		yListName       = lineInfo["yListName"]

		xStart			= lineInfo["xStart"]
		xEnd 			= lineInfo["xEnd"]
		yStart 			= lineInfo["yStart"]
		yEnd 			= lineInfo["yEnd"]

		color           = lineInfo["color"]
		linestyle       = lineInfo["linestyle"]
		linewidth       = lineInfo["linewidth"]
		marker          = lineInfo["marker"]
		yname			= lineInfo["yname"]


		if yListName in self.Data and len(self.Data[yListName]) == 0:
			return


		xEnd = len(self.Data[xListName]) if xEnd is None else xEnd
		yEnd = len(self.Data[yListName]) if yEnd is None else yEnd


		XSlice = self.Data[xListName][xStart:xEnd]
		YSlice = self.Data[yListName][yStart:yEnd]

		if len(XSlice) != len(YSlice):
			dif = len(XSlice) - len(YSlice)
			print("_____FEIL VED PLOTTING!___",flush=True)
			print(f"Kan ikke plotte {xListName} mot {yListName} (ulike lengder): len({xListName})={len(XSlice)} != len({yListName})={len(YSlice)}",flush=True)
			if dif > 0:
				print(f"Forslag: Spesifiser x={xListName}[:{-dif}] og y={yListName} i plottingen i Main.py")
			elif dif < 0:
				print(f"Forslag: Spesifiser y={yListName}[:{-dif}] og x={xListName} i plottingen i Main.py")
			print("Traceback: Sjekk 'PLOT DATA' seksjon i Main.py",flush=True)
			print("__________________________",flush=True)
			print(flush=True)
			raise SystemExit()

		
		subplot.plot(
			XSlice, 
			YSlice, 
			color=color,
			linestyle=linestyle, 
			linewidth=linewidth, 
			marker=marker,
			label= f"{yname}: {round(self.Data[yListName][yEnd-1],2)}"
		)
		subplot.legend(loc='upper left', frameon=True)


	




	def startPlot(self):
		
		if self.Configs.Online and self.gui:
			# Sender signal for å stoppe robot og stopper plottet
			def signalRobot():
				self.sock.send(b'Stop')
				self.stopPlot()
				
			# bruker tkinter (standard library)
			self.window.title("EV3 Custom Stop")
			self.window.config(bg='#567')
			ws = self.window.winfo_screenwidth()
			hs = self.window.winfo_screenheight()
			w = 250
			h = 250
			x = ws - (w)
			y = hs/2 - h/2
			self.window.geometry('%dx%d+%d+%d' % (w, h, x, y))
			button = tk.Button(self.window, text ="Stop Program!",command=signalRobot)
			button.config(font=("Consolas",15))
			button.place(relx=.5, rely=.5, anchor="center", width = 200, height = 200)


		# hide invalid subplots
		if self.nrows*self.ncols > 1:
			iterator = self.ax.flat
		else:
			iterator = [self.ax]
		for subplot in iterator:
			if not subplot in self.validSubplot:
				subplot.axis('off')
		#______________________


		# liveplot eventen som er ansvarlig for plotting.
		
		#self.livePlot = self.FuncAnimation(self.fig, self.live, self.GenerateData, interval=1, blit=True)
		self.livePlot = self.FuncAnimation(self.fig, self.live, interval=1, blit=True)
		
		if self.Configs.Online and self.gui:
			self.plt.show(block=False)
			self.window.mainloop()

		self.plt.show()


	
	
if __name__ == "__main__":
	pass