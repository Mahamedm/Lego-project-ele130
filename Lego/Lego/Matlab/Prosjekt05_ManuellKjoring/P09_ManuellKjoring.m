%++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
% P09_ManuellKjoring
% Manuell kjøring av LEGO-robot med joystick
%++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

clear; close all; clc;

%% Setup
online = true;
plotting = true;
filename = 'P09_Kjoering_1.mat';

%% Koble til hardware
if online
    % EV3 via USB
    mylego = legoev3('usb');

    % Joystick
    joystick = vrjoystick(1);

    % Motorer
    motorA = motor(mylego,'A');
    motorB = motor(mylego,'B');
    resetRotation(motorA);
    resetRotation(motorB);

    % Lyssensor
    sensor1 = colorSensor(mylego,3);

else
    load(filename)
end

%% Figur
fig1 = figure;
set(fig1,'Position',[50 50 800 900])

%% Initialisering
JoyMainSwitch = 0;
k = 0;
duration = tic;

%% Hovedløkke
while ~JoyMainSwitch

    k = k + 1;

    %% Tid
    if online
        if k == 1
            playTone(mylego,500,0.1)
            tic;
            t(k) = 0;
        else
            t(k) = toc;
        end
    else
        if k >= length(t)
            JoyMainSwitch = 1;
        end
        pause(0.01)
    end

    %% Les sensorer og joystick
    if online
        % Lysmåling
        Lys(k) = double(readReflectedLightIntensity(sensor1));

        % Joystick
        JoyAxes = axis(joystick);
        JoyButtons = button(joystick);

        JoyMainSwitch = JoyButtons(1);

        % Akser
        fart    = -JoyAxes(2)*100;
        styring = JoyAxes(1)*100;
    end

    %% Stopp etter 120 sek
    if toc(duration) > 120
        JoyMainSwitch = 1;
    end

    %% Beregninger
    if k == 1
        r(k) = Lys(k);
        y(k) = Lys(k);
        e(k) = 0;

        MAE(k) = 0;
        IAE(k) = 0;
        TVA(k) = 0;
        TVB(k) = 0;

        u_A(k) = 0;
        u_B(k) = 0;
    else
        Ts = t(k)-t(k-1);

        y(k) = Lys(k);
        r(k) = r(1);
        e(k) = r(k)-y(k);

        % Motorpådrag
        u_A(k) = fart + styring;
        u_B(k) = fart - styring;

        % Begrensning
        u_A(k) = max(-100,min(100,u_A(k)));
        u_B(k) = max(-100,min(100,u_B(k)));

        % Kvalitetsmål
        MAE(k) = MAE(k-1) + (abs(e(k))-MAE(k-1))/k;
        IAE(k) = IAE(k-1) + Ts*0.5*(abs(e(k-1))+abs(e(k)));
        TVA(k) = TVA(k-1) + abs(u_A(k)-u_A(k-1));
        TVB(k) = TVB(k-1) + abs(u_B(k)-u_B(k-1));
    end

    %% Send til motorer
    if online
        motorA.Speed = u_A(k);
        motorB.Speed = u_B(k);

        start(motorA)
        start(motorB)
    end

    %% Plot
    if plotting
        figure(fig1)

        subplot(4,1,1)
        plot(t(1:k),r(1:k),'k--'); hold on
        plot(t(1:k),y(1:k),'b');
        hold off
        grid on
        title('Lysmåling og referanse')
        ylabel('Lys')

        subplot(4,1,2)
        plot(t(1:k),e(1:k),'b')
        grid on
        title('Reguleringsavvik')
        ylabel('Avvik')

        subplot(4,1,3)
        plot(t(1:k),u_A(1:k),'b'); hold on
        plot(t(1:k),u_B(1:k),'r');
        hold off
        grid on
        title('Motorpådrag')
        ylabel('Pådrag')

        subplot(4,1,4)
        plot(t(1:k),MAE(1:k),'b'); hold on
        plot(t(1:k),IAE(1:k),'r');
        plot(t(1:k),TVA(1:k),'g');
        plot(t(1:k),TVB(1:k),'m');
        hold off
        grid on
        title('Kvalitetsmål')
        xlabel('Tid [s]')

        drawnow
    end
end

%% Stopp motorer
if online
    stop(motorA)
    stop(motorB)
end

%% Resultater
fprintf('\n--- Kvalitetsmål ---\n')
fprintf('Sluttverdi MAE : %.4f\n',MAE(end))
fprintf('Sluttverdi IAE : %.4f\n',IAE(end))
fprintf('Sluttverdi TV_A: %.4f\n',TVA(end))
fprintf('Sluttverdi TV_B: %.4f\n',TVB(end))
fprintf('Middelverdi y  : %.4f\n',mean(y))
fprintf('Standardavvik y: %.4f\n',std(y))

%% Lagre
if online
    clear mylego joystick motorA motorB sensor1
end
save(filename)