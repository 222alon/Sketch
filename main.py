import Sketch


if __name__ == "__main__":
    # Sketch.app.run(host='0.0.0.0', port='8080', debug=True)
		Sketch.socketio.run(Sketch.app, host='0.0.0.0', port='8080', debug=True)