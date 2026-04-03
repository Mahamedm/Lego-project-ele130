%++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
% P0X_.....
%
% Hensikten med programmet er å ....
% Følgende sensorer brukes:
% - Lyssensor
% - ...
% - ...
%
% Følgende motorer brukes:
% - motor A
% - ...
% - ...
%
%--------------------------------------------------------------------------


%++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
%         EXPERIMENT SETUP, FILENAME AND FIGURE

clear; close all   % Alltid lurt å rydde workspace opp først
online = true;     % Online mot EV3 eller mot lagrede data?
plotting = false;  % Skal det plottes mens forsøket kjøres 
filename = 'P0X_MeasBeskrivendeTekst_Y.mat';  % Data ved offline

if online
    % Initialiser styrestikke, sensorer og motorer. 
    % Dersom du bruker 2 like sensorer, så må du 
    % initialisere med portnummer som argument som:
    % mySonicSensor_1 = sonicSensor(mylego,3);
    % mySonicSensor_2 = sonicSensor(mylego,4);
    
    % LEGO EV3 og styrestikke
    mylego = legoev3('USB');
    joystick = vrjoystick(1);
    [JoyAxes,JoyButtons] = HentJoystickVerdier(joystick);

    % Hvilke sensorer er koplet til?
    myColorSensor = colorSensor(mylego);    
    myTouchSensor = touchSensor(mylego);
    mySonicSensor = sonicSensor(mylego);
    myGyroSensor  = gyroSensor(mylego);
    resetRotationAngle(myGyroSensor);

    % Hvilke motorer er koplet til?
    motorA = motor(mylego,'A');
    motorA.resetRotation;
    motorB = motor(mylego,'B');
    motorB.resetRotation;
    motorC = motor(mylego,'C');
    motorC.resetRotation;
    motorD = motor(mylego,'D');
    motorD.resetRotation;
else
    % Dersom online=false lastes datafil.
    load(filename)
end

fig1=figure;
%set(gcf,'units','normalized','outerposition',[0.1 0.3 0.6 0.6])
drawnow

% setter skyteknapp til 0, og initialiserer tellevariabel k
JoyMainSwitch=0;
k=0;
%----------------------------------------------------------------------



while ~JoyMainSwitch
    %+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    %                       GET TIME AND MEASUREMENT
    % Få tid og målinger fra sensorer, motorer og joystick

    k=k+1;               % oppdater tellevariabel

    if online
        if k==1 
            % Spiller av lyd slik at du vet at innsamlingen har startet
            playTone(mylego,500,0.1)   % 500Hz i 0.1 sekund
            tic          % Starter stoppeklokke
            t(1) = 0;
        else
            t(k) = toc;  % Henter ut medgått tid
        end

        % Sensorer, bruk ikke Lys(k) og LysDirekte(k) samtidig
        Lys(k) = double(readLightIntensity(myColorSensor,'reflected'));
        LysDirekte(k) = double(readLightIntensity(myColorSensor));
        Bryter(k)  = double(readTouch(myTouchSensor));
        Avstand(k) = double(readDistance(mySonicSensor));        
       
        % Bruk ikke GyroAngle(k) og GyroRate(k) samtidig
        GyroAngle(k) = double(readRotationAngle(myGyroSensor));
        GyroRate(k)  = double(readRotationRate(myGyroSensor));
 
        % Hent målinger fra motorene
        VinkelPosMotorA(k) = double(motorA.readRotation);
        VinkelPosMotorB(k) = double(motorB.readRotation);
        VinkelPosMotorC(k) = double(motorC.readRotation);
        VinkelPosMotorD(k) = double(motorC.readRotation);

        % Data fra styrestikke. Utvid selv med andre knapper og akser.
        % Bruk filen joytest.m til å finne koden for knappene og aksene.
        [JoyAxes,JoyButtons] = HentJoystickVerdier(joystick);
        JoyMainSwitch = JoyButtons(1);
        JoyForover(k) = JoyAxes(2);
    else
        % Når k er like stor som antall elementer i datavektoren Tid,
        % simuleres det at bryter på styrestikke trykkes inn.
        if k==length(t)
            JoyMainSwitch=1;
        end

        if plotting
            % Simulerer tiden som EV3-Matlab bruker på kommunikasjon 
            % når du har valgt "plotting=true" i offline
            pause(0.03)
        end
    end
    %--------------------------------------------------------------




    % +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    %             CONDITIONS, CALCULATIONS AND SET MOTOR POWER
    % Gjør matematiske beregninger og motorkraftberegninger.
    % hvis motor er tilkoplet.
    

    % Tilordne målinger til variabler
    u(k) = Lys(k);

    if k==1
        % Spesifisering av initialverdier og parametere
        a = 1;          % eksempelparameter
    else
        % Beregninger av Ts og andre variable

    end

    % Andre beregninger som ikke avhenger av initialverdi

    % Pådragsberegninger
    u_A(k) = a*JoyForover(k);
    u_B(k) = ...
    u_C(k) = ...
    u_D(k) = ...

    if online
        % Setter pådragsdata mot EV3
        % (slett de motorene du ikke bruker)
        motorA.Speed = u_A(k);
        motorB.Speed = u_B(k);
        motorC.Speed = u_C(k);
        motorD.Speed = u_D(k);

        start(motorA)
        start(motorB)
        start(motorC)
        start(motorD)
    end
    %--------------------------------------------------------------




    %++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    %                  PLOT DATA
    %
    % Husk at syntaksen plot(Tid(1:k),måling(1:k))
    % gir samme opplevelse i online=0 og online=1 siden
    % alle målingene (1:end) eksisterer i den lagrede .mat fila

    % Plotter enten i sann tid eller når forsøk avsluttes 
    if plotting || JoyMainSwitch  
        figure(fig1)

        subplot(2,2,1)
        plot(t(1:k),Lys(1:k));
        title('Lys reflektert')

        subplot(2,2,2)
        plot(t(1:k),Avstand(1:k));
        title('Avstand')

        subplot(2,2,3)
        plot(t(1:k),VinkelPosMotorB(1:k));
        title('Vinkelposisjon motor B')
        xlabel('tid [s]')

        subplot(2,2,4)
        plot(t(1:k),u_B(1:k));
        title('P{\aa}drag motor B')
        xlabel('tid [s]')

        % tegn nå (viktig kommando)
        drawnow
    end
    %--------------------------------------------------------------
end


% +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
%               STOP MOTORS
if online
    % For ryddig og oversiktlig kode, kan det være lurt å slette
    % de sensorene og motoren som ikke brukes.
    stop(motorA);
    stop(motorB);
    stop(motorC);
    stop(motorD);

end
%------------------------------------------------------------------

subplot(2,2,1)
legend('$\{u_k\}$')


