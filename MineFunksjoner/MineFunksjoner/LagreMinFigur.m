function [] = LagreMinFigur(fig_handle,figurfilnavn)
%LAGREMINFIGUR  Lagrer .fig og .pdf av gjeldende figur.
%
% Hvis du har flere vindu oppe, husk å først
% klikke i det figurvinduet du vil lagre.
%
% Syntaks
%    LagreMinFigur(gcf,'figurfilnavn')
%
% See also savefig, print

% Setter enhetene til punkter midlertidig
set(fig_handle,'units','points')

% Ved lagring til vektorgrafikk pdf
% må figurstørrelsen settes. 
fig_handle.PaperPositionMode = 'auto';
figure_pos = fig_handle.PaperPosition;
fig_handle.PaperSize = [figure_pos(3) figure_pos(4)];

% Lagrer 2 figurtyper, en *.fig slik at du kan 
% endre på figuren senere, og en *.pdf for rapport
figurename_1 = [figurfilnavn,'.fig'];
figurename_2 = [figurfilnavn,'.pdf'];

if ~exist(figurename_2)
    savefig(figurename_1)
    print('-dpdf','-vector','-bestfit',figurename_2)
else
    TekstStreng = ['Filen ''',figurename_2,...
        ''' finnes fra før. Overskrive?'];
    svar=questdlg(TekstStreng,'Advarsel','Ja','Nei','Nei');
    switch svar
        case 'Ja'
        savefig(figurename_1)
        print('-dpdf','-vector','-bestfit',figurename_2)
        case 'Nei'
            return
    end
end



