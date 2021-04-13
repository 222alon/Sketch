from flask import render_template, request, url_for, redirect, flash, make_response, send_from_directory
import os
from datetime import datetime
from flask_login import current_user, logout_user, login_required, login_user

from .models import User, db , login_manager
from flask import current_app as app
from . import socketio

# Class for handling all the strokes in the Draw Room

class canvas_strokes:
	def __init__(self):
		self.strokes = []

	def addStroke(self, stroke):
		self.strokes.append(stroke)

	def undo(self):
		self.strokes.pop()

	def delete_canvas(self):
		self.strokes = []

# ----------------------------------------------------

print("Routes intiated")

colors = ['#fafafa', '#FFBCC8', '#FF9B9B','#FFB392','#FFF585','#D8FF8F','#AAFFC0','#BDFBFD','#B5D1FF','#C2ACFF','#7E7E7E','#000000']

draw_state = canvas_strokes()

@app.route('/index')
@app.route('/')
def index():
  return render_template('index.html')

@app.route('/drawroom')
def sideBarTest():
	return render_template('draw-page.html', colors = colors)

# ERROR HANDLING PAGES

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
	socketio.emit("load-canvas", draw_state.strokes)

@socketio.on("disconnect")
def handle_disconnect():
	pass

@socketio.on("new-stroke")
def new_stroke(data):
	draw_state.addStroke(data)
	print("Stroke Added with a total of " + str(len(data)))

# @socketio.on("testArray")
# def testGettingArray(data):
# 	print(type(data))





