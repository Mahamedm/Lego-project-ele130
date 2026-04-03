# coding=utf-8

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# P04_PID_Regulering
#
# Hensikten med programmet er å demonstrere hvordan P, I, og D-leddene
# fungerer i en PID-regulator
#
# Følgende motorer brukes:
# - motor A
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
Configs.EV3_IP = "169.254.137.60"	# Avles IP-adressen på EV3-skjermen
Configs.Online = True	# Online = True  --> programmet kjører på robot  
                        # Online = False --> programmet kjører på datamaskin
Configs.livePlot = True     # livePlot = True  --> Live plot, typisk stor Ts
                            # livePlot = False --> Ingen plot, liten Ts
Configs.avgTs = 0.005	# livePlot = False --> spesifiser ønsket Ts
                        # Lav avgTs -> høy samplingsfrekvens og mye data.
                        # --> Du må vente veldig lenge for å lagre filen.
Configs.filename = "P04_TidMotorAJoy_1.txt"
                        # Målinger/beregninger i Online lagres til denne 
                        # .txt-filen. Upload til Data-mappen.
Configs.filenameOffline = "Offline_P04_TidMotorAJoy_1.txt"
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
Configs.ConnectJoystickToPC = False # True 	--> joystick direkte på datamaskin
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
data.VinkelPosMotorA = []    # måling av vinkelposisjon motor A
data.joyPotMeter = [] 

# beregninger
data.Ts = []			  	# beregning av tidsskritt
data.e = []		   	      	# beregning av e
data.e_f = []		     	# beregning av e
data.y = []			  	    
data.r = []			  	    
data.x1 = []			  	    
data.x2 = []			  	    
data.u_A = []			  	    
data.u_min = []			  	    
data.u_max = []			  	    
data.P = []			  	    
data.I = []			  	    
data.D = []			  	
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
        data.Tid.append(timer.tic())				# starter "stoppeklokken" på 0
    else:

        # lagrer "målinger" av tid
        data.Tid.append(timer.toc())
    
    # lagrer målinger
    data.VinkelPosMotorA.append(robot.motorA.angle())
    data.joyPotMeter.append(config.joyPotMeterInstance)
    
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
    u0 = 0.0 
    Kp = 0.0
    Ki = 0.0 
    Kd = 0.0 
    alfa = 1.0 

    # Initialverdier og beregninger
    if k == 0:
        # Initialverdier
        data.Ts.append(0.005)  # nominell verdi

        # Motorens tilstander
        data.x1.append(data.VinkelPosMotorA[0])
        data.x2.append(0.0)
    
        # Reguleringsavvik
        data.y.append(data.x2[0])
        data.r.append(10*data.joyPotMeter[0])
        data.e.append(data.r[0] - data.y[0])
        data.e_f.append(data.e[0])
        
        # Initialverdi PID-regulatorens deler
        data.P.append(0.0)
        data.I.append(0.0)
        data.D.append(0.0)

    else:
        # Beregninger av Ts og variable som avhenger av initialverdi
        data.Ts.append(data.Tid[-1]-data.Tid[-2])

        # Motorens tilstander
        data.x1.append(data.VinkelPosMotorA[-1])
        data.x2.append((data.x1[-1]-data.x1[-2])/data.Ts[-1])

        # Beregning av reguleringsavvik
        data.y.append(data.x2[-1])
        data.r.append(10*data.joyPotMeter[-1])
        data.e.append(data.r[-1] - data.y[-1])
        
        # Lag kode for bidragene P, I og D
        data.P.append(0.0)
        data.I.append(0.0)
        data.e_f.append(data.e[-1])
        data.D.append(0.0)
        
    # Integratorbegrensing. Bruk disse grenseverdiene til å lage anti-windup.
    # Du kan også inkludere I_min og I_max i plottet av I
    I_max = 100
    data.u_max.append(I_max)
    I_min = -100
    data.u_min.append(I_min)
    
    # if ...
            
    data.u_A.append(u0 + data.P[-1] + data.I[-1] + data.D[-1]);       
    
#__________________________________________________



# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#             5) MOTORFUNKSJONER
#
# Hvis motor(er) brukes i prosjektet så sendes
# beregnet pådrag til motor(ene).
# Motorene oppdateres for hver iterasjon etter mathcalculations
#
def setMotorPower(data,robot):
    # fjern denne om motor(er) brukes
    robot.motorA.dc(data.u_A[-1])

# Når programmet slutter, spesifiser hvordan du vil at motoren(e) skal stoppe.
# Det er 3 forskjellige måter å stoppe motorene på:
# - stop() ruller videre og bremser ikke.
# - brake() ruller videre, men bruker strømmen generert av rotasjonen til å bremse.
# - hold() bråstopper umiddelbart og holder posisjonen
def stopMotors(robot):
    # fjern denne om motor(er) brukes
    robot.motorA.stop()
#__________________________________________________



# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#             6)  PLOT DATA
#
# Dersom både nrows og ncols = 1, så benyttes bare "ax".
# Dersom enten nrows = 1 eller ncols = 1, så benyttes "ax[0]", "ax[1]", osv.
# Dersom både nrows > 1 og ncols > 1, så benyttes "ax[0,0]", "ax[1,0]", osv
def lagPlot(plt):
    nrows = 3
    ncols = 2
    sharex = False

    plt.create(nrows,ncols,sharex)
    ax,fig = plt.ax, plt.fig

    fig.suptitle('Styring av motor')

    ax[0,0].set_title('Vinkelhastighet y(t) og referanse r(t)')  
    plt.plot(
		subplot = ax[0,0],  # Definer hvilken subplot som skal plottes
		x = "Tid", 	# navn på x-verdien som plottes (fra data-objektet)     
		y = "y",	# navn på y-verdien som plottes (fra data-objektet)
	)
    plt.plot(
		subplot = ax[0,0],  # Definer hvilken subplot som skal plottes
		x = "Tid", 	# navn på x-verdien som plottes (fra data-objektet)     
		y = "r",	# navn på y-verdien som plottes (fra data-objektet)
        color = "red",	
    )

    ax[1,0].set_title('Reguleringsavvik e(t)')  
    plt.plot(
		subplot = ax[1,0],    
		x = "Tid",	# navn på x-verdien som plottes (fra data-objektet)  
		y = "e",	# navn på y-verdien som plottes (fra data-objektet)  
	)
    plt.plot(
		subplot = ax[1,0],    
		x = "Tid",	# navn på x-verdien som plottes (fra data-objektet)  
		y = "e_f",	# navn på y-verdien som plottes (fra data-objektet)  
        color = "red",	
	)

    ax[2,0].set_title('Pådrag u(t)')  
    ax[2,0].set_xlabel("Tid [sek]")
    plt.plot(
		subplot = ax[2,0],    
		x = "Tid",	# navn på x-verdien som plottes (fra data-objektet)  
		y = "u_A",	# navn på y-verdien som plottes (fra data-objektet)  
	)

    ax[0,1].set_title('P-del')  
    plt.plot(
		subplot = ax[0,1],    
		x = "Tid",	# navn på x-verdien som plottes (fra data-objektet)  
		y = "P",	# navn på y-verdien som plottes (fra data-objektet)  
	)

    ax[1,1].set_title('I-del')  
    plt.plot(
		subplot = ax[1,1],    
		x = "Tid",	# navn på x-verdien som plottes (fra data-objektet)  
		y = "I",	# navn på y-verdien som plottes (fra data-objektet)  
	)

    ax[2,1].set_title('D-del')  
    ax[2,1].set_xlabel("Tid [sek]")
    plt.plot(
		subplot = ax[2,1],    
		x = "Tid",	# navn på x-verdien som plottes (fra data-objektet)  
		y = "D",	# navn på y-verdien som plottes (fra data-objektet)  
	)



#_____________________________________________________________________________________
