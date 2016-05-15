<%inherit file="layout.mak"/>
<section id="examples" style="padding-right: 8em;">
<h2>Ajastetaan ${name}</h2>
<p>Audion kesto: ${str(int(audio_duration)//60).zfill(2)}:${str(int(audio_duration)%60).zfill(2)}.
Tekstityksen kesto: ${str(text_duration//60).zfill(2)}:${str(int(text_duration)%60).zfill(2)}.${str( text_duration%6000)[-2:].zfill(2)}</p>

%if any([kohta[0] == "manual_search" for kohta in kohdat]):
<p>Ohje: kuuntele, mitä äänessä sanotaan. Etsi oikea repliikki haun avulla, ja valitse se. Lopuksi kohdista ääni niin että ääni on kelattuna löytämäsi repliikin alkuun.</p>

<p>Haku näyttää aina kullekin repliikille muutaman sen ympärillä olevan repliikin, joten voit päätellä niistäkin, löysitkö etsimäsi. Haku pitää hiraganaa, katakanaa ja kanjia eri asioina, joten voit joutua etsimään samalle sanalle eri kirjoitusasuja, löytääksesi oikean repliikin. :(</p>
%endif

%for kohta in kohdat:

%if kohta[0] == 'known':
${known_point(*kohta)}

%elif kohta[0] == 'manual_search':
<div style="margin-top: 1.5em">
${manual_search(*kohta)}
</div>

%elif kohta[0] == 'choose_audio':
${choose_audio(*kohta)}

%elif kohta[0] == 'eval_statements':
${eval_statements(*kohta)}

%endif
%endfor # kohta in kohdat:

<%def name="known_point(poop, audio, text)">
<input type="hidden" class="known_point" name="${str(audio).replace('.', '_')}" data-audio="${audio}" data-text="${text}" data-duration="0">
</%def>


<%def name="manual_search(poop, start, backward, forward)">
<% audio_id = str(start).replace('.', '_') %>
<p class="timer" data-time="${start}">00:00.00</p>
<audio src="/audio_kuuntele?f=${name}&s=${start+backward}&e=${start+forward}" preload="auto" style="width: 600px" id="audio_${str(start).replace('.','_')}" data-start="${start}" data-backward="${backward}" controls></audio>

<div style="display:inline-block; width: 250px; padding-left: 1em; vertical-align: middle;">
<input type="checkbox" class="empty_check" style="vertical-align: top; margin-left: 1em" data-start="${start}" name="${str(start).replace('.', '_')}" id="empty_${str(start).replace('.', '_')}"><label for ="empty_${str(start).replace('.', '_')}" style="vertical-align: top">Kohdassa ei oletettavasti kuulukaan olla vuorosanoja (esim. alku/loppubiisi jne.). </label>
<input type="checkbox" class="nothing_check" style="vertical-align: top; margin-left: 1em" data-start="${start}" name="${str(start).replace('.', '_')}" id="nothing_${str(start).replace('.', '_')}"><label for ="nothing_${str(start).replace('.', '_')}" style="vertical-align: top">Ääneen ei sattunut osumaan vuorosanoja!</label>
</div>

<form action="kohdan_ajastus" class="ajastus">
<input name="f" value="${name}" type="hidden">
<input name="as" value="${start}" type="hidden">
<input name="min" value="0" type="hidden">
<input name="min2" value="0" type="hidden">
<input name="checks" value="True" type="hidden">
<input name="w" type="text">
<button type="submit"><img src="static/hae.png"></button>
</form>
<div class="results">
</div>
</%def>


<%def name="choose_audio(poop, line, text_tstamp, duration, l_audio_tstamp, r_audio_tstamp, manual)">
<% text_id = str(text_tstamp).replace('.', '_') %>
<% l_audio_id = str(l_audio_tstamp).replace('.', '_') %>
<% r_audio_id = str(r_audio_tstamp).replace('.', '_') %>
<% half_audio_id = str(manual[1]).replace('.', '_') %>
<div style="display:inline-block; width: 400px; vertical-align: middle">
<h4>Kumpi äänistä vastaa tekstiä paremmin?</h4>
<p style="font-size: 1.5em;">${line}</p>

<p>
<input type='radio' class='choice_select' name='${text_id}' data-text="${text_tstamp}" data-audio="${l_audio_tstamp}" data-duration='${duration}'  id="choice_${l_audio_id}" style="vertical-align: top" data-manual="${half_audio_id}">
<label style="font-size: 1.5em; vertical-align: top;"  for="choice_${l_audio_id}">
<audio src="/audio_kuuntele?f=${name}&s=${l_audio_tstamp-Decimal('1.5')}&e=${l_audio_tstamp+duration+Decimal('0.5')}" preload="auto" style="width: 300px; di" id="audio_${str(l_audio_id).replace('.','_')}" data-audio="${l_audio_tstamp}" data-backward="0" controls></audio>
</label>
</p>

<p>
<input type='radio' class='choice_select' name='${text_id}' data-text="${text_tstamp}" data-audio="${r_audio_tstamp}" data-duration='${duration}'  id="choice_${r_audio_id}" style="vertical-align: top" data-manual="${half_audio_id}">
<label style="font-size: 1.5em; vertical-align: top;"  for="choice_${r_audio_id}">
<audio src="/audio_kuuntele?f=${name}&s=${r_audio_tstamp-Decimal('1.5')}&e=${r_audio_tstamp+duration+Decimal('0.5')}" preload="auto" style="width: 300px; di" id="audio_${str(r_audio_id).replace('.','_')}" data-audio="${r_audio_tstamp}" data-backward="0" controls></audio>
</label>
</p>

<p>
<input type='radio' class='choice_select choice_manual' name='${text_id}' data-manual="${half_audio_id}" style="vertical-align: top" id="choice_${half_audio_id}">
<label for="choice_${half_audio_id}">Kumpikaan ei vastaa lainkaan.</label>
</p>
</div>
<div style="display:inline-block; vertical-align: middle">
<input type="checkbox" class="unclear_check" style="vertical-align: top; margin-left: 1em" data-text="${text_tstamp}" name="${text_id}" id="ready_${text_id}">
<label for="ready_${text_id}" style="vertical-align: top">Epäoleellinen/epäselvä repliikki!</label>
</div>
<div style="margin-top: 1.5em; display: none" id='manual_${half_audio_id}'>
${manual_search(*manual)}
</div>
</%def>


<%def name="eval_statements(poop, l_statement, r_statement, manual)">
<% half_audio_id = str(manual[1]).replace('.', '_') %>
<div>
<h4>Onko nämä ajastettu suunnilleen oikein?</h4>

%for line, audio_tstamp, duration, text_tstamp in [s for s in[l_statement, r_statement] if s != None]:
<% audio_id = str(audio_tstamp).replace('.', '_') %>
<p>
<input type='checkbox' class='choice_select' name="${audio_id}" data-text="${text_tstamp}" data-audio="${audio_tstamp}" data-duration='${duration}'  id="check_${audio_id}" style="vertical-align: top" data-manual="${half_audio_id}">
<label style="font-size: 1.5em; vertical-align: top;"  for="check_${audio_id}">
<audio src="/audio_kuuntele?f=${name}&s=${audio_tstamp-Decimal('1.5')}&e=${audio_tstamp+duration+Decimal('0.5')}" preload="auto" style="width: 300px; display: inline-block;" id="audio_${audio_id}" data-audio="${audio_tstamp}" data-backward="0" controls></audio>
= ${line}
</label>
<input type="checkbox" class="ready_check" style="vertical-align: top; display: inline-block; margin-left: 1em" data-audio="${audio_tstamp}" data-text="${text_tstamp}" data-duration="${duration}" name="${audio_id}" id="ready_${audio_id}">
<label for="ready_${audio_id}" style="vertical-align: top">Epäoleellinen/epäselvä repliikki!</label>
</p>
%endfor

<p>
<input type='checkbox' class='choice_select choice_manual' data-manual='${half_audio_id}' style="vertical-align: top" id="choice_${half_audio_id}">
<label for="choice_${half_audio_id}">Mikään ei ollut oikein.</label>
</p>
</div>

<div style="margin-top: 1.5em; display: none" id='manual_${half_audio_id}'>
${manual_search(*manual)}
</div>
</%def>


<%def name="choose_statements()">
<h4>Mikä näistä pitää paikkansa?</h4>
<% guess_name = str(value[0]).replace('.', '_') %>
<div>
% if backward:
<% start, v, b, f, repla = backward %>
<input type='radio' class='guess_select' data-name='${guess_name}' name='${guess_name}' data-start="${start}" value='${v}' data-duration='${f-1}'  id="guess_${start}"  style="vertical-align: top">
<label style="font-size: 1.5em; vertical-align: top;"  for="guess_${start}">
<audio src="/audio_kuuntele?f=${name}&s=${start+b}&e=${start+f}" preload="auto" style="width: 300px; di" id="audio_${str(start).replace('.','_')}" data-start="${start}" data-backward="${b}" controls></audio>
= ${repla}</label><br>
% endif
% if forward:
<% start, v, b, f, repla = forward %>
<input type='radio' class='guess_select' data-name='${guess_name}' name='${guess_name}' data-start="${start}" value='${v}' data-duration='${f-1}' id="guess_${start}" style="vertical-align: top">
<label style="font-size: 1.5em; vertical-align: top;"  for="guess_${start}">
<audio src="/audio_kuuntele?f=${name}&s=${start+b}&e=${start+f}" preload="auto" style="width: 300px; di" id="audio_${str(start).replace('.','_')}" data-start="${start}" data-backward="${b}" controls></audio>
= ${repla}</label><br>
% endif
<% start, v, b, f = value %>
<input type='radio' class='guess_select guess_ajastus' data-start="${start}" data-name='${guess_name}' name='${guess_name}' id="guess_${start}" value='' data-duration='' style="vertical-align: top">
<label for="guess_${start}">Ei mikään.</label>
</%def>

%if len(kohdat) == 0:
<h3>AJASTETTU!</h3>
%else:
<form class="master_form" action="jakson_ajastus">
<h3>Ajasta <button type="submit"><img src="static/ok.png"></button></h3>
<input type="text" id="master_input" name="points" style="width: 900px">
<input name="f" value="${name}" type="hidden">
</form>
%endif
</section>
<%block name="domloaded">
<script>

var master = {};
var tuples = [];
var highest;

function update_master() {
	var values = [];
	$(".known_point").each(function(){
		values.push($(this).attr("data-audio")+":"+$(this).attr("data-duration")+":"+$(this).attr("data-text"))
	});
	
	$(".choice_select").each(function(){
		if ($(this).is(":checked") && $(this).is(":not(.choice_manual)")) {
		delete master[$(this).attr("data-manual")];
		values.push($(this).attr("data-audio")+":"+$(this).attr("data-duration")+":"+$(this).attr("data-text"))
		}
	});
	
	$.each(master, function(key, vals) {
		if ( vals["nothing"] || vals["unclear"]) {
			var audio_pos = parseFloat(vals["audio_pos"]);
		} else {
		var audio = $("#"+vals["audio_element_id"]);
		var audio_pos = (parseFloat(vals["audio_pos"]) + audio[0].currentTime + parseFloat(vals["backward"])).toFixed(2);
		}
		values.push(audio_pos+":"+vals["duration"]+":"+ vals["text_pos"]);
	});
	$("#master_input").val(values.join('::'));
}

function repla() {
	var others = $(this).parent().siblings(":not(.zako)");
	others.hide();
	$(this).parent().prev().show();
	$(this).parent().next().show();
	var button = $(this).parent().parent().find('button');
	var audio =  $(this).parent().parent().siblings("audio");
	var backward = audio.attr("data-backward")
	button.show();
	button.click(function(){others.show();$(this).hide();});
	if ($(this).val() =='delete') {
	delete master[$(this).attr("name")];
	}
	else {
	master[$(this).attr("name")] = {"audio_element_id":audio.attr("id"),"audio_pos":$(this).attr("data-name"), "text_pos":$(this).val(), "duration":$(this).attr("data-duration"), "backward":backward};
	}
tuples = [];
for (var kee in master) tuples.push([parseFloat(master[kee]["audio_pos"]), parseFloat(master[kee]["text_pos"])]);
tuples.sort(function(a,b){return b[0]-a[0]});
highest = tuples[0];
console.log(highest);
update_master();
}

function after_results() {
$(".repla_select").click(repla);
}


$(function(){

$("audio").on("canplay canplaythrough", function(){
var back = parseFloat($(this).attr("data-backward"))
this.currentTime = -back;
});
$("audio").on("timeupdate", function(){
var time = this.currentTime + parseFloat($(this).attr("data-start")) + parseFloat($(this).attr("data-backward"))
var minutes = ((time-(time%60))/60);
var seconds = (time%60).toFixed(2);
minutes = ((minutes < 10) ? "0" + minutes : ""+minutes);
seconds = ((seconds < 10) ? "0" + seconds : ""+seconds);
var timer = $(this).parent().find(".timer");
timer.html(minutes+":"+seconds);
update_master();
});



$(".ajastus").submit(function() {
var that = $(this);
var results = that.parent().find('.results');
f = that.find('[name="f"]');
as = parseFloat(that.find("[name='as']").val());
w = that.find('[name="w"]');


if( highest &&　as > highest[0] ){
var min = highest[1];
var min2 = as + highest[1] - highest[0]-30.0;
} else {
var min = 0; var min2 = 0;
};
console.log(as);
console.log(min2);
results.load('kohdan_ajastus?f='+f.val()+'&as='+as+'&w='+w.val()+'&checks=True&min='+min+'&min2='+min2, after_results);
return false;
});

$(".ready_check").change(function() {
var audio =  $("#audio_"+$(this).attr("name"));
var backward = audio.attr("data-backward");
if ($(this).is(':checked')){
$("#check_"+$(this).attr("name")).prop('checked', false);
$(".repla_select[name="+$(this).attr("name")+"]").prop('checked', false);
master[$(this).attr("name")] = {"audio_element_id":audio.attr("id"),"audio_pos":$(this).attr("data-audio"), "text_pos":$(this).attr("data-text"), "duration":$(this).attr("data-duration"), "backward":backward};

}else{
delete master[$(this).attr("name")];
}
update_master();
});

$(".nothing_check").change(function() {
var audio =  $("#audio_"+$(this).attr("name"));
console.log(audio);
var backward = audio.attr("data-backward");
if ($(this).is(':checked')){
audio[0].currentTime = -parseFloat(audio.attr("data-backward"));
audio[0].pause();
console.log(parseFloat(audio.attr("data-backward")));
$(".repla_select[name="+$(this).attr("name")+"]").prop('checked', false);
master[$(this).attr("name")] = {"nothing":1,"audio_pos":$(this).attr("data-start"), "text_pos":"-2", "duration":"0", "backward":backward};
}else{
delete master[$(this).attr("name")];
}
update_master();
});


$(".unclear_check").change(function() {
var audio =  $("#audio_"+$(this).attr("name"));
var backward = audio.attr("data-backward");
if ($(this).is(':checked')){
$(".repla_select[name="+$(this).attr("name")+"]").prop('checked', false);
master[$(this).attr("name")] = {"unclear":1,"audio_pos":"0", "text_pos":$(this).attr("data-text"), "duration":"-1", "backward":backward};

}else{
delete master[$(this).attr("name")];
}
update_master();
});

$(".choice_select").change(function() {
if ( $(this).is(":checked")) {
$("#ready_"+$(this).attr("name")).prop('checked', false);
delete master[$(this).attr("name")];
}
if ( $(this).hasClass('choice_manual') && $(this).is(":checked")) {
$("#manual_"+$(this).attr("data-manual")).show();
}else{
$("#manual_"+$(this).attr("data-manual")).hide();
}
update_master();
});

});
</script>
</%block>
