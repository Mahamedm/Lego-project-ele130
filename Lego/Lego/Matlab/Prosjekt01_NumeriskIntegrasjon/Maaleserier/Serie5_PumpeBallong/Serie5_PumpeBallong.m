clear; close all
load('series5.mat')

q = Lys;

k0 = find(t >= 3,1);
t2 = t(k0:end);
t2 = t2 - t2(1);

q2 = q(k0:end);

uA = (max(q2) + min(q2))/2;
q2 = q2 - uA;
q2 = q2 - mean(q2);

V = TrapesIntegrasjon(t2,q2);

U = 21.495;
uA = 3.065;
T = 2.192;          
w = 2*pi/T;

q_teori = U*sin(w*(t2+0.1));
q_raw_teori = U*sin(w*t2) + uA;

V_teori = (U/w)*sin(w*t2 - pi/2);
V_teori = V_teori - mean(V_teori) + mean(V);

% Plot
figure
subplot(2,1,1)
plot(t2, q2, 'b')
hold on
plot(t2, q_teori, 'r--')
hold off
grid on
title('Vannstrøm q(t)')
legend('Målt','Teori')

subplot(2,1,2)
plot(t2, V, 'b')
hold on
plot(t2, V_teori, 'r--')
hold off
grid on
title('Ballongvolum V(t)')
xlabel('tid [s]')
legend('Numerisk integrert','Teori')