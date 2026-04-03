function [P, I_new, D, e_f_new] = MinPID(I_old, e_f_old, e, para)
% MINPID PID-regulator som anvender trapesmetoden, bakoverderivasjon og 
% første ordens lavpassfilter. Inkluderer integratorbegrensing. 
%
% Funksjonsargumenter inn:
%   - I_old:    forrige integralverdi I(k-1)
%   - e_f_old:  forrige filtrerte reguleringsavvik e_f(k-1)
%   - e:        de to siste reguleringsavvik e(k-1:k) 
%   - T_s:      tidsskritt  
%   - para:     parametervektor [Kp, Ki, Kd, I_max, I_min, tau_e]
%
% Returargumenter:
%   - P:        proporsjonaldel P(k)
%   - I_new:    integraldel I(k)
%   - D:        derivatdel D(k)
%   - e_f_new:  filtrert reguleringsavvik e_f(k)
%
% Syntaks for bruk av funksjonen:
%   -------------------------------
%   Ts = t(k) - t(k-1);             % tidsskritt
%   fc = ..;                        % ønsket knekkfrekvens
%   tau_e = ...;                    % ønsket tidskonstant filter
%   para = [Kp, Ki, Kd, I_max, I_min, tau_e, Ts];
%   [P(k),I(k),D(k),e_f(k)] = MinPID(I(k-1),e_f(k-1),e(k-1:k),para) 
%   u(k) = u0 + P(k) + I(k) + D(k);

% -------------------------------------------------------------
% Parametere
% -------------------------------------------------------------
Kp    = para(1);
Ki    = para(2);
Kd    = para(3);
I_max = para(4);
I_min = para(5);
Ts    = para(6);
tau_e = para(7);

% -------------------------------------------------------------
% Bidragene P, I og D
% -------------------------------------------------------------
P = 
I_new = 
e_f_new = 
D = 
    
% -------------------------------------------------------------
% Integratorbegrensing
% -------------------------------------------------------------
if I_new > I_max
    I_new = I_max;
elseif I_new < I_min
    I_new = I_min;
end


