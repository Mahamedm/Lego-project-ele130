% Filtrering av pixelstripe fra bilde av Lena
clear; close all
load('Serie2.mat')
u = Lys;  % intensitetsprofilen i bilde

% Lag tidsvektor (piksel-indeks som "tid")
t = (1:length(u))';

% Filtrer med ulike tau-verdier
tau1 = 2;       % enkelt filter
tau2 = 0.67;    % tre filtre i serie (samme total effekt)

% Enkelt filter
y1 = LavpassFilter(t, u, tau=tau1);

% Tre filtre i serie
y2 = LavpassFilter(t, u, tau=tau2);
y2 = LavpassFilter(t, y2, tau=tau2);
y2 = LavpassFilter(t, y2, tau=tau2);

% Plot
figure
plot(t, u, 'b-');
hold on
plot(t, y1, 'r-');
plot(t, y2, 'g-');
hold off
grid on
legend('Råsignal', ['1 filter, \tau=', num2str(tau1)], ['3 filtre i serie, \tau=', num2str(tau2)])
title('Filtrering av intensitetsprofil')
xlabel('Piksel')
ylabel('Intensitet')