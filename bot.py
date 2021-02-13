import config
import telebot
from telebot import types
import sqlite3
from telebot import apihelper
import random
from IPython import embed

apihelper.proxy = {'https':'socks5h://localhost:9050'}

bot = telebot.TeleBot(config.token)
con=sqlite3.connect("db.db", check_same_thread=False)


@bot.message_handler(content_types=["text"])
def answer(message):
	
	#db.logger.insert({'chat_id':message.chat.id,'time':time.time(),'message':message.text, 'chat_username':message.chat.username})
	if message.text == '/start' or message.text == 'start':
		main_menu(message,"Выберете что хотите приготовить:")



		#bot.send_message_md(message.chat.id, '/help - справка\n/registration - регистрация\nПо всем вопросам просьба обращаться в группу https://t.me/infosec_career\n', reply_markup=None, parse_mode="Markdown")

	elif message.text == '/help' or message.text == 'help':
		bot.send_message(message.chat.id, '''/help - справка''')

	elif message.text in ferst_menu():
		random_food(message,message.text)
	elif message.text =="Готовим!":
		keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
		button_yes_rec = types.KeyboardButton(text="Да")
		button_no_rec = types.KeyboardButton(text="Нет, знаю)")
		keyboard.add(button_yes_rec,button_no_rec)
		bot.send_message(message.chat.id,'Нужен рецепт??? :-)',reply_markup=keyboard)
	elif message.text=="Добавить":
		keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True, one_time_keyboard=True)
		a=0
		for e in range(0,(len(ferst_menu())//2)):
			button_1 = types.KeyboardButton(text=ferst_menu()[a]+"_new")
			button_2 = types.KeyboardButton(text=ferst_menu()[a+1]+"_new")
			keyboard.row(button_1, button_2)
			a=a+2
		bot.send_message(message.chat.id,'Выберете что хотите добавить:',reply_markup=keyboard)
	elif message.text in dobavit():
		type_=message.text.split("_")[0]
		sent=bot.send_message(message.chat.id, 'Введите название:')
		bot.register_next_step_handler(sent, get_name,type_)

def main_menu(message,text):
	keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True, one_time_keyboard=True)
	a=0
	for e in range(0,(len(ferst_menu())//2)):
		button_1 = types.KeyboardButton(text=ferst_menu()[a])
		button_2 = types.KeyboardButton(text=ferst_menu()[a+1])
		keyboard.row(button_1, button_2)
		a=a+2
		#for e  in ferst_menu():
			#button = types.KeyboardButton(text=e)
			#keyboard.add(button)
	button_new=types.KeyboardButton(text="Добавить")
	keyboard.add(button_new)
	bot.send_message(message.chat.id,text,reply_markup=keyboard)

def get_name(message,type_):
	name=message.text
	sent=bot.send_message(message.chat.id, 'Введите продукты,необходимые для готовки:')
	bot.register_next_step_handler(sent, get_products, name,type_)

def get_products(message,name,type_):
	products=message.text
	sent=bot.send_message(message.chat.id, 'Введите рецепт:')
	bot.register_next_step_handler(sent, save_new_recept, name,products,type_)

def save_new_recept(message,name,products,type_):
	recept_new=message.text
	cur=con.cursor()
	cur.execute("INSERT into Food(Name,Comment,Type,Recept,Composition,Photo)  VALUES(?,?,?,?,?,?)",
		(name,"",type_,recept_new,products,""))
	con.commit()
	cur.close()
	main_menu(message,"Рецепт добавлен!!! Что то хотите приготовить сейчас?")


def dobavit():
	cur=con.cursor()
	cur.execute("SELECT * from Type")
	a=cur.fetchall()
	cur.close()
	return([e[0]+"_new" for e in a if e[0]])


def ferst_menu():
	cur=con.cursor()
	cur.execute("SELECT * from Type")
	a=cur.fetchall()
	cur.close()
	return([e[0] for e in a])

def choose_food(q):
	cur=con.cursor()
	cur.execute("SELECT Name from Food where Type=?",(q,))
	a=cur.fetchall()
	cur.close()
	f=[e[0] for e in a]
	int_ren=random.randint(0,len(f)-1)
	return(f[int_ren])


def random_food(message,food_type):
	result=choose_food(food_type)
	bot.send_message(message.chat.id,result)
	keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
	button_yes = types.KeyboardButton(text="Готовим!")
	button_no = types.KeyboardButton(text="Другое блюдо...")
	keyboard.add(button_yes,button_no)
	sent = bot.send_message(message.chat.id,'Готовим??? :-)',reply_markup=keyboard)
	bot.register_next_step_handler(sent, choose_or_not, food_type,result)

def take_composion(message,result):
	if message.text=="Да":
		cur=con.cursor()
		cur.execute("SELECT Composition from Food where Name=?",(result,))
		a=cur.fetchall()
		cur.close()
		bot.send_message(message.chat.id,a)
		main_menu(message,a)
	elif message.text == "Нет":
		main_menu(message,"Что то хотите приготовить еще сейчас?")



def choose_or_not(message,food_type,result):
	if message.text=="Другое блюдо...":
		random_food(message,food_type)
	elif message.text == "Готовим!":
		cur=con.cursor()
		cur.execute("SELECT Recept from Food where Name=?",(result,))
		a=cur.fetchall()
		cur.close()
		bot.send_message(message.chat.id,a)
		keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
		button_yes = types.KeyboardButton(text="Да")
		button_no = types.KeyboardButton(text="Нет")
		keyboard.add(button_yes,button_no)
		sent = bot.send_message(message.chat.id,'Нужен список продуктов?',reply_markup=keyboard)
		bot.register_next_step_handler(sent, take_composion,result)

if __name__ == '__main__':
	bot.polling(none_stop=True)