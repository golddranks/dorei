<%inherit file="layout.mak"/>
<section id="examples" style="padding-right: 8em;">
<h2>Ajastetaan ${name}</h2>
Audion kesto: ${str(int(audio_duration)//60).zfill(2)}:${str(int(audio_duration)%60).zfill(2)}.
Viimeinen repliikki tekstin mukaan: ${str(text_duration//60).zfill(2)}:${str(int(text_duration)%60).zfill(2)}.${str(text_duration%6000)[-2:].zfill(2)}<br><br>
<p>Ohje: kuuntele, mitä äänessä sanotaan. Etsi oikea repliikki haun avulla, ja valitse se. Lopuksi kohdista ääni niin että ääni on kelattuna löytämäsi repliikin alkuun.</p><br><p>Haku näyttää aina kullekin repliikille muutaman sen ympärillä olevan repliikin, joten voit päätellä niistäkin, löysitkö etsimäsi. Haku pitää hiraganaa, katakanaa ja kanjia eri asioina, joten voit joutua etsimään samalle sanalle eri kirjoitusasuja, löytääksesi oikean repliikin. :<</p><br>
%for start, value, backward, forward in kohdat:
%if not value and start !='guess':
<div>
<p class="timer" data-time="${start}">00:00</p>
<audio src="/audio_kuuntele?f=${name}&s=${start+backward}&e=${start+forward}" preload="auto" style="width: 600px" id="audio_${str(start).replace('.','_')}" data-start="${start}" data-backward="${backward}" controls></audio>
<div style="display:inline-block; width: 250px; padding-left: 1em">
<input type="checkbox" class="ready_check" style="vertical-align: top; margin-left: 1em" data-start="${start}" name="${str(start).replace('.', '_')}" id="ready_${str(start).replace('.', '_')}"><label for="ready_${str(start).replace('.', '_')}" style="vertical-align: top">Ei tarvitse kohdistaa!</label><br>
<input type="checkbox" class="nothing_check" style="vertical-align: top; margin-left: 1em" data-start="${start}" name="${str(start).replace('.', '_')}" id="nothing_${str(start).replace('.', '_')}"><label for ="nothing_${str(start).replace('.', '_')}" style="vertical-align: top">Ei vuorosanoja!</label>
</div>
<form action="kohdan_ajastus" class="ajastus">
<input name="f" value="${name}" type="hidden">
<input name="s" value="${start}" type="hidden">
<input name="checks" value="True" type="hidden">
<input name="w" type="text">
<button type="submit"><img src="static/hae.png"></button>
</form>
<div class="results">
</div>
</div>
<br>
%elif start == 'guess':
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
<div style="display: none" id='ajastushaku_${guess_name}'>
<p class="timer" data-time="${start}">00:00</p>
<audio src="/audio_kuuntele?f=${name}&s=${start+b}&e=${start+f}" preload="auto" style="width: 600px" id="audio_${str(start).replace('.','_')}" data-start="${start}" data-backward="${b}" controls></audio>
<div style="display:inline-block; width: 250px; padding-left: 1em">
<input type="checkbox" class="ready_check" style="vertical-align: top; margin-left: 1em" data-start="${start}" name="${str(start).replace('.', '_')}" id="ready_${str(start).replace('.', '_')}"><label for="ready_${str(start).replace('.', '_')}" style="vertical-align: top">Ei tarvitse kohdistaa!</label><br>
<input type="checkbox" class="nothing_check" style="vertical-align: top; margin-left: 1em" data-start="${start}" name="${str(start).replace('.', '_')}" id="nothing_${str(start).replace('.', '_')}"><label for ="nothing_${str(start).replace('.', '_')}" style="vertical-align: top">Ei vuorosanoja!</label>
</div>
<form action="kohdan_ajastus" class="ajastus">
<input name="f" value="${name}" type="hidden">
<input name="s" value="${start}" type="hidden">
<input name="checks" value="True" type="hidden">
<input name="w" type="text">
<button type="submit"><img src="static/hae.png"></button>
</form>
<div class="results">
</div></div>
</div>
%elif value:
<input type="hidden" class="hidden_region" name="${str(start).replace('.', '_')}" data-name="${start}" value="${value}" data-duration="0">
%endif
%endfor # e in kohdat
%if len(kohdat) == 0:
<h3>AJASTETTU!</h3>
%else:
<form class="master_form" action="jakson_ajastus">
<h3>Ajasta <button type="submit"><img src="static/ok.png"></button></h3>
<input type="text" id="master_input" name="points" style="width: 700px">
<input name="f" value="${name}" type="hidden">
</form>
%endif
</section>
<%block name="domloaded">
<script>

var master = {};

function update_master() {
	var values = [];
	$(".hidden_region").each(function(){
		values.push($(this).attr("data-name")+":"+$(this).attr("data-duration")+":"+$(this).val())
	});
	$(".guess_select").each(function(){
		if ($(this).is(":checked") && $(this).is(":not(.guess_ajastus)")) {
		delete master[$(this).attr("data-name")];
		values.push($(this).attr("data-start")+":"+$(this).attr("data-duration")+":"+$(this).val())
		}
	});
	$.each(master, function(key, vals) {
		var audio = $("#"+vals["audio_id"]);
		if ( vals["nothing"]) { var audio_displacement = parseFloat(vals["start"]);}
		else {
		var audio_displacement = (parseFloat(vals["start"]) + audio[0].currentTime + parseFloat(vals["backward"])).toFixed(2); }
		values.push(audio_displacement+":"+vals["duration"]+":"+ vals["text_pos"]);
	});
	$("#master_input").val(values.join('::'));
}

function repla() {
	var others = $(this).parent().siblings();
	others.hide();
	$(this).parent().prev().show();
	$(this).parent().next().show();
	var button = $(this).parent().parent().find('button');
	var audio =  $(this).parent().parent().siblings("audio");
	var backward = audio.attr("data-backward")
	button.show();
	button.click(function(){others.show();$(this).hide();});
	master[$(this).attr("name")] = {"audio_id":audio.attr("id"),"start":$(this).attr("data-name"), "text_pos":$(this).val(), "duration":$(this).attr("data-duration"), "backward":backward};
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
s = that.find('[name="s"]');
w = that.find('[name="w"]');

var tuples = [];
for (var kee in master) tuples.push(master[kee]["text_pos"]);
tuples.sort();
var highest = tuples[tuples.length-1];
console.log(tuples);
console.log(highest);
results.load('kohdan_ajastus?f='+f.val()+'&s='+s.val()+'&w='+w.val()+'&checks=True&highest='+highest, after_results);
return false;
});

$(".ready_check").change(function() {
var audio =  $(this).parent().siblings("audio");
var backward = audio.attr("data-backward")
if ($(this).is(':checked')){
$(".repla_select[name="+$(this).attr("name")+"]").prop('checked', false);
master[$(this).attr("name")] = {"audio_id":audio.attr("id"),"start":$(this).attr("data-start"), "text_pos":"-1", "duration":"0", "backward":backward};

}else{
delete master[$(this).attr("name")];
}
update_master();
});

$(".nothing_check").change(function() {
var audio =  $(this).parent().siblings("audio");
var backward = audio.attr("data-backward")
if ($(this).is(':checked')){
audio[0].currentTime = -parseFloat(audio.attr("data-backward"));
console.log(parseFloat(audio.attr("data-backward")));
$(".repla_select[name="+$(this).attr("name")+"]").prop('checked', false);
master[$(this).attr("name")] = {"nothing":1,"audio_id":audio.attr("id"),"start":$(this).attr("data-start"), "text_pos":"-2", "duration":"0", "backward":backward};
}else{
delete master[$(this).attr("name")];
}
update_master();
});

$(".guess_select").change(function() {
if ( $(this).hasClass('guess_ajastus')) {
$("#ajastushaku_"+$(this).attr("data-name")).show();
}

update_master();
});

});
</script>
</%block>
