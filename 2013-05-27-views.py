#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tatoeba.utils.grepper import grep
from tatoeba.utils.examples import open_examples, open_audio, freq_by_lexeme, readline_backwards, humantime_to_seconds
from pyramid.view import view_config
from httpagentparser import detect as ua_detect
from os import path, SEEK_END
from pyramid.response import FileResponse, Response
from pyramid.httpexceptions import HTTPFound
import pickle
from prefixtree import PrefixDict
from pyramid.url import current_route_url
from urllib.parse import quote, unquote
from time import time
import sys
import math
from decimal import *
getcontext().prec = 10

prefix = sys.prefix+"/"

from itertools import tee

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

def threewise(iterable):
    "s -> (s0,s1,s2), (s1,s2,s3), (s2,s3,s4), ..."
    a, b, c = tee(iterable, 3)
    next(b, None)
    next(c, None)
    next(c, None)
    return zip(a, b, c)

kata = u'\
ァアィイゥウェエォオカガキギク\
グケゲコゴサザシジスズセゼソゾタ\
ダチヂッツヅテデトドナニヌネノハ\
バパヒビピフブプヘベペホボポマミ\
ムメモャヤュユョヨラリルレロヮワ\
ヰヱヲンヴヵヶ'
hira = u'\
ぁあぃいぅうぇえぉおかがきぎく\
ぐけげこごさざしじすずせぜそぞた\
だちぢっつづてでとどなにぬねのは\
ばぱひびぴふぶぷへべぺほぼぽまみ\
むめもゃやゅゆょよらりるれろゎわ\
ゐゑをんゔゕゖ'
symbols = u'ー＿。（！）、？・'

kata2hira = dict((ord(kata[n]), ord(hira[n])) for n in range(len(kata)))
hira2kata = dict((ord(hira[n]), ord(kata[n])) for n in range(len(hira)))

wclasses = {
('動詞',None,'','', '五段') : '5-vartaloinen verbi',
('動詞',None,'','','五段-ラ行特殊') : '5-vartaloinen keigo-taivutuksellinen verbi',
('動詞',None,'','','五段・カ行促音便') : '5-vartaloinen 行く-taivutuksellinen verbi',
('動詞',None,'','','五段・カ行促音便ユク') : '5-vartaloinen 行く-taivutuksellinen verbi',
('ある',None,'','','動詞','五段・ラ行', '') : '5-vartaloinen ある-taivutuksellinen verbi',
('在る',None,'','','動詞','五段・ラ行', '') : '5-vartaloinen ある-taivutuksellinen verbi',
('有る',None,'','','動詞','五段・ラ行', '') : '5-vartaloinen ある-taivutuksellinen verbi',
('動詞',None,'','','下一段') : '1-vartaloinen verbi',
('動詞',None,'','','上一段') : '1-vartaloinen verbi',
('動詞',None,'','','一段') : '1-vartaloinen verbi',
('動詞',None,'','','サ変') : 'する-verbi',
('動詞',None,'','','カ変') : 'epäsäännöllinen verbi',
('形容詞','形容詞') : 'い-adjektiivi',
('形状詞','一般') : 'な-adjektiivi',
('形状詞','タリ') : 'たる-adjektiivi',
('形容詞','不変化型') : 'いいn mukaan taipuva adjektiivi',
('形容詞','形容詞・イイ', '') : 'いいn mukaan taipuva adjektiivi',
('名詞','','助数詞') : 'laskusana',
('名詞','','地域') : 'paikannimi',
('名詞','', '副詞可能') : 'nomini/apusana',
('名詞','固有名詞','一般') : 'erisnimi',
('名詞','固有名詞','人名','一般') : 'henkilönnimi',
('名詞','固有名詞','人名','名') : 'etunimi',
('名詞','固有名詞','人名','姓') : 'sukunimi',
('名詞','固有名詞','地名','一般') : 'paikannimi',
('名詞','普通名詞','一般') : 'nomini',
('名詞','普通名詞','サ変可能') : 'nomini, する-verbi',
('名詞','普通名詞','助数詞可能') : 'nomini, laskusana',
('名詞','普通名詞','副詞可能') : 'nomini, apusana',
('名詞','数詞') : 'nomini, lukusana',
('接尾辞','名詞的','一般') : 'jälkiliite',
('接頭辞') : 'etuliite',
('副詞','') : 'apusana',
('代名詞') : 'pronomini',
('感動詞') : 'huudahdus',
('接頭詞') : 'etuliite',
('接続詞') : 'sidesana',
('記号') : 'merkki',
('助詞') : 'partikkeli',
('助詞','格助詞') : 'sijapartikkeli',
('助詞','終助詞') : 'häntäpartikkeli',
('助詞','係助詞') : 'sidospartikkeli',
('連体詞','') : 'määresana',
('感動詞', 'フィラー') : 'ölähdys',
('補助記号') : 'apu/äännemerkki',
('助動詞') : 'verbipääte/apuverbi',
('助詞','', '連語') : 'partikkelimainen fraasi',
('?') : '?',
}

def suomenna_lexeme(lex, extra):
	w = lex.split('::')
	extra = extra.split('::')
	selitys = wclasses.get((w[2], None, w[4], w[5], extra[0]))
	if not selitys:
		selitys = wclasses.get((w[2], None, w[4], w[5], extra[0].split('-')[0]))
	if not selitys:
		selitys = wclasses.get((w[2], w[3], w[4], w[5]))
	if not selitys:
		selitys = wclasses.get((w[2], w[3], w[4]))
	if not selitys:
		selitys = wclasses.get((w[2], w[3]))
	if not selitys:
		selitys = wclasses.get((w[2]))
	if not selitys:
		selitys = w[2]+w[4].split('・')[0]
	return {'sana': w[0], 'sanaluokka':w[2], 'taivutus':w[4], 'selitys':selitys}

try:
	ajastus_dict = pickle.load(open(prefix+'tatoeba/ajastukset.pickle', 'rb'))
except FileNotFoundError:
	ajastus_dict = {}

try:
	print('loading index from pickle', file=sys.stderr)
	lexeme_by_form = pickle.load(open(prefix+'tatoeba/lexemebyform.pickle', 'rb'))
except FileNotFoundError:
	print('building index (word_ep.txt)', file=sys.stderr)
	lexeme_by_form = {}
	for line in open(prefix+'tatoeba/corpus/words_ep.txt'):
		lexeme = line.strip('\n').split('\t')
		forms = lexeme[1].split('::')
		lemma = lexeme[0]
		freq = lexeme[4]
		lexeme_by_form[lemma] = freq
		for form in forms:
			l = lexeme_by_form.get(form)
			if not l:
				l = []
				lexeme_by_form[form] = l
			l.append(lexeme)
	print('index built. pickling it.', file=sys.stderr)
	pickle.dump(lexeme_by_form, open(prefix+'tatoeba/lexemebyform.pickle', 'wb'))
print('ready.', file=sys.stderr)


@view_config(route_name='home', renderer='basic.mak')
def home(request):
	start_time = time()
	global ajastus_dict
	defaults = {}
	static_path = path.join( 'docroot/static/')
	defaults['static_dir'] = request.static_url(static_path)
	try:
		defaults['ua'] = ua_detect(request.user_agent)
	except:
		defaults['ua'] = {'browser':{'name':None},'os':{'name':None}}
	search_term = request.GET.get('term')
	defaults['searchterm'] = search_term
	if search_term:
		word_list = lexeme_by_form.get(search_term, [])+lexeme_by_form.get(search_term.translate(hira2kata), [])
	else:
		word_list = []
	examples = {}
	termit = {}
	freq = {}
	result_lexemes = set()
	for line in word_list:
		lexeme = line[0]
		forms = line[1]
		extra_data = line[2]
		freq[lexeme] = int(line[4])
		example_pointers = line[5].split('::')
		result_lexemes.add(lexeme)
		examples[lexeme] = []
		termit[lexeme] = suomenna_lexeme(lexeme, extra_data)
		for ex in example_pointers[:30]:
			ex = ex.split(':')
			audio_exists = (ex[0] == 'a')
			ex_hardness = ex[1]
			ex_point = int(ex[2])
			try:
				examples[lexeme].append(open_examples(ex_point, ajastus_dict))
			except UnicodeDecodeError:
				print("Error with lexeme", lexeme)
				examples[lexeme].append(['', '', 'Error when loading examples!', '', False])
				continue
			examples[lexeme][-1][0].append(audio_exists)
			examples[lexeme][-1][0].append(ex_hardness)
	defaults['result_lexemes'] = sorted(result_lexemes, key=lambda l: freq[l], reverse=True)
	defaults['examples'] = examples
	defaults['terms'] = termit
	defaults['current_url'] = request.path_qs
	defaults['current_url_unquote'] = unquote(request.path_qs)
	end_time = time()
	defaults['elapsed'] = Decimal(end_time - start_time)
	return defaults

def jakson_alku(filename):
	path = prefix+'tatoeba/timed_text/'+filename.replace('..', '')+'.txt'
	line = open(path, 'r').readline().split('::')
	return (humantime_to_seconds( line[0] ), line[2])
	
def jakson_loppu(filename):
	path = prefix+'tatoeba/timed_text/'+filename.replace('..', '')+'.txt'
	f = open(path, 'rb')
	f.seek(0, SEEK_END)
	line = readline_backwards(f, '\n', 1024).split('::')
	return (humantime_to_seconds( line[0] ), line[2])

def aseta_paikka(text_pos, audio_pos, filename, ajatus_dict): # audio_position = original (wrong) text position
	filename = filename.replace('..', '')
	name = filename.split('/')[-1]
	serie_name = filename.split('/')[-2]
	serie = ajastus_dict.get(serie_name, {})
	ep_ajastukset = ajastus_dict.get(name, {})

	audio_displacement = audio_pos - text_pos		# audio displacement at text_pos
	ep_ajastukset[text_pos] = audio_displacement
	
	ajastus_dict[name] = ep_ajastukset
	serie[name] = ep_ajastukset
	ajastus_dict[serie_name] = serie	
	pickle.dump(ajastus_dict, open(prefix+'tatoeba/ajastukset.pickle', 'wb'))

def selvita_perusteet(filename, full_duration):
	text_start, firstline = jakson_alku(filename)
	text_end, lastline = jakson_loppu(filename)
	pass # Audion alkukohta, tekstin alkukohta, 1/3 jaksosta (tod. näk. tunnarin ja mainoskatkon välissä), 2/3 (tod. näk. mainoskatkon ja lopputunnarin välissä, 20 sekkaa audion lopusta)
	points = [0] + ( [text_start] if text_start > 20 else [] ) + [full_duration/3, full_duration*2/3, full_duration-15]
	return [(Decimal(p).quantize(Decimal('1.00')), None) for p in points]

def selvita_paikka(audio_start, text_start, audio_end, text_end, duration_start, points, filename, full_duration):
	audio_end = max(audio_end, audio_start+duration_start)
	text_end = max(text_end, text_start+duration_start)
	audio_start = audio_start + duration_start
	text_start = text_start + duration_start
	half = ((audio_start + audio_end) / 2).quantize(Decimal('1.00'))
	l_result, r_result = hae_lahin_repla(half, points, filename, audio_start+Decimal('1.00'), audio_end-Decimal('1.00'), full_duration)
	if l_result:
		left, l_audio, l_dur, l_text = l_result
		ll = (l_audio-Decimal('0.50'), l_text, Decimal('-1.50'), l_dur, left)
	else:
		ll = None
	if r_result:
		right, r_audio, r_dur, r_text = r_result
		rr = (r_audio-Decimal('0.50'), r_text, Decimal('-1.50'), r_dur, right)
	else:
		rr = None
	return [(audio_start, text_start), ['guess', (half, None), ll, rr], (audio_end, text_end)]

def binary_search(list, target, start=0):
	small = start
	large = len(list)
	while True:
		line_start = humantime_to_seconds(list[(small+large)//2][:8])
		if line_start <= target:
			small = math.ceil((small+large)/2)
		else:
			large = math.floor((small+large)/2)
		if small == large:
			start_line_no = small
			line_start = humantime_to_seconds(list[start_line_no][:8])
			return [line_start, start_line_no]

def line_to_seconds(line):
	return humantime_to_seconds(line[:8])
	
def line_duration(line):
	return humantime_to_seconds(line[10:18]) - humantime_to_seconds(line[:8])

def hae_lahin_repla(audio_target, points, filename, l_limit, r_limit, full_duration):
	for p in points:
		audio_point = p[0]
		text_point = p[2]
		if audio_point <= audio_target:
			l_audio_point = audio_point
			l_text_deviation = text_point - audio_point
			l_text_target = l_text_deviation + audio_target
		if audio_point >= audio_target:
			r_audio_point = audio_point
			r_text_deviation = text_point - audio_point
			r_text_target = r_text_deviation + audio_target
			break
	filename = prefix+'tatoeba/timed_text/'+filename.replace('..', '')+'.txt'
	f = open(filename, 'r').readlines()


	l_low_line, l_line_no = binary_search(f, l_text_target)
	l_high_line = line_to_seconds(f[l_line_no-1])
	high_line_deviation = l_text_target - l_high_line 	# hakuaikaleimaa edeltävän replan aikaero haettuun aikaan
	low_line_deviation = l_low_line - l_text_target		# hakuaikaleimaa jälkeen tulevat replan aikaero haettuun aikaan
	if high_line_deviation < low_line_deviation:
		left = l_line_no - 1
		l_line = l_high_line
	else:
		left = l_line_no
		l_line = l_low_line
	l_audio_start = l_line - l_text_deviation
	if l_audio_start < l_limit:
		left += 1
		print("vasen menee alueen ulkopuolelle (vasemmalle)?", l_audio_start, l_limit)
		l_line = line_to_seconds(f[left])
		l_audio_start = l_line - l_text_deviation
	l_dur = line_duration(f[left])
	if l_audio_start <= full_duration:
		l_result = (f[left].split('::')[2], l_audio_start, l_dur, l_line)
	else:
		l_result = None
	
	r_low_line, r_line_no = binary_search(f, r_text_target)
	r_high_line = line_to_seconds(f[r_line_no-1])
	high_line_deviation = r_text_target - r_high_line	# hakuaikaleimaa edeltävän replan aikaero haettuun aikaan
	low_line_deviation = r_low_line - r_text_target		# hakuaikaleimaa jälkeen tulevat replan aikaero haettuun aikaan
	if high_line_deviation < low_line_deviation:
		right = r_line_no - 1
		r_line = r_high_line
	else:
		right = r_line_no
		r_line = r_low_line
	r_audio_start = r_line - r_text_deviation
	if r_limit < r_audio_start:
		right -= 1
		print("oikee menee alueen ulkopuolelle (oikeelle)?", l_audio_start, l_limit)
		r_line = line_to_seconds(f[right])
		r_audio_start = r_line - r_text_deviation
	r_dur = line_duration(f[right])
	if 0 <= r_audio_start:
		r_result = (f[right].split('::')[2], r_audio_start, r_dur, r_line)
	else:
		r_result = None
	
	return [l_result, r_result]

def hae_tekstialue(audio_start, audio_end, points, filename):
	for p in points:
		audio = p[0]
		text = p[2]
		if audio <= audio_start:
			text_start = text-audio+audio_start
		if audio >= audio_end:
			text_end = text-audio+audio_end
			break
	filename = prefix+'tatoeba/timed_text/'+filename.replace('..', '')+'.txt'
	f = open(filename, 'r').readlines()
	line_start, start_line_no = binary_search(f, text_start)
	if line_start >= text_end:
		return []
	line_start, end_line_no = binary_search(f, text_end, start=start_line_no)
	return f[start_line_no:end_line_no]

@view_config(route_name='jakson_ajastus', renderer='ajastus.mak')
def ajastus_alg(request):
	filename = request.GET['f']
	global ajastus_dict
	points = request.GET.get('points')
	full_duration = open_audio(filename, 0, 0)[1]
	text_duration, lastline = jakson_loppu(filename)
	kysymys = ''
	kohdat = []
	if not points:
		kohdat.extend(selvita_perusteet(filename, full_duration))
	else:
		points = sorted([(Decimal(reg.split(':')[0]), Decimal(reg.split(':')[1]), Decimal(reg.split(':')[2])) for reg in points.split('::') if reg.split(':')[2]!='delete' ])
		print("POINTS")
		for r in points:
			print('audio:',r[0],'text:',r[2], 'diff:',(r[2]-r[0]))
		print('start\tdiff\tdifdif\tdiff\tend\tregion\tlines')
		for start, end in pairwise(points):
			audio_start, duration_start, text_start = start
			audio_end, poop, text_end = end
			tekstit = hae_tekstialue(audio_start+Decimal('0.50'), audio_end-Decimal('0.50'), points, filename)
			if len(tekstit) == 0:
				aseta_paikka(text_start, audio_start, filename, ajastus_dict)
				continue
			if text_end == -1:
				aseta_paikka(text_start, audio_start, filename, ajastus_dict)
				continue
			if text_start == -1:
				aseta_paikka(text_end, audio_end, filename, ajastus_dict)
				continue
			if text_end == -2:
				kohdat.extend([(audio_start, text_start), (audio_end-20, None)])
				continue
			if text_start == -2:
				kohdat.extend([(audio_start+20, None), (audio_end, text_end)])
				continue
			start_displacement = text_start - audio_start
			end_displacement = text_end - audio_end
			tarkenna = False
			if abs(start_displacement - end_displacement) > 3: # Jos alueen päät eroaa toisistaan
				kohdat.extend(selvita_paikka(audio_start, text_start, audio_end, text_end, duration_start, points, filename, full_duration))
				tarkenna = True
			print(str(audio_start) +"\t"+str(start_displacement)+ "\t"+str(end_displacement-start_displacement) +"\t" + str(end_displacement)+"\t"+ str(audio_end)+"\t"+str(audio_end-audio_start)+"\t"+("x" if not tarkenna else "")+"\t"+str(len(tekstit)))
	print("seuraavalle kierrokselle:")
	for k in kohdat:
		print(k)
	new_kohdat = []
	for mae, this, ato in threewise([[0]]+kohdat+[[full_duration]]):
		if this[0] == 'guess':
			audio = this[1][0]
			text = this[1][1]
			backward = max(-20, mae[0]-audio)
			forward = min(20, ato[0]-audio)
			this[1] = (audio, text, backward, forward)
			new_kohdat.append(this)
			continue
		audio = this[0]
		text = this[1]
		if text == None:
			backward = max(-20, mae[0]-audio)
		else:
			backward = None
		if text == None:
			forward = min(20, ato[0]-audio)
		else:
			forward = None
		new_kohdat.append([audio, text, backward, forward])
	print('ja seuraavin regiuunein:')
	for k in new_kohdat:
		print(k)
	return { 'kohdat' : new_kohdat, 'name' : filename, 'audio_duration': full_duration, 'text_duration': text_duration}
		
@view_config(route_name='kohdan_ajastus')
def ajastus(request):
	words = request.GET['w'].replace('"', '')
	filename = prefix+'tatoeba/timed_text/'+request.GET['f'].replace('..', '')+'.txt'
	checks = request.GET.get('checks')
	if not checks:
		out = grep(filename, words)
		resp = 'Mikä repliikin näistä kuulit? (Klikkaa ääniklipissä ekana kuuluvaa riviä, vaikka se kuuluisi vain osaksi.)<br><br>'
		contexts = out.split('--\n')
	else:
		out = grep(filename, words, '-C3')
		resp = "Mikä näistä?<br>"
		contexts = out.split('--\n')
	if len(contexts) == 1 and contexts[0] == '':
		resp = 'Sana "'+words+'" ei esiinny jaksossa!'
	else:
		zakos = False
		for con in contexts:
			con = con.strip()
			if con == '':
				continue
			lines = con.split('\n')
			if not checks:
				anchor = request.GET['a']
			for i, line in enumerate(lines):
				audio_start = Decimal(request.GET['s'])
				line = line.split("::")
				text_start = humantime_to_seconds(line[0])
				text_end = humantime_to_seconds(line[1])
				line_duration = text_end - text_start
				l = line[2]
				l = l.replace(words, '<strong>'+words+'</strong>')
				if not checks:
					if i < 3:
						resp += "<a href='tallenna_ajastus?f="+request.GET['f']+"&ts="+str(text_start)+"&as="+str(audio_start)+"&a="+anchor+"&ref="+request.GET['ref']+"'>"+l+"</a><br/>"
					else:
						resp += l+"<br/>"
				else:
					try:
						highest = Decimal(request.GET['highest'])
					except InvalidOperation:
						highest = 0
					if text_start < highest:
						zako_class = "zako"
						zakos = True
					else:
						zako_class = ""
					if i < 5:
						resp += "<p class='"+zako_class+"'><input type='radio' class='repla_select' name='"+str(audio_start).replace('.', '_')+"' data-name='"+str(audio_start)+"' value='"+str(text_start)+"' data-duration='"+str(line_duration)+"' id='repla_"+str(audio_start).replace('.', '_')+"_"+str(text_start)+"'><label style='display:inline-block' for='repla_"+str(audio_start).replace('.', '_')+"_"+str(text_start)+"'>"+line[0][3:]+" "+l+"</label></p>"
			resp += "<hr>"
		resp += "<p><input type='radio' class='repla_select' name='"+str(audio_start).replace('.', '_')+"' data-name='"+str(audio_start)+"' data-duration='0' value='delete' id='repla_"+str(audio_start).replace('.', '_')+"_delete'><label style='display:inline-block' for='repla_"+str(audio_start).replace('.', '_')+"_delete'>Ei sittenkään mikään.</label></p>"
		resp += "<button class='textbutton' style='display:" + ("block" if zakos else "none")+"'>Näytä piilotetut</button>"
	return Response(resp)

@view_config(route_name='tallenna_ajastus')
def audio_ajastus(request):
	global ajastus_dict
	filename = request.GET['f']
	text_start = Decimal(request.GET['ts'])
	audio_start = Decimal(request.GET['as']) + Decimal(request.GET.get('d', 0))
	aseta_paikka(text_start, audio_start, filename, ajastus_dict)
	return HTTPFound(location=quote(request.GET['ref']+"#"+request.GET['a'], '/=?&#'))

@view_config(route_name='listaa_ajastukset')
def ajastukset(request):
	global ajastus_dict
	resp = ''
	for key, value in sorted(ajastus_dict.items()):
		resp += key+" : "+str(value)+"<br>"
	return Response(resp)


@view_config(route_name='audio_dl')
@view_config(route_name='audio_kuuntele')
def audio(request):
	name = request.GET['f']
	start = Decimal(request.GET['s'])
	end = Decimal(request.GET['e'])
	end = min(start+60, end)
	try:
		filename, full_duration = open_audio(name, start, end)
		status_code = 200
	except Exception as e:
		print(str(e))
		filename = prefix + "tatoeba/tatoeba/docroot/static/error.mp4"
		status_code = 500
	resp =  FileResponse(filename, request=None, cache_max_age=None, content_type='audio/mp4', content_encoding=None)
	resp.status_code = status_code
	if request.matched_route.name == 'audio_dl':
		resp.content_disposition = 'attachment; filename="{0}.{1}.mp3"'.format(request.GET['f'].split('/')[-1].replace(' ', '_'), str(start))
	return resp