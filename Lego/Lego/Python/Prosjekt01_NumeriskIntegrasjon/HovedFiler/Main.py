# coding=utf-8

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# P01_NumeriskIntegrasjon
#
# Hensikten med programmet er å utføre numerisk integrasjon
#
# Følgende sensorer brukes:
# - Lyssensor
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
Configs.EV3_IP = "169.254.44.232"	# Avles IP-adressen på EV3-skjermen
Configs.Online = True	# Online = True  --> programmet kjører på robot  
                        # Online = False --> programmet kjører på datamaskin
Configs.livePlot = True 	# livePlot = True  --> Live plot, typisk stor Ts
                            # livePlot = False --> Ingen plot, liten Ts
Configs.avgTs = 0.005	# livePlot = False --> spesifiser ønsket Ts
                        # Lav avgTs -> høy samplingsfrekvens og mye data.
                        # --> Du må vente veldig lenge for å lagre filen.
Configs.filename = "P01_NumeriskIntegrasjon_1.txt"	
                        # Målinger/beregninger i Online lagres til denne 
                        # .txt-filen. Upload til Data-mappen.
Configs.filenameOffline = "Offline_P01_NumeriskIntegrasjon_1.txt"	
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
Configs.ConnectJoystickToPC = True # True  --> joystick direkte på datamaskin
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
data.u = []		   	      	# beregning av u
data.y = []			  	    # beregning av y
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

    # Tilordne målinger til variable
    data.u.append(data.Lys[-1] - init.LysInit)  
    
    # Initialverdier og beregninger 
    if k == 0:
        # Initialverdier
        data.Ts.append(0.01)  	# nominell verdi
    
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

# Når programmet slutter, spesifiser hvordan du vil at motoren(e) skal stoppe.
# Det er 3 forskjellige måter å stoppe motorene på:
# - stop() ruller videre og bremser ikke.
# - brake() ruller videre, men bruker strømmen generert av rotasjonen til brems
# - hold() bråstopper umiddelbart og holder posisjonen
def stopMotors(robot):
    return # fjern denne om motor(er) brukes
#______________________________________________________________________________




# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#             6)  PLOT DATA
#
# Dersom både nrows og ncols = 1, så benyttes bare "ax".
# Dersom enten nrows = 1 eller ncols = 1, så benyttes "ax[0]", "ax[1]", osv.
# Dersom både nrows > 1 og ncols > 1, så benyttes "ax[0,0]", "ax[1,0]", osv
def lagPlot(plt):
    nrows = 2
    ncols = 1
    sharex = True
 
    plt.create(nrows,ncols,sharex)
    ax,fig = plt.ax, plt.fig

    # Legger inn titler og aksenavn (valgfritt) for hvert subplot,  
    # sammen med argumenter til plt.plot() funksjonen. 
    # Ved flere subplot over hverandre så er det lurt å legge 
    # informasjon om x-label på de nederste subplotene (sharex = True)

    fig.suptitle('Numerisk integrasjon')

    # flow
    ax[0].set_title('fylling drikking u(t)')  
    ax[0].set_ylabel("[cl/s]")
    plt.plot(
        subplot = ax[0],  	# Definer hvilken delfigur som skal plottes
        x = "Tid", 			# navn på x-verdien (fra data-objektet)
        y = "u",			# navn på y-verdien (fra data-objektet)

        # VALGFRITT
        color = "b",		# fargen på kurven som plottes (default: blå)
        linestyle = "solid",  # "solid" / "dashed" / "dotted"
        linewidth = 1,		# tykkelse på linjen
        marker = "",       	# legg til markør på hvert punkt
    )

    # volum
    ax[1].set_title('volum y(t)')  
    ax[1].set_ylabel("[cl]")
    ax[1].set_xlabel("Tid [sek]")
    plt.plot(
        subplot = ax[1],    
        x = "Tid",       
        y = "y",
    )
#____________________________________________________________________________
