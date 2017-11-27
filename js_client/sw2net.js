var rpi0Ssocket = new WebSocket("ws://147.175.149.172:5432");
var rpi0Ready = false;

rpi0Ssocket.onopen = function (event) {
	var hello = {
		client: "sw_client"
	};
	rpi0Ssocket.send(JSON.stringify(hello)); 
};
rpi0Ssocket.onmessage = function (event) {
  console.log(event.data);
  rpi0Ready = true;
}

function buttonClick(button) {
	var out = {
		type: "mouse",
		x: 0,
		y: 0
	}
	if (button === 1) {
		out["button"] = "b1"
	}
	else if (button == 2) {
		out["button"] = "b2"
	}
	if (rpi0Ready) {
		// console.log(out)
		rpi0Ssocket.send(JSON.stringify(out));
		out["button"] = "b0"
		// console.log(out)
		rpi0Ssocket.send(JSON.stringify(out));
	}
}

function textClick() {
	var whatSend = document.getElementById("inputTypeSelect").value;
	if (whatSend == "string") {
		var text = document.getElementById("inputBox").value;
		var out = {
			type: "keyboard_string",
			string: text
		}
		// console.log(out)
		rpi0Ssocket.send(JSON.stringify(out));
	}
	else {
		var out = {
			type: "keyboard_symbol",
			button: whatSend
		}
		// console.log(out)
		rpi0Ssocket.send(JSON.stringify(out));
	}
}

function disableInput() {
	var whatSend = document.getElementById("inputTypeSelect").value;
	if (whatSend == "string") {
		document.getElementById("inputBox").disabled = false;
	}
	else {
		document.getElementById("inputBox").disabled = true;
	}
}

function main(){
	var src = document.getElementById("source");
	var clientX, clientY;
	src.addEventListener('touchstart', function(e) {
		// Cache the client X/Y coordinates
		clientX = e.touches[0].clientX;
		clientY = e.touches[0].clientY;
	}, false);

src.addEventListener('touchmove', function(e) {
		var deltaX, deltaY;
	 	deltaX = e.changedTouches[0].clientX - clientX;
	  	deltaY = e.changedTouches[0].clientY - clientY;
	  	clientX = e.changedTouches[0].clientX;
		clientY = e.changedTouches[0].clientY;
	  	// Process the data and send them to server
	  	var out = {
			type: "mouse",
			button: "b0",
			x: Math.floor(deltaX),
			y: Math.floor(deltaY)
		}
		// console.log(out)
		rpi0Ssocket.send(JSON.stringify(out));
	}, false);
}