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
		var top = this.top - 1; // because top points to index where new    element to be inserted
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

var strokes = new Stack();
var cur_stroke = new Stack();

const clearButton = document.getElementById('clear');
const stroke_weight = document.getElementById('thickness');
const color_picker = document.getElementById('colors');

const canvas = document.querySelector('canvas');
const ctx = canvas.getContext('2d');
let isDrawing = false;

canvas.addEventListener('mousedown', start);
canvas.addEventListener('mousemove', draw);
canvas.addEventListener('mouseup', stop);

clearButton.addEventListener('click', clearCanvas);

function start (e) {
  isDrawing = true;
  draw(e);
}

function draw ({clientX: x, clientY: y}) {
  if (!isDrawing) return;
  // ctx.lineWidth = stroke_weight.value;
	ctx.lineWidth = 5;
  ctx.lineCap = "round";
  // ctx.strokeStyle = color_picker.value;
	ctx.strokeStyle = "#000000";

	cur_stroke.push({ypos: y-56, xpos: x, thickness: 5})
	
  ctx.lineTo(x, y-56);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(x, y-56);
}

function stop () {
  isDrawing = false;
  ctx.beginPath();

	strokes.push(cur_stroke)
	cur_stroke = new Stack();
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

	for (i = 0; i < max_len; i++) {
		pos = canceled_stroke.pop();
		cancel_x = pos.xpos;
		cancel_y = pos.ypos;
		ctx.lineWidth = pos.thickness+2;

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
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight-56;
}
resizeCanvas();
