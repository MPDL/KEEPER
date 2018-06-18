<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>Catalog - KEEPER</title>
<meta http-equiv="Content-type" content="text/html; charset=utf-8" />
<meta name="keywords" content="File Collaboration Team Organization" />
<link rel="icon" type="image/x-icon" href="/media/img/favicon.png?t=1465786517" />
<!--[if IE]>
<link rel="shortcut icon" href="https://keeper.mpdl.mpg.de/media/img/favicon.png?t=1465786517"/>
<![endif]-->
<link rel="stylesheet" type="text/css" href="/media/assets/css/bootstrap.min.css"/>
<link rel="stylesheet" type="text/css" href="/media/css/seahub.min.css?t=1465786517" />
<link rel="stylesheet" type="text/css" href="/media/custom/catalog.css" />
<link rel="stylesheet" type="text/css" href="/media/custom/keeper.css" />
<style>
	.item-block {
		box-sizing:border-box;
		border-bottom:1px solid #dddddd;
		display:block;
		width:100%;
		padding:10px 10px 10px 45px;
	}
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
		/padding-left:10px !important;
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

	#header {
   		background: #f4f4f7 !important;
        width: 100% !important;
        font-size: 14px !important;
        border-bottom: 1px solid #e8e8e8 !important;
        padding-bottom: 4px !important;
        z-index: 1 !important;
	}

    #right-panel {
        padding-top: 0px;
    }
    .side-tabnav h3 {
        margin-top: 65px !important;
        color: #57a5b8 !important;
    }
    .side-tabnav label {
        margin-top: 0px;
    }
    .side-tabnav span.vam {
        margin-left: 5px;
    }

        
	#logo{position: absolute; top: 13px !important; left: 16px !important;}
</style>
</head>

<body>
    <div id="wrapper" class="en">

        <div id="header">
            <div id="header-inner">
                <a href="/" id="logo" class="fleft">
                    <img src="/media/%logo_path%" title="Catalog" alt="logo" width="140" height="40" />
                </a>
            </div>
        </div>

        <div id="main" class="clear">
            <div id="title-panel" class="w100 ovhd">
            </div>


            {contents}
            {data-nav}
            <div id="left-panel" class="side-tabnav" style="display: block;">

                <h3 class="hd">Show Projects</h3>
                <form id="scope-selector" method="post">
                    <label class="radio-item">
                        <input class="vam" type="radio" name="cat_scope" value="with_metadata" %checked_with_metadata%/><span class="vam">with metadata</span>
                    </label>
                    <br>
                    <label class="radio-button">
                        <input class="vam" type="radio" name="cat_scope" value="with_certificate" %checked_with_certificate%/><span class="vam">with certificate</span>
                    </label>
                    <br>
                    <label class="radio-button">
                        <input class="vam" type="radio" name="cat_scope" value="all" %checked_all%/><span class="vam">all</span>
                    </label>
                </form>
                <!--<ul class="side-tabnav-tabs">-->
                <!--<li class="tab tab-cur"><a href="#" class="lib">Alle</a></li>-->
                <!--<li class="tab"><a href="#" class="lib">Institut A</a></li>-->
                <!--<li class="tab"><a href="#" class="lib">Institut B</a></li>-->
                <!--<li class="tab"><a href="#" class="lib">Institut C</a></li>-->
                <!--<li class="tab"><a href="#" class="lib">Institut D</a></li>-->
                <!--<li class="tab"><a href="#" class="lib">Institut E</a></li>-->
                <!--</ul>-->

            </div>
            <div id="right-panel">
                <div class="hd ovhd">
                    <h3 class="fleft">The Keeper Project Catalog of Max Planck Society</h3>
                </div>
                {/data-nav}


                {dataset}
                <div class="item-block">
                    <h3>%title%</h3>
                    <p>%smalltext%</p>
                    <p>%author%</p>
                    %year%
                    <p>Contact: %contact%</p>
                </div>
                {/dataset}
                {dataset_certified}
                <div class="item-block">
                    <img src="/catalog/static/certified.png" />
                    <h3>%title%</h3>
                    <p>%smalltext%</p>
                    <p>%author%</p>
                    %year%
                    <p>Contact: %contact%</p>
                </div>
                {/dataset_certified}

                {fyear}
                <p>Year: %year%</p>
                {/fyear}

                {pagination-start}
                <p style="text-align:center;%style%">
                    {/pagination-start}

                    {page-prev}
                    <a class="pagination" href="/catalog/index.py?page=%page%&scope=%scope%">Previous</a>
                    {/page-prev}
                    {page-prev-disabled}
                    <span class="disabled">Previous</span>
                    {/page-prev-disabled}

                    {pagination}
                    <a class="pagination %cssclass%" href="/catalog/index.py?page=%page%&scope=%scope%">%page%</a>
                    {/pagination}

                    {page-next}
                    <a class="pagination" href="/catalog/index.py?page=%page%&scope=%scope%">Next</a>
                    {/page-next}
                    {page-next-disabled}
                    <span class="disabled">Next</span>
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
</div>

    %footer%   


    <script type="text/javascript" src="https://keeper.mpdl.mpg.de/media/js/jquery-1.12.1.min.js"></script>
    <script type="text/javascript" src="https://keeper.mpdl.mpg.de/media/assets/scripts/lib/jquery.simplemodal.67fb20a63282.js"></script>
    <script type="text/javascript" src="https://keeper.mpdl.mpg.de/media/assets/scripts/lib/jquery.ui.tabs.7406a3c5d2e3.js"></script>
    <script type="text/javascript" src="https://keeper.mpdl.mpg.de/media/js/jq.min.js"></script>
    <script type="text/javascript" src="https://keeper.mpdl.mpg.de/media/js/base.js?t=1465786517"></script>
    <script type="text/javascript">
        $('#scope-selector').click(function( event ) {
            var form = $( this ),
                target = $( event.target )
            if ( target.is('input') ) {
                $.post("/catalog", form.serialize(), function(){
                    form.submit();
                });
            }
        });

        function ajaxErrorHandler(xhr, textStatus, errorThrown) {
            if (xhr.responseText) {
                feedback($.parseJSON(xhr.responseText).error||$.parseJSON(xhr.responseText).error_msg, 'error');
            } else {
                feedback("Failed. Please check the network.", 'error');
            }
        }
    </script>
</body>


</html>

