function [varargout] = BakoverDerivasjon(tid, signal, opts)
% BAKOVERDERIVASJON Utfører numerisk derivasjon på et 
% signal basert på bakoverderivasjon og plotter resultatet. 
% Ved bruk av returverdi plottes ingenting.
%
% Innganger:
%    tid - tidsvektor
%    signal - signalet som skal numerisk deriveres
%    opts - valgfritt argument:
%         IC - initialverdi for den deriverte, default = 0
%
% Valgfri utgang:
%    derivert - den numerisk deriverte
%
% Syntaks:
%    BakoverDerivasjon(t, u, IC=...)
%    v = BakoverDerivasjon(t, u, IC=...)


arguments
    tid
    signal
    opts.IC double {mustBeScalarOrEmpty} = 0
end

% preallokerer plass i minne
derivert= zeros(1,length(tid));

derivert(1) = opts.IC;
for k = 2:length(tid)
    Ts = tid(k)-tid(k-1); 
    derivert(k) = (signal(k) - signal(k-1))/Ts;
end

if nargout == 1
    varargout{1} = derivert;
end

if nargout == 0
    figure
    set(gcf,'units','normalized',...
        'outerposition',[0.01 0.5 0.3 0.4],...
        'name','BakoverDerivasjon')
    subplot(2,1,1)
    plot(tid, signal, 'b-')
    grid on
    title('Signal $\{u_k\}$')

    subplot(2,1,2)
    plot(tid, derivert, 'b-')
    grid on
    title('Numerisk derivert $\{v_k\}$')
    xlabel('tid [s]')
end
