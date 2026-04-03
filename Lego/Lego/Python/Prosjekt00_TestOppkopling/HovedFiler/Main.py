# coding=utf-8

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# P00_TestOppkopling
#
# Hensikten med programmet er å teste at oppkoplingen virker.
#
# Følgende sensorer brukes:
# - Lyssensor
#
# Følgende motorer brukes:
# - Motor A
#
# OBS: Vær klar over at dersom du kobler til
# sensorer/motorer som du ikke bruker, så øker tidsskrittet
# ____________________________________________________________________________


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
Configs.EV3_IP = "169.254.250.52"	# Avles IP-adressen på EV3-skjermen
Configs.Online = False	# Online = True  --> programmet kjører på robot  
                        # Online = False --> programmet kjører på datamaskin
Configs.livePlot = True     # livePlot = True  --> Live plot, typisk stor Ts
                            # livePlot = False --> Ingen plot, liten Ts
Configs.avgTs = 0.005	# livePlot = False --> spesifiser ønsket Ts
                        # Lav avgTs -> høy samplingsfrekvens og mye data.
                        # --> Du må vente veldig lenge for å lagre filen.
Configs.filename = "P00_matplotlib.txt"
                        # Målinger/beregninger i Online lagres til denne 
                        # .txt-filen. Upload til Data-mappen.
Configs.filenameOffline = "Offline_P00_matplotlib.txt"
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
Configs.ConnectJoystickToPC = True # True 	--> joystick direkte på datamaskin
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
data.joyForward = []  		# måling av joystickbevegelse fremover

# beregninger
data.u = []           	# variabel som tilsvarer lysmåling
data.Ts = []			# beregning av tidsskritt
data.y1 = []			# beregning av dummyverdi y1
data.y2 = []			# beregning av dummyverdi y2
data.PowerA = []		# beregning av pådrag til motor A
#____________________________________________________________________________________________



# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                               3) LAGRE MÅLINGER
#
# Dersom du har flere sensorer av én type, må du spesifisere portnummeret.
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
        # Definer initialmålinger inn i init variabelen.
        # Disse kan også bli brukt i MathCalculations()
        init.nullflow = robot.ColorSensor.reflection() 	# lagrer første lysmåling
        data.Tid.append(timer.tic())				# starter "stoppeklokken" på 0
    else:

        # lagrer "målinger" av tid
        data.Tid.append(timer.toc())
    
    # lagrer målinger
    data.Lys.append(robot.ColorSensor.reflection())
    data.joyForward.append(config.joyForwardInstance)

#______________________________________________________




# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
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
    a = 0.003
    b = 5

    # Tilordne målinger til variable
    data.u.append(data.Lys[k] - init.nullflow)

    # Initialverdier og beregninger
    if k == 0:
        data.Ts.append(0.005)   # nominell verdi
        data.y1.append(0)
        data.y2.append(0)
    else:
        # Beregner tidsskrittet
        data.Ts.append(data.Tid[-1]-data.Tid[-2])

        # Kaller på 2 forskjellige funksjoner for å utføre
        #     y(k) = y(k-1) + a*u(k) + a*u(k-1)

        # Kaller på UsingElements hvor 
        # det demonstreres at parameter*liste ikke fungerer.         
        data.y1.append(UsingElements(data.y1[-1], data.u[-2:], a))     # fungerer
        # data.y1.append(UsingElements(data.y1[-1], a*data.u[-2:], 1)) # fungerer IKKE
        
        # Deretter kalles UsingLists, men denne gir ikke like mye
        # strukturell informasjon om hva som lagres hvor.
        UsingLists(data.y2, data.u, a)

    # Andre beregninger uavhengig av initialverdi

    # Pådragsberegninger
    data.PowerA.append(data.joyForward[-1] + b*data.y1[-1])

    
#__________________________________________________



# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#             5) MOTORFUNKSJONER
#
# Hvis motor(er) brukes i prosjektet så sendes
# beregnet pådrag til motor(ene).
# Motorene oppdateres for hver iterasjon etter mathcalculations
#
def setMotorPower(data,robot):
    # return # fjern denne om motor(er) brukes
    robot.motorA.dc(data.PowerA[-1])

# Når programmet slutter, spesifiser hvordan du vil at motoren(e) skal stoppe.
# Det er 3 forskjellige måter å stoppe motorene på:
# - stop() ruller videre og bremser ikke.
# - brake() ruller videre, men bruker strømmen generert av rotasjonen til å bremse.
# - hold() bråstopper umiddelbart og holder posisjonen
def stopMotors(robot):
    # return # fjern denne om motor(er) brukes
    robot.motorA.stop()
#__________________________________________________



# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#             6)  PLOT DATA
#
# Dersom både nrows og ncols = 1, så benyttes bare "ax".
# Dersom enten nrows = 1 eller ncols = 1, så benyttes "ax[0]", "ax[1]", osv.
# Dersom både nrows > 1 og ncols > 1, så benyttes "ax[0,0]", "ax[1,0]", osv
def lagPlot(plt):
    nrows = 2
    ncols = 2
    sharex = True

    plt.create(nrows,ncols,sharex)
    ax,fig = plt.ax, plt.fig

    # Legger inn titler og aksenavn (valgfritt) for hvert subplot,  
    # sammen med argumenter til plt.plot() funksjonen. 
    # Ved flere subplot over hverandre så er det lurt å legge 
    # informasjon om x-label på de nederste subplotene (sharex = True)


    fig.suptitle('Tøyseberegninger')

    # plotting av lys
    ax[0,0].set_title('Reflektert lys')  

    plt.plot(
        # OBLIGATORISK
        subplot = ax[0,0],  	# Definer hvilken (delfigurer) som skal plottes
        x = "Tid", 				# navn på x-verdien
        y = "Lys",				# navn på y-verdien

        # VALGFRITT
        color = "r",			# fargen på kurven som plottes (default: blå)
        linestyle = "dashed",  	# "solid" / "dashed" / "dotted"
        linewidth = 2,			# tykkelse på linjen
        marker = ".",      		# legg til markør på hvert punkt
    )
    
    # Verdiene av u og y1, y2 i samme figur.
    ax[0, 1].set_title('Signalene u(k), y1(k) og y2(k)')
    plt.plot(
        subplot = ax[0, 1],
        x = "Tid", 
        y = "u",
        color = "g",
    )
    plt.plot(
        subplot = ax[0, 1],
        x = "Tid", 
        y = "y1",
        color = "r",
        linestyle="dotted", 
    )
    plt.plot(
        subplot = ax[0, 1],
        x = "Tid", 
        y = "y2",
        color = "b",
        linestyle="dashed", 
    )

    # Power A
    # Minimal bruk av plot-metoden, default farge er blå
    ax[1, 0].set_title('Beregning av motorpådrag')
    # legger denne info på nederste delfigur
    ax[1, 0].set_xlabel("Tid [sek]")
    ax[1, 0].set_ylabel("[%]")
    plt.plot(
        subplot = ax[1, 0],
        x = "Tid",
        y = "PowerA",
    )

    # Tidsskrittet Ts
    ax[1, 1].set_title('Tidsskritt T_s')
    # legger denne info på nederste delfigur
    ax[1, 1].set_xlabel("Tid [sek]")
    ax[1, 1].set_ylabel("[s]")
    plt.plot(
        subplot = ax[1, 1],
        x = "Tid",
        y = "Ts",
        color="b",
        linestyle="dashed",
    )

#_____________________________________________________________________________________
