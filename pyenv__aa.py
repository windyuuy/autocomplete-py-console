# python startup file
import sys
import readline
import rlcompleter
import atexit
import os
import sys
from threading import Thread
import yaml
from time import sleep

readline.redisplay=lambda:None

from rlcompleter import Completer

get_line_buffer=readline.get_line_buffer
listdir=os.listdir
yaml_load=yaml.load

indent_sign='    ' #用了 '\t' 会出bug，光标相对正确位置右移了'\t'数量 * tab的宽度，暂未深究

extkeys=['rlcompleter','Completer','numpy','readline','system']
def get_extkeys():
	return extkeys

packageskeys=list()
def get_packageskeys():
	return packageskeys

pythonexec_path=sys.executable
pyexec_dir=os.path.dirname(pythonexec_path)+'/'
pylib_dir=pyexec_dir+'Lib/'
site_packages_dir=pylib_dir+"site-packages"

def init_keys(keys,key_source,keyname):
	if(keyname in key_source and key_source[keyname]):
		keys.__init__(key_source[keyname])
		
def update_extkeys():
	try:
		with open(pyexec_dir+'extkeys.yml') as f:
			key_source=yaml_load(f)
			extkeys=get_extkeys()
			init_keys(extkeys,key_source,'extkeys')
			
			packageskeys=get_packageskeys()
			init_keys(packageskeys,key_source,'packageskeys')
			
			site_packages=list()
			raw_packageskeys=listdir(pylib_dir)+listdir(site_packages_dir)
			for rawkey in raw_packageskeys:
				key=rawkey
				if(key.endswith('.egg-info') or key.endswith('.dist-info')):
					continue
				for ext in ['.py','.pyc','.pyd']:
					if(key.endswith(ext)):
						key=key[:-len(ext)]
						break
				site_packages.append(key)
			packageskeys+=site_packages
			
	except FileNotFoundError as e:
		#print('load key source file failed')
		pass
		
def start_reload_extkeys():
	Thread(target=update_extkeys).start()
	
start_reload_extkeys()

class CC(Completer):

	max_valid_index=-1
	cur_index=0
	cur_outputs=list()
	
	cur_text=None
	tab_press_times=0
	last_outputs=list()
	cur_indicate_text=None
	
	def complete(self,text,state):
		# complete for empty str
		if(text==''):
			if(state==0):
				return indent_sign
			return None
		
		# solution of multi tab for same text
		if(state==0):
			if(self.cur_indicate_text==text):
				self.tab_press_times+=1
			else:
				start_reload_extkeys()
				self.cur_text=text
				self.tab_press_times=1
				self.last_outputs.clear()
				self.cur_indicate_text=text
		if(self.tab_press_times>=2):
			if(state==0 and len(self.last_outputs)>0):
				ret=self.last_outputs[(self.tab_press_times-2)%len(self.last_outputs)]
				self.cur_indicate_text=ret
				return ret
			else:
				return None
		
		# complete for keys
		if(self.max_valid_index==-1):
			# complete from inline keys
			ret=super(CC,self).complete(text,state)
			if(ret):
				self.last_outputs.append(ret)
				return ret
			else:
				self.max_valid_index=state
			
		if(self.max_valid_index>=0):
			# complete from ext key source
			extkey=self.get_complete_key_ext(text)
			if(extkey):
				return extkey
				
			# clear after all
			self.max_valid_index=-1
			self.cur_index=0
			self.cur_outputs.clear()
			
		return None

	def get_complete_key_ext(self,text):
		'''complete from ext key source'''
		
		extkeys=get_extkeys()
		if(get_line_buffer()=='import '+text or get_line_buffer()=='import  '+text):
			extkeys=get_packageskeys()
			
		for i in range(self.cur_index,len(extkeys)):
			extkey=extkeys[i]
			if(extkey.startswith(text) and (extkey not in self.cur_outputs)):
				self.cur_index=i+1
				self.cur_outputs.append(extkey)
				self.last_outputs.append(extkey)
				return extkey
		return None
	
completer_obj=CC()
def nop(val, word):
	return word
completer_obj._callable_postfix = nop

readline.set_completer(completer_obj.complete)

# tab completion
readline.parse_and_bind('tab: complete')
# history file
histfile = os.path.join(os.environ['PYTHON_PATH'], '.pythonhistory')
try:
	readline.read_history_file(histfile)
except IOError:
	pass
atexit.register(readline.write_history_file, histfile)

del os, histfile, readline, rlcompleter, sys, yaml
