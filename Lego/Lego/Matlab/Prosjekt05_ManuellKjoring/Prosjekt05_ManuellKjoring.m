%==========================================================================
% Prosjekt05_ManuellKjoring.m
%
% Chapter 9 – Manual driving of the LEGO robot around the track.
%
% Sensors used:
%   - Light sensor  : measures reflected light = "position" on the track
%   - Gyro sensor   : measures robot heading angle
%   - Motors A & B  : left and right wheel
%
% Quality metrics computed in real time (recursive):
%   MAE   – Mean Absolute Error      (eq. 9.2)
%   IAE   – Integral of Absolute Error (eq. 9.3, trapezoidal)
%   TV_A  – Total Variation motor A   (eq. 9.8)
%   TV_B  – Total Variation motor B   (eq. 9.9)
%   ȳ, σ  – Mean and std of light measurements (eq. 9.10-9.11)
%   J     – Cost function             (eq. 9.12)
%==========================================================================

clear; close all

%--------------------------------------------------------------------------
% EXPERIMENT SETUP
%--------------------------------------------------------------------------
online   = true;          % true = live EV3, false = replay saved data
plotting = false;         % false = more samples, required for final report

filename = 'ManuellKjoring.mat';

%--- Joystick axis scaling -------------------------------------------------
a = 0.5;    % forward/backward gain  (JoyForover axis)
b = 0.5;    % left/right turn gain   (JoySide axis)

%--- Motor safety limits --------------------------------------------------
u_max =  100;
u_min = -100;

if online
    mylego        = legoev3('USB');
    joystick      = vrjoystick(1);
    myColorSensor = colorSensor(mylego);
    myGyroSensor  = gyroSensor(mylego);
    motorA        = motor(mylego, 'A');
    motorB        = motor(mylego, 'B');
    motorA.Speed  = 0;
    motorB.Speed  = 0;
    start(motorA);
    start(motorB);
    [JoyAxes, JoyButtons] = HentJoystickVerdier(joystick);
else
    load(filename)
end

%--- Pre-allocate (avoids repeated memory allocation in loop) -------------
% (MATLAB will extend automatically, but pre-alloc speeds things up)

figure('Name','Manuell kjøring – sanntid');

JoyMainSwitch = 0;
k = 0;

%==========================================================================
%                          MAIN WHILE-LOOP
%==========================================================================
while ~JoyMainSwitch

    %----------------------------------------------------------------------
    % 1) GET TIME AND MEASUREMENTS
    %----------------------------------------------------------------------
    k = k + 1;

    if online
        if k == 1
            playTone(mylego, 500, 0.1);
            tic;
            Tid(1) = 0;
        else
            Tid(k) = toc;
        end

        Lys(k)  = double(readLightIntensity(myColorSensor, 'reflected'));
        Gyro(k) = double(readRotationAngle(myGyroSensor));

        [JoyAxes, JoyButtons] = HentJoystickVerdier(joystick);
        JoyMainSwitch  = JoyButtons(1);
        JoyForover(k)  = JoyAxes(2);   % forward/backward (check joytest!)
        JoySide(k)     = JoyAxes(1);   % left/right

    else
        % Offline replay
        if k == numel(Tid)
            JoyMainSwitch = 1;
        end
        if plotting
            pause(0.03);   % simulate EV3 communication delay
        end
    end

    %----------------------------------------------------------------------
    % 2) CONDITIONS, CALCULATIONS AND SET MOTOR POWER
    %----------------------------------------------------------------------

    % --- Reference and error (eq. 9.1) -----------------------------------
    y(k) = Lys(k);
    r(k) = Lys(1);          % reference = first measured grey value
    e(k) = r(k) - y(k);

    % --- Motor drive (joystick) ------------------------------------------
    %
    % u_A = a*forward - b*side   → forward component shared, turn subtracts from A
    % u_B = a*forward + b*side   → turn adds to B
    % This makes left-stick → robot turns left (A slows, B speeds up)
    %
    u_A(k) = a * JoyForover(k) - b * JoySide(k);
    u_B(k) = a * JoyForover(k) + b * JoySide(k);

    % Clamp to motor limits
    u_A(k) = max(min(u_A(k), u_max), u_min);
    u_B(k) = max(min(u_B(k), u_max), u_min);

    if online
        motorA.Speed = u_A(k);
        motorB.Speed = u_B(k);
    end

    % --- Quality metrics (all recursive – computed every step) -----------

    if k == 1
        % ---- Initialise everything to zero / first value ----------------
        Ts(1)         = 0.01;   % nominal first step [s]

        % MAE  (eq. 9.2)
        e_sum(1)      = abs(e(1));
        MAE(1)        = e_sum(1);

        % IAE  (eq. 9.3, trapezoidal: needs k≥2, set to 0)
        IAE(1)        = 0;

        % TV   (eq. 9.8-9.9: needs k≥2, set to 0)
        TV_A(1)       = 0;
        TV_B(1)       = 0;

        % Mean and std  (eq. 9.10-9.11)
        y_sum(1)      = y(1);
        y_mean(1)     = y(1);
        sq_sum(1)     = 0;
        sigma(1)      = 0;

        % Cost function J  (eq. 9.12, initialise accumulators)
        J_e(1)        = e(1)^2;
        J_uA(1)       = 0;
        J_uB(1)       = 0;
        J(1)          = 0;

    else
        % ---- Sampling time ----------------------------------------------
        Ts(k) = Tid(k) - Tid(k-1);

        % ---- MAE  (eq. 9.2) --------------------------------------------
        %   MAE_k = (1/k) * sum_{i=1}^{k} |e_i|
        %   Recursive: e_sum grows by |e(k)| each step, then divide by k
        e_sum(k) = e_sum(k-1) + abs(e(k));
        MAE(k)   = e_sum(k) / k;

        % ---- IAE  (eq. 9.3) – trapezoidal rule -------------------------
        %   IAE_k = IAE_{k-1} + Ts * (|e(k)| + |e(k-1)|) / 2
        IAE(k) = IAE(k-1) + Ts(k) * (abs(e(k)) + abs(e(k-1))) / 2;

        % ---- TV  (eq. 9.8-9.9) -----------------------------------------
        %   TV grows by |Δu| every step – can never decrease
        TV_A(k) = TV_A(k-1) + abs(u_A(k) - u_A(k-1));
        TV_B(k) = TV_B(k-1) + abs(u_B(k) - u_B(k-1));

        % ---- Mean and standard deviation  (eq. 9.10-9.11) --------------
        %   Running mean: ȳ_k = ȳ_{k-1} + (y_k - ȳ_{k-1}) / k
        y_mean(k) = y_mean(k-1) + (y(k) - y_mean(k-1)) / k;

        %   Running std: Welford's online algorithm (numerically stable)
        %   sq_sum accumulates sum of squared deviations from running mean
        sq_sum(k) = sq_sum(k-1) + (y(k) - y_mean(k-1)) * (y(k) - y_mean(k));
        if k > 1
            sigma(k) = sqrt(sq_sum(k) / (k - 1));
        else
            sigma(k) = 0;
        end

        % ---- Cost function J  (eq. 9.12) --------------------------------
        %   J = Q * sum(e^2) + R * sum(ΔuA^2) + R * sum(ΔuB^2)
        %   Choose Q and R – equal weighting is a reasonable start
        Q = 1;
        R = 1;
        delta_uA = u_A(k) - u_A(k-1);
        delta_uB = u_B(k) - u_B(k-1);
        J_e(k)   = J_e(k-1)  + e(k)^2;
        J_uA(k)  = J_uA(k-1) + delta_uA^2;
        J_uB(k)  = J_uB(k-1) + delta_uB^2;
        J(k)     = Q * J_e(k) + R * J_uA(k) + R * J_uB(k);

    end

    %----------------------------------------------------------------------
    % 3) REAL-TIME PLOT  (only if plotting=true, disabled for final run)
    %----------------------------------------------------------------------
    if plotting || JoyMainSwitch

        subplot(4,2,1)
        plot(Tid(1:k), Gyro(1:k), 'b')
        grid on; ylabel('Gyro [°]'); title('Gyro sensor')

        subplot(4,2,2)
        plot(Tid(1:k), y(1:k), 'b'); hold on
        plot(Tid(1:k), r(1:k), 'r--'); hold off
        grid on; ylabel('Lys'); title('Lysmåling y(k) og referanse r(k)')
        legend('y(k)','r(k)','Location','best')

        subplot(4,2,3)
        plot(Tid(1:k), e(1:k), 'k')
        grid on; ylabel('e(k)'); title('Reguleringsavvik e(k)')

        subplot(4,2,4)
        plot(Tid(1:k), u_A(1:k), 'r'); hold on
        plot(Tid(1:k), u_B(1:k), 'b'); hold off
        grid on; ylabel('Pådrag'); title('Motorpådrag u_A(k) og u_B(k)')
        legend('u_A','u_B','Location','best')

        subplot(4,2,5)
        plot(Tid(1:k), IAE(1:k), 'b')
        grid on; ylabel('IAE'); title('Integral of Absolute Error')

        subplot(4,2,6)
        plot(Tid(1:k), TV_A(1:k), 'r'); hold on
        plot(Tid(1:k), TV_B(1:k), 'b'); hold off
        grid on; ylabel('TV'); title('Total Variation TV_A og TV_B')
        legend('TV_A','TV_B','Location','best')

        subplot(4,2,7)
        plot(Tid(1:k), MAE(1:k), 'm')
        grid on; ylabel('MAE'); xlabel('Tid [s]')
        title('Mean Absolute Error')

        subplot(4,2,8)
        plot(Tid(1:k), Ts(1:k), 'k')
        grid on; ylabel('T_s [s]'); xlabel('Tid [s]')
        title('Samplingstid T_{s,k}')

        drawnow
    end

end  % end while

%--------------------------------------------------------------------------
% 4) STOP MOTORS AND SAVE DATA
%--------------------------------------------------------------------------
if online
    motorA.Speed = 0;
    motorB.Speed = 0;
    save(filename, 'Tid','Lys','Gyro','JoyForover','JoySide')
end

%--------------------------------------------------------------------------
% 5) ADD LEGENDS TO FINAL FIGURE (required by project description §9.3)
%--------------------------------------------------------------------------
subplot(4,2,2)
legend('y(k)','r(k)','Location','best')
subplot(4,2,4)
legend('u_A(k)','u_B(k)','Location','best')
subplot(4,2,6)
legend('TV_A(k)','TV_B(k)','Location','best')

%--------------------------------------------------------------------------
% 6) PRINT FINAL SUMMARY VALUES  (for Table 9.1 in the report)
%--------------------------------------------------------------------------
fprintf('\n===== FINAL QUALITY METRICS (Table 9.1) =====\n')
fprintf('Reference r          : %.1f\n',  r(end))
fprintf('Mean y-bar           : %.3f\n',  y_mean(end))
fprintf('Std dev sigma        : %.3f\n',  sigma(end))
fprintf('IAE (final)          : %.3f\n',  IAE(end))
fprintf('MAE (final)          : %.3f\n',  MAE(end))
fprintf('TV_A (final)         : %.3f\n',  TV_A(end))
fprintf('TV_B (final)         : %.3f\n',  TV_B(end))
fprintf('Cost function J      : %.3f\n',  J(end))
fprintf('Mean Ts              : %.4f s\n',mean(Ts))
fprintf('Drive time           : %.1f s\n', Tid(end))
fprintf('Number of samples k  : %d\n',    k)
fprintf('=============================================\n')
