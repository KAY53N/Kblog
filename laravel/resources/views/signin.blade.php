
@include('public.header')

	<div class="uk-container uk-container-center uk-margin-top uk-margin-large-bottom">

		<div class="uk-alert uk-alert-danger margin_20_200"></div>

		<div class="uk-panel uk-panel-box padding_40 margin_20_200">
			<h3 class="uk-panel-title" style="margin-top:-20px">登录</h3>
				<form class="uk-form uk-form-horizontal" method="POST" action="">
				<div class="uk-form-row">
					<label for="form-user" class="uk-form-label">用户名：</label>
					<div class="uk-form-controls">
						<input type="text" placeholder="请输入用户名" name="username" id="form-user" class="uk-form-width-large" maxlength="30">
						<label class="error"></label>
					</div>
				</div>
				<div class="uk-form-row">
					<label for="form-pwd" class="uk-form-label">密码：</label>
					<div class="uk-form-controls">
						<input type="password" placeholder="请输入密码" name="upwd" id="form-pwd" class="uk-form-width-large" maxlength="16">
						<label class="error"></label>
					</div>
				</div>
				<div class="uk-form-row">
					<div class="uk-form-controls">
						<button class="uk-button uk-button-success fr" type="submit">登录</button>
					</div>
				</div>
				
				</form>
		</div>

    </div>

@include('public.footer')

<script>
$('form').validate({
		messages: vMessage,
		rules: {
			username: {
				required: true,
				minlength: 5
			},
			upwd: {
				required: true,
				minlength: 6
			}
		},
		errorPlacement: function(error, element) {  
			error.appendTo(element.parent());  
		}
});
$('input').focusin(function(){
	$('.uk-alert').detach();
});
</script>
