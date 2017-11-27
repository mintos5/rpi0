var rpi0Ready = false;
var defaultAddress = "ws://147.175.149.172:5432";
var rpi0Ssocket = new WebSocket(defaultAddress);
socketAttachHandlers();

function socketAttachHandlers() {

	rpi0Ssocket.onerror =  function (event) {
		//the connection was never ready
		if (rpi0Ready === false){
			console.log(event);
			var address = prompt("Please enter address of server:", defaultAddress);
			if (address == null || address == "") {
				console.log("No address :/");
			}
			else {
				rpi0Ssocket = new WebSocket(address);
				socketAttachHandlers();
			}
		}
		else {
			rpi0Ready = false;
		}
	}

	rpi0Ssocket.onopen = function (event) {
		var hello = {
			client: "sw_client"
		};
		rpi0Ssocket.send(JSON.stringify(hello)); 
	}

	rpi0Ssocket.onmessage = function (event) {
	 	console.log(event.data);
	 	rpi0Ready = true;
	}
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
		if (rpi0Ready) {
			// console.log(out)
			rpi0Ssocket.send(JSON.stringify(out));
		}
		document.getElementById("inputBox").value = "";
	}
	else {
		var out = {
			type: "keyboard_symbol",
			button: whatSend
		}
		if (rpi0Ready) {
			// console.log(out)
			rpi0Ssocket.send(JSON.stringify(out));
		}
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
		if (rpi0Ready) {
			// console.log(out)
			rpi0Ssocket.send(JSON.stringify(out));
		}
	}, false);
}