%++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
% Serie_5_6_7
%
% Samler inn målinger til serie 5, 6 og 7.
%
% Følgende sensorer brukes:
% - Lyssensor (måler refleksjon av utsendt lys)
%
% Følgende motorer brukes:
% - motor A
%--------------------------------------------------------------------------


%++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
%         EXPERIMENT SETUP, FILENAME AND FIGURE

clear; close all   % Alltid lurt å rydde workspace opp først
online = true;     % Online mot EV3 eller mot lagrede data?
plotting = true;  % Skal det plottes mens forsøket kjøres
filename = 'Serie5_Sinus_u20.mat';

if online

    % LEGO EV3 og styrestikke
    mylego = legoev3('USB');
    joystick = vrjoystick(1);
    [JoyAxes,JoyButtons] = HentJoystickVerdier(joystick);

    % Hvilke sensorer er koplet til?
    myColorSensor = colorSensor(mylego);

    % Hvilke motorer er koplet til?
    motorA = motor(mylego,'A');
    motorA.resetRotation;
else
    % Dersom online=false lastes datafil.
    load(filename)
end

fig1=figure;
set(gcf,'units','normalized','outerposition',...
    [0.1 0.27 0.34 0.62])
drawnow

% setter skyteknapp til 0, og initialiserer tellevariabel k
JoyMainSwitch=0;
k=0;
%----------------------------------------------------------------------


while ~JoyMainSwitch

    %+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    %                       GET TIME AND MEASUREMENT
    % Få tid og målinger fra sensorer, motorer og joystick

    % oppdater tellevariabel
    k=k+1;

    if online
        if k==1
            % Spiller av lyd slik at du vet at innsamlingen har startet
            playTone(mylego,500,0.1)   % 500Hz i 0.1 sekund
            tic         % Starter stoppeklokke
            t(1) = 0;
        else
            t(k) = toc; % Henter ut medgått tid
        end

        % sensorer
        Lys(k) = double(readLightIntensity(myColorSensor,'reflected'));
        VinkelPosMotorA(k) = double(motorA.readRotation);

        % Data fra styrestikke. Utvid selv med andre knapper og akser
        [JoyAxes,JoyButtons] = HentJoystickVerdier(joystick);
        JoyMainSwitch = JoyButtons(1);
    else
        % online=false
        % Naar k er like stor som antall elementer i datavektpren Tid,
        % simuleres det at bryter paa styrestikke trykkes inn.
        if k==numel(t)
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

    % Beregner pådrag til motor
    u_A(k) = 0;
    if t(k) > 3
         u_A(k) = 20;
    end
    
    if online && t(k) < 3.25
        % Setter pådragsdata mot EV3
        motorA.Speed = u_A(k);
        start(motorA)
    end

    %--------------------------------------------------------------


    %++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    %                  PLOT DATA
    % Husk at syntaksen plot(Tid(1:k),data(1:k))
    % for gir samme opplevelse i online=0 og online=1 siden
    % hele datasettet (1:end) eksisterer i den lagrede .mat fila

    % Plotter enten i sann tid eller når forsøk avsluttes
    if plotting || JoyMainSwitch
        figure(fig1)


        subplot(3,1,1)
        plot(t(1:k),u_A(1:k),'b-');
        title('P{\aa}drag til motoren')
        ylabel('[\%]')

        subplot(3,1,2)
        plot(t(1:k),VinkelPosMotorA(1:k),'b-');
        title('Vinkelposisjon motor A')
        ylabel('[$^{\circ}$]')

        subplot(3,1,3)
        plot(t(1:k),Lys(1:k),'b-');
        title('M{\aa}ling av reflektert lys')
        xlabel('tid [s]')

        % tegn naa (viktig kommando)
        drawnow
    end
    %--------------------------------------------------------------

end



% +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
%           STOP MOTORS

if online
    % Stopper motor etter at while-løkken er ferdig
    stop(motorA);
end


% Lager litt luft i y-retning
subplot(3,1,1)
xl = xlim(gca);        % husk x-limits
axis padded;           % legger padding på begge akser
xlim(xl);              % gjenopprett x-limits, bare y beholdes paddet
grid

% Lager litt luft i y-retning
subplot(3,1,2)
xl = xlim(gca);        % husk x-limits
axis padded;           % legger padding på begge akser
xlim(xl);              % gjenopprett x-limits, bare y beholdes paddet
grid

% Lager litt luft i y-retning
subplot(3,1,3)
xl = xlim(gca);        % husk x-limits
axis padded;           % legger padding på begge akser
xlim(xl);              % gjenopprett x-limits, bare y beholdes paddet
grid
legend(['$\{u_k\}$, $T_s{\approx}$',num2str(mean(diff(t)),2),' sek',...
    ', $f_s{\approx}$',num2str(1/(mean(diff(t))),3),' Hz'],...
    'location','best')
%------------------------------------------------------------------


