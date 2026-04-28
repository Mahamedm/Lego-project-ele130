% Måling av temperatur med termometer
clear; close all
load('filnavn.mat')
T = Lys; % temperatur i det kalde og varme vannet

% IIR low-pass filter
tau = 3.4;
Ts = 0.12;
tid = (0:length(T)-1) * Ts;
LavpassFilter(tid, T, tau=tau);
