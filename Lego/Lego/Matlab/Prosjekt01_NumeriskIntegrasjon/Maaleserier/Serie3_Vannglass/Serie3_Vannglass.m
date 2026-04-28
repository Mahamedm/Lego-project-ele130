% Fylling og drikking av et vannglass
clear; close all
load("Serie3.mat")
q = Lys;      % påfylling/drikking [cl/s]


V = TrapesIntegrasjon(t, q);      % integrated volume [cl]

figure
subplot(2,1,1)
plot(t, q)
grid on
title('Flow q')

subplot(2,1,2)
plot(t, V)
grid on
title('Volume V')
xlabel('tid [s]')
