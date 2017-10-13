from ctypes import *
import pyHook
import pythoncom
import win32gui

curwindow=win32gui.GetForegroundWindow()

def onKeyboardEvent(event):
	#print('='*30)
	# event.WindowName有时候会不好用
	# 所以调用底层API喊来获取窗口标题
	windowTitle = create_string_buffer(512)
	if(curwindow==event.Window):
		windll.user32.GetWindowTextA(event.Window,
									 byref(windowTitle),
									 512)
		windowName = windowTitle.value.decode('gbk')
		#print('当前您正处于"{0}"窗口'.format(windowName))
		#print('刚刚按下了"{0}"键'.format(chr(event.Ascii)))
	return True

# 安装钩子，监听键盘消息
hm = pyHook.HookManager()
print(hm.keyboard_funcs)
hm.SubscribeKeyDown(onKeyboardEvent)
hm.HookKeyboard()

pythoncom.PumpMessages()
