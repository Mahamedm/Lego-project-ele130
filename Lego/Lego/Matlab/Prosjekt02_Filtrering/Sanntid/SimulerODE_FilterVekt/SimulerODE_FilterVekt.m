%++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
% SimulerODE_Vannkanne
%
% Hensikten er å simulere en kjøkkenvekt.
%
%--------------------------------------------------------------------------


%++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
%         EXPERIMENT SETUP, FILENAME AND FIGURE

clear; close all   % Alltid lurt å rydde workspace opp først
online = true;     % Online mot EV3 eller mot lagrede data?
plotting = true;  % Skal det plottes mens forsøket kjøres
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

fig = figure('Name','Kjøkkenvekt Display','NumberTitle','off','Position',[500 500 300 150]);
% Lag et tekstfelt som simulerer LCD-display

lcdDisplay = uicontrol('Style','text',...
    'FontSize',40,...
    'FontName','FixedWidth',...
    'FontWeight','bold',...
    'BackgroundColor',[0.9 0.9 0.9],...
    'ForegroundColor',[0.1 0.1 0.1],... % grønn tekst som LCD
    'Position',[50 40 200 60],...
    'String','0.00');

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

        % pådragssignal vanndispenser og tappekran
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
            pause(0.01)
        end
    end
    %--------------------------------------------------------------



    % +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    %             CONDITIONS, CALCULATIONS AND SET MOTOR POWER
    % Gjør matematiske beregninger og motorkraftberegninger.

    % Tilordne målinger til variable
    w_inn(k) = Lys(k)-Lys(1);   % masseinnstrøm [g/s]
    
    if k==1
        % Initialverdier modell og filter


        % Eksperimentlengde og tidskonstant filter
        t_max = 10;      % eksperimentlengde
        tau = 2;         % gitt i oppgave

    else
       % Beregner Ts 
        Ts = t(k)-t(k-1);

        % Integrerer diff.likn. med Eulers forover
        m_dot(k-1) = ..
        m(k) = ..

        % Filtrere m(k) før visning i LCD
        alfa  = ..
        m_f(k) = ..
        
    end

    % stopper er t_max
    if t(k)>=t_max
        JoyMainSwitch=1;
    end

    %--------------------------------------------------------------


    %++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    %                  PLOT DATA
    % Husk at syntaksen plot(Tid(1:k),data(1:k))
    % for gir samme opplevelse i online=0 og online=1 siden
    % hele datasettet (1:end) eksisterer i den lagrede .mat fila

    % Skriver filtrert vekt til display
    set(lcdDisplay,'String',sprintf('%.0f gr',m_f(k))); 

    %--------------------------------------------------------------

end

% Plotter alt etter forsøksslutt
figure
subplot(2,1,1)
plot(t(1:k),w_inn(1:k),'b-');
grid
title('P{\aa}fylling av sukker')
ylabel('[g/s]')
xlim([0 t_max])

subplot(2,1,2)
plot(t(1:k),m_f(1:k),'b-');
hold on
plot(t(1:k),m(1:k),'r-');
grid
ylabel('[g]')
title('Vekt vist i display $m_f(t)$ og reell vekt $m(t)$')
xlim([0 t_max])
ylim([-10 300])





