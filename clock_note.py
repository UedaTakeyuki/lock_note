# coding:utf-8 Copy Right Atelier Ueda © 2016 -
#
import os
import sys
#sys.path.append(os.path.dirname(os.path.abspath(__file__))+"/vendor")
import datetime
import time
import subprocess
import logging
import traceback
import inspect
#import requests
import configparser

import I2C_LCD_driver as lcd
# 定数
configfile = os.path.dirname(os.path.abspath(__file__))+'/clock_note.ini'

# 設定の取得
ini = configparser.SafeConfigParser()
ini.read(configfile)

logging.basicConfig(format='%(asctime)s %(filename)s %(lineno)d %(levelname)s %(message)s',filename='/home/pi/LOG/clock_note.engine.log',level=logging.DEBUG)
lcd = lcd.lcd()

def msg_log(msg_str):
	print (str(inspect.currentframe().f_lineno) + " " + msg_str)
	logging.info(str(inspect.currentframe().f_lineno) + " " + msg_str)

def msg_err_log(msg_str):
	print (str(inspect.currentframe().f_lineno) + " " + msg_str)
	logging.error(str(inspect.currentframe().f_lineno) + " " + msg_str)

def say(phrase):
	'''
	try:
		if ini.get("path", "say_path"): # settings is NOT null then
			payload = {'phrase': phrase}
			r = requests.post(ini.get("path", "say_path"), data=payload, timeout=10, verify=False)
	except:
		msg_err_log(traceback.format_exc())
	'''

def current_ip():
	p = subprocess.Popen("hostname -I",
												stdout=subprocess.PIPE,
												shell=True)
	result = p.stdout.readline().strip()
	print (result)
	return result

def show_ip(sec):
	global lcd
	p = subprocess.Popen("hostname -I",
												stdout=subprocess.PIPE,
												shell=True)
	lcd.lcd_clear()
	lcd.lcd_display_string("IP:")
	lcd.lcd_display_string(p.stdout.readline().strip().decode('utf-8'),
	                       2)
	time.sleep(sec)

def show_temp(sec):
	global lcd
	p = subprocess.Popen("tail -n 1 "+ini.get("data", "temp_path")+"/temp.csv",
												stdout=subprocess.PIPE,
												shell=True)
	result = p.stdout.readline().strip().decode('utf-8','ignore').split(',')
	lcd.lcd_clear()
#	lcd.lcd_display_string("TEMP = " + result[1])
	lcd.lcd_display_string("TEMP = " + result[2])
	say(u"温度"+result[1]+u"度")
	time.sleep(sec)

def show_humidity(sec):
	global lcd
	p = subprocess.Popen("tail -n 1 "+ini.get("data", "humidity_path")+"/humidity.csv",
												stdout=subprocess.PIPE,
												shell=True)
	result = p.stdout.readline().strip().decode('utf-8').split(',')
	lcd.lcd_clear()
#	lcd.lcd_display_string("Humidity = " + result[1])
	lcd.lcd_display_string("Humidity = " + result[2])
	say(u"湿度"+result[1]+"%")
	time.sleep(sec)

def show_humiditydeficit(sec):
	global lcd
	p = subprocess.Popen("tail -n 1 "+ini.get("data", "humiditydeficit_path")+"/humiditydeficit.csv",
												stdout=subprocess.PIPE,
												shell=True)
	result = p.stdout.readline().strip().decode('utf-8').split(',')
	lcd.lcd_clear()
#	lcd.lcd_display_string("HumidDef = " + result[1])
	lcd.lcd_display_string("HumidDef = " + result[2])
	time.sleep(sec)

def show_CO2(sec):
	global lcd
	lcd.lcd_clear()
	if ini.get("data", "CO2_path"): # settings is NOT null then
		p = subprocess.Popen("tail -n 1 "+ini.get("data", "CO2_path")+"/co2.csv",
													stdout=subprocess.PIPE,
													shell=True)
		result = p.stdout.readline().strip().decode('utf-8').split(',')
		lcd.lcd_clear()
#		lcd.lcd_display_string("CO2 = " + result[1])
		lcd.lcd_display_string("CO2 = " + result[2])
		say(u"二酸化炭素濃度"+result[1]+u"ppmです")
		time.sleep(sec)

def fork():
	pid = os.fork()
	if pid > 0:
		f = open('/var/run/clock_note.pid','w')
		f.write(str(pid)+"\n")
		f.close()
		sys.exit()

	if pid == 0:
		main()

def main():
	global lcd
	lcd.backlight(1) # 1: On, 0: Off
	now_str_prev = datetime.datetime.now().strftime('%m-%d %H:%M:%S')
	is_said = False
	while True:
		now = datetime.datetime.now()
		now_str = datetime.datetime.now().strftime('%m-%d %H:%M:%S')
		if (now.second == 1):
			if not is_said:
				say(str(now.hour) + "時" + str(now.minute) + "分です")
				is_said = True
		if (now.second == 2):
			is_said = False
		
		if (datetime.datetime.now().second == 31):
			show_ip(2)
			show_temp(3) # openjtalk が間に合わない
			show_humidity(2)
			show_humiditydeficit(2)
			show_CO2(2)

		if not now_str == now_str_prev:
			lcd.lcd_display_string(now_str)
			now_str_prev = now_str

		time.sleep(0.1)

if __name__ == '__main__':
#	fork()
	main()
