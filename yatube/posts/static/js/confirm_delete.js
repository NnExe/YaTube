
function button_enable() {
var chbox;
    chbox=document.getElementById('protect');
    button = document.getElementById('delete_button');
	if (chbox.checked) {
		button.hidden = false
	}
	else {
		button.hidden = true
	}
}
