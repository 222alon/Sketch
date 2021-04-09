class Stack {
	constructor(){
		this.data = [];
		this.top = 0;
	}
	push(element) {
		this.data[this.top] = element;
		this.top = this.top + 1;
	}
	length() {
		return this.top;
	}
	peek() {
		return this.data[this.top-1];
	}
	isEmpty() {
		return this.top === 0;
	}
	pop() {
	if( this.isEmpty() === false ) {
		this.top = this.top -1;
		return this.data.pop(); // removes the last element
		}
	}
	print() {
		var top = this.top - 1; // because top points to index where new element to be inserted
		while(top >= 0) { // print upto 0th index
			console.log(this.data[top]);
				top--;
			}
	}
	reverse() {
			this._reverse(this.top - 1 );
	}
	_reverse(index) {
			if(index != 0) {
				this._reverse(index-1);
			}
			console.log(this.data[index]);
	}
}

// const io = require("socket.io-client");

var strokes = new Stack();
var cur_stroke = new Stack();

const clearButton = document.getElementById('clear');
const stroke_weight = document.getElementById('thickness');

// const sideBar = document.getElementById("mySidenav");
// const colorPicker = document.getElementById("colorPicker")

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

		strokes.push(cur_stroke)
		cur_stroke = new Stack();
	}
}

function start (e) {
	mousePressed = true;
	clientX = e.clientX;
  clientY = e.clientY;
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

	cur_stroke.push({ypos: y-canvasYoffset+scrolledYOffset, xpos: x-canvasXoffset+scrolledXOffset, thickness: stroke_weight.value});
	
  ctx.lineTo(x-canvas.offsetLeft+scrolledXOffset, y-canvasYoffset+scrolledYOffset);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(x-canvasXoffset+scrolledXOffset, y-canvasYoffset+scrolledYOffset);
}

function stop() {
	mousePressed = false;
  isDrawing = false;
	
	if (cur_stroke.length() != 0) {
  ctx.beginPath();

	strokes.push(cur_stroke)
	cur_stroke = new Stack();
	}
}

document.onkeydown = undo;
function undo (e){
	var check_pressed = window.event? event : e
  if (!(check_pressed.keyCode == 90 && check_pressed.ctrlKey && !isDrawing)) return;

	ctx.strokeStyle = "#fafafa";


	let cancel_x = 0;
	let cancel_y = 0;

	let canceled_stroke = strokes.pop();

	let max_len = canceled_stroke.length();

	ctx.lineWidth = parseInt(canceled_stroke.peek().thickness,10)+2;

	for (i = 0; i < max_len; i++) {
		pos = canceled_stroke.pop();
		cancel_x = pos.xpos;
		cancel_y = pos.ypos;

		ctx.lineTo(cancel_x, cancel_y);
  	ctx.stroke();
  	ctx.beginPath();
  	ctx.moveTo(cancel_x, cancel_y);

}
ctx.beginPath();
}


function clearCanvas () {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
}

// window.addEventListener('resize', resizeCanvas);
function resizeCanvas () {
  canvas.width = window.innerWidth-2;
  canvas.height = window.innerHeight-canvas.offsetTop-2;
}
resizeCanvas();
