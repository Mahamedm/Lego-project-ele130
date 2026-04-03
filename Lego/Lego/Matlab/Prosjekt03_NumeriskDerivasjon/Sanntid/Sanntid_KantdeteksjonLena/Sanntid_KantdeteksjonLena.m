%++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
% Sanntid_KantdeteksjonLena
%
% Estimere kantene i bildet.
%
%--------------------------------------------------------------------------


%++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
%         EXPERIMENT SETUP, FILENAME AND FIGURE

clear; close all   % Alltid lurt å rydde workspace opp først
online = true;    % Online mot EV3 eller mot lagrede data?
plotting = true;   % Skal det plottes mens forsøket kjøres 
filename = 'TidLys.mat'; 

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
    
    
    % +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    %             CONDITIONS, CALCULATIONS AND SET MOTOR POWER
    % Gjør matematiske beregninger og motorkraftberegninger.
   
    % Tilordne målinger til variabler
    u(k) = Lys(k);        
 
    if k==1
        terskelverdi = 0;
        % Spesifisering av initialverdier og parametere
        v(1) = 0;
        u_f(1) = 0;
        kant(1) = 0;
    else
        % Beregner samplingstiden Ts og implementer
        % sanntidsversjonen av et første ordens
        % lavpassfilter og for å beregne u_f(k) 
        % og sanntidsversjonen av bakoverderivasjon for 
        % å beregne v(k)
        v(k) = 0;
        u_f(k) = 0;
        kant(k) = 0;
    end
    
    %--------------------------------------------------------------

    
    %++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    %                  PLOT DATA
    %
    % Husk at syntaksen plot(Tid(1:k),data(1:k))
    % for gir samme opplevelse i online=0 og online=1 siden
    % hele datasettet (1:end) eksisterer i den lagrede .mat fila
    
    % Plotter enten i sann tid eller når forsøk avsluttes
    if plotting || JoyMainSwitch

        subplot(3,1,1)
        plot(t(1:k),u(1:k),t(1:k),u_f(1:k))
        grid
        title('Intensitetsprofil')
        
        subplot(3,1,2)
        plot(t(1:k),v(1:k))
        grid
        hold on
        yline(terskelverdi)
        yline(-terskelverdi)
        hold off
        title('Derivert av intensitetsprofil (x. ordens lavpass)')

        subplot(3,1,3)
        plot(t(1:k),kant(1:k),'b-');
        grid
        title('Kantdeteksjon') 
        ylim([-0.1 1.1])
        xlabel('tid [s]')

        % tegn naa (viktig kommando)
        drawnow
        %--------------------------------------------------------------
    end        
end


subplot(3,1,1)
legend('M{\aa}ling','Filtrert')

subplot(3,1,2)
legend('Derivert','{\O}vre deteksjonsgrense','Nedre detektsjonsgrense')

subplot(3,1,3)
legend('Kanter i bildet')

