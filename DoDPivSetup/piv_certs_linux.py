#!/usr/bin/python3

import subprocess

actions: list = ['wget https://github.com/OpenSC/OpenSC/releases/download/0.21.0/opensc-0.21.0.tar.gz',
	'tar xfvz opensc-*.tar.gz',
	'tar xfvz opensc-*.tar.gz'

for action in actions:
	print(f'Running {action}\n')
	_ = subprocess.run(action, shell=True, stdout=subprocess.DEVNULL)



