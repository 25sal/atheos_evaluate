var settings = getSettings();

    context_menu_2 = new dhtmlXMenuObject();
	context_menu_2.setIconsPath('./static/codebase/imgs/');
	context_menu_2.renderAsContextMenu();

	if(settings.language=="vhdl")
		context_menu_2.loadStruct('<menu><item type="item" id="delete" text="delete file" /><item type="item" id="download" text="download" /><item type="item" id="menuitem_2" text="cancel" /></menu>');
	else
		context_menu_2.loadStruct('<menu><item type="item" id="download" text="download" /><item type="item" id="menuitem_2" text="cancel" /></menu>');



	window.dhx4.skin = 'dhx_web';

	var main_layout = new dhtmlXLayoutObject(document.body, '2E');
      


	var upper_cell = main_layout.cells('a');
	var layout_up= upper_cell.attachLayout('2U')
        var a = layout_up.cells('a');
	var layout_1 = a.attachLayout('2E');
	var toolbar = upper_cell.attachToolbar();
	toolbar.setIconsPath('./static/codebase/imgs/');
	
	toolbar.loadStruct('testtoolbar', function() {});
	//upper_cell.setHeight('700');
	//upper_cell.setWidth('550');



	//upper_cell.fixSize(1,1);
	toolbar.attachEvent('onClick', function(id){
		if(id=="logout")
		{
			window.location="/logout";
			
		}
		else if(id=="info")
			showinfo();
	});


	
        var cell_1 = layout_1.cells('a');
        cell_1.setHeight('220');
        //cell_1.fixSize(1,1);
	var cell_2 = layout_1.cells('b');
	var grid_2 = cell_2.attachGrid();
	grid_2.setIconsPath('./static/codebase/imgs/');
	cell_2.hideHeader();
	//cell_2.fixSize(1,1);

	
	
	grid_2.load('testgrid', 'xml');
	
	grid_2.attachEvent('onRowSelect', function(id, ind){
	
		
		context_menu_2.setUserData("delete", "filename",grid_2.getRowData(id)['c1']);
		context_menu_2.setUserData("download", "filename",grid_2.getRowData(id)['c1']);
		//context_menu_2.addContextZone(id);
		context_menu_2.showContextMenu(100,300);

	});
	
	grid_2.attachEvent('onRightClick', function(id, ind, obj){
		context_menu_2.setUserData("delete", "filename",grid_2.getRowData(id)['c1']);
		//context_menu_2.addContextZone(id);
		context_menu_2.setUserData("download", "filename",grid_2.getRowData(id)['c1']);
		context_menu_2.showContextMenu(100,300);
	});

	



	var rightcells = layout_up.cells('b');
	var right_layoyt=rightcells.attachLayout('1C');

	var test_status = right_layoyt.cells('a');
	test_status.setHeight('250');
	test_status.setWidth('1100');
	test_status.fixSize(1,1);
	test_status.setText("Test Status");

/*
	var out_test=right_layoyt.cells('b');
	out_test.attachURL('./data/default.html', true);
	out_test.hideHeader();
	*/


	var str = [
		{ type:"settings" , labelWidth:80, inputWidth:250, position:"absolute"  },
		{ type:"button" , name:"Test", label:"Test", value:"Test", width:"250", inputLeft:5, inputTop:20  },
		{ type:"input" , name:"form_input_1", label:"Last Test Result", value:"Failed", labelWidth:250, readonly:true, tooltip:"Number of", info: true, labelLeft:550, labelTop:5, inputLeft:550, inputTop:21  },
		{ type:"input" , name:"form_input_2", label:"Test Passed", labelWidth:250, labelAlign:"left", labelLeft:275, labelTop:5, inputLeft:275, inputTop:21  },
		{ type:"btn2state" , name:"consegna", label:"Consegna", labelWidth:150, labelLeft:5, labelTop:80, inputLeft:80, inputTop:74  },
		{ type: "input", name:"testlog", label: "Test Ouput", rows:36, value: "", width:1050, inputTop:150, labelTop:130 }
	];
	var testform = test_status.attachForm();
	testform.loadStruct("testform");
	testform.attachEvent('onChange', function(id, value){
	
		 $.ajax
                  ({
                         url: 'submit.php?status='+testform.isItemChecked(id),
                         type: 'get',
                         contentType: false,
                         processData: false,
                         success: function(response)
                                 {
				     if(testform.isItemChecked(id))
					alert("compito consegnato");
				     else
					alert("compito ritirato");
				  }
		});


          });
	testform.attachEvent("onButtonClick", function (name,command)
	   {
		

		 testform.enableItem("consegna");


		if(name=='Test')
		{
		  $.ajax
		  ({
			 url: 'exec',
			 type: 'get',
			 contentType: false,
			 processData: false,
			 success: function(response)
				  {
					var oldtext = testform.getItemValue("testlog");
					testform.setItemValue("testlog",response+"-----------------------------\n"+oldtext);
					 $.ajax
                                                                ({
                                                                   url: 'results',
                                                                   type: 'get',
                                                                   success: function(response)
                                                                   {
                                                                        var results = JSON.parse(response);
                                                                        testform.setItemValue("tp",results.tp);
																		testform.setItemValue("tf",results.tf);
																		if(!results.hasOwnProperty("built")||(results.built==0))
																		 testform.setItemLabel("msg_consegna", "Il programma non ha compilato");
													  				    else if(!results.hasOwnProperty("execution")||(results.execution==0))
																		 testform.setItemLabel("msg_consegna", "Il programma non esegue");
																		else if(!results.hasOwnProperty("outfile")||(results.outfile==0))
																		 testform.setItemLabel("msg_consegna", "Il file output.bin non viene creato");
																		else 
																		{	testform.enableItem("consegna");
																		 if(!results.hasOwnProperty("test")||(results.test==0))
																			 {  testform.setItemLabel("msg_consegna", "Consegna abilitata, ma nessun test concluso con successo");
																			    $.notify("test failed","warn");
																   			}
																		 else
																			{
																			  testform.setItemLabel("msg_consegna", "Consegna incoraggiata, almeno un test concluso con successo");
																			  $.notify("test passed","success");
																			 }
																			}
																		 
																		  
                                                                        }
                                                                        });

				   },
			  });


			  logtext.detachObject(true);
			  logtext.attachURL("checks");

			 }


	   }
	
	);







	function exercise()
	{return '<a href="exercise" target="_blank"> Apri Traccia</a>';}

	var exercise_list = getExercises();
	
	var ex_select =  { type:"select" , name:"exercise", label:"Seleziona Traccia", inputWidth:140, options: exercise_list, width:175, labelWidth:175, labelLeft:5, labelTop:15 };


	 var strForm =[
		 
		//{ type:"fieldset" , name:"form_fieldset_1", label:"Files", list:[
		ex_select,
		{type: "template", label: "", value: "Scarica traccia", format:exercise, width:125, inputWidth:125},
		{type:"label" , name:"Load_file", label:"Load "+settings.language+" file", width:175, labelWidth:175   },
		{ type:"file" ,id:"fileSelect", name:"fileSelect", inputWidth:220, labelLeft:395 },
		{ type:"button"  ,name:"Upload_File", label:"Upload File", value:"Upload File", width:"125", inputWidth:125},
	//]}
		
	 ];
	
	
	var files_form = cell_1.attachForm(strForm);
			


	

			cell_1.setText(settings.language + " Language");
			files_form.attachEvent('onChange', function(id, value){

				if(id=="exercise")
				{
					var fd = new FormData();
					fd.append('exercise', value);
					$.ajax
					({
					   url: 'test',
					   type: 'post',
					   data: fd,
					   contentType: false,
					   processData: false,
					   success: function(response)
							{
								grid_2.load('testgrid', 'xml');
								$.ajax
			                                        ({
        			                                   url: 'results',
                                           			   type: 'get',
                                           			   success: function(response)
                                                                   {
                                                                        var results = JSON.parse(response);	
									testform.setItemValue("testlog","");
									testform.setItemValue("tp",results.tp);
									testform.setItemValue("tf",results.tf);
                                                         		}      
                                                			});

								
							 },
						});
	 			 }
				}
			);
			
		


			files_form.attachEvent('onButtonClick', function(name, command)
		 {
			if(name=='Upload_File')
			{
      
	       var fd = new FormData();
		     var files = document.getElementsByName('fileSelect')[0].files[0];
		     // console.log(files);
		     if(files==undefined)
				 {
          			alert("inserisci file");
				 }else{
              fd.append('file', files);
              $.ajax
							 ({
				 		       url: 'upload',
				 		       type: 'post',
				 		       data: fd,
				 		       contentType: false,
				 		       processData: false,
				 		       success: function(response)
									 {

										$.notify("uploaded","info");
										grid_2.load('testgrid', 'xml');
										logtext.detachObject(true);
										logtext.attachURL("checks");
										if(testform.getItemLabel("msg_consegna")=="Manca upload della soluzione")
										 testform.setItemLabel("msg_consegna","Il programma non è stato compilato");

							 		 },
						       error:  function (xhr, ajaxOptions, thrownError) {
        							//alert(xhr.status);
        							//alert(thrownError);
								$.notify("upload failure","error");
								alert("Upload Failed, please Refresh the page.");
								},
							complete: function (data) {
        							document.getElementsByName('fileSelect')[0].value=""; // this will reset the form fields
   										}	
								 });
                }
			
			  }
			 
			  
			});


context_menu_2.attachEvent('onClick', function(id, zoneId, casState){
	
		if(id=="delete")
		  {
			   var fd = new FormData();
			   fd.append("filename",context_menu_2.getUserData(id,"filename"));
			   $.ajax
							 ({
				 		       url: 'delete',
				 		       type: 'post',
				 		       data: fd,
				 		       contentType: false,
				 		       processData: false,
				 		       success: function(response)
									 {
										$.notify("deleted");
									    grid_2.load('testgrid', 'xml');
							 		 },
								 });
			  
			  }
	
			  else if(id=="download")
			  {
				
										window.location = 'download?filename='+context_menu_2.getUserData(id,"filename");

			  }
			   
	});



	var logcell = main_layout.cells("b");
	logcell.hideHeader();
	logcell.setHeight('100');
        logcell.fixSize(1,1);


	var loglayout = logcell.attachLayout("2U");
	var countdown = loglayout.cells("a");
	countdown.hideHeader()
	
	countdown.attachURL('static/countdown/countdown.html');
	//countdown.setHeight("150");
	countdown.setWidth('200');
	countdown.fixSize(1,1);
	
	var logtext = loglayout.cells("b");
	logtext.hideHeader();
	logtext.attachURL("checks");
	
	

function getSettings()
{
	var jsonsettings;
	var fd = new FormData();
	$.ajax
				  ({
					 url: '/setoptions',
					 type: 'post',
					 data: fd,
					 contentType: false,
					 processData: false,
					 async: false,
					 success: function(response)
						  {
							 jsonsettings = JSON.parse(response);

						   },
					  });
	return jsonsettings;
}

function getExercises()
{
    var exercises=[];
	var fd = new FormData();
	$.ajax
				  ({
					 url: '/listexercise',
					 type: 'post',
					 data: fd,
					 contentType: false,
					 processData: false,
					 async: false,
					 success: function(response)
						  {
							  console.log("success");
							 var options = JSON.parse(response);
							 for (var i=0;i< options.length;i++)
							  {
								  var option = {};
								  option["value"] = options[i].value;
								  option["text"] = options[i].text;
								  if(settings.exercise==options[i].value)
								    option["selected"]="true";
								  exercises[i]=option;

							  }
							   

						   },
					  });
	return exercises;

}

function setLanguage(lang)
{
	
	var fd = new FormData();
			   fd.append("language", lang);
			   $.ajax
							 ({
				 		       url: '/setoptions',
				 		       type: 'post',
								data: fd,
				 		       contentType: false,
								processData: false,
								async: false,
				 		       success: function(response)
									 {
										window.location = '/test';

							 		 },
								 });

}

function showinfo()
{
  	var windows = new dhtmlXWindows();
	windows.setSkin('dhx_web');

	var window_1 = windows.createWindow('infowindow', 400, 200, 600, 500);
	window_1.attachURL('/static/data/info.html', true);

	window_1.button('minmax').show();
	window_1.button('minmax').enable();
	window_1.setText('Info');
}
