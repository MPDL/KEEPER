<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>KEEPER</title>
<meta http-equiv="Content-type" content="text/html; charset=utf-8" />
<meta name="keywords" content="File Collaboration Team Organization" />
<link rel="icon" type="image/x-icon" href="https://keeper.mpdl.mpg.de/media/img/favicon.png?t=1465786517" />
<!--[if IE]>
<link rel="shortcut icon" href="https://keeper.mpdl.mpg.de/media/img/favicon.png?t=1465786517"/>
<![endif]-->
<link rel="stylesheet" type="text/css" href="https://keeper.mpdl.mpg.de/media/css/seahub.min.css?t=1465786517" />
<link rel="stylesheet" type="text/css" href="https://keeper.mpdl.mpg.de/media/custom/keeper.css" />
<style>
	.item-block {
		box-sizing:border-box;
		border-bottom:1px solid #dddddd;
		display:block;
		width:100%;
		padding:10px 10px 10px 45px;
		/*margin-top:10px;
		margin-bottom:10px;*/
	}
	/*.item-block:hover {
		background-color:#eeeeee;
	}*/
	.item-block img {
		float:left;
		margin-top:4px;
		margin-left:-35px;
		width:20px;
	}
	.item-block h3,
	.item-block p {
		margin: 0;
		padding: 0;
	}
	a.pagination {
		display:inline-block;
		padding:5px 10px;
		/*background-color:#f5f5f5;*/
	}
	a.pagination.active {
		background-color:#57a5b8;
		color:#ffffff;
	}
	a.pagination:hover {
		background-color:#f4efde;
		text-decoration:none;
	}
	a.lib {
		padding-left:10px !important;
	}
	a.lib:hover {
		text-decoration:none;
	}
	.errmsg {
		color:#cc0000;
	}
	span.disabled {
		padding:5px 10px;
		color:#cccccc;
		font-weight: bold;
	}
</style>
</head>

<body>
    <div id="wrapper" class="en">
        
        
        

        <div id="header">
            <div id="header-inner">
                
                <a href="https://keeper.mpdl.mpg.de/" id="logo" class="fleft">
                    
                    <img src="https://keeper.mpdl.mpg.de/media/custom/KeeperLogo.svg" title="Seafile" alt="logo" width="140" height="40" />
                    
                </a>
                

                
                 
                <div class="fright" id="lang">
                    <a href="#" id="lang-context" data-lang="en">English <span class="icon-caret-down"></span></a>
                    <ul id="lang-context-selector" class="hide">
                        
                        <li><a href="https://keeper.mpdl.mpg.de/i18n/?lang=de">Deutsch</a></li>
                        
                        <li><a href="https://keeper.mpdl.mpg.de/i18n/?lang=en">English</a></li>
                        
                    </ul>
                </div>
                
                
            </div>
        </div>

        <div id="main" class="clear">
            <div id="title-panel" class="w100 ovhd">
            </div>
            
            {contents}
			{data-nav}
            <div id="left-panel" class="side-tabnav hide" role="navigation" style="display: block;">
				<h3 class="hd">Institute</h3>
                <ul class="side-tabnav-tabs">
					<li class="tab tab-cur"><a href="#" class="lib">Alle</a></li>
					<li class="tab"><a href="#" class="lib">Institut A</a></li>
					<li class="tab"><a href="#" class="lib">Institut B</a></li>
					<li class="tab"><a href="#" class="lib">Institut C</a></li>
					<li class="tab"><a href="#" class="lib">Institut D</a></li>
					<li class="tab"><a href="#" class="lib">Institut E</a></li>
				</ul>
            </div>
            <div id="right-panel">
            	    <div class="hd ovhd">
						<h3 class="fleft">Projektkatalog</h3>
						<!--<button class="repo-create btn-white fright"><span aria-hidden="true" class="icon-plus-square add vam"></span><span class="vam">New Library</span></button>-->
					</div>
			{/data-nav}
					
					
					{dataset}
						<div class="item-block">
							<h3>%title%</h3>
							<p>%smalltext%</p>
							<p>%author%</p>
							<p>Contact: %contact%</p>
						</div>
					{/dataset}
					{dataset_certified}
						<div class="item-block">
							<img src="certified.png" />
							<h3>%title%</h3>
							<p>%smalltext%</p>
							<p>%author%</p>
							<p>Contact: %contact%</p>
						</div>
					{/dataset_certified}
					
					
					{pagination-start}
						<p style="text-align:center;%style%">
					{/pagination-start}
					
					{page-prev}
						<a class="pagination" href="index.py?page=%page%">vorherige</a>
					{/page-prev}
					{page-prev-disabled}
						<span class="disabled">vorherige</span>
					{/page-prev-disabled}
					
					{pagination}
						<a class="pagination %cssclass%" href="index.py?page=%page%">%page%</a>
					{/pagination}
					
					{page-next}
						<a class="pagination" href="index.py?page=%page%">nächste</a>
					{/page-next}
					{page-next-disabled}
						<span class="disabled">nächste</span>
					{/page-next-disabled}
					
					{pagination-end}
						</p>
					{/pagination-end}
				
			{data-nav-end}
            </div>
			{/data-nav-end}
			{/contents}
			
            <div id="main-panel" class="clear w100 ovhd">
				<h3 class="errmsg" style="max-width:450px;text-align:center;margin:auto;padding:50px 0;">%errmsg%</h3>
            </div>
        </div>

    </div>

        
<div id="footer" class="ovhd">
  <div class="items fleft">
	<div class="item">
      <h4>What you need to know</h4>	   		
      <ul>
        <li><a href="https://keeper.mpdl.mpg.de/f/d17ecbb967/" target="_blank">About Keeper</a></li>
		<li><a href="https://keeper.mpdl.mpg.de/f/1b0bfceac2/" target="_blank">Cared Data Commitment</a></li>
		<li><a href="https://keeper.mpdl.mpg.de/f/f62758e53c/" target="_blank">Terms of Service</a></li>
      </ul>
    </div>

	
    <div class="item">
		<h4>Desktop Client</h4>
		<ul>
			<li><a href="https://keeper.mpdl.mpg.de/download_client_program/">Download the Keeper client for Windows, Linux and Mac</a></li>
			<li>&nbsp;</li>
			<li>&nbsp;</li>
		</ul>
	</div>	
   <div class="item">
			<h4>The software behind Keeper</h4>
			<img src="https://keeper.mpdl.mpg.de/media/custom/seafile-logo.png" alt="Max Planck Digital Library" height="35" width="40"/>	   
			<ul>
				<p>© 2016 Seafile </p>
				<li><a href="https://seafile.com/en/home/" target="_blank">About Seafile</a></li>	
			</ul>
		</div>
  </div>
  <div class="other-info fright">
	<div class="item">
      <h4>A service by</h4>	   
	  <img src="https://keeper.mpdl.mpg.de/media/custom/mpdl.png" alt="Max Planck Digital Library" height="30" width="105"/>
      <ul>
		<li><a href="https://keeper.mpdl.mpg.de/help/" target="_blank">Help</a></li>		
		<li><a href="mailto:keeper@mpdl.mpg.de">Keeper Support</a></li>
		<li><a href="https://keeper.mpdl.mpg.de/f/7121a8a69d/" target="_blank">Impressum</a></li>
      </ul>
    </div>
  
</div>


</div>

<script type="text/javascript" href="https://keeper.mpdl.mpg.de/media/js/jquery-1.12.1.min.js"></script>
<script type="text/javascript" href="https://keeper.mpdl.mpg.de/media/assets/scripts/lib/jquery.simplemodal.67fb20a63282.js"></script>
<script type="text/javascript" href="https://keeper.mpdl.mpg.de/media/assets/scripts/lib/jquery.ui.tabs.7406a3c5d2e3.js"></script>
<script type="text/javascript" href="https://keeper.mpdl.mpg.de/media/js/jq.min.js"></script>
<script type="text/javascript" href="https://keeper.mpdl.mpg.de/media/js/base.js?t=1465786517"></script>
<script type="text/javascript">
$.jstree._themes = 'https://keeper.mpdl.mpg.de/media/js/themes/';
function ajaxErrorHandler(xhr, textStatus, errorThrown) {
    if (xhr.responseText) {
        feedback($.parseJSON(xhr.responseText).error||$.parseJSON(xhr.responseText).error_msg, 'error');
    } else {
        feedback("Failed. Please check the network.", 'error');
    }
}
 
(function() {
    var lang_context = $('#lang-context'),
        lang_selector = $('#lang-context-selector');

    lang_context.parent().css({'position':'relative'});
    lang_selector.css({
        'top': lang_context.position().top + lang_context.height() + 5,
        'right': 0
        });

    lang_context.click(function() {
        lang_selector.toggleClass('hide');
        return false;
    });

    $(document).click(function(e) {
        var element = e.target || e.srcElement;
        if (element.id != 'lang-context-selector' && element.id != 'lang-context') {
            lang_selector.addClass('hide');
        }
    });
})();
</script>

</body>
</html>

