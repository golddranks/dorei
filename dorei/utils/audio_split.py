#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import re
from subprocess import PIPE, Popen, STDOUT
from threading  import Thread
from decimal import *
getcontext().prec = 10
try:
	from Queue import Queue, Empty
except ImportError:
	from queue import Queue, Empty
prefix = sys.prefix+"/"

def humantime_to_seconds(humantime):
	humantime = humantime.split(':')
	seconds = Decimal(humantime[0])*3600 + Decimal(humantime[1])*60 + Decimal(humantime[2])
	return seconds.quantize(Decimal('1.00'))

def enqueue_output(out, q):
	for line in iter(out.readline, b''):
		q.put(line.decode('utf-8').strip())
	out.close()
    
def enqueue_input(inp, q):
	while True:
		fields = q.get()
		buff = ('::'.join([str(f) for f in fields])+ '\n').encode('utf-8')
		inp.write(buff)
	inp.close()

if __name__ == "__main__":
	dura_pattern = re.compile(b'Duration: (.*?),')
	while(True):
		try:
			fields = input().strip().split('::')
			try:
				poop, filename, start, end, out_file = fields
			except ValueError:
				raise Exception('tarjottiin kakkaa'+str(fields))
			start = Decimal(start)
			end = Decimal(end)
			splitter = Popen(['ffmpeg','-y', '-i', filename, '-ss', str(start), '-t', str(end-start), '-acodec', 'copy', out_file], stderr=PIPE, close_fds=True) # ffmpeg ulostaa kaiken tekstioutputin stderriin
			output = splitter.communicate()[1]
			duration = dura_pattern.search(output)
			if duration:
				duration = humantime_to_seconds(duration.group(1).decode('utf-8'))
			else:
				raise Exception('No duration! '+output.decode('utf-8'))
			if duration < end:
				raise Exception("Audio on liian lyhyt! "+str(end)+" vs. "+str(duration))
			output = output.decode('utf-8')
			if 'Error' in output:
				raise Exception('Some kind of fucking ERROR! '+output)
			print('ok::'+'::'.join(fields[1:])+'::'+str(duration))
		except Exception as e:
			print('error::'+'::'.join(fields[1:])+'::'+str(duration)+"::Exception inside audio_split.py looper! "+str(e).replace('\n', '')+"  "+str(output.decode('utf-8').replace('\n','\\n')))
else:
	print("Starting audio_split")
	splitter = Popen(['python',prefix+'dorei/dorei/utils/audio_split.py'],stdout=PIPE, stdin=PIPE, stderr=STDOUT)
	input_queue = Queue()
	t_input = Thread(target=enqueue_input, args=(splitter.stdin, input_queue))
	t_input.daemon = True
	t_input.start()

	output_queue = Queue()
	t_output = Thread(target=enqueue_output, args=(splitter.stdout, output_queue))
	t_output.daemon = True
	t_output.start()

def split_audio(filename, start, end, out_file):
	input_queue.put(['split', filename, start, end, out_file])
	out = output_queue.get()
	if out.startswith('ok'):
		out = out.split('::')
		duration = Decimal(out[5])
	else:
		raise Exception("Virhe! '''"+out+"'''")	
	return duration
