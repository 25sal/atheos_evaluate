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
var hostname = "http://"+window.location.hostname+":8025";

var username = "test";
var secret = "test";



function update_results()
{
	const url = hostname+'/api/results'; // L'URL dell'API
	const token = localStorage.getItem('jwtToken');
	fetch(url, {
		method: 'POST',
		headers: {
			'Authorization': `Bearer ${token}`
			}
		})
		
	  .then(response => {
		// Controlla se la risposta è stata ricevuta con successo (status 200)
		if (!response.ok) {
		  throw new Error('Network response was not ok');
		}
		//return response.json(); // Parsifica la risposta come JSON
		return response.json();
	  })
	  .then(data => {
		

		toggle_checks('evaluate_built', data['built']);
		toggle_checks('evaluate_exec', data['execution']);
		toggle_checks('evaluate_outfile', data['outfile']);
		toggle_checks('evaluate_test', data['passed']);
		tpsd = document.getElementById('test_passed');
		tpsd.value=data['passed'];
		tpsd = document.getElementById('test_failed');
		tpsd.value=data['failed'];
			
	  })
	  .catch(error => {
		// Gestisce gli errori della chiamata API
		atheos.toast.show('error:', error);
	  });


}


function toggle_checks(item, value)

{
	ev_b = document.getElementById(item);
	if(value >0)
	{
	   ev_b.classList.remove('fa-times');
	   ev_b.classList.add('fa-check');	
	   ev_b.style.color="blue";				
	}
	else
	{
	   ev_b.classList.remove('fa-check');
	   ev_b.classList.add('fa-times');	
	   ev_b.style.color="red";
	}

}

function html_logs(output){

no_of_warnings =0;
no_of_errors=0;
html_string="";
output.split(/\r?\n|\r/).forEach((line) => {
  let str = line;
  str = he.decode(str);
  if (str.toLowerCase().includes('warning:')) {
    html_string +='<span style="color: orange;">' + str + '</span><br>';
    html_string +='<br>'; // Empty line
    no_of_warnings++;
  } else if (str.toLowerCase().includes('in function')) {
    html_string +='<br>';
    html_string +='<strong>' + str + '</strong><br>';
  } else if (str.toLowerCase().includes('error:')) {
    //html_string +='<span style="color: red; ">' + '-'.repeat(str.length) + '</span><br>';
    html_string +='<span style="color: red; ">' + str + '</span><br>';
    //html_string +='<span style="color: red;">' + '-'.repeat(str.length) + '</span><br>';
    no_of_errors++;
  } else if (str.includes(' Error ')||  str.includes('undefined reference')) {
    //html_string +='<span style="color: red; ">' + '-'.repeat(str.length) + '</span><br>';
    html_string +='<span style="color: red; ">' + str + '</span><br>';
    //html_string +='<span style="color: red; ">' + '-'.repeat(str.length) + '</span><br>';
    no_of_errors++;
  } else {
    html_string +='<span style="color: white;">' + str + '</span><br>';
  }
});



return html_string;
}



function activeLog(){
	document.getElementById("evaluate_tests").style.display = "None";
	document.getElementById("evaluate_logs").style.display = "Block";
	document.getElementById("evaluate_build").style.display = "None";
}

function activeBuild(){
	document.getElementById("evaluate_tests").style.display = "None";
	document.getElementById("evaluate_logs").style.display = "None";
	document.getElementById("evaluate_build").style.display = "Block";
}
function activeTest(){
	document.getElementById("evaluate_tests").style.display = "Block";
	document.getElementById("evaluate_logs").style.display = "None";
	document.getElementById("evaluate_build").style.display = "None";
}

function aggiungiSottolineaturaElemento(idElemento) {
    var elemento = document.getElementById(idElemento);
    if (elemento) {
        elemento.style.textDecoration = "underline white";
        elemento.style.textDecorationThickness = "2px";
        elemento.style.textDecorationSkipInk = "none";
        elemento.style.textUnderlineOffset = "4px";
    } else {
        console.error("L'elemento con l'ID specificato non esiste.");
    }
}
function rimuoviSottolineaturaElemento(idElemento) {
    var elemento = document.getElementById(idElemento);
    if (elemento) {
        elemento.style.textDecoration = "None";
    } else {
        console.error("L'elemento con l'ID specificato non esiste.");
    }
}

function apriScheda(evt, nomeScheda) {
	var i, testoscheda, pulsante;
	testoscheda = document.getElementsByClassName("testoscheda");
	if(nomeScheda === "buttonLogs"){
		activeLog();
		aggiungiSottolineaturaElemento("logs");
		rimuoviSottolineaturaElemento("build");
		rimuoviSottolineaturaElemento("test");
	}
	else if (nomeScheda === "buttonBuild"){
		activeBuild();
		aggiungiSottolineaturaElemento("build");
		rimuoviSottolineaturaElemento("logs");
		rimuoviSottolineaturaElemento("test");

	}
	else if (nomeScheda === "buttonTest"){
		activeTest();
		aggiungiSottolineaturaElemento("test");
		rimuoviSottolineaturaElemento("build");
		rimuoviSottolineaturaElemento("logs");

	}
  }

(function() {

	let self = false;

	// Initiates plugin as a third priority in the system.
	carbon.subscribe('system.loadExtra', () => atheos.elpro.init());
	
	atheos.elpro = {
		sideExpanded: true,

		init: function() {
			if (self) return;
			self = this;
			console.log('Elpro plugin loaded!');
			$('#fm_toggle_hidden').remove();
			

			ul_checks = '<table style="text-align:center;"><tbody><tr><td>build</td><td>exec</td><td>outfile</td><td>test</td></tr>';
			ul_checks += '<tr><td><i id="evaluate_built" class="fas fa-times" style="color:red"></i></td><td><i id="evaluate_exec" class="fas fa-times" style="color:red"></i></td><td><i id="evaluate_outfile" class="fas fa-times" style="color:red"></i></td><td><i id="evaluate_test" class="fas fa-times" style="color:red"></i></td></tr><tr><td colspan=2>passed:<input id="test_passed" enabled=false value="0" size=1 /></td> <td colspan=2>failed:<input enabled=false size=1  value=0 id="test_failed"/></td></tr></tbody></table>';
            out_wind = '<div id="evaluate_out"><div class="title"><h2>Test Output</h2> <i id="test-collapse" class="fas fa-chevron-circle-down"></i></div><div class="content">'+ul_checks+'</div>';
			logs_space = '<div id="logs"><div class="title"><h2>Test Output</h2> <i id="test-collapse" class="fas fa-chevron-circle-down"></i></div><div class="content"><div class="scheda"><button class="pulsante" onclick="apriScheda(event, \'HTML\')" id="schedaPredefinita">HTML</button><button class="pulsante" onclick="apriScheda(event, \'CSS\')">CSS</button><button class="pulsante" onclick="apriScheda(event, \'JS\')">JS</button></div></div>';

			$('#SBRIGHT').append(out_wind);

                        //start_exam_button = '<div class="overlay" id="overlay"><button class="block-button" onclick="unblockPage()">Premi iniziare il test</button></div>';
                        //$('#EDITOR').append(start_exam_button);

                        // Inserisce lo stile del CSS direttamente nel JavaScript
          var style = document.createElement('style');
          style.innerHTML = `
                body {
                  margin: 0;
                  padding: 0;
                }

                /* Stile dell'overlay */
                .overlay {
                  position: fixed;
                  top: 0;
                  left: 0;
                  width: 100%;
                  height: 100%;
                  background-color: rgba(0, 0, 0, 0.5); /* Sfondo semitrasparente */
                  display: flex;
                  justify-content: center;
                  align-items: center;
                }
                 /* Stile del pulsante */
                .block-button {
                  padding: 20px 40px;
                  font-size: 18px;
                  background-color: #007bff;
                  color: #fff;
                  border: none;
                  cursor: pointer;
                  border-radius: 5px;
                }
				.buttonChoice {
					position: relative;
					z-index: 1;
					height: 23px;
					color: var(--fontColorMinor);
					grid-area: bottom;
					top-margin: 10px;
					
				}
				.buttonChoice:hover {
					color: white; 

				}
	

          `;

          // Aggiunge il CSS dinamico al tag head della pagina
          document.head.appendChild(style);





			document.getElementById("workspace").style.gridTemplateRows = "auto 1fr 1fr auto";
			document.getElementById("workspace").style.gridTemplateAreas = `"leftsb active rightsb" "leftsb editor rightsb" "leftsb logs rightsb" "leftsb bottom rightsb" `;
			const newArea = document.createElement("div");
			newArea.id= "LOGS"
			newArea.style.gridArea = 'logs';
			document.getElementById("workspace").appendChild(newArea);
			const buttonDiv = document.createElement("div");
			buttonDiv.innerHTML = '</div><div class="scheda"></div><a class="buttonChoice" onclick="apriScheda(event, \'buttonLogs\')" id="logs"><i class="fas fa-bug"></i> Logs</a> &nbsp;<a style="color: var(--fontColorMinor);">|</a>&nbsp; <a class="buttonChoice" onclick="apriScheda(event, \'buttonTest\')"  style="margin-right:5px;" id="test"><i class="fas fa-hammer"></i> Test</a>&nbsp;<a style="color: var(--fontColorMinor);">|</a>&nbsp;<a class="buttonChoice" onclick="apriScheda(event, \'buttonBuild\')"  style="margin-left:5px;" id="build"><i class="fas fa-cogs"></i> Build</a></div>';
			const handleDiv = document.createElement('div');
			handleDiv.classList.add('handle');
			//set innerHTML of handleDiv with a centered text
			handleDiv.innerHTML = '<p style="width:100%; text-align:center">---</p>';
			newArea.appendChild(handleDiv);
			handleDiv.style.width="100%";
			handleDiv.style.height="15px";
			handleDiv.style.cursor="row-resize";



			const handleDiv2 = document.createElement('div');
			handleDiv2.classList.add('handle');
			//set innerHTML of handleDiv with a centered text
			handleDiv2.innerHTML = '<p style="width:100%; text-align:center"></p>';
			handleDiv2.style.width="100%";
			handleDiv2.style.height="20px";
			handleDiv2.style.cursor="row-resize";
			handleDiv2.appendChild(buttonDiv);
			newArea.appendChild(handleDiv2);

			//create div to contain tex
			const textDiv = document.createElement('div');
			textDiv.classList.add('container');
			textDiv.setAttribute('id', 'evaluate_logs');
			//textDiv.style.overflow='auto';
			newArea.appendChild(textDiv);
			const testDivs = document.createElement('div');
			testDivs.classList.add('container');
			testDivs.setAttribute('id', 'evaluate_tests');
			//textDiv.style.overflow='auto';
			newArea.appendChild(testDivs);
			const buildDiv = document.createElement('div');
			buildDiv.classList.add('container');
			buildDiv.setAttribute('id', 'evaluate_build');
			//textDiv.style.overflow='auto';
			newArea.appendChild(buildDiv);
			document.getElementById("evaluate_tests").style.display = "None";
			document.getElementById("evaluate_logs").style.display = "None";
			document.getElementById("evaluate_build").style.display = "None";
			


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
			if(token == null){
				echo({
					url: atheos.controller,
					data: {
						target: 'Elpro',
						action: 'login'
					},
					settled: function(status, reply) {
						
						if (status === 'error') 
						{
						   atheos.toast.show("error", "Evaluate authentication error");
						   return;
						}
						if (reply == 'invalid_token')
						{
							atheos.toast.show("error", "Invalid JWT Token");
							carbon.publish('evaluate.invalid_token', reply.path);
						}
						
						const token = JSON.parse(reply['text']);
					
						localStorage.setItem('jwtToken',token['access_token']);
						atheos.toast.show("success", "Evaluate authentication ok!");
						

						update_results();	


						/* Notify listeners. */
						//carbon.publish('project.open', reply.path);
						//console.log(token);
					}
			});
		  }
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

 
						var xhttp = new XMLHttpRequest();
						xhttp.onreadystatechange = function() {
						if (this.readyState == 4 && this.status == 200) {
							//console.log(html_logs(this.responseText));
						$('#evaluate_build').html(html_logs(this.responseText));	
                                                activeBuild();
							
						}
						};
						//xhttp.withCredentials = true;
						xhttp.open("POST", hostname+"/build", true);
						const token = localStorage.getItem('jwtToken');
						 xhttp.setRequestHeader('Authorization',`Bearer ${token}`);

						xhttp.send();


				
			},
		
			//////////////////////////////////////////////////////////////////////80
			// TEST_METHOD: build and test main.c file
			//////////////////////////////////////////////////////////////////////80
			test:  function() {
				const url = hostname+'/api/test'; // L'URL dell'API
				const token = localStorage.getItem('jwtToken');
				fetch(url, {
					method: 'GET',
					headers: {
						'Authorization': `Bearer ${token}`
						}
					})
					
				  .then(response => {
					// Controlla se la risposta è stata ricevuta con successo (status 200)
					if (!response.ok) {
					  throw new Error('Network response was not ok');
					}
					//return response.json(); // Parsifica la risposta come JSON
					return response.json();
				  })
				  .then(data => {
					//console.log(data);
					//results = JSON.parse(data);
					$('#evaluate_build').html(html_logs(data['build_logs']));
					$('#evaluate_tests').html(html_logs(data['test_logs']));
					$('#evaluate_logs').html(html_logs(data['exec_logs']));
					activeTest();
					toggle_checks('evaluate_built', data['built']);
					toggle_checks('evaluate_exec', data['execution']);
					toggle_checks('evaluate_outfile', data['outfile']);
					toggle_checks('evaluate_test', data['passed']);
					tpsd = document.getElementById('test_passed');
					tpsd.value=data['passed'];
					tpsd = document.getElementById('test_failed');
					tpsd.value=data['failed'];
						
				  })
				  .catch(error => {
					// Gestisce gli errori della chiamata API
					atheos.toast.show('error:', error);
				  });
				
					
				},
			restoreInput: function(){
				echo({
					url: atheos.controller,
					data: {
						target: 'elpro',
						action: 'resetInput'
					},
					settled: function(status, reply) {
						if (status == 'success') 
						  atheos.toast.show("notice", "Input restored");
						else 
						atheos.toast.show("error", "Input not restored!");

						
					}
				});



			},
			//////////////////////////////////////////////////////////////////////80
			// TEST_METHOD: open the file with the exam description
			//////////////////////////////////////////////////////////////////////80
			getTraccia: function() {
				const url = hostname+'/api/exercise'; // L'URL dell'API
				const token = localStorage.getItem('jwtToken');
				fetch(url, {
					method: 'GET',
					headers: {
						'Authorization': `Bearer ${token}`
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
					atheos.modal.load(900, {
						target: 'Elpro',
						action: 'openDialog',
						callback: function() {
							oX('#Traccia').html(data['htmlpage']);
							//console.log(data['htmlpage']);
						}
					});
				  })
				  .catch(error => {
					// Gestisce gli errori della chiamata API
					console.error('Error:', error);
				  });
				
					
				},
                          reload_page: function() {
                                location.reload();
                        }
			
	};



})();


  function openFullscreen() {
        var elem = document.documentElement; // Ottieni l'elemento root del documento (la pagina stessa)

        if (elem.requestFullscreen) {
          elem.requestFullscreen();
        } else if (elem.mozRequestFullScreen) { /* Firefox */
          elem.mozRequestFullScreen();
        } else if (elem.webkitRequestFullscreen) { /* Chrome, Safari & Opera */
          elem.webkitRequestFullscreen();
        } else if (elem.msRequestFullscreen) { /* Internet Explorer / Edge */
          elem.msRequestFullscreen();
        }
  }


function unblockPage() {
        // Rimuove l'overlay e il pulsante
        var overlay = document.getElementById("overlay");
        overlay.parentNode.removeChild(overlay);
        openFullscreen();
        // Aggiungi l'event listener per il cambio di modalit       a schermo intero
        document.addEventListener("fullscreenchange", function() {
          if (!document.fullscreenElement) {
                // Se si esce dalla modalit       a schermo intero, ricrea l'overlay e il pulsante
                DivinePunishment();
          }
        });
  }



 function forceLogout() {
				echo({
                                        url: atheos.controller,
                                        data: {
                                                target: 'Elpro',
                                                action: 'forced_logout'
                                        }});
                                carbon.publish('user.logout');
                                atheos.settings.save();
                                echo({
                                        data: {
                                                target: 'user',
                                                action: 'logout'
                                        },
                                        settled: function() {
                                                window.location.reload();
                                        }
                                });
                        };

  function DivinePunishment() {
        forceLogout();
        // Crea l'overlay e il pulsante
        var overlay = document.createElement("div");
        overlay.className = "overlay";
        overlay.id = "overlay";


        document.body.appendChild(overlay);
  }
