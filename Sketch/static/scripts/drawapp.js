var socket = io('https://' + document.domain + ':' + location.port ,{ secure: true });

var cur_stroke = [];
var cur_update = [];

var drawingInterval;

const clearButton = document.getElementById('clear');
const stroke_weight = document.getElementById('thickness');

const canvas = document.querySelector('canvas');
const ctx = canvas.getContext('2d');

let isDrawing = false;
let mousePressed = false;

window.addEventListener('touchstart', touchOutsideCanvas);
window.addEventListener('mousedown', touchOutsideCanvas);

canvas.addEventListener('touchstart', startTouch);
canvas.addEventListener('touchmove', touchMove);
window.addEventListener('touchend', stop);

canvas.addEventListener('mousedown', start);
window.addEventListener('mousemove', mouseMove);
window.addEventListener('mouseup', stop);
canvas.addEventListener('mouseout', outsideTrigger);

clearButton.addEventListener('click', clearCanvas);

function touchOutsideCanvas() {
	mousePressed = true;
}

function startTouch(e) {
	isDrawing = true;
	clientX = e.touches[0].clientX;
  clientY = e.touches[0].clientY;
	drawingInterval = setInterval(update_draw, 100);
	draw(clientX, clientY)
}

function touchMove(e) {
	clientX = e.touches[0].clientX;
  clientY = e.touches[0].clientY;
	draw(clientX, clientY)
}


function outsideTrigger() {
	if (isDrawing) {
		isDrawing = false;
  	ctx.beginPath();

	}
}

function start (e) {
	mousePressed = true;
	clientX = e.clientX;
  clientY = e.clientY;
	drawingInterval = setInterval(update_draw, 100);
	draw(clientX, clientY)
}

function mouseMove(e){
	clientX = e.clientX;
  clientY = e.clientY;
	draw(clientX, clientY)
}

function draw (x, y) {

	if (mousePressed) isDrawing = true;
  if (!isDrawing) return;

	
  ctx.lineWidth = stroke_weight.value;
	color = document.querySelector('input[name="color"]:checked').value;
  ctx.lineCap = "round";
  ctx.strokeStyle = color;

	let scrolledYOffset = window.scrollY;
	let scrolledXOffset = window.scrollX;

	let canvasYoffset = canvas.offsetTop;
	let canvasXoffset = canvas.offsetLeft;

	cur_pos = {ypos: y-canvasYoffset+scrolledYOffset, xpos: x-canvasXoffset+scrolledXOffset, thickness: stroke_weight.value, point_color: color}

	cur_stroke.push(cur_pos);
	cur_update.push(cur_pos);
	
  ctx.lineTo(x-canvas.offsetLeft+scrolledXOffset, y-canvasYoffset+scrolledYOffset);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(x-canvasXoffset+scrolledXOffset, y-canvasYoffset+scrolledYOffset);

}

function stop() {
	mousePressed = false;
  isDrawing = false;

	clearInterval(drawingInterval);

	cur_update = [];
	
	if (cur_stroke.length != 0) {
  ctx.beginPath();

	socket.emit('new-stroke', cur_stroke);
	cur_stroke = [];
	}
}

function update_draw() {
	socket.emit('mid-stroke', cur_update);
	cur_update = [];
	console.log("Dummy update");
}

document.onkeydown = undo;
function undo (e){
	var check_pressed = window.event? event : e
  if (!(check_pressed.keyCode == 90 && check_pressed.ctrlKey && !isDrawing)) return;

	socket.emit('undo');

};


function clearCanvas () {
	socket.emit('clear');
  // ctx.clearRect(0, 0, canvas.width, canvas.height);
}

window.addEventListener('resize', resizeCanvas);
function resizeCanvas () {
  canvas.width = window.innerWidth-2;
  canvas.height = window.innerHeight-canvas.offsetTop-2;
	socket.emit('refresh-canvas');
}
resizeCanvas();

// -------SocketIO stuff---------

socket.on('connect', function() {
	console.log("Connected!");
});

socket.on('new-stroke', function(data){
	console.log("Adding stroke from another client!")

	ctx.beginPath();

	data.forEach(function (pos , pointIndex){

			ctx.strokeStyle = pos.point_color;
			ctx.lineWidth = parseInt(pos.thickness, 10);
			cur_x = pos.xpos;
			cur_y = pos.ypos;

			
			ctx.lineTo(cur_x, cur_y);
			ctx.stroke();
			ctx.beginPath();
			ctx.moveTo(cur_x, cur_y);

		})
	ctx.beginPath();
});

socket.on('load-canvas', function(data) {
	console.log("Loading canvas from server memory");
	
	ctx.lineCap = "round";

	let cur_x = 0;
	let cur_y = 0;

	ctx.clearRect(0, 0, canvas.width, canvas.height);

	ctx.beginPath();

	data.forEach(function (stroke, strokeIndex) {
		stroke.forEach(function (pos , pointIndex){

			ctx.strokeStyle = pos.point_color;
			ctx.lineWidth = parseInt(pos.thickness, 10);
			cur_x = pos.xpos;
			cur_y = pos.ypos;

			
			ctx.lineTo(cur_x, cur_y);
			ctx.stroke();
			ctx.beginPath();
			ctx.moveTo(cur_x, cur_y);



		})
	ctx.beginPath();
	});

});

