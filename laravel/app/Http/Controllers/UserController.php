<?php
namespace App\Http\Controllers;

use App\User;
use App\Http\Controllers\Controller;

class UserController extends Controller
{
    /**
     * 为指定用户显示详情
     *
     * @param int $id
     * @return Response
     */
    public function showProfile($id)
    {
        return view('welcome', ['id'=>$id]);
    }
}