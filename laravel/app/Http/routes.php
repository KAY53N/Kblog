<?php

Route::group(['middleware' => ['web']], function(){
	//Route::get('account/{id}', 'UserController@showProfile');
	Route::get('index', 'PageController@index');
	Route::get('signin', 'AccountController@signin');
	Route::post('signin', 'AccountController@signin');
});
