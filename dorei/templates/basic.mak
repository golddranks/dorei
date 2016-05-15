<%inherit file="layout.mak"/>
<nav>
<header>
<h1 style="font-family: 'Tauri', sans-serif; font-size: 2.5em"><span style="font-size: 0.85em">ど</span>例。<span style="font-size: 0.85em">DO</span>REI。</h1>
</header>
${elapsed} sekuntia.
<form action="/" method="get">
<input type="text" name="term" placeholder="${searchterm if searchterm else 'sana perusmuodossaan'}"/>
<button type="submit"><img src="static/hae.png"></button>
</form>
% if searchterm:
<h2>Löytyi:</h2>
% endif
<ol>
% for lexeme in result_lexemes:
<li><a href="#${lexeme}" style="font-weight: bold">${terms[lexeme]['sana']} (${terms[lexeme]['selitys']})</a></li>
% endfor
</ol>
<div class="disclaimer" style="border: 2px dotted #090; width: 80%; margin-bottom: 1em; margin-top: 1em; padding-bottom: 1em; padding-left: 0.5em; padding-right: 0.3em">
<h3>Disclaimer:</h3>
Sivusto on testivaiheessa!
<ul style="list-style-type: disc; list-style-position: inside">
<li>Ominaisuudet ovat vielä puutteellisia (ideoita ja parannus- ja korjausehdoituksia otetaan vastaan!)</li>
<li>Automaattisesti luoduissa furiganoissa on virheitä.</li>
<li>Automaattisesti päätellyt sanavälit saattavat olla väärin.</li>
<li>Teksti ja ääni saattavat olla epäsynkassa.</li>
<li>Firefox ja IE testaamatta.</li>
</ul>
</div>
</nav>
<section id="examples">
% for lexeme in result_lexemes:
<% ex = examples[lexeme] %>
<a name="${lexeme}"></a>
<h2>Esimerkkilauseet – ${terms[lexeme]['sana']} (${terms[lexeme]['selitys']})</h2>

<ul>
%for ii, e in enumerate(ex):
<%
filename = e[0][0]
audio_exists = e[0][1]
hardness = e[0][2]
firstline =  e[1] if e[1] else e[2]
lastline =  e[3] if e[3] else e[2]

name = filename.split('/')[0].replace('_', ' ')
epnro = filename.split('_')[-1]
text = ''
timestr = firstline.start
displacement = firstline.displacement

time = ((timestr[0]+':') if timestr[0] != '00' else '') + timestr[1] + ':' + timestr[2]
if time[0] == '0':
	time = time[1:]
%>
<li>
<a name="${lexeme}::${ii}"></a>
<h3>${name}, jakso ${epnro}, kohta ${time}<button class="amend_ep_name textbutton" style="display: none">Väärä nimi?</button></h3>
<button class="amend_japanese textbutton" style="display: none">Jotain muuta kieltä kuin japania?</button>
<div style='display:table; margin-bottom: 1em' class='lines'>
<% ankitext = name+", jakso "+epnro+", kohta "+time+"\n" %>
%for line in e[1:]:
%if line:
<p style='display:table-row'>
<span style='display:table-cell; white-space: nowrap' class='speaker'>${line.speaker}</span>
<% ankitext += line.speaker+'　' %>
<span style='display:table-cell'>
% for word in line:
<% kanji, furigana, mukaigana, okurigana = word.hatsuon()
mainword = " mainword" if word.lexeme == lexeme else ""%>\
%if furigana != '':
<% runningword = (mukaigana+" "+kanji+ "["+furigana+"]"+okurigana) if mainword == "" else str(word) %>\
<span class='rword${mainword}' >${mukaigana}<ruby>${kanji}<rt>${furigana}</rt>${okurigana}</ruby></span>\
%else:
<% runningword = str(word) %>\
<span class='rword${mainword}'>${runningword}</span>\
%endif
<% ankitext += runningword if mainword == "" else "<b>"+runningword+"</b>" %>\
%endfor # word in line
<% ankitext += '\n' %>\
</span>
<button class="amend_furigana textbutton" style="display: none">Furigana väärin?</button>
<button class="amend_kireme textbutton" style="display: none">Sana jaettu väärin?</button>
</p>
%endif
%endfor # line in e
</div>
<div class="ankitext" style='display:none; margin-bottom: 1em;font-size: 1.6em; border: 1px solid black;'>
${ankitext.strip().replace('\n', '<br>\n')| n}</div>
<div class="controls">
%if audio_exists:
<div class="audio_amend" style="display: none">
<button class="amend_serifu textbutton">Äänessä on aivan eri repliikit kuin tekstissä?</button><br>
<button class="amend_momeru textbutton">Ääni on alkaa myöhässä tai katkeaa kesken?</button><br>
<a href="jakson_ajastus?f=${filename}" class="episode_sync textbutton">Ajasta jakso!</a><br>
</div>
<div style="display:none; margin: 0.5em" class="adjustform">
Säädä liukusäätimellä:<br>
<div style="display: flex; display: -webkit-flex; justify-content: space-between; -webkit-justify-content: space-between; width: 30em; margin: 0;">
<span>alusta puuttuu osa</span><span>lopusta puuttuu osa</span>
</div>
<div style="display: flex; display: -webkit-flex; justify-content: space-between; -webkit-justify-content: space-between; width: 29em; margin: 0.5em;" class='sliderlabel'>
<span>10 s</span><span>5 s</span><span>0</span><span>5 s</span><span>10 s</span>
</div>
<form action="tallenna_ajastus" method="get">
<input name="ref" value="${current_url_unquote}" type="hidden">
<input name="f" value="${filename}" type="hidden">
<input name="a" value="${lexeme}" type="hidden">
<input name="ts" value="${firstline.text_start_seconds}" type="hidden">
<input name="as" value="${firstline.start_seconds}" type="hidden">
<input id="range01" type="range" min="-10" max="10" style="width: 30em" name="d"/>
<button type="submit"><img src="static/ok.png"></button>
</form>
</div>
<div style="display:none; margin: 0.5em" class="amendform">
Jos ääni ja teksti eivät synkkaa, kirjoita tähän jokin sana, joka äänessä kuuluu:<br>
<form action="kohdan_ajastus" class="ajastus">
<input name="f" value="${filename}" type="hidden">
<input name="s" value="${firstline.start_seconds}" type="hidden">
<input name="w" type="text">
<button type="submit"><img src="static/ok.png"></button>
</form>
<div class="amend_results">
</div>
</div>
<audio src="/audio_kuuntele?f=${filename}&s=${firstline.start_seconds}&e=${lastline.end_seconds}" preload="none" controls></audio>
<a href="/audio_dl?f=${filename}&s=${firstline.start_seconds}&e=${lastline.end_seconds}"><img src="static/dl.png"></a>

%endif # http://dabuttonfactory.com/b.png?t=ANKI&f=DejaVuSansCondensed-Bold&ts=21&tc=ffffff&it=png&c=5&bgt=gradient&bgc=666666&ebgc=333333&hp=21&vp=7
<button class="ankify"><img src="static/anki.png"></button>
<button class="normify" style="display:none"><img src="static/x.png"></button>
<button class="amendbutton"><img src="static/virhe2.png"></button>
<button class="cancelamendbutton" style="display:none"><img src="static/x.png"></button>
</div>
</li>
%endfor # e in ex
</ul>
%endfor # word_struct in items
</section>
<%block name="domloaded">
<script>
function normify(listitem, controls){
listitem.children(".ankitext").hide();
listitem.children(".lines").show();
controls.children(".ankify").show();
controls.children(".normify").hide();
}
function cancelamend(listitem, controls){
controls.children(".amendbutton").show();
controls.children(".cancelamendbutton").hide();
listitem.find(".amend_ep_name").hide();
listitem.find(".amend_japanese").hide();
listitem.find(".amend_furigana").hide();
listitem.find(".amend_kireme").hide();
listitem.find(".audio_amend").hide();
}

$(function(){
$(".ankify").click(function() {
var controls = $(this).parent();
var listitem = controls.parent();
listitem.children(".ankitext").show();
listitem.children(".lines").hide();
controls.children(".ankify").hide();
controls.children(".normify").show();
cancelamend(listitem, controls);
});
$(".normify").click(function() {
var controls = $(this).parent();
var listitem = controls.parent();
normify(listitem, controls);
});
$(".amendbutton").click(function() {
var controls = $(this).parent();
var listitem = controls.parent();
controls.children(".amendbutton").hide();
controls.children(".cancelamendbutton").show();
normify(listitem, controls);
listitem.find(".amend_ep_name").show();
listitem.find(".amend_japanese").show();
listitem.find(".amend_furigana").show();
listitem.find(".amend_kireme").show();
listitem.find(".audio_amend").show();
});
$(".cancelamendbutton").click(function() {
var controls = $(this).parent();
var listitem = controls.parent();
cancelamend(listitem, controls);
});
$(".amend_serifu").click(function() {
var listitem = $(this).closest('li');
var controls = listitem.children(".controls");
listitem.find(".amendform").show();
cancelamend(listitem, controls);
});
$(".amend_momeru").click(function() {
var listitem = $(this).closest('li');
var controls = listitem.children(".controls");
listitem.find(".adjustform").show();
cancelamend(listitem, controls);
});
$(".ajastus").submit(function() {
var listitem = $(this).closest('li');
var amendform = listitem.find("div.amendform");
var amendresults = amendform.find("div.amend_results");
f = amendform.find('[name=f]');
s = amendform.find('[name=s]');
w = amendform.find('[name=w]');
a = listitem.find('a').attr('name');
amendresults.load('kohdan_ajastus?f='+f.val()+'&s='+s.val()+'&w='+w.val()+'&a='+a+'&ref=${current_url}');
return false;
});
});
</script>
</%block>
