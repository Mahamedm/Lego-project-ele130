%++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
% Sanntid_Vannglass
%
% Hensikten med programmet er å simulere fylling av og drikking fra
% et vannglass i sanntid. For å lage vannstrømmen {q_k} [cl/s] inn
% og av glasset så brukes lyssensoren og et gråskalark. 
% For å berenge volumet {V_k} i glasset benyttes trapesmetoden.
%
% Hensikten er du skal fylle vann i glasset slik at volumet 
% følge et referansevolum {r_k}. 
%
% Følgende sensorer brukes:
% - Lyssensor
%--------------------------------------------------------------------------

%++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
%         EXPERIMENT SETUP, FILENAME AND FIGURE

clear; close all   % Alltid lurt å rydde workspace opp først
online = true;     % Online mot EV3 eller mot lagrede data?
plotting = true;  % Skal det plottes mens forsøket kjøres
filename = 'student1.mat';

if online

    % LEGO EV3 og styrestikke
    mylego = legoev3('USB');
    joystick = vrjoystick(1);
    [JoyAxes,JoyButtons] = HentJoystickVerdier(joystick);

    % sensorer
    myColorSensor = colorSensor(mylego);

else
    % Dersom online=false lastes datafil.
    load(filename)
end

fig1=figure;
%set(gcf,'Position',[.., .., .., ..])
drawnow

% setter skyteknapp til 0, og initialiserer tellevariabel k
JoyMainSwitch=0;
k=0;
%----------------------------------------------------------------------

% Starter stoppeklokke for å stoppe 
% eksperiment automatisk når t>19 sekund. 
% Du kan også stoppe med skyteknappen som før.
duration = tic;


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
            tic
            t(1) = 0;
        else
            t(k) = toc;
        end

        % sensorer
        Lys(k) = double(readLightIntensity(myColorSensor,'reflected'));

        % Data fra styrestikke.
        [JoyAxes,JoyButtons] = HentJoystickVerdier(joystick);
        JoyMainSwitch = JoyButtons(1);

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

    % Stopper automatisk når t>19 sekund
    if toc(duration) > 19
        JoyMainSwitch = 1;
    end

    % Tilordne målinger til variabler
    q(k) = Lys(k);
    q(k) = q(k) - Lys(1);   % Trekker fra første verdi Lys(1). 
                            % Hvorfor kan vi ikke skrive 
                            % q(k) = q(k) - q(1)?

    if k==1
        % Ønsket volum i glass som funksjon av tid
        tidspunkt =  [0, 2, 10];  % sekund
        RefVolum = [0, 20, 0];    % cl

        % Spesifisering av initialverdier og parametere
        V(1) = 0;
        r(1) = 0;
    
    else
        % Beregn samplingstiden Ts og implementer
        % sanntidsversjonen av trapesmetoden
        % for å beregne volumet V(k)


        % Stegvis referanse: holder forrige verdi til neste tidspunkt nås
        r(k) = interp1(tidspunkt, RefVolum, t(k), 'previous', 'extrap');

        V(k) = 0;
    end

    %--------------------------------------------------------------



    %++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    %                  PLOT DATA
    %
    % Husk at syntaksen plot(Tid(1:k),data(1:k))
    % gir samme opplevelse i online=0 og online=1 siden
    % hele datasettet (1:end) eksisterer i den lagrede .mat fila

    % Plotter enten i sann tid eller når forsøk avsluttes
    if plotting || JoyMainSwitch
        subplot(2,1,1)
        plot(t(1:k),q(1:k));
        title('Volumstr{\o}m')
        ylabel('[cl/s]')
        grid on

        subplot(2,1,2)
        plot(t(1:k),V(1:k));
        hold on
        plot(t(1:k),r(1:k),'k--');
        hold off        
        title('Volum i glass')
        xlabel('tid [s]')
        ylabel('[cl]')
        grid on

        % tegn nå (viktig kommando)
        drawnow
    end
    %--------------------------------------------------------------

end


subplot(2,1,1)
legend('Volumstr{\o}m $\{q_k\}$')

subplot(2,1,2)
legend('Volum $\{V_k\}$','{\O}nsket volum $\{r_k\}$')
