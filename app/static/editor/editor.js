function reset() {
    $('#in').css({'display':'block'});
    $('#in').removeClass('fullwidth');
    $('#in').addClass('halfwidth');
    $('#out').css({'display':'block', 'position':'fixed'});
}

function isNormalMode() {
    return ($('#in').hasClass('halfwidth') && $('#in').css('display') == 'block');
}

$('#preview-btn').click( function(){
    if ( isNormalMode() ) {
        $('#in').css({'display':'none'});
        $('#out').css({'position':'inherit'});
    } else {
        reset();
    }
});

$('#edit-btn').click( function(){
    if ( isNormalMode() ) {
        $('#in').toggleClass('halfwidth fullwidth');
        $('#out').css({'display':'none'});
    } else {
        reset();
    }
});

var isMacOS = (navigator.appVersion.indexOf("Mac") != -1);
document.addEventListener('keydown', function(e){
	if(e.keyCode == 83 && ((e.ctrlKey && !isMacOS) || (e.metaKey && isMacOS))){
		$('#save').click();
		e.preventDefault();
		return false;
	}

	if(e.keyCode === 27){
		cancel_btn.click();
		e.preventDefault();
		return false;
	}
});

// close flashed error messages
var i;
for (i = 0; i < $('.closebtn').length; i++) {
	$('.closebtn')[i].onclick = function(){
		var div = this.parentElement;

		div.style.opacity = "0";
		setTimeout(function(){ div.style.display = "none"; }, 600);
	}
}

// Close the dropdown menu if the user clicks outside of it
window.onclick = function(event) {
	if (!event.target.matches('.bars')) {

		var i;
		for (i = 0; i < $('.menu-content').length; i++) {
			var openDropdown = $('.menu-content')[i];
			if (openDropdown.classList.contains('show')) {
				openDropdown.classList.remove('show');
			}
		}
	}
}

// change img_dir to /static/emoji
emojify.setConfig({ img_dir: '/static/emoji' });

function update(e){
	setOutput(e.getValue());
}

function setOutput(val){
	var out = document.getElementById('out');
	var old = out.cloneNode(true);
	out.innerHTML = marked(val);
	emojify.run(out);
	MathJax.Hub.Queue(["Typeset",MathJax.Hub]);

	var allold = old.getElementsByTagName("*");
	if (allold === undefined) return;

	var allnew = out.getElementsByTagName("*");
	if (allnew === undefined) return;

	for (var i = 0, max = Math.min(allold.length, allnew.length); i < max; i++) {
		if (!allold[i].isEqualNode(allnew[i])) {
			out.scrollTop = allnew[i].offsetTop;
			return;
		}
	}
}

var editor = CodeMirror.fromTextArea(document.getElementById('code'), {
	mode: 'gfm',
	lineNumbers: true,
	lineWrapping: true,
	indentUnit: 4,
	theme: 'base16-light',
	extraKeys: {"Enter": "newlineAndIndentContinueMarkdownList"}
});

editor.on('change', update);
update(editor);
editor.focus();