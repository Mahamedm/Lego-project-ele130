function [varargout] = FrekvensSpekter(tid, signal, opts)
% FREKVENSSPEKTER Beregner og plotter frekvenspekteret 
% til et signal basert på fft-funksjonen. 
% Ved bruk av returverdi plottes ingenting.
%
% Innganger:
%     tid - tidsvektoren til signalet
%     signal - signalet som det beregnes frekvensspekter av
%     opts - valgfrie argument:
%          title - tekst som vises i tittel, default = '$\{u_k\}$'    
%          fmax - største frekvens [Hz] på x-aksen, default = fN
%          fc - vise valgt knekkfrekvensen fc [Hz]
%          draw - for å velge 'stem' som plottefunksjon
%
% Valgfrie utganger:
%     varargout = [frekvensene, spekteret]
%
% Syntaks: 
%    FrekvensSpekter(t, u, title=..., fc=..., fmax=...)
%    [frekvensene, spekteret] = FrekvensSpekter(t, u)
%
% See also: fft

arguments
    tid
    signal
    opts.title string = '$\{u_k\}$'
    opts.fmax double {mustBeScalarOrEmpty, mustBePositive} = []
    opts.fc double {mustBePositive} = []
    opts.draw string = []
end

if max(isnan(tid)) | max(isnan(signal))
    error('--> Argumentene inneholder elementer med NaN')
end    

% Sjekker om fc (hvis spesifisert) er mindre enn fmax (hvis spesifisert)
if ~isempty(opts.fc) && ~isempty(opts.fmax) && max(opts.fc) > opts.fmax
        error('--> Du må kan ikke spesifisere f_c > f_max')
end

Ts = mean(diff(tid));   % samplingstid [s]
fs = 1/Ts;              % samplingsfrekvens [Hz]
fN = fs/2;              % Nyquistfrekvensen [Hz]

% Hvis bruker ikke oppga fmax, bruk fN som fmax
if isempty(opts.fmax)
    fmax = fN;
else
    fmax = opts.fmax;
end

N = numel(signal);  % Lengden av signalet
      
% Fouriertransformasjon
X = fft(signal,N)/N; 

% Frekvenser langs x-aksen for plotting fra 0 til fN (Nyquistfrekvensen).
% Lengde på frekvensvektoren er halvparten av N siden
% vi skal bare plotte halvparten av frekvensspekteret.
frekvenser = fN*linspace(0,1,round(N/2)); 

% Frekvenskomponentene i X er komplekse størrelser, og vi skal
% plotte kun lengden (amplituden) på disse. Bruker derfor abs().
spekteret = abs(X(1:round(N/2)));

% Vi multipliser spekteret i de positive frekvensene med 2. 
% Vi trenger ikke multiplisere amplitude(1) og amplitude(end) 
% med 2 fordi disse amplitudene tilsvarer henholdsvis 
% null- og Nyquistfrekvensene, og de har ikke kompleks
% konjugerte par i negative frekvenser.
spekteret(2:end-1) = 2*spekteret(2:end-1);

if nargout == 2
       varargout{1} = frekvenser;
       varargout{2} = spekteret;
end

if nargout == 0
    figure;
    set(gcf,'units','normalized',...
        'outerposition',[0.01 0.5 0.3 0.4],...
        'name','FrekvenSpekter')
    subplot(2,1,1)
    plot(tid,signal)
    grid
    title(opts.title)
    xlabel('tid [s]')
    legend(sprintf(['$T_s =$ ',sprintf('%0.2g',Ts),...
        ' sek \n$f_s =$ ',sprintf('%0.3g',fs),' Hz']))

    % Lager litt luft i y-retning
    xl = xlim(gca);        % husk x-limits
    axis padded;           % legger padding på begge akser
    xlim(xl);              % gjenopprett x-limits, bare y beholdes paddet

    
    % Plotter halvparten av fourierspekteret.
    subplot(2,1,2)
    if isempty(opts.draw)
        plot(frekvenser,spekteret)
    elseif strcmp(opts.draw,'stem')
        stem(frekvenser,spekteret,'b','linewidth',1)
    else
        errordlg('Du kan kun velge draw=''stem'' som valgfritt argument')
    end        
    grid
    title('Frekvensspekteret')
    legend(sprintf(['$f_N =$ ',sprintf('%0.3g',fN),' Hz']));
    xlabel('frekvenser [Hz] i signalet')
    ylabel('amplitude')
    xlim([0 fmax])

    % Begrenser x-aksen dersom fmax er spesifisert
    if ~isempty(opts.fmax)
        ticks = xticks;              % Hent nåværende ticks
        labels = string(ticks);      % konvertere til tekst
        labels(end) = ['$f_{max}=$ ', num2str(fmax)];
        xticklabels(labels)          % Sett de nye labelene
    end

    % Tegner inn loddrett rød strek dersom fc er spesifisert 
    if ~isempty(opts.fc)
        if ~isempty(opts.fmax) && max(opts.fc) > opts.fmax
            errordlg('Knekkfrekvensen vises ikke siden f_c > f_max')
            return
        end
        if isscalar(opts.fc)
            xline(opts.fc,'r--','LineWidth',2,...
                'DisplayName',['$f_c=$',num2str(opts.fc),' Hz'])
        else
            xline(opts.fc,'r--','LineWidth',2,...
                'DisplayName','$f_{c}$')            
        end
    end
end

