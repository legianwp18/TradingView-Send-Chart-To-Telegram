import time
import sys
import os
import shutil
import telebot
import mysql.connector
from mysql.connector import errorcode
from datetime import datetime
from datetime import date
from telebot import types
from selenium import webdriver
from PIL import Image
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC1
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
# from MysqlTradingview import *

chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument('disable-infobars')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument("test-type")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-web-security")
chrome_options.add_argument("--allow-running-insecure-content")
chrome_options.add_argument("--allow-insecure-localhost")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--disable-gpu")
#chrome_options.add_argument("--headless")

if os.path.isfile('setting_log.txt'):
	with open('setting_log.txt', 'r') as r:
		data = r.readlines()
	EMAIL = data[0].rstrip('\n')
	PASS = data[1].rstrip('\n')
	URL1 = data[2].rstrip('\n')
	URL2 = data[3].rstrip('\n')
	URL3 = data[4].rstrip('\n')
	URL4 = data[5].rstrip('\n')
	URL5 = data[6].rstrip('\n')
	TIME_LOADING = int(data[7].rstrip('\n'))
	CURRENT_FILE = data[8].rstrip('\n')
	HOST_DB = data[9].rstrip('\n')
	USER_DB = data[10].rstrip('\n')
	PASS_DB = data[11].rstrip('\n') if len(data) > 11 else ""
else:
	print("Please fill in the following data")
	EMAIL = str(input("Enter email : "))
	PASS = str(input("Enter password : "))
	URL1 = str(input("Enter url 1 Tradingview : "))
	URL2 = str(input("Enter url 2 Tradingview : "))
	URL3 = str(input("Enter url 3 Tradingview : "))
	URL4 = str(input("Enter url 4 Tradingview : "))
	URL5 = str(input("Enter url 5 Tradingview : "))
	TIME_LOADING = int(input("Enter Time Loading : "))
	CURRENT_FILE = str(input("Enter Current File Image Tradingview : "))
	HOST_DB = str(input("Enter Hostname MySQL : "))
	USER_DB = str(input("Enter User MySQL : "))
	PASS_DB = str(input("Enter Password MySQL : "))
	with open('setting_log.txt', 'w') as a:
		a.write(
			EMAIL+'\n'
			+PASS+'\n'
			+URL1+'\n'
			+URL2+'\n'
			+str(TIME_LOADING)+'\n'
			+CURRENT_FILE+'\n'
			+HOST_DB+'\n'
			+USER_DB+'\n'
			+PASS_DB
		)

TOKEN = '1642994002:AAEF5UrQYAYmbprpAMl9BQ-69OTB0HHvvtw'
HOST = HOST_DB if HOST_DB else "localhost"
USER = USER_DB if USER_DB else "root"
PASSWD = PASS_DB if PASS_DB else ""
DATABASE = "tradingview"
LOGFILE = "tradingview.log"

try:
	db = mysql.connector.connect(
		host=HOST,
		user=USER,
		passwd=PASSWD,
	)
	cursor = db.cursor()
	cursor.execute("SET sql_notes = 0; ")
	sql = """CREATE DATABASE IF NOT EXISTS {0};""".format(DATABASE)
	cursor.execute(sql)
	sql = """USE {};""".format(DATABASE)
	cursor.execute(sql)

	sql = """CREATE TABLE IF NOT EXISTS users (
		id INT AUTO_INCREMENT PRIMARY KEY,
		chat_id BIGINT(20),
		first_name Varchar(255),
		username Varchar(255),
		kouta INT(10), 
		exp_date DATE,
		admin BOOLEAN DEFAULT False
		);
		"""
	cursor.execute(sql)

	sql = """CREATE TABLE IF NOT EXISTS groups (
		id INT AUTO_INCREMENT PRIMARY KEY,
		name VARCHAR(255),
		group_id BIGINT(20),
		kouta INT(10)
		);
		"""
	cursor.execute(sql)

	sql = """CREATE TABLE IF NOT EXISTS command (
		id INT AUTO_INCREMENT PRIMARY KEY,
		command VARCHAR(255),
		user_id BIGINT(20),
		date DATE,
		type VARCHAR(255),
		status BOOLEAN
		);
		"""
	cursor.execute(sql)
	cursor.execute("SET sql_notes = 1;")

except mysql.connector.Error as err:
	if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
		print("Something is wrong with your user name or password")
		sys.exit()
	elif err.errno == errorcode.ER_BAD_DB_ERROR:
		print("Database does not exist")
		sys.exit()
	else:
		print(err)
		sys.exit()

knownUsers = []
waitUsers = [] 
user_dict = {}
user_set = {}
group_dict = {}

commands = {  # command description used in the "help" command
	'cuanSignal'       : 'Get used to the bot',
	'help'        : 'Gives you information about the available commands',
	'gicsignal'    : 'Send a signal | /gicsignal [pair chart] [timeframe]',
	'gicwin'    : 'Send a signal | /gicwin [pair chart] [timeframe]',
	'gicrrg'    : 'Send a signal | /gicrrg [pair chart] [timeframe]',
	'gicsd'    : 'Send a signal | /gicsd [pair chart] [timeframe]',
	'gicsw'    : 'Send a signal | /gicsw [pair chart] [timeframe]',
	'my_qouta'       : 'Get quota usage information',
	'group_id'       : 'Get your group id',
	'user_id'        : 'Get your user id',
}

commands_admin = {  # command description used in the "helpAdmin" command
	'cuanSignal'         : 'Get used to the bot',
	'help'          : 'Gives you information about the available commands',
	'gicsignal'       : 'Send a signal | /gicsignal [pair chart] [timeframe]',
	'gicwin'        : 'Send a signal | /gicwin [pair chart] [timeframe]',
	'gicrrg'    : 'Send a signal | /gicrrg [pair chart] [timeframe]',
	'gicsd'    : 'Send a signal | /gicsd [pair chart] [timeframe]',
	'gicsw'    : 'Send a signal | /gicsw [pair chart] [timeframe]',
	'my_qouta'       : 'Get quota usage information',
	'group_id'       : 'Get your group id',
	'user_id'        : 'Get your user id',
	'getQuotaGroup' : 'Get your group qouta',
	'setQuotaGroup' : 'Set your group qouta',
	'getQuotaUser'  : 'Get your group qouta',
	'setQuotaUser'  : 'Set your group qouta',
	'getUserAll'    : 'Get a list of all users',
	'getGroupAll'   : 'Get a list of all groups',
	'setExpDate'    : 'Set exp date user',
}

class User:
	def __init__(self, chat_id):
		self.chat_id = chat_id
		self.first_name=''
		self.username=''
		self.exp_date=''
		self.kouta =''
		self.admin=0

class Group:
	def __init__(self, group_id):
		self.group_id = group_id
		self.name = ''
		self.kouta =0

#save log application
def writeLog (logString):
	try:
		print(logString.encode("utf-8"))
		with open(LOGFILE, 'a') as f:
			f.write(('%s - %s\n' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), logString.encode("utf-8"))))
		f.close()
	except Exception as e:
		print("[ERROR]  : Error Log Application")

writeLog("[DEBUG] Application Start...")
driver = webdriver.Chrome(options=chrome_options)

try:
	driver.get ("https://www.tradingview.com/#signin")
	driver.maximize_window()
	email_button_box = WebDriverWait(driver, 20).until(EC1.presence_of_element_located((By.XPATH, '//*[@class="tv-signin-dialog"]/div/div/div/div[4]')))
	email_button = email_button_box.click()
	box_login = driver.find_elements_by_class_name("tv-control-error")
	email_box = box_login[0].find_element_by_tag_name("input")
	pass_box = box_login[1].find_element_by_tag_name("input")
	email_box.send_keys(EMAIL)
	pass_box.send_keys(PASS)
	driver.find_element_by_class_name("tv-button__loader").click()
except Exception as e:
   writeLog("[ERROR]  : {}".format(e))
time.sleep(20)

# only used for console output now
def listener(messages):
	"""
	When new messages arrive TeleBot will call this function.
	"""
	for m in messages:
		if m.content_type == 'text':
			cid=m.chat.id
			name = m.from_user.first_name
			msg_id = m.from_user.id
			if "/" in m.text and m.text != "/send_log" :
				writeLog("[DEBUG]  : "+str(name) + " [" + str(msg_id) + "]: " + m.text)

def qoutaUser(uid,group_id,first_name,username,title):
	sql = "SELECT * FROM users WHERE chat_id={}".format(uid)
	cursor.execute(sql)
	users = cursor.fetchone()
	if users:
		qouta_user = users[4]
		exp_date = users[5]
	else:
		qouta_user = 0
		exp_date = None
	
	sql = "SELECT * FROM groups WHERE group_id={}".format(group_id)
	cursor.execute(sql)
	groups = cursor.fetchone()
	if groups:
		qouta_group = groups[3]
	else:
		qouta_group = 0

	sql = """SELECT COUNT(*) FROM command WHERE date=CURDATE() and type='{0}' 
		and status=1 and user_id={1};""".format("user",uid)
	cursor.execute(sql)
	results_user = cursor.fetchone()
	if results_user:
		data_user = results_user[0]
	else:
		data_user = 0

	sql = """SELECT COUNT(*) FROM command WHERE date=CURDATE() and type='{0}' 
		and status=1 and user_id={1};""".format("group",group_id)
	cursor.execute(sql)
	results_group = cursor.fetchone()
	if results_group:
		data_group = results_group[0]
	else:
		data_group = 0
	
	if qouta_user > data_user:
		if exp_date:
			if date.today() >= exp_date:
				if qouta_group > data_group :
					return 2
					# min group
				else:
					return 4
			else:
				return 1
				# min user
		else:
			return 1
			# min user
	elif qouta_group > data_group :
		return 3
		# min group
	else:
		return 5

def isAdmin(chat_id):
	uid=chat_id
	sql = "SELECT * FROM users WHERE chat_id={}".format(chat_id)
	cursor.execute(sql)
	admin = cursor.fetchone()
	if admin:
		return True
	else:
		return False

def watermark_with_transparency(input_image_path,
								output_image_path,
								watermark_image_path,
								position):
	base_image = Image.open(input_image_path)
	watermark = Image.open(watermark_image_path)
	width, height = base_image.size
 
	transparent = Image.new('RGBA', (width, height), (0,0,0,0))
	transparent.paste(base_image, (0,0))
	transparent.paste(watermark, position, mask=watermark)
	# transparent.show()
	transparent.save(output_image_path)

bot = telebot.TeleBot(TOKEN)
bot.set_update_listener(listener)  # register listener

# handle the "/cuanSignal" command
@bot.message_handler(commands=['cuanSignal'])
def command_start(m):
	try :
		chat_id = m.from_user.id
		cid = m.chat.id
		first_name = m.from_user.first_name
		username = m.from_user.username
		sql_user = "SELECT * FROM users WHERE chat_id={}".format(m.from_user.id)
		cursor.execute(sql_user)
		users = cursor.fetchone()
		if users:
			writeLog("[DEBUG]  : "+str(m.from_user.first_name) + " [" + str(m.from_user.id) + "]: " + "Registered User")
		else:
			sql = "INSERT INTO users (chat_id, first_name, username, kouta, exp_date, admin) VALUES (%s, %s, %s, %s, %s, %s);"
			val = (m.from_user.id,m.from_user.first_name,m.from_user.username,0,"0000-00-00",False)
			cursor.execute(sql, val)
			db.commit()
		if chat_id not in knownUsers:  # if user hasn't used the "/start" command yet:
			knownUsers.append(chat_id)  # save user id, so you could brodcast messages to all users of this bot later
			bot.send_message(cid, "Hello, stranger, let me scan you...")
			bot.send_message(cid, "Scanning complete, I know you now")
			command_help(m)  # show the new user the help page
		else:
			bot.reply_to(m, "I already know you, no need for me to scan you again!")
	except Exception as e:
		bot.reply_to(m, "An error occurred or the internet connection lost. Please try again.")
		writeLog("[ERROR]  : {0} | {1}".format(cid,e))

@bot.message_handler(commands=['help'])
def command_help(m):
	cid = m.chat.id
	try:
		help_text = "The following commands are available: \n"
		for key in commands:  # generate help text out of the commands dictionary defined at the top
			help_text += "/" + key + ": "
			help_text += commands[key] + "\n"
		bot.reply_to(m, help_text)  # send the generated help page
	except Exception as e:
		bot.reply_to(m, "An error occurred or the internet connection lost. Please try again.")
		writeLog("[ERROR]  : {0} | {1}".format(cid,e))

# help page admin
@bot.message_handler(commands=['helpAdmin'])
def command_help_admin(m):
	cid = m.chat.id
	try:
		if isAdmin(m.from_user.id):
			help_text = "The following commands are available: \n"
			for key in commands_admin: 
				help_text += "/" + key + ": "
				help_text += commands_admin[key] + "\n"
			bot.reply_to(m, help_text) 
		else:
			bot.reply_to(m, "Sorry you are not allowed access")
	except Exception as e:
		bot.reply_to(m, "An error occurred or the internet connection lost. Please try again.")
		writeLog("[ERROR]  : {0} | {1}".format(cid,e))


# chat_action tradingview
@bot.message_handler(commands=['gicsignal'])
def command_signal(m):
	cid = m.chat.id
	try:
		if m.chat.type == "group" or m.chat.type == "supergroup" :
			sql_user = "SELECT * FROM users WHERE chat_id={}".format(m.from_user.id)
			cursor.execute(sql_user)
			users = cursor.fetchone()
			if users:
				writeLog("[DEBUG]  : "+str(m.from_user.first_name) + " [" + str(m.from_user.id) + "]: " + "Registered User")
			else:
				sql = "INSERT INTO users (chat_id, first_name, username, kouta, exp_date, admin) VALUES (%s, %s, %s, %s, %s, %s);"
				val = (m.from_user.id,m.from_user.first_name,m.from_user.username,0,"0000-00-00",False)
				cursor.execute(sql, val)
				db.commit()
			group_title = m.chat.title
			uid = m.from_user.id
			first_name = m.from_user.first_name
			username = m.from_user.username
			res = qoutaUser(uid,cid,first_name,username,group_title)
			if res >=1 and res <= 3:
				message = str(m.text).split(" ")
				if len(message) > 1:
					if message[0] and message[1] :  #Melakukan filter jika command mengandung /signaln-[0] dan pair-[1] akan dieksekusi
						#setelah mengandung 2 parameter diatas maka masuk antrian
						waitUsers.append(uid) #ambil nomor antrian setelah terfilter
						if len(waitUsers) > 1:
							writeLog("[DEBUG]  : {0} | Waiting other command ({1}) ".format(uid,m.text))
							bot.reply_to(m, "Please wait other command ({}) ...".format(len(waitUsers)-1))
							bot.send_chat_action(cid, 'typing')  # show the bot "typing" (max. 5 secs)
							waittime = (5 + TIME_LOADING) * len(waitUsers)
							time.sleep(waittime)
						else : 
							bot.reply_to(m, "Please wait ({}) ...".format(len(waitUsers)-1))
							bot.send_chat_action(cid, 'typing')  # show the bot "typing" (max. 5 secs)
						driver.get(URL1)
						time.sleep(3) #waktu jeda saat url diakses menunggu web tampil sempurna
						try:
							WebDriverWait(driver, 3).until(EC1.alert_is_present(),
							'Timed out waiting for PA creation ' +
							'confirmation popup to appear.')
							alert = driver.switch_to.alert
							alert.accept()
							writeLog("[DEBUG]  : {0} | Alert Accepted ({1})".format(uid,m.text))
						except TimeoutException:
							writeLog("[DEBUG]  : {0} | No Alert ({1})".format(uid,m.text))					
						try:
							element_body = WebDriverWait(driver, 20).until(EC1.presence_of_element_located((By.TAG_NAME, "body")))
							search = WebDriverWait(element_body, 20).until(EC1.presence_of_element_located((By.ID, "header-toolbar-symbol-search")))
							search.click()
							search_box = WebDriverWait(element_body, 20).until(EC1.presence_of_element_located((By.ID, "overlap-manager-root")))
							search_input = WebDriverWait(search_box, 20).until(EC1.presence_of_element_located((By.TAG_NAME, "input")))
							time.sleep(1) #Menunggu tampilan box pairnya
							search_input.send_keys("OANDA:"+str(message[1]))
							time.sleep(1) #Jeda 1 detik bot memasukan pair ke dalam box
							search_input.send_keys(Keys.ENTER)
							if len(message) > 2:
								time.sleep(1) #jeda 1 detik menunggu chart muncul
								element_body.send_keys(0)
								interval = WebDriverWait(element_body, 20).until(EC1.presence_of_element_located((By.ID, "overlap-manager-root")))
								interval_input = WebDriverWait(interval, 20).until(EC1.presence_of_element_located((By.TAG_NAME, "input")))
								time.sleep(1) #jeda 1 detik menunggu box timeframe muncul
								interval_input.send_keys(message[2])
								time.sleep(1) #jeda 1 detik menunggu chart tampil
								interval_input.send_keys(Keys.ENTER)
							else: 
								time.sleep(1) #jeda 1 detik menunggu chart muncul
								element_body.send_keys(0)
								interval = WebDriverWait(element_body, 20).until(EC1.presence_of_element_located((By.ID, "overlap-manager-root")))
								interval_input = WebDriverWait(interval, 20).until(EC1.presence_of_element_located((By.TAG_NAME, "input")))
								time.sleep(1) #jeda 1 detik menunggu box timeframe muncul
								element_body.send_keys("1D")
								time.sleep(1) #jeda 1 detik menunggu chart tampil
								element_body.send_keys(Keys.ENTER)
							time.sleep(TIME_LOADING)
							ActionChains(driver).key_down(Keys.ALT).send_keys('s').perform()
							element = WebDriverWait(driver, 20).until(EC1.element_to_be_clickable((By.LINK_TEXT, 'Save image')))
							element.click()
							time.sleep(3) #jeda 2 detik untuk menunggu proses simpan image
							filename = str(element.get_attribute('href')).split("/")[4]+".png"
							element_body.send_keys(Keys.ESCAPE)
							new_name = time.strftime("%Y-%m-%d_%H%M%S") + ".png"
							dest_dir = os.path.abspath(os.getcwd())
							current_file_name = CURRENT_FILE+"/"+filename
							location_file_name = dest_dir+"/image/"+new_name
							watermark_file_name = dest_dir+"/watermark/"+new_name
							os.rename(current_file_name, location_file_name)
							watermark_with_transparency(
								location_file_name, 
								watermark_file_name,
								dest_dir+'/watermark.png', 
								position=(0,0))
							# ganti watermark_file_name dengan location_file_name apabila tanpa watermark
							bot.send_photo(cid, open(watermark_file_name, 'rb'))
							writeLog("[DEBUG]  : {0} | Send Chart Success ({1})".format(uid,m.text))
							if res == 1:
								sql = "INSERT INTO command (user_id,command,date,type,status) VALUES (%s, %s, CURDATE(), %s, %s);"
								val = (m.from_user.id,m.text,"user",1)
								cursor.execute(sql, val)
								db.commit()
							else:
								sql = "INSERT INTO command (user_id,command,date,type,status) VALUES (%s, %s, CURDATE(), %s, %s);"
								val = (cid,m.text,"group",1)
								cursor.execute(sql, val)
								db.commit()
						except Exception as e:
							element_body = WebDriverWait(driver, 20).until(EC1.presence_of_element_located((By.TAG_NAME, "body")))
							element_body.send_keys(Keys.ESCAPE)
							writeLog("[ERROR]  : {0} | {1}".format(cid,e))
							bot.send_message(cid, "Sorry something went wrong, try again!")
							if res == 1:
								sql = "INSERT INTO command (user_id,command,date,type,status) VALUES (%s, %s, CURDATE(), %s, %s);"
								val = (m.from_user.id,m.text,"user",0)
								cursor.execute(sql, val)
								db.commit()
							else:
								sql = "INSERT INTO command (user_id,command,date,type,status) VALUES (%s, %s, CURDATE(), %s, %s);"
								val = (cid,m.text,"group",0)
								cursor.execute(sql, val)
								db.commit()
						waitUsers.remove(uid)
					else:
						bot.reply_to(m, "Sorry your command structure was wrong.\nUse : /gicsignal [pair chart] [timeframe]")
				else:
					bot.reply_to(m, "Sorry your command structure was wrong.\nUse : /gicsignal [pair chart] [timeframe]")
			elif res == 4 :
				bot.reply_to(m, "Sorry, your user quota has expired and group qouta is 0")
			else:
				bot.reply_to(m, "Sorry, your user quota is 0 and group qouta is 0")
		else:
			bot.reply_to(m, "Please use " + str(m.text) + " command in your group")
	except Exception as e:
		bot.reply_to(m, "An error occurred or the internet connection lost. Please try again.")
		writeLog("[ERROR]  : {0} | {1}".format(cid,e))


# chat_action tradingview
@bot.message_handler(commands=['gicwin'])
def command_signal(m):
	cid = m.chat.id
	try:
		if m.chat.type == "group" or m.chat.type == "supergroup" :
			sql_user = "SELECT * FROM users WHERE chat_id={}".format(m.from_user.id)
			cursor.execute(sql_user)
			users = cursor.fetchone()
			if users:
				writeLog("[DEBUG]  : "+str(m.from_user.first_name) + " [" + str(m.from_user.id) + "]: " + "Registered User")
			else:
				sql = "INSERT INTO users (chat_id, first_name, username, kouta, exp_date, admin) VALUES (%s, %s, %s, %s, %s, %s);"
				val = (m.from_user.id,m.from_user.first_name,m.from_user.username,0,"0000-00-00",False)
				cursor.execute(sql, val)
				db.commit()
			group_title = m.chat.title
			uid = m.from_user.id
			first_name = m.from_user.first_name
			username = m.from_user.username
			res = qoutaUser(uid,cid,first_name,username,group_title)
			if res >=1 and res <= 3:
				message = str(m.text).split(" ")
				if len(message) > 1:
					if message[0] and message[1] : #filter command
						#antrian command 
						waitUsers.append(uid) #ambil nomor antrian setelah terfilter
						if len(waitUsers) > 1:
							writeLog("[DEBUG]  : {0} | Waiting other command ({1}) ".format(uid,m.text))
							bot.reply_to(m, "Please wait other command ({}) ...".format(len(waitUsers)-1))
							bot.send_chat_action(cid, 'typing')  # show the bot "typing" (max. 5 secs)
							waittime = (5 + TIME_LOADING) * len(waitUsers)
							time.sleep(waittime)
						else : 
							bot.reply_to(m, "Please wait ({}) ...".format(len(waitUsers)-1))
							bot.send_chat_action(cid, 'typing')  # show the bot "typing" (max. 5 secs)
						driver.get(URL2)
						time.sleep(3) #jeda 3 detik menunggu web tampil sempurna
						try:
							WebDriverWait(driver, 3).until(EC1.alert_is_present(),
							'Timed out waiting for PA creation ' +
							'confirmation popup to appear.')	
							alert = driver.switch_to.alert
							alert.accept()
							writeLog("[DEBUG]  : {0} | Alert Accepted ({1})".format(uid,m.text))
						except TimeoutException:
							writeLog("[DEBUG]  : {0} | No Alert ({1})".format(uid,m.text))
						try:
							element_body = WebDriverWait(driver, 20).until(EC1.presence_of_element_located((By.TAG_NAME, "body")))
							search = WebDriverWait(element_body, 20).until(EC1.presence_of_element_located((By.ID, "header-toolbar-symbol-search")))
							search.click()
							search_box = WebDriverWait(element_body, 20).until(EC1.presence_of_element_located((By.ID, "overlap-manager-root")))
							search_input = WebDriverWait(search_box, 20).until(EC1.presence_of_element_located((By.TAG_NAME, "input")))
							time.sleep(1) #jeda 1 detik untuk menunggu box pair muncul
							search_input.send_keys("OANDA:"+str(message[1]))
							time.sleep(1) #jeda 1 detik untuk pair
							search_input.send_keys(Keys.ENTER)
							if len(message) > 2:
								time.sleep(1) #jeda satu detik untuk menampilkan chart
								element_body.send_keys(0)
								interval = WebDriverWait(element_body, 20).until(EC1.presence_of_element_located((By.ID, "overlap-manager-root")))
								interval_input = WebDriverWait(interval, 20).until(EC1.presence_of_element_located((By.TAG_NAME, "input")))
								time.sleep(1) #jeda 1 detik untuk menampilkan timefram box
								interval_input.send_keys(message[2])
								time.sleep(1) #jeda 1 detik untuk menampilkan chart
								interval_input.send_keys(Keys.ENTER)
							else: 
								time.sleep(1) #jeda satu detik untuk menampilkan chart
								element_body.send_keys(0)
								interval = WebDriverWait(element_body, 20).until(EC1.presence_of_element_located((By.ID, "overlap-manager-root")))
								interval_input = WebDriverWait(interval, 20).until(EC1.presence_of_element_located((By.TAG_NAME, "input")))
								time.sleep(1) #jeda 1 detik untuk menampilkan timefram box
								element_body.send_keys("1D")
								time.sleep(1) #jeda 1 detik untuk menampilkan chart
								element_body.send_keys(Keys.ENTER)
							time.sleep(TIME_LOADING)
							ActionChains(driver).key_down(Keys.ALT).send_keys('s').perform()
							element = WebDriverWait(driver, 20).until(EC1.element_to_be_clickable((By.LINK_TEXT, 'Save image')))
							element.click()
							time.sleep(3) #proses simpan image
							filename = str(element.get_attribute('href')).split("/")[4]+".png"
							element_body.send_keys(Keys.ESCAPE)
							new_name = time.strftime("%Y-%m-%d_%H%M%S") + ".png"
							dest_dir = os.path.abspath(os.getcwd())
							current_file_name = CURRENT_FILE+"/"+filename
							location_file_name = dest_dir+"/image/"+new_name
							watermark_file_name = dest_dir+"/watermark/"+new_name
							os.rename(current_file_name, location_file_name)
							watermark_with_transparency(
								location_file_name, 
								watermark_file_name,
								dest_dir+'/watermark.png', 
								position=(0,0))
							# ganti watermark_file_name dengan location_file_name apabila tanpa watermark
							bot.send_photo(cid, open(watermark_file_name, 'rb'))
							writeLog("[DEBUG]  : {0} | Send Chart Success ({1})".format(uid,m.text))
							if res == 1:
								sql = "INSERT INTO command (user_id,command,date,type,status) VALUES (%s, %s, CURDATE(), %s, %s);"
								val = (m.from_user.id,m.text,"user",1)
								cursor.execute(sql, val)
								db.commit()
							else:
								sql = "INSERT INTO command (user_id,command,date,type,status) VALUES (%s, %s, CURDATE(), %s, %s);"
								val = (cid,m.text,"group",1)
								cursor.execute(sql, val)
								db.commit()
						except Exception as e:
							element_body = WebDriverWait(driver, 20).until(EC1.presence_of_element_located((By.TAG_NAME, "body")))
							element_body.send_keys(Keys.ESCAPE)
							writeLog("[ERROR]  : {0} | {1}".format(cid,e))
							bot.send_message(cid, "Sorry something went wrong, try again!")
							if res == 1:
								sql = "INSERT INTO command (user_id,command,date,type,status) VALUES (%s, %s, CURDATE(), %s, %s);"
								val = (m.from_user.id,m.text,"user",0)
								cursor.execute(sql, val)
								db.commit()
							else:
								sql = "INSERT INTO command (user_id,command,date,type,status) VALUES (%s, %s, CURDATE(), %s, %s);"
								val = (cid,m.text,"group",0)
								cursor.execute(sql, val)
								db.commit()
						waitUsers.remove(uid)
					else:
						bot.reply_to(m, "Sorry your command structure was wrong.\nUse : /gicwin [pair chart] [timeframe]")
				else:
					bot.reply_to(m, "Sorry your command structure was wrong.\nUse : /gicwin [pair chart] [timeframe]")
			elif res == 4 :
				bot.reply_to(m, "Sorry, your user quota has expired and group qouta is 0")
			else:
				bot.reply_to(m, "Sorry, your user quota is 0 and group qouta is 0")
		else:
			bot.reply_to(m, "Please use " + str(m.text) + " command in your group")
	except Exception as e:
		bot.reply_to(m, "An error occurred or the internet connection lost. Please try again.")
		writeLog("[ERROR]  : {0} | {1}".format(cid,e))

# chat_action tradingview
@bot.message_handler(commands=['gicrrg'])
def command_signal(m):
	cid = m.chat.id
	try:
		if m.chat.type == "group" or m.chat.type == "supergroup" :
			sql_user = "SELECT * FROM users WHERE chat_id={}".format(m.from_user.id)
			cursor.execute(sql_user)
			users = cursor.fetchone()
			if users:
				writeLog("[DEBUG]  : "+str(m.from_user.first_name) + " [" + str(m.from_user.id) + "]: " + "Registered User")
			else:
				sql = "INSERT INTO users (chat_id, first_name, username, kouta, exp_date, admin) VALUES (%s, %s, %s, %s, %s, %s);"
				val = (m.from_user.id,m.from_user.first_name,m.from_user.username,0,"0000-00-00",False)
				cursor.execute(sql, val)
				db.commit()
			group_title = m.chat.title
			uid = m.from_user.id
			first_name = m.from_user.first_name
			username = m.from_user.username
			res = qoutaUser(uid,cid,first_name,username,group_title)
			if res >=1 and res <= 3:
				message = str(m.text).split(" ")
				if len(message) > 1:
					if message[0] and message[1] :  #Melakukan filter jika command mengandung /signaln-[0] dan pair-[1] akan dieksekusi
						#setelah mengandung 2 parameter diatas maka masuk antrian
						waitUsers.append(uid) #ambil nomor antrian setelah terfilter
						if len(waitUsers) > 1:
							writeLog("[DEBUG]  : {0} | Waiting other command ({1}) ".format(uid,m.text))
							bot.reply_to(m, "Please wait other command ({}) ...".format(len(waitUsers)-1))
							bot.send_chat_action(cid, 'typing')  # show the bot "typing" (max. 5 secs)
							waittime = (5 + TIME_LOADING) * len(waitUsers)
							time.sleep(waittime)
						else : 
							bot.reply_to(m, "Please wait ({}) ...".format(len(waitUsers)-1))
							bot.send_chat_action(cid, 'typing')  # show the bot "typing" (max. 5 secs)
						driver.get(URL3)
						time.sleep(3) #waktu jeda saat url diakses menunggu web tampil sempurna
						try:
							WebDriverWait(driver, 3).until(EC1.alert_is_present(),
							'Timed out waiting for PA creation ' +
							'confirmation popup to appear.')
							alert = driver.switch_to.alert
							alert.accept()
							writeLog("[DEBUG]  : {0} | Alert Accepted ({1})".format(uid,m.text))
						except TimeoutException:
							writeLog("[DEBUG]  : {0} | No Alert ({1})".format(uid,m.text))					
						try:
							element_body = WebDriverWait(driver, 20).until(EC1.presence_of_element_located((By.TAG_NAME, "body")))
							search = WebDriverWait(element_body, 20).until(EC1.presence_of_element_located((By.ID, "header-toolbar-symbol-search")))
							search.click()
							search_box = WebDriverWait(element_body, 20).until(EC1.presence_of_element_located((By.ID, "overlap-manager-root")))
							search_input = WebDriverWait(search_box, 20).until(EC1.presence_of_element_located((By.TAG_NAME, "input")))
							time.sleep(1) #Menunggu tampilan box pairnya
							search_input.send_keys("OANDA:"+str(message[1]))
							time.sleep(1) #Jeda 1 detik bot memasukan pair ke dalam box
							search_input.send_keys(Keys.ENTER)
							if len(message) > 2:
								time.sleep(1) #jeda 1 detik menunggu chart muncul
								element_body.send_keys(0)
								interval = WebDriverWait(element_body, 20).until(EC1.presence_of_element_located((By.ID, "overlap-manager-root")))
								interval_input = WebDriverWait(interval, 20).until(EC1.presence_of_element_located((By.TAG_NAME, "input")))
								time.sleep(1) #jeda 1 detik menunggu box timeframe muncul
								interval_input.send_keys(message[2])
								time.sleep(1) #jeda 1 detik menunggu chart tampil
								interval_input.send_keys(Keys.ENTER)
							else: 
								time.sleep(1) #jeda 1 detik menunggu chart muncul
								element_body.send_keys(0)
								interval = WebDriverWait(element_body, 20).until(EC1.presence_of_element_located((By.ID, "overlap-manager-root")))
								interval_input = WebDriverWait(interval, 20).until(EC1.presence_of_element_located((By.TAG_NAME, "input")))
								time.sleep(1) #jeda 1 detik menunggu box timeframe muncul
								element_body.send_keys("1D")
								time.sleep(1) #jeda 1 detik menunggu chart tampil
								element_body.send_keys(Keys.ENTER)
							time.sleep(TIME_LOADING)
							ActionChains(driver).key_down(Keys.ALT).send_keys('s').perform()
							element = WebDriverWait(driver, 20).until(EC1.element_to_be_clickable((By.LINK_TEXT, 'Save image')))
							element.click()
							time.sleep(3) #jeda 2 detik untuk menunggu proses simpan image
							filename = str(element.get_attribute('href')).split("/")[4]+".png"
							element_body.send_keys(Keys.ESCAPE)
							new_name = time.strftime("%Y-%m-%d_%H%M%S") + ".png"
							dest_dir = os.path.abspath(os.getcwd())
							current_file_name = CURRENT_FILE+"/"+filename
							location_file_name = dest_dir+"/image/"+new_name
							watermark_file_name = dest_dir+"/watermark/"+new_name
							os.rename(current_file_name, location_file_name)
							watermark_with_transparency(
								location_file_name, 
								watermark_file_name,
								dest_dir+'/watermark.png', 
								position=(0,0))
							# ganti watermark_file_name dengan location_file_name apabila tanpa watermark
							bot.send_photo(cid, open(watermark_file_name, 'rb'))
							writeLog("[DEBUG]  : {0} | Send Chart Success ({1})".format(uid,m.text))
							if res == 1:
								sql = "INSERT INTO command (user_id,command,date,type,status) VALUES (%s, %s, CURDATE(), %s, %s);"
								val = (m.from_user.id,m.text,"user",1)
								cursor.execute(sql, val)
								db.commit()
							else:
								sql = "INSERT INTO command (user_id,command,date,type,status) VALUES (%s, %s, CURDATE(), %s, %s);"
								val = (cid,m.text,"group",1)
								cursor.execute(sql, val)
								db.commit()
						except Exception as e:
							element_body = WebDriverWait(driver, 20).until(EC1.presence_of_element_located((By.TAG_NAME, "body")))
							element_body.send_keys(Keys.ESCAPE)
							writeLog("[ERROR]  : {0} | {1}".format(cid,e))
							bot.send_message(cid, "Sorry something went wrong, try again!")
							if res == 1:
								sql = "INSERT INTO command (user_id,command,date,type,status) VALUES (%s, %s, CURDATE(), %s, %s);"
								val = (m.from_user.id,m.text,"user",0)
								cursor.execute(sql, val)
								db.commit()
							else:
								sql = "INSERT INTO command (user_id,command,date,type,status) VALUES (%s, %s, CURDATE(), %s, %s);"
								val = (cid,m.text,"group",0)
								cursor.execute(sql, val)
								db.commit()
						waitUsers.remove(uid)
					else:
						bot.reply_to(m, "Sorry your command structure was wrong.\nUse : /gicrrg [pair chart] [timeframe]")
				else:
					bot.reply_to(m, "Sorry your command structure was wrong.\nUse : /gicrrg [pair chart] [timeframe]")
			elif res == 4 :
				bot.reply_to(m, "Sorry, your user quota has expired and group qouta is 0")
			else:
				bot.reply_to(m, "Sorry, your user quota is 0 and group qouta is 0")
			
		else:
			bot.reply_to(m, "Please use " + str(m.text) + " command in your group")
	except Exception as e:
		bot.reply_to(m, "An error occurred or the internet connection lost. Please try again.")
		writeLog("[ERROR]  : {0} | {1}".format(cid,e))

# chat_action tradingview
@bot.message_handler(commands=['gicsd'])
def command_signal(m):
	cid = m.chat.id
	try:
		if m.chat.type == "group" or m.chat.type == "supergroup" :
			sql_user = "SELECT * FROM users WHERE chat_id={}".format(m.from_user.id)
			cursor.execute(sql_user)
			users = cursor.fetchone()
			if users:
				writeLog("[DEBUG]  : "+str(m.from_user.first_name) + " [" + str(m.from_user.id) + "]: " + "Registered User")
			else:
				sql = "INSERT INTO users (chat_id, first_name, username, kouta, exp_date, admin) VALUES (%s, %s, %s, %s, %s, %s);"
				val = (m.from_user.id,m.from_user.first_name,m.from_user.username,0,"0000-00-00",False)
				cursor.execute(sql, val)
				db.commit()
			group_title = m.chat.title
			uid = m.from_user.id
			first_name = m.from_user.first_name
			username = m.from_user.username
			res = qoutaUser(uid,cid,first_name,username,group_title)
			if res >=1 and res <= 3:
				message = str(m.text).split(" ")
				if len(message) > 1:
					if message[0] and message[1] :  #Melakukan filter jika command mengandung /signaln-[0] dan pair-[1] akan dieksekusi
						#setelah mengandung 2 parameter diatas maka masuk antrian
						waitUsers.append(uid) #ambil nomor antrian setelah terfilter
						if len(waitUsers) > 1:
							writeLog("[DEBUG]  : {0} | Waiting other command ({1}) ".format(uid,m.text))
							bot.reply_to(m, "Please wait other command ({}) ...".format(len(waitUsers)-1))
							bot.send_chat_action(cid, 'typing')  # show the bot "typing" (max. 5 secs)
							waittime = (5 + TIME_LOADING) * len(waitUsers)
							time.sleep(waittime)
						else : 
							bot.reply_to(m, "Please wait ({}) ...".format(len(waitUsers)-1))
							bot.send_chat_action(cid, 'typing')  # show the bot "typing" (max. 5 secs)
						driver.get(URL4)
						time.sleep(3) #waktu jeda saat url diakses menunggu web tampil sempurna
						try:
							WebDriverWait(driver, 3).until(EC1.alert_is_present(),
							'Timed out waiting for PA creation ' +
							'confirmation popup to appear.')
							alert = driver.switch_to.alert
							alert.accept()
							writeLog("[DEBUG]  : {0} | Alert Accepted ({1})".format(uid,m.text))
						except TimeoutException:
							writeLog("[DEBUG]  : {0} | No Alert ({1})".format(uid,m.text))					
						try:
							element_body = WebDriverWait(driver, 20).until(EC1.presence_of_element_located((By.TAG_NAME, "body")))
							search = WebDriverWait(element_body, 20).until(EC1.presence_of_element_located((By.ID, "header-toolbar-symbol-search")))
							search.click()
							search_box = WebDriverWait(element_body, 20).until(EC1.presence_of_element_located((By.ID, "overlap-manager-root")))
							search_input = WebDriverWait(search_box, 20).until(EC1.presence_of_element_located((By.TAG_NAME, "input")))
							time.sleep(1) #Menunggu tampilan box pairnya
							search_input.send_keys("OANDA:"+str(message[1]))
							time.sleep(1) #Jeda 1 detik bot memasukan pair ke dalam box
							search_input.send_keys(Keys.ENTER)
							if len(message) > 2:
								time.sleep(1) #jeda 1 detik menunggu chart muncul
								element_body.send_keys(0)
								interval = WebDriverWait(element_body, 20).until(EC1.presence_of_element_located((By.ID, "overlap-manager-root")))
								interval_input = WebDriverWait(interval, 20).until(EC1.presence_of_element_located((By.TAG_NAME, "input")))
								time.sleep(1) #jeda 1 detik menunggu box timeframe muncul
								interval_input.send_keys(message[2])
								time.sleep(1) #jeda 1 detik menunggu chart tampil
								interval_input.send_keys(Keys.ENTER)
							else: 
								time.sleep(1) #jeda 1 detik menunggu chart muncul
								element_body.send_keys(0)
								interval = WebDriverWait(element_body, 20).until(EC1.presence_of_element_located((By.ID, "overlap-manager-root")))
								interval_input = WebDriverWait(interval, 20).until(EC1.presence_of_element_located((By.TAG_NAME, "input")))
								time.sleep(1) #jeda 1 detik menunggu box timeframe muncul
								element_body.send_keys("1D")
								time.sleep(1) #jeda 1 detik menunggu chart tampil
								element_body.send_keys(Keys.ENTER)
							time.sleep(TIME_LOADING)
							ActionChains(driver).key_down(Keys.ALT).send_keys('s').perform()
							element = WebDriverWait(driver, 20).until(EC1.element_to_be_clickable((By.LINK_TEXT, 'Save image')))
							element.click()
							time.sleep(3) #jeda 2 detik untuk menunggu proses simpan image
							filename = str(element.get_attribute('href')).split("/")[4]+".png"
							element_body.send_keys(Keys.ESCAPE)
							new_name = time.strftime("%Y-%m-%d_%H%M%S") + ".png"
							dest_dir = os.path.abspath(os.getcwd())
							current_file_name = CURRENT_FILE+"/"+filename
							location_file_name = dest_dir+"/image/"+new_name
							watermark_file_name = dest_dir+"/watermark/"+new_name
							os.rename(current_file_name, location_file_name)
							watermark_with_transparency(
								location_file_name, 
								watermark_file_name,
								dest_dir+'/watermark.png', 
								position=(0,0))
							# ganti watermark_file_name dengan location_file_name apabila tanpa watermark
							bot.send_photo(cid, open(watermark_file_name, 'rb'))
							writeLog("[DEBUG]  : {0} | Send Chart Success ({1})".format(uid,m.text))
							if res == 1:
								sql = "INSERT INTO command (user_id,command,date,type,status) VALUES (%s, %s, CURDATE(), %s, %s);"
								val = (m.from_user.id,m.text,"user",1)
								cursor.execute(sql, val)
								db.commit()
							else:
								sql = "INSERT INTO command (user_id,command,date,type,status) VALUES (%s, %s, CURDATE(), %s, %s);"
								val = (cid,m.text,"group",1)
								cursor.execute(sql, val)
								db.commit()
						except Exception as e:
							element_body = WebDriverWait(driver, 20).until(EC1.presence_of_element_located((By.TAG_NAME, "body")))
							element_body.send_keys(Keys.ESCAPE)
							writeLog("[ERROR]  : {0} | {1}".format(cid,e))
							bot.send_message(cid, "Sorry something went wrong, try again!")
							if res == 1:
								sql = "INSERT INTO command (user_id,command,date,type,status) VALUES (%s, %s, CURDATE(), %s, %s);"
								val = (m.from_user.id,m.text,"user",0)
								cursor.execute(sql, val)
								db.commit()
							else:
								sql = "INSERT INTO command (user_id,command,date,type,status) VALUES (%s, %s, CURDATE(), %s, %s);"
								val = (cid,m.text,"group",0)
								cursor.execute(sql, val)
								db.commit()
						waitUsers.remove(uid)
					else:
						bot.reply_to(m, "Sorry your command structure was wrong.\nUse : /gicsd [pair chart] [timeframe]")
				else:
					bot.reply_to(m, "Sorry your command structure was wrong.\nUse : /gicsd [pair chart] [timeframe]")
			elif res == 4 :
				bot.reply_to(m, "Sorry, your user quota has expired and group qouta is 0")
			else:
				bot.reply_to(m, "Sorry, your user quota is 0 and group qouta is 0")
		else:
			bot.reply_to(m, "Please use " + str(m.text) + " command in your group")
	except Exception as e:
		bot.reply_to(m, "An error occurred or the internet connection lost. Please try again.")
		writeLog("[ERROR]  : {0} | {1}".format(cid,e))

# chat_action tradingview
@bot.message_handler(commands=['gicsw'])
def command_signal(m):
	cid = m.chat.id
	try:
		if m.chat.type == "group" or m.chat.type == "supergroup" :
			sql_user = "SELECT * FROM users WHERE chat_id={}".format(m.from_user.id)
			cursor.execute(sql_user)
			users = cursor.fetchone()
			if users:
				writeLog("[DEBUG]  : "+str(m.from_user.first_name) + " [" + str(m.from_user.id) + "]: " + "Registered User")
			else:
				sql = "INSERT INTO users (chat_id, first_name, username, kouta, exp_date, admin) VALUES (%s, %s, %s, %s, %s, %s);"
				val = (m.from_user.id,m.from_user.first_name,m.from_user.username,0,"0000-00-00",False)
				cursor.execute(sql, val)
				db.commit()
			group_title = m.chat.title
			uid = m.from_user.id
			first_name = m.from_user.first_name
			username = m.from_user.username
			res = qoutaUser(uid,cid,first_name,username,group_title)
			if res >=1 and res <= 3:
				message = str(m.text).split(" ")
				if len(message) > 1:
					if message[0] and message[1] :  #Melakukan filter jika command mengandung /signaln-[0] dan pair-[1] akan dieksekusi
						#setelah mengandung 2 parameter diatas maka masuk antrian
						waitUsers.append(uid) #ambil nomor antrian setelah terfilter
						if len(waitUsers) > 1:
							writeLog("[DEBUG]  : {0} | Waiting other command ({1}) ".format(uid,m.text))
							bot.reply_to(m, "Please wait other command ({}) ...".format(len(waitUsers)-1))
							bot.send_chat_action(cid, 'typing')  # show the bot "typing" (max. 5 secs)
							waittime = (5 + TIME_LOADING) * len(waitUsers)
							time.sleep(waittime)
						else : 
							bot.reply_to(m, "Please wait ({}) ...".format(len(waitUsers)-1))
							bot.send_chat_action(cid, 'typing')  # show the bot "typing" (max. 5 secs)
						driver.get(URL5)
						time.sleep(3) #waktu jeda saat url diakses menunggu web tampil sempurna
						try:
							WebDriverWait(driver, 3).until(EC1.alert_is_present(),
							'Timed out waiting for PA creation ' +
							'confirmation popup to appear.')
							alert = driver.switch_to.alert
							alert.accept()
							writeLog("[DEBUG]  : {0} | Alert Accepted ({1})".format(uid,m.text))
						except TimeoutException:
							writeLog("[DEBUG]  : {0} | No Alert ({1})".format(uid,m.text))					
						try:
							element_body = WebDriverWait(driver, 20).until(EC1.presence_of_element_located((By.TAG_NAME, "body")))
							search = WebDriverWait(element_body, 20).until(EC1.presence_of_element_located((By.ID, "header-toolbar-symbol-search")))
							search.click()
							search_box = WebDriverWait(element_body, 20).until(EC1.presence_of_element_located((By.ID, "overlap-manager-root")))
							search_input = WebDriverWait(search_box, 20).until(EC1.presence_of_element_located((By.TAG_NAME, "input")))
							time.sleep(1) #Menunggu tampilan box pairnya
							search_input.send_keys("OANDA:"+str(message[1]))
							time.sleep(1) #Jeda 1 detik bot memasukan pair ke dalam box
							search_input.send_keys(Keys.ENTER)
							if len(message) > 2:
								time.sleep(1) #jeda 1 detik menunggu chart muncul
								element_body.send_keys(0)
								interval = WebDriverWait(element_body, 20).until(EC1.presence_of_element_located((By.ID, "overlap-manager-root")))
								interval_input = WebDriverWait(interval, 20).until(EC1.presence_of_element_located((By.TAG_NAME, "input")))
								time.sleep(1) #jeda 1 detik menunggu box timeframe muncul
								interval_input.send_keys(message[2])
								time.sleep(1) #jeda 1 detik menunggu chart tampil
								interval_input.send_keys(Keys.ENTER)
							else: 
								time.sleep(1) #jeda 1 detik menunggu chart muncul
								element_body.send_keys(0)
								interval = WebDriverWait(element_body, 20).until(EC1.presence_of_element_located((By.ID, "overlap-manager-root")))
								interval_input = WebDriverWait(interval, 20).until(EC1.presence_of_element_located((By.TAG_NAME, "input")))
								time.sleep(1) #jeda 1 detik menunggu box timeframe muncul
								element_body.send_keys("1D")
								time.sleep(1) #jeda 1 detik menunggu chart tampil
								element_body.send_keys(Keys.ENTER)
							time.sleep(TIME_LOADING)
							ActionChains(driver).key_down(Keys.ALT).send_keys('s').perform()
							element = WebDriverWait(driver, 20).until(EC1.element_to_be_clickable((By.LINK_TEXT, 'Save image')))
							element.click()
							time.sleep(3) #jeda 2 detik untuk menunggu proses simpan image
							filename = str(element.get_attribute('href')).split("/")[4]+".png"
							element_body.send_keys(Keys.ESCAPE)
							new_name = time.strftime("%Y-%m-%d_%H%M%S") + ".png"
							dest_dir = os.path.abspath(os.getcwd())
							current_file_name = CURRENT_FILE+"/"+filename
							location_file_name = dest_dir+"/image/"+new_name
							watermark_file_name = dest_dir+"/watermark/"+new_name
							os.rename(current_file_name, location_file_name)
							watermark_with_transparency(
								location_file_name, 
								watermark_file_name,
								dest_dir+'/watermark.png', 
								position=(0,0))
							# ganti watermark_file_name dengan location_file_name apabila tanpa watermark
							bot.send_photo(cid, open(watermark_file_name, 'rb'))
							writeLog("[DEBUG]  : {0} | Send Chart Success ({1})".format(uid,m.text))
							if res == 1:
								sql = "INSERT INTO command (user_id,command,date,type,status) VALUES (%s, %s, CURDATE(), %s, %s);"
								val = (m.from_user.id,m.text,"user",1)
								cursor.execute(sql, val)
								db.commit()
							else:
								sql = "INSERT INTO command (user_id,command,date,type,status) VALUES (%s, %s, CURDATE(), %s, %s);"
								val = (cid,m.text,"group",1)
								cursor.execute(sql, val)
								db.commit()
						except Exception as e:
							element_body = WebDriverWait(driver, 20).until(EC1.presence_of_element_located((By.TAG_NAME, "body")))
							element_body.send_keys(Keys.ESCAPE)
							writeLog("[ERROR]  : {0} | {1}".format(cid,e))
							bot.send_message(cid, "Sorry something went wrong, try again!")
							if res == 1:
								sql = "INSERT INTO command (user_id,command,date,type,status) VALUES (%s, %s, CURDATE(), %s, %s);"
								val = (m.from_user.id,m.text,"user",0)
								cursor.execute(sql, val)
								db.commit()
							else:
								sql = "INSERT INTO command (user_id,command,date,type,status) VALUES (%s, %s, CURDATE(), %s, %s);"
								val = (cid,m.text,"group",0)
								cursor.execute(sql, val)
								db.commit()
					else:
						bot.reply_to(m, "Sorry your command structure was wrong.\nUse : /gicsw [pair chart] [timeframe]")
				else:
					bot.reply_to(m, "Sorry your command structure was wrong.\nUse : /gicsw [pair chart] [timeframe]")
			elif res == 4 :
				bot.reply_to(m, "Sorry, your user quota has expired and group qouta is 0")
			else:
				bot.reply_to(m, "Sorry, your user quota is 0 and group qouta is 0")
			waitUsers.remove(uid)
		else:
			bot.reply_to(m, "Please use " + str(m.text) + " command in your group")
	except Exception as e:
		bot.reply_to(m, "An error occurred or the internet connection lost. Please try again.")
		writeLog("[ERROR]  : {0} | {1}".format(cid,e))

@bot.message_handler(commands=['group_id'])
def command_getGroupID(m):
	cid = m.chat.id
	uid=  m.from_user.id
	try :
		if m.chat.type == "group" or m.chat.type == "supergroup" :
			sql = "SELECT * FROM groups WHERE group_id={}".format(m.chat.id)
			cursor.execute(sql)
			groups = cursor.fetchone()
			if groups:
				writeLog("[DEBUG]  : "+str(m.from_user.first_name) + " [" + str(m.from_user.id) + "]: " + "Registered Group")
			else:
				sql = "INSERT INTO groups (name,group_id,kouta) VALUES (%s, %s, %s);"
				val = (m.chat.title,m.chat.id,0)
				cursor.execute(sql, val)
				db.commit()
			bot.reply_to(m, "Hi {0}, your group ID : {1}".format(m.from_user.first_name,m.chat.id))
		else :
			bot.reply_to(m, "Please use " + str(m.text) + " command in your group")
	except Exception as e:
		bot.reply_to(m, "An error occurred or the internet connection lost. Please try again.")
		writeLog("[ERROR]  : {0} | {1}".format(cid,e))

@bot.message_handler(commands=['user_id'])
def command_getUsersID(m):
	cid = m.chat.id
	try:
		sql_user = "SELECT * FROM users WHERE chat_id={}".format(m.from_user.id)
		cursor.execute(sql_user)
		users = cursor.fetchone()
		if users:
			writeLog("[DEBUG]  : "+str(m.from_user.first_name) + " [" + str(m.from_user.id) + "]: " + "Registered User")
		else:
			sql = "INSERT INTO users (chat_id, first_name, username, kouta, exp_date, admin) VALUES (%s, %s, %s, %s, %s, %s);"
			val = (m.from_user.id,m.from_user.first_name,m.from_user.username,0,"0000-00-00",False)
			cursor.execute(sql, val)
			db.commit()
		chat_id = m.from_user.id
		first_name = m.from_user.first_name
		username = m.from_user.username
		bot.reply_to(m, "Hi {0}, your User ID : {1}".format(m.from_user.first_name,m.from_user.id))
	except Exception as e:
		bot.reply_to(m, "An error occurred or the internet connection lost. Please try again.")
		writeLog("[ERROR]  : {0} | {1}".format(cid,e))

@bot.message_handler(commands=['my_qouta'])
def command_getMyQouta(m):
	cid = m.chat.id
	try:
		if m.chat.type == "group" or m.chat.type == "supergroup" :
			bot.reply_to(m, "Please wait ...")
			bot.send_chat_action(cid, 'typing')
			uid = m.from_user.id
			group_id = m.chat.id
			first_name = m.from_user.first_name

			sql = "SELECT * FROM users WHERE chat_id={}".format(uid)
			cursor.execute(sql)
			users = cursor.fetchone()
			if users:
				qouta_user = users[4]
				exp_date = users[5]
			else:
				qouta_user = 0
				exp_date = "00-00-0000"

			sql = "SELECT * FROM groups WHERE group_id={}".format(group_id)
			cursor.execute(sql)
			groups = cursor.fetchone()
			if groups:
				qouta_group = groups[3]
			else:
				qouta_group = 0

			sql = """SELECT COUNT(*) FROM command WHERE date=CURDATE() and type='{0}' 
				and status=1 and user_id={1};""".format("user",uid)
			cursor.execute(sql)
			results_user = cursor.fetchone()
			if results_user:
				data_user = results_user[0]
			else:
				data_user = 0

			sql = """SELECT COUNT(*) FROM command WHERE date=CURDATE() and type='{0}' 
				and status=1 and user_id={1};""".format("group",group_id)
			cursor.execute(sql)
			results_group = cursor.fetchone()
			if results_group:
				data_group = results_group[0]
			else:
				data_group = 0
			user_now = qouta_user-data_user
			group_now = qouta_group-data_group
			msg_send='''
Hi {0},
Qouta User Today = {1}/{2}
Qouta Group Today = {3}/{4}
Exp Date Qouta User = {5}
	'''.format(first_name,user_now,qouta_user,group_now,qouta_group,exp_date)
			bot.reply_to(m,msg_send)
		else :
			bot.reply_to(m, "Please use " + str(m.text) + " command in your group")
	except Exception as e:
		bot.reply_to(m, "An error occurred or the internet connection lost. Please try again.")
		writeLog("[ERROR]  : {0} | {1}".format(cid,e))

@bot.message_handler(commands=['tdgAdmin'])
def command_registersersID(m):
	cid = m.chat.id
	try:
		uid=m.from_user.id
		first_name=m.from_user.first_name
		username=m.from_user.username

		sql = "SELECT * FROM users WHERE chat_id={}".format(uid)
		cursor.execute(sql)
		users = cursor.fetchone()
		if users:
			sql = "UPDATE users SET admin=%s WHERE chat_id=%s;"
			val = (True,uid)
			cursor.execute(sql, val)
			res = db.commit()
		else:
			sql = "INSERT INTO users (chat_id, first_name, username, kouta, exp_date, admin) VALUES (%s, %s, %s, %s, %s, %s);"
			val = (uid,first_name,username,0,"0000-00-00",True)
			cursor.execute(sql, val)
			db.commit()

		bot.reply_to(m, "Hi {0}, Update Status Success".format(m.from_user.first_name))
	except Exception as e:
		bot.reply_to(m, "An error occurred or the internet connection lost. Please try again.")
		writeLog("[ERROR]  : {0} | {1}".format(cid,e))

@bot.message_handler(commands=['getUserAll'])
def command_getUserAll(m):
	cid = m.chat.id
	try:
		if isAdmin(m.from_user.id):
			bot.reply_to(m, "Please wait ...")
			bot.send_chat_action(cid, 'typing')
			user_text = "The following list of your application users: \n"
			user_text += "ID USER|FIRST NAME|USERNAME|QUOTA|EXP DATE|ADMIN"+"\n"
			# users = mysql.searchUser()
			sql = "SELECT * FROM users "
			cursor.execute(sql)
			users = cursor.fetchall()
			for key in users: 
				if key[6]:
					s ="admin"
				else:
					s=""
				user_text += str(key[1])+" | "+str(key[2])+" | "+str(key[3])+" | "+str(key[4])+" | "+str(key[5])+" | "+s+"\n"
			bot.reply_to(m, user_text) 
		else:
			bot.reply_to(m, "Sorry you are not allowed access")
	except Exception as e:
		bot.reply_to(m, "An error occurred or the internet connection lost. Please try again.")
		writeLog("[ERROR]  : {0} | {1}".format(cid,e))

@bot.message_handler(commands=['getGroupAll'])
def command_getGroupAll(m):
	cid = m.chat.id
	try:
		if isAdmin(m.from_user.id):
			bot.reply_to(m, "Please wait ...")
			bot.send_chat_action(cid, 'typing')
			group_text = "The following list of your application groups: \n"
			group_text += "ID GROUP|NAME GROUP|QUOTA"+"\n"
			# groups = mysql.searchGroup()
			sql = "SELECT * FROM groups"
			cursor.execute(sql)
			groups = cursor.fetchall()
			for key in groups: 
				group_text += str(key[2])+" | "+str(key[1])+" | "+str(key[3])+"\n"
			bot.reply_to(m,group_text) 
		else:
			bot.reply_to(m, "Sorry you are not allowed access")
	except Exception as e:
		bot.reply_to(m, "An error occurred or the internet connection lost. Please try again.")
		writeLog("[ERROR]  : {0} | {1}".format(cid,e))

@bot.message_handler(commands=['getQuotaUser'])
def command_getQuotaUser(m):
	cid = m.chat.id
	try:
		msg_send='''
Please enter your user id!

*use /user_id to know your user id
'''
		msg = bot.reply_to(m, msg_send)
		bot.register_next_step_handler(msg,getqoutauser)
	except Exception as e:
		bot.reply_to(m, "An error occurred or the internet connection lost. Please try again.")
		writeLog("[ERROR]  : {0} | {1}".format(cid,e))

def getqoutauser(m):
	text = m.text
	cid=m.chat.id
	uid=m.from_user.id
	try:
		if '/user_id' in text:
			command_getUsersID(m)
		elif '/' not in text:
			bot.reply_to(m, "Please wait ...")
			bot.send_chat_action(cid, 'typing')
			# user_set[uid] = mysql.searchUserId(text)
			sql = "SELECT * FROM users WHERE chat_id={}".format(text)
			cursor.execute(sql)
			users = cursor.fetchone()
			if users:
				bot.reply_to(m, "Hi {0}, your user quota : {1}".format(m.from_user.first_name,users[4]))
			else :
				bot.reply_to(m, "Hi {0}, your user quota : {1}".format(m.from_user.first_name,0))
		else:
			bot.reply_to(m, "Sorry, your id is not found")
	except Exception as e:
		bot.reply_to(m, "An error occurred or the internet connection lost. Please try again.")
		writeLog("[ERROR]  : {0} | {1}".format(cid,e))

# set Qouta user message
@bot.message_handler(commands=['setQuotaUser'])
def command_setQuotaUser(m):
	cid = m.chat.id
	try:
		chat_id = m.from_user.id
		if isAdmin(chat_id):
			text = m.text
			msg_send='''
Please enter your user id!

*use /user_id to know your user id
'''
			msg = bot.reply_to(m, msg_send)
			bot.register_next_step_handler(msg,setqoutauser)
		else:
			bot.reply_to(m, "Sorry you are not allowed access")
	except Exception as e:
		bot.reply_to(m, "An error occurred or the internet connection lost. Please try again.")
		writeLog("[ERROR]  : {0} | {1}".format(cid,e))

def setqoutauser(m):
	text = m.text
	cid=m.chat.id
	uid=m.from_user.id
	try :
		chat_id = m.from_user.id
		msg_send='''
Enter your qouta user!
'''
		if '/user_id' in text:
			command_getUsersID(m)
		elif '/' not in text :
			bot.reply_to(m, "Please wait ...")
			bot.send_chat_action(cid, 'typing')
			# user_set[uid] = mysql.searchUserId(text)
			sql = "SELECT * FROM users WHERE chat_id={}".format(text)
			cursor.execute(sql)
			users = cursor.fetchone()
			if users:
				msg = bot.reply_to(m, msg_send)
				user = User(text)
				user_dict[chat_id] = user
				bot.register_next_step_handler(msg,setqoutauserproccess)
			else:
				bot.reply_to(m, "Sorry, your id is not found")
		else:
			bot.reply_to(m, "Sorry, your id is not found")
	except Exception as e:
		bot.reply_to(m, "An error occurred or the internet connection lost. Please try again.")
		writeLog("[ERROR]  : {0} | {1}".format(cid,e))

def setqoutauserproccess(m):
	text = m.text
	cid = m.chat.id
	try:
		chat_id = m.from_user.id
		user = user_dict[chat_id]
		user.kouta = text
		# res = mysql.updateUser(user.chat_id,user.kouta)
		sql = "UPDATE users SET kouta=%s WHERE chat_id=%s;"
		val = (user.kouta,user.chat_id)
		cursor.execute(sql, val)
		res = db.commit()
		msg = bot.reply_to(m, "Set user quota success")
	except Exception as e:
		bot.reply_to(m, "An error occurred or the internet connection lost. Please try again.")
		writeLog("[ERROR]  : {0} | {1}".format(cid,e))
		
# get Qouta group message
@bot.message_handler(commands=['getQuotaGroup'])
def command_getQuotaGroup(m):
	cid = m.chat.id
	try:
		chat_id = m.from_user.id
		if isAdmin(chat_id):
			msg_send='''
Please enter your group id!

*use /group_id to know group id in your group
'''
			msg = bot.reply_to(m, msg_send)
			bot.register_next_step_handler(msg,getqoutagroup)
		else:
			bot.reply_to(m, "Sorry you are not allowed access")
	except Exception as e:
		bot.reply_to(m, "An error occurred or the internet connection lost. Please try again.")
		writeLog("[ERROR]  : {0} | {1}".format(cid,e))

def getqoutagroup(m):
	cid = m.chat.id
	uid = m.from_user.id
	text = m.text
	try:
		chat_id = m.from_user.id
		if '/group_id' in text:
			command_getGroupID(m)
		elif '/' not in text:
			bot.reply_to(m, "Please wait ...")
			bot.send_chat_action(cid, 'typing')
			sql = "SELECT * FROM groups WHERE group_id={}".format(text)
			cursor.execute(sql)
			groups = cursor.fetchone()
			if groups:
				msg_send_found='''
Your group qouta {}
'''.format(groups[3])
				bot.reply_to(m, msg_send_found)
			else:
				msg_send_notfound='''
Group quota has not been set!
Please enter /setQuotaGroup to set group qouta.
			'''
				bot.reply_to(m, msg_send_notfound)
		else:
			bot.reply_to(m, "Sorry, your id is not found")
	except Exception as e:
		bot.reply_to(m, "An error occurred or the internet connection lost. Please try again.")
		writeLog("[ERROR]  : {0} | {1}".format(cid,e))

# set Qouta group message
@bot.message_handler(commands=['setQuotaGroup'])
def command_setQuotaGroup(m):
	cid = m.chat.id
	text = m.text
	try:
		chat_id = m.from_user.id
		if isAdmin(chat_id):
			text = m.text
			msg_send='''
Please enter your group id!

*use /group_id to know group id in your group
'''
			msg = bot.reply_to(m, msg_send)
			bot.register_next_step_handler(msg,setqoutagroup)
		else:
			bot.reply_to(m, "Sorry you are not allowed access")
	except Exception as e:
		bot.reply_to(m, "An error occurred or the internet connection lost. Please try again.")
		writeLog("[ERROR]  : {0} | {1}".format(cid,e))

def setqoutagroup(m):
	cid = m.chat.id
	uid=m.from_user.id
	text = m.text
	try:
		chat_id = m.from_user.id
		if '/group_id' in text:
			command_getGroupID(m)
		elif '/' not in text:
			bot.reply_to(m, "Please wait ...")
			bot.send_chat_action(cid, 'typing')
			sql = "SELECT * FROM groups WHERE group_id={}".format(text)
			cursor.execute(sql)
			groups = cursor.fetchone()
			group = Group(text)
			group_dict[chat_id] = group
			if groups:
				msg_send_found='''
Your group qouta {} 
Enter the group quota!
				'''.format(groups[3])
				msg = bot.reply_to(m, msg_send_found)
				bot.register_next_step_handler(msg,setqoutaprosess)
			else :
				msg_send_notfound='''
Group quota has not been set!
Enter the group quota!
				'''
				msg = bot.reply_to(m, msg_send_notfound)
				bot.register_next_step_handler(msg,setqoutanfprosess)
		else:
			bot.reply_to(m, "Sorry, your id is not found")
	except Exception as e:
		bot.reply_to(m, "An error occurred or the internet connection lost. Please try again.")
		writeLog("[ERROR]  : {0} | {1}".format(cid,e))

def setqoutaprosess(m):
	cid = m.chat.id
	text = m.text
	try:
		chat_id = m.from_user.id
		group = group_dict[chat_id]
		group.kouta = text
		sql = "UPDATE groups SET kouta=%s WHERE group_id=%s;"
		val = (group.kouta,group.group_id)
		cursor.execute(sql, val)
		db.commit()
		bot.reply_to(m, "Set group quota success")
	except Exception as e:
		bot.reply_to(m, "An error occurred or the internet connection lost. Please try again.")
		writeLog("[ERROR]  : {0} | {1}".format(cid,e))

def setqoutanfprosess(m):
	cid = m.chat.id
	text = m.text
	try:
		chat_id = m.from_user.id
		group = group_dict[chat_id]
		group.kouta = text
		title = m.chat.title
		# res = mysql.insertGroup(title,group.group_id,group.kouta)
		sql = "INSERT INTO groups (name,group_id,kouta) VALUES (%s, %s, %s);"
		val = (title,group.group_id,group.kouta)
		cursor.execute(sql, val)
		db.commit()
		msg = bot.reply_to(m, "Set group quota success")
	except Exception as e:
		bot.reply_to(m, "An error occurred or the internet connection lost. Please try again.")
		writeLog("[ERROR]  : {0} | {1}".format(cid,e))

# set Exp Date user message
@bot.message_handler(commands=['setExpDate'])
def command_setExpDate(m):
	cid = m.chat.id
	try:
		chat_id = m.from_user.id
		if isAdmin(chat_id):
			text = m.text
			msg_send='''
Please enter your user id!

*use /user_id to know your user id
'''
			msg = bot.reply_to(m, msg_send)
			bot.register_next_step_handler(msg,setexpdate)
		else:
			bot.reply_to(m, "Sorry you are not allowed access")
	except Exception as e:
		bot.reply_to(m, "An error occurred or the internet connection lost. Please try again.")
		writeLog("[ERROR]  : {0} | {1}".format(cid,e))

def setexpdate(m):
	text = m.text
	cid=m.chat.id
	try :
		chat_id = m.from_user.id
		msg_send='''
Enter your exp date user!
Format : DD-MM-YYYY
'''
		if '/user_id' in text:
			command_getUsersID(m)
		elif '/' not in text :
			bot.reply_to(m, "Please wait ...")
			bot.send_chat_action(cid, 'typing')
			msg = bot.reply_to(m, msg_send)
			user = User(text)
			user_dict[chat_id] = user
			bot.register_next_step_handler(msg,setexpdateproccess)
		else:
			bot.reply_to(m, "Sorry, your id is not found")
	except Exception as e:
		bot.reply_to(m, "An error occurred or the internet connection lost. Please try again.")
		writeLog("[ERROR]  : {0} | {1}".format(cid,e))

def setexpdateproccess(m):
	cid = m.chat.id
	text = m.text
	try:
		chat_id = m.from_user.id
		user = user_dict[chat_id]
		tgl = str(text).split("-")
		user.exp_date = tgl[2]+"-"+tgl[1]+"-"+tgl[0]
		# res = mysql.updateUserDate(user.chat_id,user.exp_date)
		sql = "UPDATE users SET exp_date=%s WHERE chat_id=%s;"
		val = (user.exp_date,user.chat_id)
		cursor.execute(sql, val)
		db.commit()
		msg = bot.reply_to(m, "Set exp date user success")
	except Exception as e:
		bot.reply_to(m, "An error occurred or the internet connection lost. Please try again.")
		writeLog("[ERROR]  : {0} | {1}".format(cid,e))

@bot.message_handler(commands=['send_log'])
def command_sendLog(m):
	cid = m.chat.id
	try:
		bot.reply_to(m, "Please wait ...")
		bot.send_chat_action(cid, 'typing')
		bot.send_document(cid, open(LOGFILE, 'rb'))
	except Exception as e:
		bot.reply_to(m, "An error occurred or the internet connection lost. Please try again.")
		writeLog("[ERROR]  : {0} | {1}".format(cid,e))

# filter on a specific message
@bot.message_handler(func=lambda message: message.text == "hi")
def command_text_hi(m):
	if m.chat.type == "private":
		bot.send_message(m.chat.id, "Hi {}".format(m.chat.first_name))

# default handler for every other text
@bot.message_handler(func=lambda message: True, content_types=['text'])
def command_default(m):
	# this is the standard reply to a normal message
	if m.chat.type =="private":
		bot.send_message(m.chat.id, "I don't understand \"" + m.text + "\"\nMaybe try the help page at /help")

# Enable saving next step handlers to file "./.handlers-saves/step.save".
# Delay=2 means that after any change in next step handlers (e.g. calling register_next_step_handler())
# saving will hapen after delay 2 seconds.
bot.enable_save_next_step_handlers(delay=2)

# Load next_step_handlers from save file (default "./.handlers-saves/step.save")
# WARNING It will work only if enable_save_next_step_handlers was called!
bot.load_next_step_handlers()

if __name__ == '__main__':
	writeLog("[DEBUG]  : Bot Running!")
	bot.polling(none_stop=True)