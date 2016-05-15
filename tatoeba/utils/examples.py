#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tatoeba.utils.audio_split import split_audio
import sys
import os
import math
import time
from decimal import *
from itertools import tee
getcontext().prec = 10

prefix = sys.prefix+"/"
bunseki_blob = open(prefix+'tatoeba/corpus/bunseki_blob.txt', 'rb')

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

freq_by_lexeme = {}

kata2hira = dict((ord(kata[n]), ord(hira[n])) for n in range(len(kata)))

class RunningWord(object):
	def __init__(self, line):
		self.originalline = line
		self.runningword = line[0]
		self.pronunciation = line[1]
		self.lemma = line[2]
		self.lexeme = '::'.join([line[2], line[3], line[6], line[7], line[8], line[9]])
		try:
			self.hardness = str(int(1000/freq_by_lexeme[self.lexeme]))
		except:
			self.hardness = "???"
	
	def __repr__(self):
		return self.runningword
	
	def __str__(self):
		return self.runningword
	
	def hatsuon(self):
		start = 0
		end = 0
		pronun = self.pronunciation.translate(kata2hira)
		word = self.runningword.translate(kata2hira)
		if len(pronun) == 0:
			return [word, '', '', '']
		while end>-len(word) and end>-len(pronun)  and pronun[end-1] == word[end-1]:
			end -=1
		while start<len(word) and start<len(pronun) and pronun[start] == word[start]:
			start += 1
		word = self.runningword
		word_end = len(word)+end
		pronun_end = len(pronun)+end
		return [word[start:word_end], pronun[start:pronun_end], word[:start], word[word_end:]]

def humantime_to_seconds(humantime):
	humantime = humantime.split(':')
	seconds = Decimal(humantime[0])*Decimal('3600.00') + Decimal(humantime[1])*Decimal('60.00') + Decimal(humantime[2])
	return seconds.quantize(Decimal('1.00'))


class Line(list):
	def __init__(self, header, ajastus_dict):
		super().__init__()
		self.header = header.split('::')
		self.filename = self.header[0][:-4]
		self.linenumber = self.header[1]
		self.start = self.header[2]
		self.end = self.header[3]
		self.speaker = self.header[4]
		self.text_start_seconds = humantime_to_seconds(self.start)
		self.text_end_seconds = humantime_to_seconds(self.end)
		self.displacement = get_displacement(ajastus_dict, self.filename, self.text_start_seconds)
		print(self.text_start_seconds, self.displacement)
		self.start_seconds = self.text_start_seconds + self.displacement
		self.end_seconds = self.text_end_seconds + self.displacement
		self.start = [
			str(self.start_seconds//3600).zfill(2),
			str((self.start_seconds%3600)//60).zfill(2),
			str((self.start_seconds%3600)%60).zfill(2)
		]
		self.end = [
			str(self.end_seconds//3600).zfill(2),
			str((self.end_seconds%3600)//60).zfill(2),
			str((self.end_seconds%3600)%60).zfill(2)
		]
		self.cost = 0

	def clear(self):
		del self[:]

def readline_backwards(f_pointer, newline_marker, chunk_size):
	chunk = chunk_size
	linepos = f_pointer.tell()
	pos = linepos
	lines = []
	lines_text = ''
	while len(lines) <= 2:
		justread = '\uFFFD'
		pluschunk = 0
		while justread.startswith('\uFFFD'):	# jos tiedosto on oikein koodattu ei voi tapahtua tied. alussa
			newpos = max(pos-chunk, 0) # joko normiperuutus chunkin verran, tai vähemmän jos tiedoston alussa
			thischunk = chunk - min(pos-chunk, 0) # joko 1024 tai vähemmän, jos tiedoston alussa
			f_pointer.seek(newpos+pluschunk, os.SEEK_SET)
			justread = f_pointer.read(thischunk-pluschunk).decode('utf-8', 'replace')
			pluschunk += 1
		pos = newpos+pluschunk-1
		lines_text = justread + lines_text
		lines = lines_text.split(newline_marker)
	f_pointer.seek(linepos, 0)
	return lines[-2]

def get_line_before(linepos, ajastus_dict):
	bunseki_blob.seek(linepos, os.SEEK_SET)
	last_line = readline_backwards(bunseki_blob,'\n\n', 2100).split('\n')
	header = last_line[0].split('::')
	line_before= Line(last_line[0].strip(), ajastus_dict)
	for i, l in enumerate(last_line):
		last_line[i] = l.split('\t')
	try:
		for last_l in last_line[1:]:
			line_before.append(RunningWord(last_l))
	except IndexError:
		line_before = None
	return line_before

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

def neighborhood(iterable):
    iterator = iter(iterable)
    item = next(iterator)  # throws StopIteration if empty.
    yield (None,item)
    for next_i in iterator:
        yield (item,next_i)
        item = next_i
    yield (item,None)

def get_displacement(ajastus_dict, filename, text_start):
	seriename = filename.split('/')[0]
	epname = filename.split('/')[1]
	ep_dict = ajastus_dict.get(epname, None)
	if ep_dict:
		print('154',ep_dict)
		for left, right in pairwise([None]+sorted(ep_dict.items())+[None]):
			if not left:
				displacement = right[1][0]
			elif not right:
				displacement = left[1][1]
			elif left[0] <= text_start <= right[0]:
				displacement = ( left[1][1] + right[1][0] ) / 2
				print('165', displacement, left, right)
				break
	else:
		displacement = 0
	return displacement

def open_examples(pointer, ajastus_dict):
	example_sentences = []
	line_before = get_line_before(pointer, ajastus_dict)
	bunseki_blob.seek(pointer)
	line_header = bunseki_blob.readline().decode('utf-8').strip()
	line_itself = Line(line_header, ajastus_dict)
	while True:		# Jos tiedoston vika rivi ei pääty '\n', jää ikilooppiin jos vika serifu on kyseessä?
		line = bunseki_blob.readline().decode('utf-8').split('\t') # Jos kokonaisilla riveillä on encoodausvirheitä, voi bugata?
		if line[0] == '\n':
			break
		if len(line) < 5:
			raise(Exception("JOSSAIN MÄTTÄÄ!!! "+line))
		word = RunningWord(line)
		line_itself.append(word)
	line_after_header = bunseki_blob.readline().decode('utf-8').strip()
	if line_after_header == '' or '::' not in line_after_header:
		line_after = None
	else:
		line_after = Line(line_after_header, ajastus_dict)
		while True:
			line = bunseki_blob.readline().decode('utf-8').split('\t')
			if line[0] == '\n':
				break
			line_after.append(RunningWord(line))

		if line_before and line_before.end_seconds < line_itself.start_seconds-5:
			line_before = None
		if line_after and line_after.start_seconds > line_itself.end_seconds+5:
			line_after = None

	return [[line_itself.filename], line_before, line_itself, line_after]

def open_audio(filename, start, end):
	filename = filename.replace('..', '')
	filename = os.path.join(prefix, 'tatoeba/audio/', filename+'.m4a')
	nyt = int(time.time()*100)
	out_file = prefix+'tatoeba/temp/'+str(nyt)+".m4a"
	duration = split_audio(filename, start, end, out_file)
	files = os.listdir(prefix+'tatoeba/temp')
	for f in files:
		try:
			f_i = int(f[:-4])
		except:
			continue
		if f_i < nyt-(60*100):
			os.unlink(prefix+'tatoeba/temp/'+f)
	return out_file, duration

if __name__ == "__main__":
	from helper import plot
		
#	words = {}
#	for line in lines:
#		line = line.split('\t')
#		words[line[0]] = 1/int(line[2])
	kaikki_jaksot = set()

	for i, line in enumerate(open(prefix+'tatoeba/corpus/words_ep.txt')):
		line = line.strip('\n').split('\t')
		word = line[0]
		examples = line[3:]
		example_sentences = []
		ex_files = set()
		for episode in examples[:10]:
			episode = episode.split('::')
			file_p = episode[0]
			posis = episode[1].split(':')
			for pos_p in posis:
				ex = open_examples(int(file_p), int(pos_p))
				example_sentences.append(ex)
		write_path = os.path.join('examples', word+'.txt')
		if not os.path.exists('examples'):
			os.makedirs('examples')
		with open(write_path, 'w') as f:
			for s in sorted(example_sentences, key=lambda line: line[2].cost):
				f.write(str(s[0])+'\n'+str(s[1])+'\n'+str(s[2])+'\n'+str(s[3])+'\n')
				
		if i >= 1:
			break