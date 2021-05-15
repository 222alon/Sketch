from flask import render_template, request, url_for, redirect, make_response, session
import os
from datetime import datetime
from flask_login import current_user, logout_user, login_required, login_user

from .models import User, db , login_manager
from flask import current_app as app
from . import socketio
from flask_socketio import send, emit



# Class for handling all the strokes in the Draw Room

class canvas_strokes:
	def __init__(self):
		self.strokes = []

	def addStroke(self, stroke):
		self.strokes.append(stroke)

	def undo(self):
		if (len(self.strokes) > 0):
			self.strokes.pop()

	def delete_canvas(self):
		self.strokes = []

# ----------------------------------------------------

print("Routes intiated")

colors = ['#fafafa', '#FFBCC8', '#FF9B9B','#FFB392','#FFF585','#D8FF8F','#AAFFC0','#BDFBFD','#B5D1FF','#C2ACFF','#7E7E7E','#000000']

draw_state = canvas_strokes()

@app.route('/harry')
@app.route('/garry')
def garry():
  return render_template('garry.html')

@app.route('/index')
@app.route('/')
def index():
  return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	if not current_user.is_authenticated:
		if 'user' in session:
			if logged_user := User.query.filter_by(username=session['user']).first():
				login_user(logged_user)
				redirect(url_for('index'))
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

@app.route('/register', methods=['GET', 'POST'])
def signup():
	if request.method == 'POST':
		email = request.form['email']
		name = request.form['username']
		password = request.form['password']
		conf_password = request.form['pass_conf']

		user = User.query.filter_by(email=email).first()
		if user:
			return render_template('signup.html', err='This email is already registered.')
		if password != conf_password:
			return render_template('signup.html', err='Password does not match.')

		new_user = User(email=email, username=name, password=password)

		db.session.add(new_user)
		db.session.commit()

		return redirect(url_for('login'))

	return render_template('signup.html')

@app.route('/logout')
def logout():
	if 'user' in session:
		session['user'] = ''
		logout_user()
	return redirect(url_for('login'))


@app.route('/drawroom')
def sideBarTest():
	return render_template('draw-page.html', colors = colors)

# ERROR HANDLING PAGES

@login_manager.unauthorized_handler
def unauthorized():
	return redirect(url_for('login'), err = 'Login to access this')


@app.errorhandler(404)
def not_found(error):
  print(error)  # error is a "werkzeug.exceptions.NotFound" object.
  # Handle a 404 error
  # todo update 404error.html to be better
  return make_response(render_template('404error.html'), 404)

# SocketIO stuff

@socketio.on("connect")
def handle_connect():
	print("User connected!")
	emit("load-canvas", draw_state.strokes)

@socketio.on("disconnect")
def handle_disconnect():
	pass

@socketio.on("new-stroke")
def new_stroke(data):
	draw_state.addStroke(data)
	emit("new-stroke", data, broadcast=True)
	print("Stroke Added with a total of " + str(len(data)))

@socketio.on("undo")
def undo_stroke():
	draw_state.undo()
	print("Undid a stroke")
	emit("load-canvas", draw_state.strokes, broadcast=True)

@socketio.on("refresh-canvas")
def refresh_canvas():
	emit("load-canvas", draw_state.strokes)

@socketio.on("mid-stroke")
def update_cur_strokes(data):
	emit("new-stroke", data, broadcast=True, include_self=False)

@socketio.on("clear")
def clear_canvas():
	print("Deleted canvas!")
	draw_state.delete_canvas()
	emit("load-canvas", draw_state.strokes, broadcast=True)





