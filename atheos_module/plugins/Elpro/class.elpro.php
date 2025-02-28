<?php

//////////////////////////////////////////////////////////////////////////////80
// Template Class
//////////////////////////////////////////////////////////////////////////////80
// Copyright (c) 2020 Liam Siira (liam@siira.io), distributed as-is and without
// warranty under the MIT License. See [root]/license.md for more.
// This information must remain intact.
//////////////////////////////////////////////////////////////////////////////80
// Authors: Atheos Team, @hlsiira
//////////////////////////////////////////////////////////////////////////////80

class Elpro {

	//////////////////////////////////////////////////////////////////////////80
	// PROPERTIES
	//////////////////////////////////////////////////////////////////////////80
	private $activeUser = null;
	private $api_key='1234';

	//////////////////////////////////////////////////////////////////////////80
	// METHODS
	//////////////////////////////////////////////////////////////////////////80

	// ----------------------------------||---------------------------------- //

	//////////////////////////////////////////////////////////////////////////80
	// Construct
	//////////////////////////////////////////////////////////////////////////80
	public function __construct($activeUser) {
		$this->activeUser = $activeUser;
		

	}
	public function py_authenticate(){
		$data = array();
		$data['user_id'] = $this->activeUser;
		$data['api_key'] = $this->api_key;
 		$token = $this->httpPost('localhost:5000/auth_token', $data);
		return $token;
	}



	public function notify_event($event){
		$data = array();
		$data['user_id'] = $this->activeUser;
		$data['api_key'] = $this->api_key;
		$data['event'] = $event;
		$data['info'] = ''.time();
 		$token = $this->httpPost('localhost:5000/api/notify', $data);
		return $token;
	}



	function httpPost($url, $data)
	{
    $curl = curl_init($url);
    curl_setopt($curl, CURLOPT_POST, true);
    curl_setopt($curl, CURLOPT_POSTFIELDS, http_build_query($data));
    curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
    $response = curl_exec($curl);
    curl_close($curl);
    return $response;
}

	
	public function test()
	{
       return "ciao";
	}

}
