function [varargout] = IIRfilter(tid, signal, B, A, opts)
% IIRFILTER Generelt IIR-filter som filtrerer og som kan lage
% en figur med 5 delfigurer med signal- og filterinformasjon.
% 
% Figuren er strukturet med:
%  - to delfigurer til venstre som viser
%    inngangssignalet {u_k} med tilhørede frekvensspekter
%  - en delfigur i midten som viser
%    amplitudeforsterkningen A=Y/U til filteret
%  - to delfigurer til venstre som viser det filtrerte
%    utgangssignal {y_k} med tilhørende frekvensspekter
%
% Argumenter:
%     tid - tidsvektoren {t_k}
%     signal - signalet som skal filtreres
%     B - filterparametere, [b0 b1 b2 ..]
%     A - filterparametere, [ 1 a1 a2 ..]
%     opts - valgfritt argument:
%         IC - initialverdi for den filtrerte, default = 0
%         fmax - største frekvens på x-aksen
%         fc - vise valgt knekkfrekvens som ble brukt i
%              beregningen av parametervektorene B og A
%
% Valgfri utgang:
%     filtrert - det filtrerte signalet
%
% Syntaks:
%     IIRfilter(t, u, B, A, IC=..., fmax=..., fc=...)
%     y = IIRfilter(t, u, B, A, IC=...)
%
% See also: FrekvensSpekter, freqz,

arguments
    tid
    signal
    B
    A
    opts.IC double {mustBeScalarOrEmpty} = 0
    opts.fmax double {mustBeScalarOrEmpty, mustBePositive} = []
    opts.fc double {mustBeScalarOrEmpty, mustBePositive} = []
end

% Sjekker om fc (hvis spesifisert) er mindre enn fmax (hvis spesifisert)
if ~isempty(opts.fc) && ~isempty(opts.fmax) && max(opts.fc) > opts.fmax
        error('--> Du må kan ikke spesifisere f_c > f_max')
end

%----------------------------------------------------------
% Utfører først filtrering basert på B og A
M = numel(B);
N = numel(A)-1;        % teller ikke med a0

% Sørger for at signalet som skal filtreres
% blir en liggende vektor.
if size(signal,1) > size(signal,2)
    signal = signal'; % transponerer
end

filtrert(1) = opts.IC;
for k = 2:length(tid)
    if length(signal(1:k)) < M || length(filtrert) < N
        filtrert(k) = opts.IC;   % foretar ikke filtrering før nok u eller y
    else
        U = signal(k:-1:k-M+1);         % snur hele signal-vektoren
        Y = filtrert(end:-1:end-N+1);   % snur hele filtrert-vektoren
        filtrert(k) = - Y*A(2:end)' + U*B';
    end
end

if nargout == 1
    varargout{1} = filtrert;
elseif nargout == 0

    Ts = mean(diff(tid));
    fs = 1/Ts;
    fN = fs/2;

    % Hvis bruker ikke oppga fmax, bruk fN
    if isempty(opts.fmax)
        fmax = fN;
    else
        fmax = opts.fmax;
    end

    figure
    set(gcf,'units','normalized',...
        'outerposition',[0.35 0.17 0.6 0.6],...
        'name','IIRfilter')

    % ------------------------------------------------------
    % subplot(2,3,1)
    % ------------------------------------------------------
    % inngangssignalet {u_k} plottet som funksjon av tid
    subplot(2,3,1)
    plot(tid, signal)
    grid
    title('Inngangssignal $\{u_k\}$')
    xlabel('tid [s]')
    legend(sprintf(['$T_s =$ ',sprintf('%0.2g',Ts),...
        ' sek \n$f_s =$ ',sprintf('%0.3g',fs),' Hz']))
    axis_u = axis;
    axis(axis_u);
    ylim_u = ylim;   % tar vare på y-aksegrenser til bruk for {y_k}



    % ------------------------------------------------------
    % subplot(2,3,3)
    % ------------------------------------------------------
    % det filtrert signalet {y_k} plottet som funksjon av tid
    subplot(2,3,3)
    plot(tid, filtrert)
    grid
    title('Utgangssignal $\{y_k\}$')
    xlabel('tid [s]')
    
    % ------------------------------------------------------
    % subplot(2,3,4)
    % ------------------------------------------------------
    % frekvensspekteret til inngangssignalet {u_k}
    subplot(2,3,4)
    [frekvenser_inn, spekter_inn] = FrekvensSpekter(tid, signal);
    plot(frekvenser_inn, spekter_inn)
    grid
    title('Frekvensspekteret til $\{u_k\}$')
    xlabel('frekvenser [Hz] i inngangssignalet')
    ylabel('amplituder $U$')
    ax_inn_spekter = axis;
    axis(ax_inn_spekter)
    hold on
    legend(sprintf(['$f_N =$ ',sprintf('%0.3g',fN),' Hz']),...
        'location','best')

    % Tegner inn loddrett rød strek dersom fc er spesifisert
    if ~isempty(opts.fc)
        xline(opts.fc,'r--','LineWidth',2,...
            'DisplayName',['$f_c=$',num2str(opts.fc),' Hz'])
    end

    xlim([0 fmax])
    if ~isempty(opts.fmax)
        ticks = xticks;              % Hent nåværende ticks
        labels = string(ticks);      % konvertere til tekst
        labels(end) = ['$f_{max}=$ ', num2str(fmax)];
        xticklabels(labels)          % Sett de nye labelene
    end

    % ------------------------------------------------------
    % subplot(2,3,X)
    % ------------------------------------------------------
    % Frekvensresponsen (kun amplitudeforsterkningen)
    % til filteret med de valgte koeffisientene A og B
    subplot(4,3,[5,8])
    numOfFreq = 1000;
    [amplitude,frekvenser]=freqz(B,A,numOfFreq,fs);
    plot(frekvenser,abs(amplitude))       % lineær x-akse
    grid
    title('Filterets amplitudeforsterkning $A(f)$','fra {\tt freqz}-funksjonen')
    ylabel('$A = \frac{Y}{U}$')
    ax_freqz = axis;
    axis(ax_freqz)
    hold on
    legend('$A(f)$')
    % Tegner inn loddrett rød strek dersom fc er spesifisert
    if ~isempty(opts.fc)
        xline(opts.fc,'r--','LineWidth',2,...
            'DisplayName',['$f_c=$',num2str(opts.fc),' Hz'])
    end

    xlabel('frekvens [Hz]')
    xl = xlim;
    xlim([xl(1) fmax])
    if ~isempty(opts.fmax)
        ticks = xticks;              % Hent nåværende ticks
        labels = string(ticks);      % konvertere til tekst
        labels(end) = ['$f_{max}=$ ', num2str(fmax)];
        xticklabels(labels)          % Sett de nye labelene
    end

    % ------------------------------------------------------
    % subplot(2,3,6)
    % ------------------------------------------------------
    % frekvensspekteret til utgangssignal y
    subplot(2,3,6)
    [frekvenser_ut, spekter_ut] = FrekvensSpekter(tid, filtrert);
    plot(frekvenser_ut, spekter_ut)
    grid
    title('Frekvensspekteret til $\{y_k\}$')
    xlabel('frekvenser [Hz] i utgangssignalet')
    ylabel('amplituder $Y$')
    axis(ax_inn_spekter);
    hold on
    xlim([0 fmax])

    if ~isempty(opts.fmax)
        ticks = xticks;              % Hent nåværende ticks
        labels = string(ticks);      % konvertere til tekst
        labels(end) = ['$f_{max}=$ ', num2str(fmax)];
        xticklabels(labels)          % Sett de nye labelene
    end
end
