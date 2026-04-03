# coding=utf-8

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# P0X_BeskrivendeTekst
#
# Hensikten med programmet er å ................
#
# Følgende sensorer brukes:
# - Lyssensor
# - ...
# - ...
#
# Følgende motorer brukes:
# - ...
# - ...
#
# OBS: Vær klar over at dersom du kobler til 
# sensorer/motorer som du ikke bruker, så øker tidsskrittet
#____________________________________________________________________________


# +++++++++++++++++++++++++++++ IKKE ENDRE ++++++++++++++++++++++++++++++++++++++++
# Setter opp midlertidige søkestier og importerer pakker (sjekker om vi er på ev3)
import os
import sys
if sys.implementation.name.lower().find("micropython") != -1:
    import moduler.config as config
    from moduler.EV3AndJoystick import *
else:
    # Making sure that the project directory is in the path
    file_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(file_dir)
    sys.path.append(project_dir)
from HovedFiler.MineFunksjoner import *
from moduler.funksjoner import *
data = Bunch()              # dataobjektet ditt (punktum notasjon)
Configs = Bunch()           # konfiguarsjonene dine
init = Bunch()              # initalverdier (brukes i addmeasurement og mathcalculations)
timer = clock()             # timerobjekt med tic toc funksjoner
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                            1) KONFIGURASJON
#
Configs.EV3_IP = "169.254.7.251"	# Avles IP-adressen på EV3-skjermen
Configs.Online = True	# Online = True  --> programmet kjører på robot  
						# Online = False --> programmet kjører på datamaskin
Configs.livePlot = True 	# livePlot = True  --> Live plot, typisk stor Ts
							# livePlot = False --> Ingen plot, liten Ts
Configs.avgTs = 0.005	# livePlot = False --> spesifiser ønsket Ts
						# Lav avgTs -> høy samplingsfrekvens og mye data.
						# --> Du må vente veldig lenge for å lagre filen.
Configs.filename = "P0X_BeskrivendeTekst_Y.txt"	
						# Målinger/beregninger i Online lagres til denne 
						# .txt-filen. Upload til Data-mappen.
Configs.filenameOffline = "Offline_P0X_BeskrivendeTekst_Y.txt"	
						# I Offline brukes den opplastede datafilen 
						# og alt lagres til denne .txt-filen.
Configs.plotMethod = 1	# verdier: 1 eller 2, hvor hver plottemetode 
						# har sine fordeler og ulemper.
						# Bruker du mac, velges backend "macosx" i neste linje
						# automatisk, og da må du bruke plotMethod = 1
Configs.plotBackend = ""	# Ønsker du å bruke en spesifikk backend, last ned
							# og skriv her. Eks.: qt5agg, qtagg, tkagg, macosx. 
Configs.limitMeasurements = False	# Mulighet å kjøre programmet lenge 
									# uten at roboten kræsjer pga minnet
Configs.ConnectJoystickToPC = False # True  --> joystick direkte på datamaskin
									# False	--> koble joystick på EV3-robot
									# False	--> også når joystick ikke brukes
#____________________________________________________________________________



# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                           2) VELG MÅLINGER OG DEFINER VARIABLE
#
# Dataobjektet "data" inneholder både målinger og beregninger.
# OBS! Bruk kun punktum notasjon for dette objektet. 
# data.variabelnavn = []. IKKE d["variabelnavn"] = []

# målinger
data.Tid = []            	# måling av tidspunkt
data.Lys = []            	# måling av reflektert lys fra ColorSensor

# beregninger
data.Ts = []			  	# beregning av tidsskritt

"""
# Utvalg av målinger
data.LysDirekte = []         # måling av lys direkte inn fra ColorSensor
data.Bryter = []             # registrering av trykkbryter fra TouchSensor
data.Avstand = []            # måling av avstand fra UltrasonicSensor
data.GyroAngle = []          # måling av gyrovinkel fra GyroSensor
data.GyroRate = []           # måling av gyrovinkelfart fra GyroSensor

data.VinkelPosMotorA = []    # måling av vinkelposisjon motor A
data.HastighetMotorA = []    # måling av vinkelhastighet motor A
data.VinkelPosMotorB = []    # måling av vinkelposisjon motor B 
data.HastighetMotorB = []    # måling av vinkelhastighet motor B
data.VinkelPosMotorC = []    # måling av vinkelposisjon motor C
data.HastighetMotorC = []    # måling av vinkelhastighet motor C
data.VinkelPosMotorD = []    # måling av vinkelposisjon motor D
data.HastighetMotorD = []    # måling av vinkelhastighet motor D

data.joyForward = []         # måling av foroverbevegelse styrestikke
data.joySide = []            # måling av sidebevegelse styrestikke
data.joyTwist = []           # måling av vribevegelse styrestikke
data.joyPotMeter = []        # måling av potensionmeter styrestikke
data.joyPOVForward = []      # måling av foroverbevegelse toppledd
data.joyPOVSide = []         # måling av sidebevegelse toppledd

data.joy1 = []               # måling av knapp 1 (skyteknapp)
data.joy2 = []               # måling av knapp 2 (ved tommel)
data.joy3 = []               # måling av knapp 3 
data.joy4 = []               # måling av knapp 4 
data.joy5 = []               # måling av knapp 5 
data.joy6 = []               # måling av knapp 6 
data.joy7 = []               # måling av knapp 7 
data.joy8 = []               # måling av knapp 8 
data.joy9 = []               # måling av knapp 9 
data.joy10 = []              # måling av knapp 10 
data.joy11 = []              # måling av knapp 11 
data.joy12 = []              # måling av knapp 12

# Utvalg av beregninger
data.PowerA = []         # berenging av motorpådrag A
data.PowerB = []         # berenging av motorpådrag B
data.PowerC = []         # berenging av motorpådrag C
data.PowerD = []         # berenging av motorpådrag D
"""
#____________________________________________________________________________________________



# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                               3) LAGRE MÅLINGER
#
# Dersom du har flere sensorer av samme type, må du spesifisere portnummeret.
# Eks: Du har 2 lyssensorer i port 1 og 4, og
# for å hente disse kaller du "robot.ColorSensor1" og "robot.ColorSensor4"
#
# Husk at målingene her kommer fra avlesning av sensorene (bortsett fra Tid).
#
# data: "data-objektet" der du får tak i variablene dine med punktum notasjon
# robot: inneholder sensorer, motorer og diverse
# init: initalverdier som settes i addMeasurements() ved k==0 og som
#       kan også brukes i MathCalculations()
# k: indeks som starter på 0 og øker [0,--> uendelig]
# config: inneholder joystick målinger


def addMeasurements(data,robot,init,k):
	if k==0:
		# Definer initielle lmålinger inn i init variabelen.
        # Initialverdiene kan brukes i MathCalculations()
		init.LysInit = robot.ColorSensor.reflection() 	# lagrer første lysmåling

		data.Tid.append(timer.tic())		# starter "stoppeklokken" på 0
	else:

		# lagrer "målinger" av tid
		data.Tid.append(timer.toc())
	
	# lagrer målinger av lys
	data.Lys.append(robot.ColorSensor.reflection())

	"""
	data.LysDirekte.append(robot.ColorSensor.ambient())
	data.Bryter.append(robot.TouchSensor.pressed())
	data.Avstand.append(robot.UltrasonicSensor.distance())
	data.GyroAngle.append(robot.GyroSensor.angle())
	data.GyroRate.append(robot.GyroSensor.speed())

	data.VinkelPosMotorA.append(robot.motorA.angle())
	data.HastighetMotorA.append(robot.motorA.speed())
	data.VinkelPosMotorB.append(robot.motorB.angle())
	data.HastighetMotorB.append(robot.motorB.speed())
	data.VinkelPosMotorC.append(robot.motorC.angle())
	data.HastighetMotorC.append(robot.motorC.speed())
	data.VinkelPosMotorD.append(robot.motorD.angle())
	data.HastighetMotorD.append(robot.motorD.speed())

	data.joyForward.append(config.joyForwardInstance)
	data.joySide.append(config.joySideInstance)
	data.joyTwist.append(config.joyTwistInstance)
	data.joyPotMeter.append(config.joyPotMeterInstance)
	data.joyPOVForward.append(config.joyPOVForwardInstance)
	data.joyPOVSide.append(config.joyPOVSideInstance)

	data.joy1.append(config.joy1Instance)
	data.joy2.append(config.joy2Instance)
	data.joy3.append(config.joy3Instance)
	data.joy4.append(config.joy4Instance)
	data.joy5.append(config.joy5Instance)
	data.joy6.append(config.joy6Instance)
	data.joy7.append(config.joy7Instance)
	data.joy8.append(config.joy8Instance)
	data.joy9.append(config.joy9Instance)
	data.joy10.append(config.joy10Instance)
	data.joy11.append(config.joy11Instance)
	data.joy12.append(config.joy12Instance)
	"""
#______________________________________________________

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#             4) UTFØR BEREGNINGER (MathCalculations)
#
# Bruker målinger til å beregne nye variable som
# på forhånd må være definert i seksjon 2).
# Funksjonen brukes både i online og offline.
#
def MathCalculations(data,k,init):
	# return  	# Bruk denne dersom ingen beregninger gjøres,
				# som for eksempel ved innhentning av kun data for 
				# bruk i offline.

	# Parametre
	a = 0.7

    # Tilordne målinger til variable
    
    # Initialverdier og beregninger 
	if k == 0:
		# Initialverdier
		data.Ts.append(0.005)  	# nominell verdi
	
	else:
        # Beregninger av Ts og variable som avhenger av initialverdi
		data.Ts.append(data.Tid[-1]-data.Tid[-2])

    # Andre beregninger uavhengig av initialverdi

    # Pådragsberegninger
#_____________________________________________________________________________



# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#             5) MOTORFUNKSJONER
#
# Hvis motor(er) brukes i prosjektet så sendes
# beregnet pådrag til motor(ene).
# Motorene oppdateres for hver iterasjon etter mathcalculations
#
def setMotorPower(data,robot):
	return # fjern denne om motor(er) brukes
	robot.motorA.dc(data.PowerA[-1])
	robot.motorB.dc(data.PowerB[-1])
	robot.motorC.dc(data.PowerC[-1])
	robot.motorD.dc(data.PowerD[-1])

# Når programmet slutter, spesifiser hvordan du vil at motoren(e) skal stoppe.
# Det er 3 forskjellige måter å stoppe motorene på:
# - stop() ruller videre og bremser ikke.
# - brake() ruller videre, men bruker strømmen generert av rotasjonen til brems
# - hold() bråstopper umiddelbart og holder posisjonen
def stopMotors(robot):
	return # fjern denne om motor(er) brukes
	robot.motorA.stop()
	robot.motorB.brake()
	robot.motorC.hold()
	robot.motorD.hold()
#______________________________________________________________________________




# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#             6)  PLOT DATA
#
# Dersom både nrows og ncols = 1, så benyttes bare "ax".
# Dersom enten nrows = 1 eller ncols = 1, så benyttes "ax[0]", "ax[1]", osv.
# Dersom både nrows > 1 og ncols > 1, så benyttes "ax[0,0]", "ax[1,0]", osv
def lagPlot(plt):
	nrows = 3
	ncols = 1
	sharex = True
	plt.create(nrows,ncols,sharex)
	ax,fig = plt.ax, plt.fig

	# Legger inn titler og aksenavn (valgfritt) for hvert subplot,  
    # sammen med argumenter til plt.plot() funksjonen. 
    # Ved flere subplot over hverandre så er det lurt å legge 
    # informasjon om x-label på de nederste subplotene (sharex = True)

	fig.suptitle('Her kan du bruke en tittel for hele figuren')

	# plotting av lys
	ax[0].set_title('Reflektert lys')  
	ax[0].set_xlabel("Tid [sek]")	 
	ax[0].set_ylabel("Lys")
	plt.plot(
		subplot = ax[0],  	# Definer hvilken delfigur som skal plottes
		x = "Tid[-1:]", 	# navn på x-verdien (fra data-objektet)
		y = "Lys[-1:]",		# navn på y-verdien (fra data-objektet)

		# VALGFRITT
		color = "b",		# fargen på kurven som plottes (default: blå)
		linestyle = "solid",  # "solid" / "dashed" / "dotted"
		linewidth = 1,		# tykkelse på linjen
		marker = "",       	# legg til markør på hvert punkt
	)

	# plotting av lys (minimumsversjon)
	ax[1].set_title('Lys')  
	ax[1].set_xlabel("Tid [sek]")
	ax[1].set_ylabel("Lys")
	plt.plot(
		subplot = ax[1],    
		x = "Tid",	# navn på x-verdien (fra data-objektet)  
		y = "Lys",	# navn på y-verdien (fra data-objektet)  
	)

	# plotting av Ts (benytter utvalg av listene)
	ax[2].set_title('Beregning av Ts')  
	ax[2].set_xlabel("Tid [sek]")
	ax[2].set_ylabel("tidsskritt")
	plt.plot(
		subplot = ax[2],    
		x = "Tid",       
		y = "Ts",
		color = "b",
		linestyle = "dashed",
	)
#____________________________________________________________________________
