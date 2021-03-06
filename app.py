from flask import Flask, session, render_template, request, abort, redirect, url_for, flash, send_from_directory
import os
from functools import wraps
from flask_bcrypt import generate_password_hash, check_password_hash
import sqlite3

con=sqlite3.connect("db.db", check_same_thread=False)

app = Flask(__name__)

SECRET_KEY = 'X8jdfhjfdhuuueppqxnniwigrewyvz;zziuIEYVIWEI77IVuvvIUI7TyO6d'
app.config.from_object(__name__)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                          'favicon.ico',mimetype='image/vnd.microsoft.icon')

def login_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if 'user' not in session:
			flash('Login please!')
			return redirect(url_for('login'))
		return f(*args, **kwargs)
	return decorated_function

def session_login(username):
	session['user'] = username


def get_user():
	login = 'user' in session	
	if login:
		login=session['user']
		return (True, login)
	return (False, None)

@app.route('/', methods=['GET'])
def null():
	if request.method == 'GET':
		if get_user()[0]:
			return redirect(url_for('menu_action'))
		else:
			return redirect(url_for('login'))



@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'GET':
		return render_template('login.html')
	elif request.method == 'POST':
		username = request.form['login']
		passw = request.form['password']

		cur=con.cursor()
		cur.execute("SELECT pass from Users where login=?",(username,))
		a=cur.fetchall()
		cur.close()
		if a:
			if check_password_hash(a[0][0],passw):
				session_login(username)
				return redirect(url_for('menu_action'))
			else:
				return render_template('login.html')

		else:
			return render_template('login.html')
#		else:
#			if check_password_hash(user['password'],passw):
#				session_login(username)
#				return redirect(url_for('secret'))
	else:
		return abort(405)


@app.route('/add',methods=['GET', 'POST'])
@login_required
def index():
	if request.method == 'GET':
		login,user=get_user()
		if login:
			cur=con.cursor()
			cur.execute("SELECT Type from Type")
			Food_types=[e[0] for e in cur.fetchall()]
			print(Food_types)
			cur.close()
			return render_template('index.html',Food_types=Food_types)
		else:
			return redirect("/login")
	if request.method == 'POST':
		Type = request.form['type']
		Name = request.form['name']
		Prod = request.form['product']
		Rec=request.form['recept']
		cur=con.cursor()
		cur.execute("INSERT into Food(Name,Comment,Type,Recept,Composition,Photo)  VALUES(?,?,?,?,?,?)",
		(Name,"",Type,Rec,Prod,""))
		con.commit()
		cur.close()

		print (Type, Name, Prod, Rec)
		flash('Рецепт Добавлен!')
		return(redirect(url_for("index")))


@app.route('/menu_action',methods=['GET', 'POST'])
@login_required
def menu_action():
	return render_template('menu.html')


@app.route('/search',methods=['GET', 'POST'])
@login_required
def edit():
	cur=con.cursor()
	cur.execute("SELECT * from Food")
	Food=[e for e in cur.fetchall()]
	print(Food)
	cur.close()
	return render_template('edit.html',food=Food)


@app.route('/<id_1>/edit',methods=['GET', 'POST'])
@login_required
def edit_rec(id_1):
	if request.method == 'GET':
		cur=con.cursor()
		cur.execute("SELECT * from Food WHERE id=?",(id_1,))
		Food=[e for e in cur.fetchall()]
		cur.execute("SELECT Type from Type")
		Food_types=[e[0] for e in cur.fetchall()]
		print(Food)
		cur.close()
	if request.method == 'POST':
		Type = request.form['type']
		Name = request.form['name']
		Prod = request.form['product']
		Rec=request.form['recept']
		_id=request.form['id']
		print(_id)
		cur=con.cursor()
		cur.execute("UPDATE Food SET Name=?,Comment=?,Type=?,Recept=?,Composition=?,Photo=? WHERE id=?" ,
		(Name,"",Type,Rec,Prod,"",_id))
		con.commit()
		cur.close()

		print (Type, Name, Prod, Rec)
		flash('Рецепт изменен!')
		return(redirect(url_for("edit")))
	return render_template('edit_rec.html',food=Food, Food_types=Food_types)


@app.route('/<id_1>/del',methods=['GET', 'POST'])
@login_required
def del_rec(id_1):
	cur=con.cursor()
	cur.execute("DELETE from Food where id=?",(id_1,))
	con.commit()
	cur.close()
	return redirect(url_for("edit"))

if __name__ == '__main__':
    app.run(port=3000, host='0.0.0.0',debug=False)