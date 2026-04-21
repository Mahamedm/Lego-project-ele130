% Pumpe vann (med luftbobler) inn og ut av ballong som en sinus-strømning
clear; close all
load('Serie6_SinusStoy_u20.mat')
q = Lys;       % volumstrøm inn og ut av ballong [cl/s]
t_s = t;

FrekvensSpekter(t_s, q);
fs = 2 * 2.35;
fc = 1.2;
[B, A] = butter(2, fc / (fs/2), 'low');
filtered = IIRfilter(t_s, q, B, A);


figure;
plot(t_s, q, 'b');
hold on;
plot(t_s, filtered, 'r', 'LineWidth', 2);
legend('Original', 'Filtered');
xlabel('Tid [s]');
ylabel('Volumstrøm [cl/s]');
title('Filtrert signal');
