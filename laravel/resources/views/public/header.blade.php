<!DOCTYPE html>
<html>
<head>
  <!-- Standard Meta -->
  <title>Kblog</title>

  <meta charset="utf-8" />
  <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">

  <link rel="stylesheet" href="/static/uikit/css/uikit.min.css" />
  <link rel="stylesheet" href="/static/css/css.css" />
  <script src="/static/js/jquery-2.1.1.min.js"></script>
  <script src="/static/js/jquery.cookie.js"></script>
  <script src="/static/uikit/js/uikit.min.js"></script>
  <script type="text/javascript" src="/static/jquery-validation/jquery.validate.js"></script>
  <script type="text/javascript" src="/static/jquery-validation/localization/messages_zh.js"></script>
  <script type="text/javascript" src="/static/uikit/js/components/form-password.js"></script>
  <script>
	$('.J-changeCheckcode').click(function(){
		$('.verify').trigger('click');
	});
	function csrfSafeMethod(method) {
		// these HTTP methods do not require CSRF protection
		return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
	}
	$.ajaxSetup({
		beforeSend: function(xhr, settings) {
			if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
				xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
			}
		}
	});
  </script>
  <script src="/static/uikit/js/components/notify.js"></script>
  <style>
.tm-navbar {
    padding: 15px 0;
    border: none;
    background: #000;
}

.tm-navbar .uk-navbar-content,
.tm-navbar .uk-navbar-brand,
.tm-navbar .uk-navbar-toggle {
    height: 40px;
    margin-top: 0;
    text-shadow: none;
}

.tm-navbar .uk-navbar-nav > li > a {
    height: 40px;
    margin: 0;
    border: none;
    border-radius: 3px !important;
    text-shadow: none;
    font-size: 15px;
	color:#888;
}

.tm-navbar .uk-navbar-nav > li { margin-left: 20px; }

/* Hover */
.tm-navbar .uk-navbar-nav > li:hover > a,
.tm-navbar .uk-navbar-nav > li > a:focus,
.tm-navbar .uk-navbar-nav > li.uk-open > a {
    border: none;
    color: #FFF;
}
/* Active */
.tm-navbar .uk-navbar-nav > li.uk-active > a {
    background-color: #2BA3D4;
    color: #FFF;
}

/* OnClick */
.tm-navbar .uk-navbar-nav > li > a:active { background-color: transparent; }

/*
 * Nav
 */

.tm-nav > li > a { color: #777; }

/* Hover */
.tm-nav > li > a:hover,
.tm-nav > li > a:focus,
.tm-nav > li.uk-active > a  {
    background: #F5F5F5;
    color: #444;
}

/* Sub-object: `nav-header` */
.tm-nav .uk-nav-header {
    color: #222;
    font-weight: normal;
}

/*
 * Nav
 */

.tm-subnav > li:nth-child(n+2) { margin-left: 20px; }
/* Active */
.tm-navbar .uk-navbar-nav > li.uk-active > a {
    background-color: #2BA3D4;
    color: #FFF;
}
.tm-footer {
	padding: 50px 0;
	background:#252525;
}
.tm-footer .uk-subnav-line > li::before {
    border-color: #ddd;
}
.tm-footer, .tm-footer a {
    color: #ddd !important;
}
.tm-footer a:hover {
    color: #fff !important;
}
  </style>
</head>

<body>

    <nav class="tm-navbar uk-navbar uk-navbar-attached uk-margin-large-bottom">
		<div class="uk-container uk-container-center">

			<a href="/" class="uk-navbar-brand uk-hidden-small"><img width="90" height="30" alt="UIkit" title="UIkit" src="http://www.getuikit.net/docs/images/logo_uikit.svg" class="uk-margin uk-margin-remove"></a>

			<ul class="uk-navbar-nav uk-hidden-small">
    		</ul>

			<a data-uk-offcanvas="" class="uk-navbar-toggle uk-visible-small" href="#tm-offcanvas"></a>

			<div class="uk-navbar-brand uk-navbar-center uk-visible-small"><img width="90" height="30" alt="UIkit" title="UIkit" src="/static/images/logo_uikit.svg"></div>

	
				<div class="fr f_white"> 你好！&nbsp;&nbsp;
					<div class="uk-button-dropdown">
						<button class="uk-button uk-button-primary uk-button-small">管理</button>
						<div class="uk-dropdown uk-dropdown-small">
							<ul class="uk-nav uk-nav-dropdown">
								<li><a href="/manage/">控制台</a></li>
								<li><a href="/logout/">退出</a></li>
							</ul>
						</div>
					</div>
					<a href="/logout/">退出</a>
				</div>
		
			<div class="uk-button-group fr mt05">
				<a href="/signin/" class="uk-button uk-button-danger">登陆</a>
				<a href="/signup/" class="uk-button uk-button-danger">注册</a>
			</div>
		

		</div>
	</nav>


