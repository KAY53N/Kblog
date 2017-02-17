@include('public.header')

	<!-- Codemirror 和 marked 依赖 kaysen -->
	<link rel="stylesheet" href="/static/codemirror/lib/codemirror.css">
    <script src="/static/js/jquery.cookie.js"></script>
	<script src="/static/codemirror/lib/codemirror.js"></script>
	<script src="/static/codemirror/mode/markdown/markdown.js"></script>
	<script src="/static/codemirror/addon/mode/overlay.js"></script>
	<script src="/static/codemirror/mode/xml/xml.js"></script>
	<script src="/static/codemirror/mode/gfm/gfm.js"></script>
	<script src="/static/js/marked.min.js"></script>

	<div class="uk-container uk-container-center uk-margin-top uk-margin-large-bottom">

		<div class="uk-grid" data-uk-grid-margin>
			<div class="uk-width-medium-3-4">
				<article class="uk-article">

					<h2 class="uk-article-title">
						<a href="/detail/?aid="></a>
					</h2>
					<p class="uk-article-meta">
						<a href="" class="uk-icon-calendar f_light_blue mr20">&nbsp;</a>
						<a href="" class="uk-icon-eye f_light_blue mr20">&nbsp;</a>
						<a href="" class="uk-icon-comment f_light_blue mr20">&nbsp;</a>
					</p>

					<p>
						<a href="/detail/?aid="><img src=""></a>
					</p>

					<script type="text/html" id="mkHtml_"></script>
					<div class="word_wrap">
						<script>document.write(marked('#123'));</script>
					</div>

					<p>
	    				<a class="uk-button uk-button-primary" href="/detail/?aid=">Continue Reading</a>
					</p>

				</article>
				{% endfor %}

				<ul class="uk-pagination">ee
						<li><a href="?page=">上一页</a></li>

						<li class="uk-active">
							当前：
						</li>
						<li class="has_other_pages()"></li>
							<li><a href="?page=">下一页</a></li>
					</span>
				</ul>
			{% endif %}

			</div>

			<div class="uk-width-medium-1-4">
				<div class="uk-panel uk-panel-box uk-text-center">
					<img class="uk-border-circle" width="120" height="120" src="" alt="">
					<h3>Kaysen</h3>
					<p class="lh30 ta_l">
					技术方向:PHP、Linux、Mysql、Python<br />
					WooYun白帽子与开发者 <br />
					</p>
				</div>
				<div class="uk-panel uk-form">
					<form action="" method="POST">
						<span style="width:180px;" class="fl mr05"><input type="text" placeholder="" name="word" class="uk-width-1-1" value=""></span>
						<button type="submit" class="uk-button"><i class="uk-icon-search"></i>&nbsp;搜索</button>
					</form>
				</div>
				<div class="uk-panel">
					<h3 class="uk-panel-title">Archives</h3>
					<ul class="uk-list uk-list-line">
						<li><a href="#"></a></li>
					</ul>
				</div>
				<div class="uk-panel">
					<h3 class="uk-panel-title">Category</h3>
					<ul class="uk-list uk-list-line">
						<li><a href=""></a></li>
					</ul>
				</div>
				<div class="uk-panel">
					<h3 class="uk-panel-title">Social Links</h3>
					<ul class="uk-list">
						<li><a href="#">GitHub</a></li>
						<li><a href="#">Twitter</a></li>
						<li><a href="#">Facebook</a></li>
					</ul>
				</div>
			</div>
		</div>

	</div>

@include('public.footer')