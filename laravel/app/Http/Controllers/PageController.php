<?php
namespace App\Http\Controllers;

use App\Page;
use Illuminate\Http\Request;

use DB;
use App\Http\Controllers\Controller;

class PageController extends Controller
{
    public function index(Request $request)
    {
    	$userInfo = $request->session()->get('uInfo');
        return view('index', ['userInfo'=>$userInfo]);
    }
}