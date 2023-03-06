// Vanyle UI Library.
// All rights reserved. Copyright 2020.
/*
We provide a set of UI related JS functions that are often useful.
vui.js does not need any css and works standalone.
You can of course add your own css to futher customize the appearance of vui.js
By default, the elements have a 2015 style I'd say, with a neutral modern theme.
*/

// Similar to vprompt but without text input, simple OK/CANCEL dialog.
// Can be used to ask cookie permission for example.
function vask(msg,success_callback,cancel_callback){
	// I know that putting all this css in js code is ugly
	// but I feel that it's worth it because how, we have standalone methods !
	let div = document.createElement('div');
	let htmlTxt = "<div>"+msg+"</div>";
	htmlTxt += "<div><button class='ok'>Ok</button><button class='cancel'>Cancel</button></div>";
	div.innerHTML = htmlTxt;

	div.style.display = 'flex';
	div.style.flexDirection = 'column';
	div.style.alignItems = 'center';
	div.style.color = '#333';
	div.style.backgroundColor = 'white';
	div.style.padding = '1vw';
	div.style.fontSize = '2vw';
	div.style.borderRadius = '10px';
	div.style.boxShadow = '1px 1px 3px #000';
	div.style.transition = '1000ms';
	div.style.position = 'fixed';
	div.style.top = '50%';
	div.style.left = '50%';
	div.style.transform = 'translate(-50%,-50%)';
	div.style.zIndex = 2;
	document.body.appendChild(div);

	let darkVeil = document.createElement('div'); // clicking the veil is the same as clicking cancel.
	darkVeil.style.opacity = .5;
	darkVeil.style.backgroundColor = '#333';
	darkVeil.style.position = 'fixed';
	darkVeil.style.top = '0';
	darkVeil.style.left = '0';
	darkVeil.style.width = '100%';
	darkVeil.style.height = '100%';
	darkVeil.style.zIndex = 1;
	document.body.appendChild(darkVeil);

	function cancel(){
		document.body.removeChild(darkVeil);
		document.body.removeChild(div);
		(cancel_callback || (() => {})) ();
	}
	function ok(){
		document.body.removeChild(darkVeil);
		document.body.removeChild(div);
		(success_callback || (() => {})) ();
	}
	darkVeil.onclick = cancel;
	div.querySelector('.cancel').onclick = cancel;
	div.querySelector('.ok').onclick = ok;
}

function vprompt(msg,success_callback,cancel_callback){
	// I know that putting all this css in js code is ugly
	// but I feel that it's worth it because how, we have standalone methods !
	let div = document.createElement('div');
	let htmlTxt = "<div>"+msg+"</div><input type='text'/>";
	htmlTxt += "<div>";
	htmlTxt += "<button class='ok'>Ok</button><button class='cancel'>Cancel</button></div>";
	div.innerHTML = htmlTxt;

	div.style.display = 'flex';
	div.style.flexDirection = 'column';
	div.style.alignItems = 'center';
	div.style.color = '#333';
	div.style.backgroundColor = 'white';
	div.style.padding = '1vw';
	div.style.fontSize = '2vw';
	div.style.borderRadius = '10px';
	div.style.boxShadow = '1px 1px 3px #000';
	div.style.transition = '1000ms';
	div.style.position = 'fixed';
	div.style.top = '50%';
	div.style.left = '50%';
	div.style.transform = 'translate(-50%,-50%)';
	div.style.zIndex = 2;
	document.body.appendChild(div);

	let darkVeil = document.createElement('div'); // clicking the veil is the same as clicking cancel.
	darkVeil.style.opacity = .5;
	darkVeil.style.backgroundColor = '#333';
	darkVeil.style.position = 'fixed';
	darkVeil.style.top = '0';
	darkVeil.style.left = '0';
	darkVeil.style.width = '100%';
	darkVeil.style.height = '100%';
	darkVeil.style.zIndex = 1;
	document.body.appendChild(darkVeil);

	div.querySelector('input').focus();

	function cancel(){
		document.body.removeChild(darkVeil);
		document.body.removeChild(div);
		(cancel_callback || (() => {})) ();
	}
	function ok(){
		let val = div.querySelector('input').value;	
		document.body.removeChild(darkVeil);
		document.body.removeChild(div);
		(success_callback || (() => {})) (val);
	}
	darkVeil.onclick = cancel;
	div.querySelector('.cancel').onclick = cancel;
	div.querySelector('.ok').onclick = ok;
	div.querySelector('input').onkeyup = (e) => {
		console.log(e);
		if(e.key == "Enter") ok();
	};
}


// Portable reusable toast function. Works without any css
function toast(msg){
	let div = document.createElement('div');
	div.innerHTML = msg;

	// some style!
	div.style.display = 'inline-block';
	div.style.color = 'white';
	div.style.backgroundColor = '#333';
	div.style.padding = '1vw';
	div.style.fontSize = '2vw';
	div.style.borderRadius = '10px';
	div.style.boxShadow = '1px 1px 3px #000';
	div.style.transition = '1000ms';
	div.style.position = 'fixed';
	div.style.bottom = '10%';
	div.style.left = '50%';
	div.style.transform = 'translate(-50%,-50%)';

	document.body.appendChild(div);
	setTimeout(() => {
		div.style.opacity = 0;
		div.style.bottom = '-20%';
		setTimeout(() => {
			document.body.removeChild(div);
		},1000);
	},2000);
}


// returns an html element that behaves like a slider with the following structure:
// <div class='slider'><div class='thumb'></div><div class='progress'></div></div>
// it can be used for process bars, sliders, showing durations, etc ...
// onvaluechange is called when the user attempts to change the value of the slider.
// you can do nothing on this event to have a readonly slider
// we also return a set value function to set the value of the slider.
// the value should be between 0 and 1.
// Usage example:
/*
let {slider, setValue} = makeSlider((value) => {
	audio.volume = value;
	setValue(value); // this line is needed to update the slider render. if not, the slider would be readonly.
});
setValue(.5) // nice default i guess.
slider.id = "volume_slider";
insertAfter(volume_button,slider);
*/
function makeSlider(onvaluechange){
	onvaluechange = (onvaluechange || function(){});
	let slider = document.createElement('div');
	slider.className = 'slider';
	// slider is larger than display to have a fine bar but have a big area to handle events.
	slider.innerHTML = "<div class='display_dom'><div class='progress_bar_dom'></div><div class='thumb_dom'></div></div>"

	// setup css (provide sane defaults, should be customizable.)
	slider.style.padding = '0';

	let display_dom = slider.querySelector('.display_dom');
	display_dom.style.height = '30%';
	display_dom.style.width = '100%';
	display_dom.style.display = 'flex';
	display_dom.style.alignItems = 'center';

	let thumb = slider.querySelector('.thumb_dom');
	thumb.style.borderRadius =  "50%";

	let progress_bar_dom = slider.querySelector('.progress_bar_dom');

	let setValue = function(newval){
		let progress_bar = slider.querySelector('.progress_bar_dom');
		newval = Math.min(Math.max(0,newval),1);
		progress_bar.style.width = (newval * 100) + '%';
	};

	slider.onclick = (e) => {
		let xpos = e.clientX - slider.offsetLeft - thumb.offsetWidth / 2;
		xpos = Math.min(Math.max(0,xpos),slider.offsetWidth);
		xpos /= slider.offsetWidth; // xpos : 0-1
		onvaluechange(xpos);
	}

	let mousemovehandler = (e) => {
		if(e.touches !== undefined){
			e = e.touches[0];
		}
		let xpos = e.clientX - slider.offsetLeft - thumb.offsetWidth / 2;
		xpos = Math.min(Math.max(0,xpos),slider.offsetWidth);
		xpos /= slider.offsetWidth; // xpos : 0-1
		onvaluechange(xpos);
	}

	// For mobile
	addEventListener('touchend', () => {
		removeEventListener('touchmove',mousemovehandler,{passive: true});
	},{passive: true});
	slider.querySelector('.thumb_dom').addEventListener('touchstart',(e) => {
		addEventListener('touchmove',mousemovehandler,{passive: true});
	},{passive: true});

	// For desktop
	addEventListener('mouseup', () => {
		removeEventListener('mousemove',mousemovehandler,{passive: true});
	},{passive: true});
	slider.querySelector('.thumb_dom').addEventListener('mousedown',(e) => {
		addEventListener('mousemove',mousemovehandler,{passive: true});
	},{passive: true});


	return {slider:slider,setValue:setValue};
}

/*
	options_text: ["Download","Delete","Open"]
	handlers: download_callback, delete_callback, etc...

*/
function showContextMenu(x,y,option_text,handlers){
	let div = document.createElement('div');
	div.className = 'contextmenu';

	if(document.getElementById('context_menu_css') === null){
		let css = `
			.contextmenu > div:hover{
				background-color: #aaa;
			}
			.contextmenu{
				display:flex;
				color: #333;
				background-color:white;
				flex-direction:column;
				font-size: 20px;
				box-shadow:1px 1px 5px #000;
				position:fixed;
			}
			@media (max-width: 800px) {
				.contextmenu{
					width:100%;
					left:0px;
					bottom:0px;
					text-align:center;
					transform: translate(0%,0%) !important;
				}
			}`;
		let style = document.createElement('style');
		style.id = "context_menu_css";
		style.appendChild(document.createTextNode(css));
		document.head.appendChild(style);
	}

	let htmltext = "";
	for(let i in option_text){
		htmltext += "<div style='padding:10px;white-space: nowrap;'>" + option_text[i] + "</div>";
	}

	div.innerHTML = htmltext;
	// some style!
	if(innerWidth > 800){
		div.style.left = x+'px';
		div.style.top = y+'px';
	}
	document.body.appendChild(div); // add element to body to render it and be able to access offsetWidth property.

	// This is to prevent the context menu from being offscreen
	// Contrains (in order of priority for the algorithm)
	// 1. the context menu is always created so that the mouse if at an edge of the box.
	// 2. The context menu is fully visible on screen
	// 3. Mouse is located at the top left of the context menu on creation.

	let xshift = 0;
	let yshift = 0;
	if(x + div.offsetWidth > innerWidth){
		xshift = -100;
	}
	if(y + div.offsetHeight > innerHeight){
		yshift = -100;
	}
	div.style.transform = "translate("+xshift+"%,"+yshift+"%)";

	// Event management

	div.querySelectorAll('div').forEach((d,i) => {
		d.onclick = (e) => {
			e.preventDefault();
			(handlers[i] || function(){})();
		}
	});

	let closeMenu = (e) => {
		e.preventDefault();
		document.body.removeChild(div);
		document.body.removeEventListener('click',closeMenu);
		document.body.removeEventListener('contextmenu',closeMenu);
	};

	setTimeout(() => {
		document.body.addEventListener('click',closeMenu);
		document.body.addEventListener('contextmenu',closeMenu);
	},1);
}

/*
Used to make menus with tabs
First argument is a selector for the element to show
Select argument is a selector for the elements to hide. 
*/
function showSection(toShow,toHide){
	document.querySelectorAll(toHide).forEach((e) => {
		e.style.display = 'none';
	});
	document.querySelector(toShow).style.display = '';
}

function sanitize(txt){
	let soap = document.createElement('div');
	soap.innerText = txt;
	return soap.innerHTML;
}