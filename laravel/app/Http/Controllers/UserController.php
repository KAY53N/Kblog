<?php
namespace App\Http\Controllers;

use App\User;
use App\Http\Controllers\Controller;

class UserController extends Controller
{
    /**
     * Ϊָ���û���ʾ����
     *
     * @param int $id
     * @return Response
     */
    public function showProfile($id)
    {
        return view('welcome', ['id'=>$id]);
    }
}