#! /usr/bin/env/python3
# -*- coding: utf-8 -*-

import os, sys, time, subprocess

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def log(s):
	print('[Monitor] %s' %s)

#定义文件变化类
class MyFileSystemEventHander(FileSystemEventHandler):

	def __init__(self, fn):
		super(MyFileSystemEventHander,self).__init__()
		self.restart = fn

	def on_any_event(self, event):
		if event.src_path.endswith('.py'):
			log('Python source file changed: %s' % event.src_path)
			self.restart()

command = ['echo', 'ok']
process = None		

#关闭进程
def kill_process():
	global process
	if process:
		log('kill process [%s]...' % process.pid)
		process.kill()
		process.wait()
		log('Process ended with code %s' %process.returncode)
		process=None
#开始进程
def start_process():
	global process, command
	log('Start process %s...' % ' '.join(command))
	process = subprocess.Popen(command, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
#重启进程
def restart_process():
	kill_process()
	start_process()
#开始监视
def start_watch(path, callback):
	observer = Observer()
	observer.schedule(MyFileSystemEventHander(restart_process), path, recursive=True)
	observer.start()
	log('Watching directory %s' % path)
	start_process()
	try:
		while True:
			time.sleep(0.5)
	except KeyboardInterrupt:
		observer.stop()
	observer.join()
#执行更改
if __name__ == '__main__':
	argv = sys.argv[1:]
	if not argv:
		print('Usage: ./pymonitor your-script.py')
		exit(0)
	if argv[0] != 'python':
		argv.insert(0,'python ')
	command = argv
	path = os.path.abspath('.')
	start_watch(path, None) 