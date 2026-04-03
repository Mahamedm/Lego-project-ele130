function [varargout] = HoypassFilter(tid, signal, opts)
% HOYPASSFILTER Utfører første ordens høypassfiltrering 
% på et signal og plotter resultatet. 
% Ved bruk av returverdi plottes ingenting.
%
% Innganger:
%    tid - tidsvektor
%    signal - signalet som skal høypassfiltreres
%    opts - valgfritt argument:
%         IC - initialverdi for den filtrerte, default = 0
%         tau - ønsket tidskonstant for filteret
%         fc - ønsket knekkfrekvens for filteret
%
% Valgfri utgang:
%    filtrert - det høypassfiltrerte signalet
%
% Syntaks:
%    HoypassFilter(t, u, IC=..., tau=.../fc=...)
%    y = HoypassFilter(t, u, IC=..., tau=.../fc=...)


arguments
    tid
    signal
    opts.IC double {mustBeScalarOrEmpty} = 0
    opts.tau double {mustBeScalarOrEmpty} = []
    opts.fc double {mustBeScalarOrEmpty} = []
end

% Sjekker at enten tau eller fc er spesifisert
if isempty(opts.tau) & isempty(opts.fc)
    error('Du må enten spesifisere ønsket tau eller ønsket fc')
elseif ~isempty(opts.tau) & ~isempty(opts.fc)
    error('Du kan ikke spesifisere både ønsket tau og ønsket fc')
end

% Filterspesifikasjoner
if ~isempty(opts.fc)
    tau = 1/(2*pi*opts.fc);          % Beregner først tau ut fra valgt fc
elseif ~isempty(opts.tau)
    tau = opts.tau;
end


% preallokerer plass i minne
filtrert= zeros(1,length(tid));

filtrert(1) = opts.IC;
for k = 2:length(tid)
    Ts = tid(k) - tid(k-1);                   % Beregner tidsskritt
    betta = exp(-Ts/tau);       % Parameter for første ordens høypassfilter
    filtrert(k) = betta*filtrert(k-1) + betta*(signal(k)-signal(k-1));
end

if nargout == 1
    varargout{1} = filtrert;
end

if nargout == 0
    figure
    set(gcf,'units','normalized',...
        'outerposition',[0.01 0.5 0.3 0.4],...
        'name','HoypassFilter'))

    subplot(3,1,1)
    plot(tid, signal, 'b-')
    grid on
    title('Signal $\{u_k\}$')

    % Lager litt luft i y-retning
    xl = xlim(gca);        % husk x-limits
    axis padded;           % legger padding på begge akser
    xlim(xl);              % gjenopprett x-limits, bare y beholdes paddet

    subplot(3,1,2)
    plot(tid, filtrert, 'r-')
    grid on
    title('H{\o}ypassfiltrert signal $\{y_k\}$')

    subplot(3,1,3)
    plot(tid, signal, 'b-')
    grid on
    hold on
    plot(tid, filtrert, 'r-')
    title('Signal $\{u_k\}$ og h{\o}ypassfiltrert signal $\{y_k\}$')
    xlabel('tid [s]')
end
