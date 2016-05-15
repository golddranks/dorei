#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tatoeba.utils.grepper import grep
from tatoeba.utils.examples import open_examples, open_audio, freq_by_lexeme, readline_backwards, humantime_to_seconds
import sys
from os import path, SEEK_END
from decimal import *
import math
import pickle
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

try:
	text_to_audio = pickle.load(open(prefix+'tatoeba/text_to_audio.pickle', 'rb'))
except FileNotFoundError:
	text_to_audio = {}
try:
	audio_to_text = pickle.load(open(prefix+'tatoeba/audio_to_text.pickle', 'rb'))
except FileNotFoundError:
	audio_to_text = {}

def get_ajastus():
	return text_to_audio

def get_ajastus_reverse():
	return audio_to_text

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

def spottaa_clip(l_text, r_text, l_audio, r_audio, filename):
	filename = filename.replace('..', '')
	name = filename.split('/')[-1]
	serie_name = filename.split('/')[-2]

	text_to_audio = get_ajastus()
	serie_text_to_audio = text_to_audio.get(serie_name, {})
	ep_text_to_audio = text_to_audio.get(name, {})
	clip_text = (( l_text + r_text ) / 2).quantize(Decimal('1.00'))
	l_audio_displacement = l_audio - l_text
	r_audio_displacement = r_audio - r_text
	ep_text_to_audio[clip_text] = (l_audio_displacement, r_audio_displacement)
	serie_text_to_audio[name] = ep_text_to_audio
	text_to_audio[name] = ep_text_to_audio
	text_to_audio[serie_name] = serie_text_to_audio	
	pickle.dump(text_to_audio, open(prefix+'tatoeba/text_to_audio.pickle', 'wb'))
	
	audio_to_text = get_ajastus_reverse()
	serie_audio_to_text = audio_to_text.get(serie_name, {})
	ep_audio_to_text = audio_to_text.get(name, {})
	clip_audio = (( l_audio + r_audio ) / 2).quantize(Decimal('1.00'))
	l_text_displacement = l_text - l_audio
	r_text_displacement = r_text - r_audio
	ep_audio_to_text[clip_audio] = (l_text_displacement, r_text_displacement)
	audio_to_text[name] = ep_audio_to_text
	serie_audio_to_text[name] = ep_audio_to_text
	audio_to_text[serie_name] = serie_audio_to_text	
	pickle.dump(audio_to_text, open(prefix+'tatoeba/audio_to_text.pickle', 'wb'))


def selvita_perusteet(filename, full_duration):
	text_start, firstline = jakson_alku(filename)
# Audion alkukohta, tekstin alkukohta, 1/3 jaksosta (tod. näk. tunnarin ja mainoskatkon välissä), 2/3 (tod. näk. mainoskatkon ja lopputunnarin välissä, 20 sekkaa audion lopusta)
	points = [0] + ( [text_start] if text_start > 20 else [] ) + [full_duration/3, full_duration*2/3, full_duration-15]
	ask = [['manual_search', Decimal(p).quantize(Decimal('1.00')), max(Decimal('-20.00'), -p), min(Decimal('20.00'), full_duration-p)] for p in points]
	return ask

def text_file(filename):
	filename = prefix+'tatoeba/timed_text/'+filename.replace('..', '')+'.txt'
	with open(filename, 'r') as f:
		f = f.readlines()
	return f

def hae_lahin_repliikki(text_target, f, l_limit, r_limit, unclearz=0):
	line_tstamp, line_no = binary_search(f, text_target)
	if unclearz > 0:
		line_no -= (-1 ** unclearz) * math.ceil(unclearz/2)
		line_tstamp = line_to_seconds(f[line_no])
	if line_tstamp <= l_limit:
		line_no += 1
		line_tstamp = line_to_seconds(f[line_no])
		if r_limit <= line_tstamp:
			return None
	if r_limit <= line_tstamp:
		line_no -= 1
		line_tstamp = line_to_seconds(f[line_no])
		if line_tstamp <= l_limit:
			return None
	return line_tstamp, line_duration(f[line_no]), line_no, f[line_no]

def line_to_seconds(line):
	return humantime_to_seconds(line[:8])
	
def binary_search(list, target, start=0):
	small = start
	large = len(list)
	while True:
		line_start = line_to_seconds(list[(small+large)//2])
		if line_start <= target:
			small = math.ceil((small+large)/2)
		else:
			large = math.floor((small+large)/2)
		if small == large:
			start_line_no = small
			line_start = line_to_seconds(list[start_line_no])
			return [line_start, start_line_no]

def line_duration(line):
	return humantime_to_seconds(line[10:18]) - humantime_to_seconds(line[:8])

def choose_audio(text_half, f, l_displacement, r_displacement, l_text, r_text, l_audio, r_audio, unclearz):
	line_tstamp, line_duration, line_no, line = hae_lahin_repliikki(text_half, f, l_text, r_text, unclearz)
	l_audio_tstamp = line_tstamp - l_displacement
	r_audio_tstamp = line_tstamp - r_displacement
	print(l_audio, l_audio_tstamp)
	print(r_audio, r_audio_tstamp)
	if l_audio_tstamp <= l_audio or r_audio_tstamp <= l_audio:
		raise RuntimeError("Ylittää raja-arvon vasemmalta")
	if r_audio <= l_audio_tstamp or r_audio <= r_audio_tstamp:
		raise RuntimeError("Ylittää raja-arvon oikealta")
	line = line.split('::')[2]
	return ['choose_audio', line, line_tstamp, line_duration, l_audio_tstamp, r_audio_tstamp]

def make_statement(f, line_no, line_tstamp, displacement):
	line = f[line_no].split('::')[2]
	line_dur = line_duration(f[line_no])
	audio_tstamp = line_tstamp - displacement
	return [line, audio_tstamp, line_dur, line_tstamp]	

def test_statements(text_half, f, l_displacement, r_displacement, l_text, r_text):
	line_tstamp, line_duration, line_no, line = hae_lahin_repliikki(text_half, f, l_text, r_text)
	while True:
		line_tstamp = line_to_seconds(f[line_no])
		if line_tstamp < text_half:
			l_line_no = line_no
			l_line_tstamp = line_tstamp
			break
		else:
			line_no -= 1
	if l_line_tstamp > l_text:
		l_statement = make_statement(f, l_line_no, l_line_tstamp, l_displacement)
	else:
		print('DEBUG!. vasen meni vasemman laidan vasemmalle puolelle.')
		l_statement = None
	while True:
		line_tstamp = line_to_seconds(f[line_no])
		if line_tstamp > text_half:
			r_line_no = line_no
			r_line_tstamp = line_tstamp
			break
		else:
			line_no += 1
	if r_line_tstamp < r_text:
		r_statement = make_statement(f, r_line_no, r_line_tstamp, r_displacement)
	else:
		print('DEBUG!. oikee meni oikeen laidan oikeelle puolelle.')
		r_statement = None
	try:	# olettaen että ne ei oo None-typeä
		if l_statement[1] > r_statement[1]: # [1] on yhtä kuin repliikin audio_tstamp. Jos
			return ['choose_statement', l_statement, r_statement]		# jos mappaukset "menevät ristiin", eli jos vasen on mapattuna isommaksi kuin oikea, vain toinen ajastuksista voi olla oikein!
	except TypeError:
		pass
	return ['eval_statements', l_statement, r_statement]		# molemmat voivat olla oikein

def selvita_tekstin_pohjalta(l_text, r_text, l_displacement, r_displacement, l_audio, r_audio, filename, unclearz):
	f = text_file(filename)
	text_half = (( l_text + r_text ) / 2).quantize(Decimal('1.00'))
	clip = r_displacement - l_displacement
	audio_region = r_audio - l_audio
	if clip < audio_region:
		try:
			return choose_audio(text_half, f, l_displacement, r_displacement, l_text, r_text, l_audio, r_audio, unclearz)	# optimaalinen algoritmi tilanteesta riippuen (try, koska optimaalisuus selviää osittain vasta algoritmin sisällä)
		except RuntimeError:
			return test_statements(text_half, f, l_displacement, r_displacement, l_text, r_text)
	else:
		return test_statements(text_half, f, l_displacement, r_displacement, l_text, r_text)

def selvita_audion_pohjalta(l_audio, r_audio):
	half = ((l_audio + r_audio) / 2).quantize(Decimal('1.00'))
	backward = max(Decimal('-20.00'), l_audio - half)
	forward = min(Decimal('20.00'), r_audio - half)
	return ['manual_search', half, backward, forward]

def selvita_vali(l_audio, r_audio, l_text, r_text, line_duration, filename, unclearz=0):
	l_displacement = l_text - l_audio
	r_displacement = r_text - r_audio
	r_audio = max(r_audio, l_audio+line_duration)	# jos väli on niin pieni, että eka repla ei mahu siihen sisään, kasvatetaan vähän loppupäätä.
	r_text = max(r_text, l_text+line_duration)
	l_audio = l_audio + line_duration	# joka tapauksessa kutistetaan väliä alusta sen ekan replan verran
	l_text = l_text + line_duration
	tekstin_pohjalta = selvita_tekstin_pohjalta(l_text, r_text, l_displacement, r_displacement, l_audio, r_audio, filename, unclearz)
	audion_pohjalta = selvita_audion_pohjalta(l_audio, r_audio)
	tekstin_pohjalta.append(audion_pohjalta)
	return [['known', l_audio, l_text], tekstin_pohjalta, ['known', r_audio, r_text]]

def hae_tekstialue(l_text, r_text, filename):
	f = text_file(filename)
	l_line_tstamp, l_line_no = binary_search(f, l_text)
	if l_line_tstamp >= r_text:
		return []
	r_line_tstamp, r_line_no = binary_search(f, r_text, start=l_line_no)
	return f[l_line_no:r_line_no-1+1]

def hae_maarittelematon_tekstialue(l_audio, r_audio, l_displacement, r_displacement, filename):
	l_text = l_audio + r_displacement
	r_text = r_audio + l_displacement
	return hae_tekstialue(l_text, r_text, filename)

def ajastus_alg(filename, points):
	audio_duration = open_audio(filename, 0, 0)[1]
	text_duration, lastline = jakson_loppu(filename)
	kohdat = []
	if not points:
		kohdat.extend(selvita_perusteet(filename, audio_duration))
	else:
		unclears = [(Decimal(reg.split(':')[0]), Decimal(reg.split(':')[2])) for reg in points.split('::') if reg.split(':')[1]=='-1' ]
		points = sorted([(Decimal(reg.split(':')[0]), Decimal(reg.split(':')[1]), Decimal(reg.split(':')[2])) for reg in points.split('::') if (reg.split(':')[2]!='delete' and reg.split(':')[1]!='-1') ])
		print("POINTS")
		for r in points:
			print('audio:',r[0],'text:',r[2], 'displacement:',(r[2]-r[0]))
		print('l\tdisp\tdiff\tdisp\tr\tregion\tmerge\tlines\tunclear lines')
		for left, right in pairwise(points):
			l_audio, line_duration, l_text = left
			r_audio, unneccessary_poop, r_text = right
			
			l_displacement = l_text - l_audio
			r_displacement = r_text - r_audio
			
			unclear_match = False
			for u_audio, u_text in unclears:
				print('uclear',u_audio, u_text)
				if l_text < u_text and u_text < r_text:
					print('unclear_region')
					kohdat.extend(selvita_vali(l_audio, r_audio, l_text, r_text, 0, filename, 1))
					unclear_match = True
			if unclear_match: continue
			if int(r_text) == -2:	# -2 == ei vuorosanoja alueella, kysytään ensi kerralla eri kohtaa
				if l_audio < r_audio-Decimal('20.00'):
					kohdat.extend([['known', l_audio, l_text], ['manual_search', r_audio-Decimal('20.00'), max(Decimal('-20.00'), l_audio-r_audio), min(Decimal('20.00'), audio_duration-r_audio)]])
					print(str(l_audio) +"\t"+str(l_displacement)+ "\t"+"?"+"\t" + "?"+"\t"+ str(r_audio)+"\t"+str(r_audio-l_audio)+"\t"+"<<"+"\t"+"\t")
				continue
			if int(l_text) == -2:
				if l_audio+Decimal('20.00') < r_audio:
					kohdat.extend([['manual_search', l_audio+Decimal('20.00'), max(Decimal('-20.00'), -l_audio), min(Decimal('20.00'), r_audio-l_audio)], ['known', r_audio, r_text]])
					print(str(l_audio) +"\t"+"?"+ "\t"+"?" +"\t" + str(r_displacement)+"\t"+ str(r_audio)+"\t"+str(r_audio-l_audio)+"\t"+">>"+"\t"+"\t")
				continue

			clip = l_displacement - r_displacement

			tekstit = hae_tekstialue(l_text+Decimal('0.50'), r_text-Decimal('0.50'), filename)
			janna = hae_maarittelematon_tekstialue(l_audio, r_audio, l_displacement, r_displacement, filename)
			
			if ( len(tekstit) == 0 and abs(clip) > Decimal('3.50')): # alue ei tarvitse ajastamista -> se on kypsä poimittavaksi
				spottaa_clip(l_text, r_text, l_audio, r_audio, filename)
				print(str(l_audio) +"\t"+str(l_displacement)+ "\t"+str(clip) +"\t" + str(r_displacement)+"\t"+ str(r_audio)+"\t"+str(r_audio-l_audio)+"\t"+"!!!"+"\t"+str(len(tekstit))+"\t"+str(len(janna)))
				continue

			tarkenna = False
			if abs(clip) > Decimal('3.50'): # Jos alueen päät eroaa toisistaan, etsitään, missä kulkee raja
				kohdat.extend(selvita_vali(l_audio, r_audio, l_text, r_text, line_duration, filename))
				tarkenna = True
			print(str(l_audio) +"\t"+str(l_displacement)+ "\t"+str(clip) +"\t" + str(r_displacement)+"\t"+ str(r_audio)+"\t"+str(r_audio-l_audio)+"\t"+("x" if not tarkenna else "")+"\t"+str(len(tekstit))+"\t"+str(len(janna)))
	for l, r in pairwise(kohdat):
		if l[0] == 'known' and r[0] == 'known':
			poop, l_audio, l_text = l
			poop, r_audio, r_text = r
			l_displacement = l_text - l_audio
			r_displacement = r_text - r_audio
			clip = l_displacement - r_displacement
			if abs(clip) <= Decimal('3.50'):
				middle_displacement = ((l_displacement + r_displacement)/2).quantize(Decimal('1.00'))
				l[2] = l_audio + middle_displacement
				r[2] = r_audio + middle_displacement
				
				
	print("seuraavalle kierrokselle:")
	for k in kohdat:
		print(k)
	return { 'kohdat' : kohdat, 'name' : filename, 'audio_duration': audio_duration, 'text_duration': text_duration, 'Decimal': Decimal}