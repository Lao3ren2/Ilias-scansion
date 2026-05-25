
--------------------digbib aufbereitung------------------
Digbib_Odyssee.pdf und Digbib_Ilias.pdf sind von digbib.org heruntergeladen.
Diese habe ich dann mit pdftotext zu txts gemacht, dann manuell die anfänglichen Zeilen und kapitelzusammenfassungen entfernt, 
die Kapitelangaben zu Zahlen gemacht und ein paar Verse, die in eine Zeile geraten waren, wieder getrennt.
------------------
In der Ilias waren das:

Was an Gut die liebliche Stadt inwendig verschließet: Aber warum bewegte das Herz mir solche Gedanken?

405 Ihm antwortete Priamos drauf, der göttliche Herrscher:

In der Odyssee:

Welche du Trotziger jetzo hegst, da du immer die Stadt durch-
Irrst, indes die Herde von bösen Hirten verderbt wird!
------------------
Außerdem in der Ilias hab ich geändert:
Priamos, Dardalios Enkel, an Rat den Unsterblichen ähnlich;
zu
Priamos, Dardanos Enkel, an Rat den Unsterblichen ähnlich;

Um den erhabenen Idomeneus her, und den mutigen Nestor
zu
Um den erhabnen Idomeneus her, und den mutigen Nestor

Eilten sie freudiges Mutes auf die Danaer, hoffend, nicht obstehn
zu
Eilten sie freudiges Muts auf die Danaer, hoffend, nicht obstehn

Doch in dem Besiegeten stellt' er ein blühendes Weib in den Kampfkreis,
zu
Doch dem Besiegeten stellt' er ein blühendes Weib in den Kampfkreis,

so ist es in der textgrid xml, und sonst sind es zuviele Silben
----------------------------textgrid aufbereitung---------------
In Textgrid_Ilias.xml habe ich geändert:
<l rend="zenoPLm0n4" xml:id="tg8.2.25">ene nunmehr blieb schweigend und redete nichts, Athenäa,</l>
zu
<l rend="zenoPLm0n4" xml:id="tg8.2.25">Jene nunmehr blieb schweigend und redete nichts, Athenäa,</l>

<l rend="zenoPLm0n4" xml:id="tg15.2.541">Dichtes Gewühl, zu zerstreuen, wo er stürmete! Grauses Getümmel</l>
zu
<l rend="zenoPLm0n4" xml:id="tg15.2.541">Dichtes Gewühl, zu zerstreun, wo er stürmete! Grauses Getümmel</l>
(So ist es in digbib und sonst ist eine silbe zuviel)
 und
<l rend="zenoPLm0n4" xml:id="tg27.2.531">Aber Meriones dr auf, Idomeneus' tapferer Kriegsfreund,</l>
zu
<l rend="zenoPLm0n4" xml:id="tg27.2.531">Aber Meriones drauf, Idomeneus' tapferer Kriegsfreund,</l>
--------
der parser xml_parser.py ist von claude gevibecodet, das ergebnis sieht korrekt aus.

