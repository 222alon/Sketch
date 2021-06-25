from flask import render_template, request, url_for, redirect, make_response, session
import os

import random
import string

from datetime import datetime

import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from expiringdict import ExpiringDict

from flask_login import current_user, logout_user, login_required, login_user

from .models import User, db , login_manager
from flask import current_app as app
from . import socketio
from flask_socketio import send, emit, join_room, leave_room


def update_active(page):
	session['active-page'] = {'home': '', 'public': '', 'private': '', 'login': '', 'signup': '', 'settings': '', 'none': ''}
	session['active-page'][page] = 'active-item'
	# print (session['active-page'])

# Class for handling all the strokes in a Draw Room

class canvas_strokes:
	def __init__(self):
		self.strokes = []
		self.backgroundImage = ""

	def addStroke(self, stroke):
		self.strokes.append(stroke)

	def undo(self):
		if (len(self.strokes) > 0):
			self.strokes.pop()

	def delete_canvas(self):
		self.strokes = []

# ----------------------------------------------------

print("Routes intiated")

# email = 'SketchConfirmation@gmail.com' 
# password = 'SketchPassword' 
# This should only be gotten as a python input but
# Too lazy to secure the password, go nuts.


colors = ['#fafafa', '#FFBCC8', '#FF9B9B','#FFB392','#FFF585','#D8FF8F','#AAFFC0','#BDFBFD','#B5D1FF','#C2ACFF','#7E7E7E','#000000']

icons = ['fas fa-circle', 'fas fa-square-full', 'fas fa-certificate' , 'fas fa-tint', 'fas fa-paint-brush', 'fas fa-fill']

draw_state = {'public' : canvas_strokes()}

codes = ExpiringDict(max_len=100, max_age_seconds=300) # This has a max size which could prove problamatic, however it is good enough for the limited use my site will have.
# codes['test'] = 'TESTING' # Will expire after 5 minutes, raise KeyError after.

@app.route('/index')
@app.route('/')
def index():
	update_active('home')
	return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	if not current_user.is_authenticated:
		if 'user' in session:
			if logged_user := User.query.filter_by(username=session['user']).first():
				login_user(logged_user)
				redirect(url_for('index'))

		update_active('login')

		if request.method == 'POST':
			name = request.form['username']
			password = request.form['password']
			if logged_user := User.query.filter_by(username= name).first():
				if logged_user.validate_password(password):
					session['user'] = logged_user.username
					login_user(logged_user)
					print(current_user)
					return redirect(url_for('index'))
			return render_template('login.html', err = 'Invalid credentials')
		return render_template('login.html')
	return redirect(url_for('index'))

@app.route('/recover', methods=['GET', 'POST'])
def recover():
	if request.method == 'POST':
		if User.query.filter_by(email=request.form['username']).first():
			session['email_to_reset'] = request.form['username']
		elif User.query.filter_by(username=request.form['username']).first():
			user_email = User.query.filter_by(username=request.form['username']).first().email
			session['email_to_reset'] = user_email
		else:
			session['email_to_reset'] = ''
		
		return redirect(url_for('confirm'))
	update_active('none')
	return render_template('recover.html')

@app.route('/confirm', methods=['GET', 'POST'])
def confirm():
	if request.method == 'POST':
		conf_code = codes[session['email_to_reset']]
		if request.form['conf_code'] == conf_code:
			resetted_user = User.query.filter_by(email=session['email_to_reset']).first()
			session['user'] = resetted_user.username
			login_user(resetted_user)
			session['email_to_reset'] = ''
			return redirect(url_for('reset_password'))

		else:
			return render_template('confirm.html', err = 'Invalid Code.')

	update_active('none')

	if session['email_to_reset']:
		message = MIMEMultipart("alternative")
		message["Subject"] = "Sketch Confirmation Code"
		message["From"] = "SketchConfirmation@gmail.com"
		message["To"] = session['email_to_reset']

		conf_code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
		codes[session['email_to_reset']] = conf_code
		raw_msg = """
Subject: Sketch Confirmation Email.

Your confirmation code is {}, if you did not request an account recovery please ignore this message.""".format(conf_code)
		html_msg = """
<html> 
	<body>

		<a href="https://sketch.222alon.repl.co"> Sent from Sketch by Alon Levi </a>
		</br>
		<p style="color = hsl(200, 4%, 17%);"> Your confirmation code is </br>
		<div style="font-size: 50px;">{}</div> 
		</br>if you did not request an account recovery please ignore this message.</p>

	</body>
</html>""".format(conf_code)

		message.attach(MIMEText(raw_msg, 'plain'))
		message.attach(MIMEText(html_msg, 'html'))

		context = ssl.create_default_context()
		with smtplib.SMTP_SSL("smtp.gmail.com", 587, context=context) as server:
			print('Sending test msg')

			server.login("SketchConfirmation@gmail.com", 'SketchPassword')
			server.sendmail("SketchConfirmation@gmail.com", session['email_to_reset'], message.as_string())
	else:
		print("Given user does not exist.")
	return render_template('confirm.html')

@app.route('/reset_password', methods=['GET', 'POST'])
@login_required
def reset_password():
	update_active('none')
	if request.method == 'POST':
		password = request.form['password']
		conf_password = request.form['pass_conf']

		if password != conf_password:
			return render_template('resetpass.html', err='Password does not match.')
		
		current_user.password = password
		db.session.commit()
		return redirect(url_for('index'))

	return render_template('resetpass.html')
	
@app.route('/register', methods=['GET', 'POST'])
def signup():
	update_active('signup')
	if request.method == 'POST':
		email = request.form['email']
		name = request.form['username']
		password = request.form['password']
		conf_password = request.form['pass_conf']

		
		if User.query.filter_by(email=email).first() or User.query.filter_by(username=name).first():
			return render_template('signup.html', err='Credentials already registered.')
		if password != conf_password:
			return render_template('signup.html', err='Password does not match.')

		new_user = User(email=email, username=name, password=password)

		db.session.add(new_user)
		db.session.commit()

		return redirect(url_for('login'))

	return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
	if 'user' in session:
		session['user'] = ''
		logout_user()
	return redirect(url_for('login'))

@app.route('/drawroom')
def public_drawroom():
	return redirect(url_for('private_drawroom', room_id = 'public'))

# 'public' is the public draw room
@app.route('/drawroom/<room_id>')
def private_drawroom(room_id):
	if room_id not in draw_state:
		return make_response(render_template('404error.html'), 404)
	if (room_id == 'public'):
		update_active('public')
	else:
		update_active('private')
	if current_user.is_authenticated:
		return render_template('draw-page.html', colors = current_user.colors.split(','), icon = current_user.icon)
	return render_template('draw-page.html', colors = colors, icon = icons[3])

def generate_roomid():
	# 839,299,365,868,340,224 <- max amount of rooms.
	room_id = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(10))
	if room_id in draw_state:
		return generate_roomid()
	return room_id

@app.route('/create_room')
def create_room():
	room_id = generate_roomid()
	draw_state[room_id] = canvas_strokes()
	return redirect(url_for('private_drawroom', room_id = room_id))

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
	update_active('settings')
	if request.method == 'POST':
		new_colors = []
		for key, value in request.form.items():
			if key == 'icon':
				current_user.icon = value
			else:
				new_colors.append(value)
		current_user.colors = ','.join(new_colors)
		db.session.commit()
	
	print(current_user.colors.split(','))
	return render_template('settings.html', colors = current_user.colors.split(','), icons = icons, cur_icon = current_user.icon)

@app.route('/reset_settings')
@login_required
def reset_settings():
	current_user.colors = ','.join(colors);
	current_user.icon = 'fas fa-tint';
	db.session.commit()
	return redirect(url_for('settings'))

# ERROR HANDLING PAGES

@login_manager.unauthorized_handler
def unauthorized():
	return render_template('unauthorized.html')

@app.errorhandler(404)
def not_found(error):
	print(error)  # error is a "werkzeug.exceptions.NotFound" object.
	# Handle a 404 error
	# todo update 404error.html to be better
	return make_response(render_template('404error.html'), 404)

# SocketIO stuff

# mysite/drawroom/askufgaskvj

@socketio.on('join-room')
def join_drawroom(room_id):
	session['room-id'] = room_id
	join_room(room_id)
	print('joining room ' + room_id)
	emit("change-background", draw_state[room_id].backgroundImage)

@socketio.on("connect")
def handle_connect():
	print("User connected!")

@socketio.on("disconnect")
def handle_disconnect():
	pass

@socketio.on("new-stroke")
def new_stroke(data):
	draw_state[session['room-id']].addStroke(data)
	emit("new-stroke", data, room=session['room-id'])
	print("Stroke Added with a total of " + str(len(data)) + " at " + session['room-id'])

@socketio.on("undo")
def undo_stroke():
	draw_state[session['room-id']].undo()
	print("Undid a stroke")
	emit("load-canvas", draw_state[session['room-id']].strokes, room=session['room-id'])

@socketio.on("change-background")
def change_background(data):
	draw_state[session['room-id']].backgroundImage = data
	emit("change-background", data, room=session['room-id'], include_self=False)
	
@socketio.on("refresh-canvas")
def refresh_canvas():
	emit("load-canvas", draw_state[session['room-id']].strokes)

@socketio.on("mid-stroke")
def update_cur_strokes(data):
	emit("new-stroke", data, room=session['room-id'], include_self=False)

@socketio.on("clear")
def clear_canvas():
	print("Deleted canvas {}!".format(session['room-id']))
	draw_state[session['room-id']].delete_canvas()
	emit("load-canvas", draw_state[session['room-id']].strokes, room=session['room-id'])





