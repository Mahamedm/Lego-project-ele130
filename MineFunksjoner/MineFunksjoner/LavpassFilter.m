function [varargout] = LavpassFilter(tid, signal, opts)
% LAVPASSFILTER Utfører første ordens lavpassfiltrering 
% på et signal og plotter resultatet. 
% Ved bruk av returverdi plottes ingenting.
%
% Innganger:
%    tid - tidsvektor
%    signal - signalet som skal lavpassfiltreres
%    opts - valgfritt argument:
%         IC - initialverdi for den filtrerte, default = 0
%         tau - ønsket tidskonstant for filteret
%         fc - ønsket knekkfrekvens for filteret
%
% Valgfri utgang:
%    filtrert - det lavpassfiltrerte signalet
%
% Syntaks: 
%    LavpassFilter(t, u, IC=..., tau=.../fc=...)
%    y = LavpassFilter(t, u, IC=..., tau=.../fc=...)


arguments
    tid
    signal
    opts.IC double {mustBeScalarOrEmpty} = 0
    opts.tau double {mustBeScalarOrEmpty} = []
    opts.fc double {mustBeScalarOrEmpty} = []
end

% Sjekker at enten tau eller fc er spesifisert
if isempty(opts.tau) & isempty(opts.fc)
    error('--> Du må enten spesifisere ønsket tau eller ønsket fc')
elseif ~isempty(opts.tau) & ~isempty(opts.fc)
    error('--> Du kan ikke spesifisere både ønsket tau og ønsket fc')
end

% Filterspesifikasjoner
if ~isempty(opts.fc)
    tau = 1/(2*pi*opts.fc);          % Beregner først tau ut fra valgt fc
elseif ~isempty(opts.tau)
    tau = opts.tau;
end

%betta = exp(-Ts/tau);       % Parameter for første ordens høypassfilter

% preallokerer plass i minne
filtrert= zeros(1,length(tid));

filtrert(1) = opts.IC;
for k = 2:length(tid)
    Ts = tid(k) - tid(k-1);                   % Beregner tidsskritt
    alfa = 1 - exp(-Ts/tau);    % Parameter for første ordens lavpassfilter
    filtrert(k) = (1-alfa)*filtrert(k-1) + alfa*signal(k);
end

if nargout == 1
    varargout{1} = filtrert;
end

if nargout == 0
    figure
    set(gcf,'units','normalized',...
        'outerposition',[0.01 0.25 0.3 0.65], ...
        'name','LavpassFilter')

    subplot(3,1,1)
    plot(tid, signal, 'b-')
    grid on
    title('Signal $\{u_k\}$')

    % Lager litt luft i y-retning
    xl = xlim(gca);        % husk x-limits
    axis padded;           % legger padding på begge akser
    xlim(xl);              % gjenopprett x-limits, bare y beholdes paddet
    yl = ylim(gca);        % husk x-limits

    subplot(3,1,2)
    plot(tid, filtrert, 'r-')
    grid on
    title('Lavpassfiltrert signal $\{y_k\}$')
    ylim(yl);              
    
    subplot(3,1,3)
    plot(tid, signal, 'b-')
    grid on
    hold on
    plot(tid, filtrert, 'r-')
    title('Signal $\{u_k\}$ og lavpassfiltrert signal $\{y_k\}$')
    xlabel('tid [s]')
    ylim(yl);              
    
end
