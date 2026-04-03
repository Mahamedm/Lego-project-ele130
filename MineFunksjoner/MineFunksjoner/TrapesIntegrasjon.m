function [varargout] = TrapesIntegrasjon(tid, signal, opts)
% TRAPESINTEGRASJON Utfører numerisk integrasjon på et 
% signal basert på trapesmetoden og plotter resultatet. 
% Ved bruk av returverdi plottes ingenting.
%
% Innganger:
%    tid - tidsvektor
%    signal - signalet som skal numerisk integreres
%    opts - valgfritt argument:
%         IC - initialverdi for integralet, default = 0
%
% Valgfri utgang:
%    integral - den numerisk integrerte
%
% Syntaks:
%    TrapesIntegrasjon(t, u, IC=...)
%    y = TrapesIntegrasjon(t, u, IC=....)
%

arguments
    tid
    signal
    opts.IC double {mustBeScalarOrEmpty} = 0
end

% preallokerer plass i minne
integral = zeros(1,length(tid));

integral(1) = opts.IC;
for k = 2:length(tid)
    Ts = tid(k)-tid(k-1); 
    integral(k) = integral(k-1) + Ts*(0.5*signal(k-1)+0.5*signal(k));
end

if nargout == 1
    varargout{1} = integral;
end

if nargout == 0
    figure
    set(gcf,'units','normalized',...
        'outerposition',[0.01 0.5 0.3 0.4],...
        'name','TrapesIntegrasjon')
    subplot(2,1,1)
    plot(tid, signal, 'b-')
    grid on
    title('Signal $\{u_k\}$')
    % Lager litt luft i y-retning
    xl = xlim(gca);        % husk x-limits
    axis padded;           % legger padding på begge akser
    xlim(xl);              % gjenopprett x-limits, bare y beholdes paddet

    subplot(2,1,2)
    plot(tid, integral, 'b-')
    grid on
    title('Numerisk integrert $\{y_k\}$')
    xlabel('tid [s]')

    % Lager litt luft i y-retning
    xl = xlim(gca);        % husk x-limits
    axis padded;           % legger padding på begge akser
    xlim(xl);              % gjenopprett x-limits, bare y beholdes paddet
end
