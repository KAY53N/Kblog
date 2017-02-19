<?php
namespace App\Http\Controllers;

use App\Account;
use Illuminate\Http\Request;

use DB;
use App\Http\Controllers\Controller;

class AccountController extends Controller
{
    public function signin(Request $request)
    {
        $context = [];

        if($request->isMethod('post'))
        {
            $username = trim(strtolower($request->input('username')));
            $password = $request->input('upwd');

            $userInfo = DB::table('users')->where('username', $username)->first();
            $verifyStatus = password_verify($password, $userInfo->password);

            if(!$verifyStatus)
            {
                $context['errorMsg'] = '用户名或密码错误';
            }
            else
            {
                $request->session()->put('uInfo', [
                    'group'    => $userInfo->group,
                    'user_id'  => $userInfo->user_id,
                    'username' => $userInfo->username
                ]);

                return redirect()->action('PageController@index');            }

        }

        return view('signin', $context);
    }
}