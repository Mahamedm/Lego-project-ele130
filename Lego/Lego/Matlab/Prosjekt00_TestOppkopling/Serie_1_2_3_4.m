%++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
% Serie_1_2_3_4
%
% Samler inn målinger til serie 1, 2, 3 og 4.
%
% Følgende sensorer brukes:
% - Lyssensor (måler refleksjon av utsendt lys)
%--------------------------------------------------------------------------


%++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
%         EXPERIMENT SETUP, FILENAME AND FIGURE

clear; close all   % Alltid lurt å rydde workspace opp først
online = true;     % Online mot EV3 eller mot lagrede data?
plotting = true;  % Skal det plottes mens forsøket kjøres
filename = 'Serie1_Sprang.mat';

if online
    % Initialiser styrestikke, sensorer og motorer. 

    % LEGO EV3 og styrestikke
    mylego = legoev3('USB');
    joystick = vrjoystick(1);
    [JoyAxes,JoyButtons] = HentJoystickVerdier(joystick);

    % Hvilke sensorer er koplet til?
    myColorSensor = colorSensor(mylego);

else
    % Dersom online=false lastes datafil.
    load(filename)
end

fig1=figure;
set(gcf,'units','normalized','outerposition',...
    [0.15 0.6 0.35 0.35])
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

        % Hent målinger fra sensorene
        Lys(k) = double(readLightIntensity(myColorSensor,'reflected'));

        % Data fra styrestikke. Utvid selv med andre knapper og akser
        [JoyAxes,JoyButtons] = HentJoystickVerdier(joystick);
        JoyMainSwitch = JoyButtons(1);
    else
        % Når k er like stor som antall elementer i datavektoren Tid,
        % simuleres det at bryter på styrestikke trykkes inn.
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


    %--------------------------------------------------------------


    %++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    %                  PLOT DATA
    % Husk at syntaksen plot(Tid(1:k),data(1:k))
    % for gir samme opplevelse i online=0 og online=1 siden
    % hele datasettet (1:end) eksisterer i den lagrede .mat fila

    % Plotter enten i sann tid eller når forsøk avsluttes
    if plotting || JoyMainSwitch
        figure(fig1)

        plot(t(1:k),Lys(1:k));
        title('M{\aa}ling av reflektert lys')
        xlabel('tid [s]')

        % tegn naa (viktig kommando)
        drawnow
    end
    %--------------------------------------------------------------

end


% +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
%                STOP MOTORS

% Lager litt luft i y-retning
xl = xlim(gca);        % husk x-limits
axis padded;           % legger padding på begge akser
xlim(xl);              % gjenopprett x-limits, bare y beholdes paddet

grid on
legend(['$\{u_k\}$, $T_s{\approx}$',num2str(mean(diff(t)),2),' sek',...
    ', $f_s{\approx}$',num2str(1/(mean(diff(t))),3),' Hz'],...
    'location','best')


%------------------------------------------------------------------




