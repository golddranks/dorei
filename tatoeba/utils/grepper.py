#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from subprocess import PIPE, Popen, STDOUT
from threading  import Thread
try:
	from Queue import Queue, Empty
except ImportError:
	from queue import Queue, Empty
prefix = sys.prefix+"/"

def enqueue_output(out, q):
	buffer = b''
	for line in iter(out.readline, b''):
		if line == b'\n':
			q.put(buffer.decode('utf-8').strip())
			buffer = b''
		else:
			buffer += line
	out.close()
    
def enqueue_input(inp, q):
	line = True
	while(line):
		fields = q.get()
		fields = '::'.join([str(f) for f in fields])
		inp.write((fields+"\n").encode('utf-8'))
	inp.close()

if __name__ == "__main__":
	while(True):
		command = input()
		poop, filename, words, context = command.split('::')
		grepper = Popen(['grep', context, words, filename], stdout=PIPE, stderr=PIPE, close_fds=True)
		out, err = grepper.communicate()
		sys.stdout.buffer.write(out+b'\n')
else:
	print("Starting grepper")
	splitter = Popen(['python',prefix+'tatoeba/tatoeba/utils/grepper.py'],stdout=PIPE, stdin=PIPE, stderr=STDOUT)
	input_queue = Queue()
	t_input = Thread(target=enqueue_input, args=(splitter.stdin, input_queue))
	t_input.daemon = True
	t_input.start()

	output_queue = Queue()
	t_output = Thread(target=enqueue_output, args=(splitter.stdout, output_queue))
	t_output.daemon = True
	t_output.start()

def grep(filename, words, context='-C2'):
	input_queue.put(['grep', filename, words, context])
	out = output_queue.get()
	return out
