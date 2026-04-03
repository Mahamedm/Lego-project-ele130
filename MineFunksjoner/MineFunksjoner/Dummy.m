function [varargout] = Dummy(tid, signal, opts)
% DUMMY Utfører følgende beregning:
%  
%   verdi = signal.^a.*tid + C
%
% hvor defaultverdien av eksponenten er a=2, og konstanten er C=0.
%
% Innganger:
%    tid - tidsvektor
%    signal - signalet som det skal gjøres beregninger ut fra
%    opts - valgfrie argument:
%         C - konstant. Hvis utelatt: C=0
%         a - eksponenten i ligningen. Hvis utelatt: a=2
%
% Valgfri utgang:
%    verdi - de beregnde verdiene 
%
% Syntaks: 
%    Dummy(t, x)
%    Dummy(t, x, C=.., a=..)
%    y = Dummy(t, x, C=.., a=..)
%
% See also: .^

arguments
    tid
    signal
    opts.C double {mustBeScalarOrEmpty} = 0
    opts.a double {mustBeScalarOrEmpty} = 2
end

% preallokerer plass i minne
verdi = zeros(1,length(tid));

% beregner verdien
verdi = signal.^opts.a.*tid + opts.C;

if nargout == 1
    varargout{1} = verdi;
elseif nargout == 0
    figure
    set(gcf,'units','normalized','outerposition',[0.01 0.5 0.3 0.4])
    plot(tid, signal, 'b-')
    grid on
    hold on
    plot(tid, verdi, 'r-')
    title('Signal $\{u_k\}$ og beregning $\{y_k\}$')
    legend('$\{u_k\}$',['$\{y_k\}$, C=',num2str(opts.C),...
        ', eksponent =',num2str(opts.a)])
    xlabel('tid [s]')
end
