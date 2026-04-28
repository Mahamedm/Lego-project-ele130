%++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
% P04_PID
%
% Hensikten med programmet er å styre
% hastigheten til en motor med en komplett PID-regulator
%
% Følgende  motorer brukes: 
%  - motor A
%
%--------------------------------------------------------------------------


%++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
%         EXPERIMENT SETUP, FILENAME AND FIGURE

clear; close all
online = true;
plotting = true;
filename = 'P04_PID2.mat';

if online
    mylego = legoev3('USB');
    joystick = vrjoystick(1);
    [JoyAxes,JoyButtons] = HentJoystickVerdier(joystick);
    motorA = motor(mylego,'A');
    motorA.resetRotation;
else
    load(filename)
end

fig1=figure;
set(fig1,'Position',[657   257   477   618])
drawnow

JoyMainSwitch=0;
k=0;

duration = tic;

while ~JoyMainSwitch

    k=k+1;

    if online
        if k==1
            playTone(mylego,500,0.1)
            tic
            t(1) = 0;
        else
            t(k) = toc;
        end
        VinkelPosMotorA(k) = double(motorA.readRotation);
        [JoyAxes,JoyButtons] = HentJoystickVerdier(joystick);
        JoyMainSwitch = JoyButtons(1);
    else
        if k==numel(t)
            JoyMainSwitch=1;
        end
        pause(0.001)
    end

    if toc(duration) > 29
        JoyMainSwitch = 1;
    end

    x1(k) = VinkelPosMotorA(k);

    if k==1
        % Regulatorparametre
        u0 = 0;
        Kp = 0.1;
        Ki = 0.05;
        Kd = 0.05;
        tau_e = 1;
        I_max = 100;
        I_min = -100;

        % Referanse
        tidspunkt =  [0, 2,  6,   10,   14,  18];
        RefVerdier = [0 300 600, 900, 1200, 500];
        RefVerdiIndeks = 1;

        % Initialverdier
        tau_pos = 0.2;
        x1_f(1) = 0;
        x2(1) = 0;

        y(1) = x2(1);
        r(1) = 0;
        e(1) = r(1)-y(1);
        e_f(1) = e(1);

        P(1) = 0;
        I(1) = 0;
        D(1) = 0;

    else
        Ts = t(k) - t(k-1);

        alfa_pos  = 1 - exp(-Ts/tau_pos);
        x1_f(k) = (1 - alfa_pos)*x1_f(k-1) + alfa_pos*x1(k);

        x2(k) = (x1_f(k) - x1_f(k-1))/Ts;

        y(k) = x2(k);

        r(k) = interp1(tidspunkt, RefVerdier, t(k), 'previous', 'extrap');

        e(k) = r(k) - y(k);

        % PID
        P(k) = Kp * e(k);
        I(k) = I(k-1) + Ki * e(k) * Ts;

        % Integratorbegrensing
        if I(k) > I_max
            I(k) = I_max;
        elseif I(k) < I_min
            I(k) = I_min;
        end

        alfa_e  = 1 - exp(-Ts/tau_e);
        e_f(k) = (1 - alfa_e)*e_f(k-1) + alfa_e*e(k);
        D(k) = Kd * (e_f(k) - e_f(k-1)) / Ts;

        if online && r(k) ~= r(k-1)
            RefVerdiIndeks = RefVerdiIndeks + 1;
            playTone(mylego,RefVerdier(RefVerdiIndeks),0.5)
        end
    end

    u_A(k) = u0 + P(k) + I(k) + D(k);

    if online
        motorA.Speed = u_A(k);
        start(motorA)
    end

    if plotting || JoyMainSwitch
        figure(fig1)
        subplot(3,1,1)
        plot(t(1:k),r(1:k),'k--');
        hold on
        plot(t(1:k),y(1:k),'b-');
        hold off
        grid
        ylabel('[$^{\circ}$/s]')
        text(t(k),r(k),['$',sprintf('%1.0f',r(k)),'^{\circ}$/s']);
        text(t(k),y(k),['$',sprintf('%1.0f',y(k)),'^{\circ}$/s']);
        title('M{\aa}lt vinkelhastighet og referanse')

        subplot(3,1,2)
        plot(t(1:k),e(1:k),'b-');
        hold on
        plot(t(1:k),e_f(1:k),'r--');
        hold off
        grid
        title('Reguleringsavvik')
        ylabel('[$^{\circ}$/s]')

        subplot(3,1,3)
        plot(t(1:k),P(1:k),'b-');
        hold on
        plot(t(1:k),I(1:k),'b-.');
        plot(t(1:k),D(1:k),'b--');
        plot(t(1:k),u_A(1:k),'k-');
        yline(100, 'k:','linewidth',2,'HandleVisibility','off')
        yline(-100, 'k:','linewidth',2,'HandleVisibility','off')
        hold off
        grid
        title('Bidragene P, I, og D og totalp{\aa}draget')
        xlabel('Tid [sek]')

        drawnow
    end

end

if online
    stop(motorA);
end

subplot(3,1,1)
legend('$\{r_k\}$','$\{y_k\}$')
subplot(3,1,2)
legend('$\{e_k\}$',['$\{e_{f,k}\}$, $\tau_e$=',num2str(tau_e),' s'])
subplot(3,1,3)
legend(['P-del, $K_p$=',num2str(Kp)],...
    ['I-del,  $K_i$=',num2str(Ki)],...
    ['D-del,  $K_d$=',num2str(Kd),' og $\tau_e$=',num2str(tau_e)],...
    '$\{u_k\}$')



