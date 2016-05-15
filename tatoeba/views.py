#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tatoeba.utils.grepper import grep
from tatoeba.utils.examples import open_examples, open_audio, freq_by_lexeme, readline_backwards, humantime_to_seconds
from tatoeba.ajastus import ajastus_alg, get_ajastus, get_ajastus_reverse

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
from decimal import *

prefix = sys.prefix+"/"

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



try: # TODO: tsekkaa, jos words_ep.txt on muuttunut. Jos on, pickle on vanhentunut.
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
	ajastus_dict = get_ajastus()
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

@view_config(route_name='jakson_ajastus', renderer='ajastus.mak')
def jakson_ajastus(request):
	filename = request.GET['f']
	points = request.GET.get('points')
	return ajastus_alg(filename, points)
	
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
				audio_start = Decimal(request.GET['as'])
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
						minimize = Decimal(request.GET['min'])
						minimize2 = Decimal(request.GET['min2'])
					except InvalidOperation:
						minimize = 0
						minimize2 = 0
					if text_start < minimize:
						zako_class = ' class="zako"'
						zakos = True
					elif text_start < minimize2:
						zako_class = ' class="hanzako"'
					else:
						zako_class = ""
					if i < 5:
						resp += "<p"+zako_class+"><input type='radio' class='repla_select' name='"+str(audio_start).replace('.', '_')+"' data-name='"+str(audio_start)+"' value='"+str(text_start)+"' data-duration='"+str(line_duration)+"' id='repla_"+str(audio_start).replace('.', '_')+"_"+str(text_start)+"'><label for='repla_"+str(audio_start).replace('.', '_')+"_"+str(text_start)+"'>"+line[0][3:]+" "+l+"</label></p>"
			if text_start > minimize and text_start > minimize2:
				resp += "<hr>"
		resp += "<p><input type='radio' class='repla_select' name='"+str(audio_start).replace('.', '_')+"' data-name='"+str(audio_start)+"' data-duration='0' value='delete' id='repla_"+str(audio_start).replace('.', '_')+"_delete'><label for='repla_"+str(audio_start).replace('.', '_')+"_delete'>Ei sittenkään mikään.</label></p>"
		resp += "<button class='textbutton' style='display: none'>Näytä piilotetut</button>"
	return Response(resp)

@view_config(route_name='tallenna_ajastus')
def audio_ajastus(request):
	ajastus_dict = get_ajastus()
	filename = request.GET['f']
	text_start = Decimal(request.GET['ts'])
	audio_start = Decimal(request.GET['as']) + Decimal(request.GET.get('d', 0))
	hienosaada_ajastus(text_start, audio_start, filename, ajastus_dict)
	return HTTPFound(location=quote(request.GET['ref']+"#"+request.GET['a'], '/=?&#'))

@view_config(route_name='listaa_ajastukset')
def ajastukset(request):
	ajastus_dict = get_ajastus()
	resp = ''
	for key, value in sorted(ajastus_dict.items()):
		resp += key+"<br>"
		for text, audio in value.items():
			resp += str(text) +" -> "+str(audio)+"<br>"
		resp += "<br>"
	return Response(resp)

@view_config(route_name='listaa_ajastukset_reverse')
def ajastukset_reverse(request):
	audio_to_text = get_ajastus_reverse()
	resp = ''
	for key, value in sorted(audio_to_text.items()):
		resp += key+"<br>"
		for text, audio in value.items():
			resp += str(text) +" -> "+str(audio)+"<br>"
		resp += "<br>"
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