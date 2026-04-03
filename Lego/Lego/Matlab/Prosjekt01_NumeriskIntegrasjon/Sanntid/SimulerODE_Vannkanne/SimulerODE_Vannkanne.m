%++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
% SimulerODE_Vannkanne
%
% Hensikten er å simulere fylling og tapping 
% fra en vannkanne, helt likt eksempel 12.5 i kompendiet.
%--------------------------------------------------------------------------


%++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
%         EXPERIMENT SETUP, FILENAME AND FIGURE

clear; close all   % Alltid lurt å rydde workspace opp først
online = true;     % Online mot EV3 eller mot lagrede data?
plotting = true;  % Skal det plottes mens forsøket kjøres
filename = 'vannkanne_1.mat';

if online

    % LEGO EV3 og styrestikke
    mylego = legoev3('USB');
    joystick = vrjoystick(1);
    [JoyAxes,JoyButtons] = HentJoystickVerdier(joystick);


    % motorer
    motorA = motor(mylego,'A');
    motorA.resetRotation;               % resetter motor-posisjon
    motorB = motor(mylego,'B');
    motorB.resetRotation;               % resetter motor-posisjon
else
    % Dersom online=false lastes datafil.
    load(filename)
end

fig1=figure;
set(gcf,'units','normalized','outerposition',[0.15 0.03 0.36 0.9])
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

        % Motorposisjonen til motor A skal simulere
        % pådragssignalet til blandebatteriet
        motorPosA(k) = double(motorA.readRotation);

        % Motorposisjonen til motor B skal simulere
        % pådragssignalet til tappenkranen
        motorPosB(k) = double(motorB.readRotation);

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
    %   Motorposisjonen til motor A 0<motorPosA(k)<90 skal simulere
    %   pådragssignalet u(k) til blandebatteriet 0<u(k)<1.
    %   Må derfor justere med verdien ...
    u(k) = motorPosA(k)..;
    %   På grunn av unøyaktighet i motorens posisjon,
    %   så kan du noen ganger oppleve å få verdier som er
    %   u(k) = -0.011 eller u(k) = 1.01.
    %   Tvinger derfor u(k) til å være mellom 0 og 1.
    u(k) = max(min(...));

    %   Tilsvarende for motorposisjon til motor B.
    %   Pådragssignal tappekran  0<v(k)<1
    v(k) = motorPosB(k)..;
    %   Tvinger v(k) til å være mellom 0 og 1
    v(k) = max(min(...));


    if k==1
        % Modellparametere
        rho = 1000;               % tetthet [kg/m^3]
        g = 9.8;                  % tyngdekraft [m/s^2]
        A = pi*0.05^2;            % areal vannflate [m^2]
        Kv_HV2_SI = 3e-6;         % Kv_SI tappekran [m^3/(s∗sqrt(Pa))]
        q_max = 0.00016;          % max volumstrøm blandebatteri [m3/s]
        h_max = 0.3;              % største nivå i kanne

        % Initialverdier blandebatteri
        u(1) = 0;       % åpning blandebatteri [-]
        q_inn(1) = 0;   % innstrøm fra blandebatteri [m3/s]

        % Initialverdier kanne
        h(1) = -0.08 + 0.17;     % nivå i vannkanne [m]

        % Initialverdier tappekran
        v(1) = 0;       % åpning tappekran [-]
        q_ut(1) = 0;    % utstrøm tappekran [m3/s]

        % Nye initialverder i forhold til eksempel 12.5
        J(1) = 0;        % initialverdi kriteriefunksjon
        r(1) = h(1);     % initialverdi ønsket nivå i kanne

        t_max = 60;      % eksperimentlengde

    else
       % Beregner Ts 
        Ts = t(k)-t(k-1);

        % Beregner ratene [m3/s] inn og ut av kanna
        q_inn(k-1) = ..;  % [m3/s]
        q_ut(k-1) = ..;   % [m3/s]

        % Integrerer diff.likn. med Eulers forover
        h_dot(k-1) = ..;
        h(k) = ..;

        % Fysiske begrensinger i kannen
        if h(k) > h_max
            h(k) = h_max;
        elseif h(k) < 0
            h(k) = 0;
        end

        % Referanse for nivået r(k), forhåndsdefinert
        r(k) = -0.08*cos(2*pi*0.03*t(k)) + 0.17;
        e(k) = ..;         % avviket
        delta_u(k) = ..;   % endring i påfyllingspådrag
        delta_v(k) = ..;   % endring i tappekranpådrag

        % Beregner kriteriefunksjon J
        Q = 10;    % vekting på avviket e(k)
        R = 1;     % vekting på delta_u(k) og delta_v(k)
        J(k) = ..
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

    % Plotter enten i sann tid eller når forsøk avsluttes
    if plotting || JoyMainSwitch
        figure(fig1)

        subplot(3,2,1)
        plot(t(1:k),u(1:k));
        grid 
        title('P{\aa}drag $u(t)$ blandebatteri')
        ylabel('[-]')
        xlim([0 t_max])
        ylim([-0.05 1.05])

        subplot(3,2,2)
        plot(t(1:k),v(1:k));
        grid
        title('P{\aa}drag $v(t)$ tappekran')
        ylabel('[-]')
        xlim([0 t_max])
        ylim([-0.05 1.05])

        subplot(3,2,3)
        plot(t(1:k-1),q_inn(1:k-1)*10000);
        grid
        title('Volumstr{\o}m $q_{inn}(t)$ blandebatteri')
        ylabel('[dl/s]')
        xlim([0 t_max])


        subplot(3,2,4)
        plot(t(1:k-1),q_ut(1:k-1)*10000);
        grid
        title('Volumutstr{\o}m $q_{ut}(t)$ tappekran')
        ylabel('[dl/s]')
        xlim([0 t_max])

        subplot(3,2,5)
        plot(t(1:k),h(1:k));
        hold on
        plot(t(1:k),r(1:k));
        hold off
        grid
        title('Vanniv{\aa} $h(t)$ og {\o}nsket niv{\aa} $r(t)$')
        ylabel('[m]')
        xlabel('tid [s]')
        xlim([0 t_max])
        ylim([-0.02 h_max+0.02])

        subplot(3,2,6)
        plot(t(1:k),J(1:k));
        grid
        title('Kriteriefunksjonen $J(t)$')
        ylabel('[-]')
        xlabel('tid [s]')
        xlim([0 t_max])

        % tegn naa (viktig kommando)
        drawnow
    end
    %--------------------------------------------------------------

end






