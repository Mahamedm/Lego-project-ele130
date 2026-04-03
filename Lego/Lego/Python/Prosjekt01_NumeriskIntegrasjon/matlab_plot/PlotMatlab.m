%% Matlabfil for plotting av data fra Python-prosjekt
clear all
close all

%% Navn: datafil (offline eller online)
% Du kan laste inn flere .txt-filer og sammenligne.
% Bruk i så fall filename1, filename2 og data1, data2
filename = 'P00_matplotlib.txt';
data = ParseData(filename);


%% Legg inn verdiene dine (punktum notasjon med 'data')
figure(1)
set(0,'defaultTextInterpreter','latex');
set(0,'defaultAxesFontSize',14)
set(gcf,'Position',[100 200 800 700])

subplot(2,2,1);
plot(data.Tid,data.Lys,'r--o','LineWidth',1)
grid on
hold on
title('Reflektert lys')
xlabel('Tid [sek]')
ylabel('Lys')
% axis([XMIN XMAX YMIN YMAX])


subplot(2,2,2);
plot(data.Tid,data.u,'g','Marker','.','LineWidth',1)
grid on
hold on
title('Signalene $u(k)$, $y_1(k)$ og $y_2(k)$')
xlabel('Tid [sek]')
plot(data.Tid,data.y1,'r:','LineWidth',1)
plot(data.Tid,data.y1,'b--','LineWidth',1)
legend('$u$','$y_1$','$y_2$','interpreter','latex')
%axis([XMIN XMAX YMIN YMAX])



subplot(2,2,3);
plot(data.Tid,data.PowerA,'b','LineWidth',1)
grid on
title('Beregning av motorp{\aa}drag')
xlabel('Tid [sek]')
ylabel('[\%]')
% axis([XMIN XMAX YMIN YMAX])

subplot(2,2,4);
plot(data.Tid,data.Ts,'b--','LineWidth',1)
grid on
title('Tidsskritt $T_s$')
xlabel('Tid [sek]')
ylabel('[sek]')
% axis([XMIN XMAX YMIN YMAX])

