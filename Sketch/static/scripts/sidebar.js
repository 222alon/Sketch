// $(document).ready(function () {
// 	$("#sidebar").mCustomScrollbar({
// 		theme: "minimal"
// 	});

// 	$('#dismiss, .overlay').on('click', function () {
// 		$('#sidebar').removeClass('active');
// 		$('.overlay').removeClass('active');
// 	});

// 	$('#sidebarCollapse').on('click', function () {
// 		$('#sidebar').addClass('active');
// 		$('.overlay').addClass('active');
// 		$('.collapse.in').toggleClass('in');
// 		$('a[aria-expanded=true]').attr('aria-expanded', 'false');
//   });
// });

function close(){
	document.getElementById("dismiss").classList.remove('active');
	document.getElementsByClassName('overlay').classList.remove('active');
}

function open(){
	document.getElementById("dismiss").classList.add('active');
	document.getElementsByClassName('overlay').classList.add('active');
	document.getElementsByClassName('collapse.in').classList.toggle('in')
}