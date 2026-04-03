%++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
% TestOppkopling
%
% Hensikten med programmet er å teste at opplegget fungerer på PC/Mac
% Følgende sensorer brukes:
% - Lyssensor (måler refleksjon av utsendt lys)
% - Ultralydsensor (måler avstand)
% - Gyrosensor (måler vinkel)
% - Bryter-sensor (måler 0 eller 1)
%
% Følgende motorer brukes:
% - motor A
% - motor B
%
%--------------------------------------------------------------------------

%++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
%         EXPERIMENT SETUP, FILENAME AND FIGURE

clear; close all   % Alltid lurt å rydde workspace opp først
online = true;     % Online mot EV3 eller mot lagrede data?
plotting = true;  % Skal det plottes mens forsøket kjøres 
filename = 'MeasTest_1.mat';
%--------------------------------------------------------------------------

if online

    % Initialiser styrestikke, sensorer og motorer. 
    % LEGO EV3 og styrestikke
    mylego = legoev3('USB');
    joystick = vrjoystick(1);
    [JoyAxes,JoyButtons] = HentJoystickVerdier(joystick);

    % Hvilke sensorer er koplet til?
    myColorSensor = colorSensor(mylego);
    myTouchSensor = touchSensor(mylego);
    mySonicSensor = sonicSensor(mylego);
    myGyroSensor  =  gyroSensor(mylego);
    resetRotationAngle(myGyroSensor);   % resetter gyro-vinkel

    % Hvilke motorer er koplet til?
    motorA = motor(mylego,'A');
    motorA.resetRotation;               % resetter motor-posisjon
    motorB = motor(mylego,'B');
    motorB.resetRotation;               % resetter motor-posisjon
else
    % Dersom online=false lastes datafil.
    load(filename)
end

fig1=figure;
set(gcf,'units','normalized','outerposition',[0.1 0.3 0.6 0.6])
drawnow

fig2=figure;
set(gcf,'units','normalized','outerposition',[0.7 0.7 0.25 0.2])
drawnow

% setter skyteknapp til 0, og initialiserer tellevariabel k
JoyMainSwitch=0;
k=0;

fig3 = figure;
set(gcf,'units','normalized','outerposition',[0.3 0.2 0.5 0.5])
drawnow
%----------------------------------------------------------------------


while ~JoyMainSwitch
    %+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    %                       GET TIME AND MEASUREMENT
    % Få tid og målinger fra sensorer, motorer og joystick

    k=k+1;    % Oppdater tellevariabel

    if online
        if k==1
            % Spiller av lyd slik at du vet at innsamlingen har startet
            playTone(mylego,500,0.1)   % 500Hz i 0.1 sekund
            tic         % Starter stoppeklokke
            t(1) = 0;
        else
            t(k) = toc; % Henter ut medgått tid
        end

        % Hent målinger fra sensorene
        Lys(k) = double(readLightIntensity(myColorSensor,'reflected'));
        Bryter(k)  = double(readTouch(myTouchSensor));
        Avstand(k) = double(readDistance(mySonicSensor));
        GyroAngle(k) = double(readRotationAngle(myGyroSensor));

        % Hent målinger fra motorene
        VinkelPosMotorA(k) = double(motorA.readRotation);
        VinkelPosMotorB(k) = double(motorB.readRotation);

        % Data fra styrestikke. Utvid selv med andre knapper og akser
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
    % hvis motor er tilkoplet
    
    % Tilordne målinger til variabler
    u_A(k) = JoyForover(k);
    u_B(k) = JoyForover(k);

    if k==1
        % Spesifisering av initialverdier og parametere
        Ts(1) = 0.05;    % nominell verdi
    else
        % Beregninger av Ts(k) og andre variable
        Ts(k) = t(k) - t(k-1); 
    end

    if online
        % Setter pådragsdata mot EV3
        motorA.Speed = u_A(k);
        start(motorA)
        motorB.Speed = u_B(k);
        start(motorB)
    end
    %--------------------------------------------------------------


    %++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    %                  PLOT DATA
    %
    % Husk at syntaksen plot(Tid(1:k), variabel(1:k))
    % gir samme opplevelse i online=false og online=true siden
    % alle målingene (1:end) eksisterer i den lagrede .mat fila

    % Plotter enten i sann tid eller når forsøk avsluttes 
    if plotting || JoyMainSwitch  
        figure(fig3)

        subplot(2,1,1)
        plot(t(1:k), Lys(1:k), 'b')
        grid on
        ylim([-5 105])
        title('Reflektert lys')
        ylabel('Lys')
        
        subplot(2,1,2)
        plot(t(1:k), VinkelPosMotorA(1:k), 'b')
        hold on
        plot(t(1:k), VinkelPosMotorB(1:k), 'r--')
        hold off
        grid on
        title('Motorposisjon A og B')
        xlabel('tid [s]')
        ylabel('grader')

        % tegn naa (viktig kommando)
        drawnow
    end
    %--------------------------------------------------------------
end


% +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
%                STOP MOTORS
if online
    % Stopper motor etter at while-løkken er ferdig. 
    % 1 - betyr at den bremser
    % 0 - betyr at den ruller til stopp
    % se https://se.mathworks.com/help/matlab/supportpkg/legomindstormsev3iospidev.stop.html
    stop(motorA,1);
    stop(motorB,0);
end
%------------------------------------------------------------------





