//////////////////////////////////////////////////////////////////////////////80
// Plugin Template
//////////////////////////////////////////////////////////////////////////////80
// Copyright (c) Atheos & Liam Siira (Atheos.io), distributed as-is and without
// warranty under the MIT License. See [root]/LICENSE.md for more.
// This information must remain intact.
//////////////////////////////////////////////////////////////////////////////80
// Description: 
//	A blank plugin template to provide a basic example of a typical Atheos
//	plugin.
//////////////////////////////////////////////////////////////////////////////80
// Suggestions:
//	- A small line about improvements that can be made to this plugin/file
//////////////////////////////////////////////////////////////////////////////80
// Usage:
//  - desc: A short description of use
//
//////////////////////////////////////////////////////////////////////////////80


var token = null;
(function() {

	let self = false;

	// Initiates plugin as a third priority in the system.
	carbon.subscribe('system.loadExtra', () => atheos.elpro.init());
	var htmlpage;
	atheos.elpro = {
		sideExpanded: true,

		init: function() {
			if (self) return;
			self = this;
			console.log('Elpro plugin loaded!');
			//import interface.js and call LoadInterface
			loadInterface();
			if(token == null){
				echo({
					url: 'plugins/Elpro/controller.php',
					data: {
						target: 'Elpro',
						action: 'login'
					},
					settled: function(status, reply) {
						atheos.toast.show(reply);
						if (status === 'error') return;
						if (reply == 'invalid_token')
						{
							carbon.publish('evaluate.invalid_token', reply.path);
						}
						token = reply;
					}
			});
		  }

				var formData = {
					"user_id": 'test123@test123.it' //TODO sostituire con active user
				};
				
				fetch("http://checkhost.local:8025/auth_token", {
					method: "POST",
					headers: {
					"Content-Type": "application/json"
					},
					body: JSON.stringify(formData)
				})
				.then(response => {
					if (!response.ok) {
					throw new Error('Network response was not ok');
					}
					return response.json();
				})
				.then(data => {
					console.log(data);
					const token = data.access_token;
					localStorage.setItem('jwtToken', token.split("'")[1].split("'")[0]);
					if (data === "authenticated") {
					carbon.publish('evaluate.authenticated', reply.path);
					} else if (data === "authentication_error") {
					carbon.publish('evaluate.authentication_error', reply.path);
					}
				})
				.catch(error => {
					console.error('Error:', error);
				});
		},
		dock: {
			load: function() {
				self.dock.collapse();
			},
			expand: function() {
				self.sideExpanded = true;
				oX('#SBRIGHT #evaluate_out').css('height', '');
				oX('#SBRIGHT>.content').css('bottom', '');
				oX('#test-collapse').replaceClass('fa-chevron-circle-up', 'fa-chevron-circle-down');
			},
			collapse: function() {
				self.sideExpanded = false;
				var height = oX('#SBRIGHT #evaluate_out .title').height();
				oX('#SBRIGHT #evaluate_out').css('height', height + 'px');
				oX('#SBRIGHT>.content').css('bottom', height + 'px');
				oX('#test-collapse').replaceClass('fa-chevron-circle-down', 'fa-chevron-circle-up');
			}
		},

		//////////////////////////////////////////////////////////////////////80
		// BUILD_METHOD: build main.c file
		//////////////////////////////////////////////////////////////////////80
		build: function() {
				buildAction();
				console.log("build");
			},
			//////////////////////////////////////////////////////////////////////80
			// TEST_METHOD: build and test main.c file
			//////////////////////////////////////////////////////////////////////80
			test: function() {
					testAction();
					console.log("test");
				},
			//////////////////////////////////////////////////////////////////////80
			// DO NOTHING METHOD: it enables the override of the default behaviour with an empty behaviour
			//////////////////////////////////////////////////////////////////////80
			doNothing: function() {
				console.log("Operation not allowed");
			},
			getTraccia: function() {
					tracciaAction();
					
				},

			
	};

})();

function apriScheda(evt, nomeScheda) {
	var i, testoscheda, pulsante;
	console.log("hello");
	testoscheda = document.getElementsByClassName("testoscheda");
	for (i = 0; i < testoscheda.length; i++) {
	  testoscheda[i].style.display = "none";
	}
	pulsante = document.getElementsByClassName("pulsante");
	for (i = 0; i < pulsante.length; i++) {
	  pulsante[i].className = pulsante[i].className.replace(" active", "");
	}
	document.getElementById(nomeScheda).style.display = "block";
	evt.currentTarget.className += " active";
  }


            
function loadInterface() { 
	ul_checks = '<table style="text-align:center;"><tbody><tr><td>build</td><td>exec</td><td>outfile</td><td>test</td></tr>';
	ul_checks += '<tr><td><i class="fas fa-archive"></i></td><td><i class=\"fas fa-archive\"></i></td><td><i class=\"fas fa-archive\"></i></td><td><i class=\"fas fa-archive\"></i></td></tr></tbody></table>';
	out_wind = '<div id="evaluate_out"><div class="title"><h2>Test Output</h2> <i id="test-collapse" class="fas fa-chevron-circle-down"></i></div><div class="content">'+ul_checks+'</div>';
	logs_space = '<div id="logs"><div class="title"><h2>Test Output</h2> <i id="test-collapse" class="fas fa-chevron-circle-down"></i></div><div class="content"><div class="scheda"><button class="pulsante" onclick="apriScheda(event, \'HTML\')" id="schedaPredefinita">HTML</button><button class="pulsante" onclick="apriScheda(event, \'CSS\')">CSS</button><button class="pulsante" onclick="apriScheda(event, \'JS\')">JS</button><button class="pulsante" onclick="apriScheda(event, \'PHP\')">PHP</button></div></div>';

	$('#SBRIGHT').append(out_wind);
	document.getElementById("workspace").style.gridTemplateRows = "auto 1fr 1fr auto";
	document.getElementById("workspace").style.gridTemplateAreas = `"leftsb active rightsb" "leftsb editor rightsb" "leftsb logs rightsb" "leftsb bottom rightsb" `;
	const newArea = document.createElement("div");
	newArea.id= "LOGS";
	newArea.style.gridArea = 'logs';
	document.getElementById("workspace").appendChild(newArea);

	const handleDiv = document.createElement('div');
	handleDiv.classList.add('handle');
	//set innerHTML of handleDiv with a centered text
	handleDiv.innerHTML = '<p style="width:100%; text-align:center">---</p>';
	newArea.appendChild(handleDiv);

	handleDiv.style.width="100%";
	handleDiv.style.height="15px";
	handleDiv.style.cursor="row-resize";
	//create div to contain tex
	const textDiv = document.createElement('div');
	textDiv.classList.add('title');
	textDiv.innerHTML = '<div class="scheda"><button class="pulsante" onclick="apriScheda(event, \'HTML\')" id="schedaPredefinita">HTML</button><button class="pulsante" onclick="apriScheda(event, \'CSS\')" id="schedaCSS">CSS</button><button class="pulsante" onclick="apriScheda(event, \'JS\')" id="schedaJS">JS</button></div>';
	newArea.appendChild(textDiv);
	document.getElementById("schedaPredefinita").innerHTML = "<div id=\"HTML\" class=\"testoscheda\"><h2>HTML</h2><p>HyperText Markup Language</p></div>";
	document.getElementById("schedaCSS").innerHTML = "<div id=\"HTML\" class=\"testoscheda\"><h2>HTML</h2><p>HyperText Markup Language</p></div>";
	document.getElementById("schedaJS").innerHTML = "<div id=\"HTML\" class=\"testoscheda\"><h2>HTML</h2><p>HyperText Markup Language</p></div>";



	let isDragging = false;

	// Aggiungi le coordinate dell'ultimo punto di click sul manico (handleDiv)
	let lastY;
	
	// Aggiungi gli eventi di mouse per iniziare e terminare il trascinamento
	handleDiv.addEventListener('mousedown', (e) => {
	  isDragging = true;
	  lastY = e.clientY;
	  e.preventDefault(); // Evita la selezione indesiderata del testo
	});
	
	document.addEventListener('mouseup', () => {
	  isDragging = false;
	});
	
	const minLogsPercentage = 10; // Puoi regolare questo valore a tuo piacimento

	document.addEventListener('mousemove', (e) => {
	if (!isDragging) return;

	// Calcola la posizione verticale del manico rispetto all'altezza totale dell'area
	const workspace = document.getElementById('workspace');
	const totalHeight = workspace.offsetHeight;
	const handlePosition = e.clientY - workspace.offsetTop;

	// Calcola le percentuali di altezza per le righe
	const editorPercentage = (handlePosition / totalHeight) * 100;
	const logsPercentage = 100 - editorPercentage - minLogsPercentage;

	// Imposta le altezze delle righe in base alle percentuali calcolate
	workspace.style.gridTemplateRows = `auto ${editorPercentage}% ${logsPercentage}% auto`;

	// Imposta lastY al valore corrente per il prossimo spostamento
	lastY = e.clientY;
	});


	fX('#test-collapse').on('click', function() {
		if (self.sideExpanded) {
			self.dock.collapse();
			//atheos.settings.save('project.dockOpen', false, true);
			//storage('project.dockOpen', false);
		} else {
			self.dock.expand();
			//atheos.settings.save('project.dockOpen', true, true);
			//storage('project.dockOpen', true);
		}
	});


	var linkElementCodeGit = $('#SBRIGHT a[onclick="atheos.codegit.showCodeGit();"]');
	linkElementCodeGit.css({'display': 'None'});
	linkElementCodeGit.attr("onclick", "atheos.elpro.doNothing()")

	var linkElementMacroEditor = $('#SBRIGHT a[onclick="atheos.macro.showMacro();"]');
	linkElementMacroEditor.css({'display': 'None'});
	linkElementMacroEditor.attr("onclick", "atheos.elpro.doNothing()")



	var linkElementSettings = $('#SBRIGHT a[onclick="atheos.settings.show();"]');
	linkElementSettings.css({'display': 'None'});
	linkElementSettings.attr("onclick", "atheos.elpro.doNothing()")

	var linkElementPassword = $('#SBRIGHT a[onclick="atheos.user.changePassword();"]');
	linkElementPassword.css({'display': 'None'});
	linkElementPassword.attr("onclick", "atheos.elpro.doNothing()")

	var linkElementHelp = $('#SBRIGHT a[onclick="window.open(\'https://www.atheos.io/\');"]');
	linkElementHelp.css({'display': 'None'});
	linkElementHelp.attr("onclick", "atheos.elpro.doNothing()")


}



function buildAction() { 

	const url = 'http://localhost:8025/build'; // L'URL dell'API
	const token = localStorage.getItem('jwtToken');
	fetch(url, {
		method: 'POST',
		headers: {
			'Authorization': `JWT ${token}`
			}
		})
	  .then(response => {
		// Controlla se la risposta è stata ricevuta con successo (status 200)
		if (!response.ok) {
		  throw new Error('Network response was not ok');
		}
		return response.json(); // Parsifica la risposta come JSON
	  })
	  .then(data => {
		// Usa i dati ottenuti dalla chiamata API
		console.log(data);
	  })
	  .catch(error => {
		// Gestisce gli errori della chiamata API
		console.error('Error:', error);
	  });

}


function testAction() { 
	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
	if (this.readyState == 4 && this.status == 200) {
		console.log(this.responseText);
	}
	};
	xhttp.withCredentials = true;
}


function tracciaAction() { 
	const url = 'http://localhost:8025/exercise_atheos'; // L'URL dell'API
				const token = localStorage.getItem('jwtToken');
				fetch(url, {
					method: 'GET',
					headers: {
						'Authorization': `JWT ${token}`
						}
					})
				  .then(response => {
					// Controlla se la risposta è stata ricevuta con successo (status 200)
					if (!response.ok) {
					  throw new Error('Network response was not ok');
					}
					return response.json(); // Parsifica la risposta come JSON
				  })
				  .then(data => {
					//get htmlpage field of the json data
					htmlpage = data.htmlpage;
				})
				  .catch(error => {
					// Gestisce gli errori della chiamata API
					console.error('Error:', error);
				  });
				atheos.modal.load(900, {
					target: 'elpro',
					action: 'openDialog',
					callback: function() {
						console.log("callback");
						var tracciaHTML = htmlpage;
			
						// Inserisci il codice HTML nel div con ID "Traccia"
						$('#Traccia').html(tracciaHTML);
					}
				});
				console.log("getTraccia");
	
}

