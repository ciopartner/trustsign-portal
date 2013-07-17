// JavaScript Document
//


		
		function vediossl(){
		
		var vedioparentwidth=$('.videoas1').width();
		var vedioparentheightper=56.2;
		var vedioparentheight=(vedioparentwidth*vedioparentheightper)/100;
		$('.videoas1').height(vedioparentheight);
		
		}

	$(document).ready(function(e) {
        $('.rounddiv').height($('.rounddiv').width());
		vediossl();
		
		//alert($('.rounddiv').width()+'----'+$('.rounddiv').height());
		
    });


	$(window).resize(function(){
		$('.rounddiv').height($('.rounddiv').width());
		vediossl();
	});


$('.activoverfl').mouseover(function(){
	$(this).addClass('activoverfl2');
	$('.foty').fadeIn(0);
});

$('.activoverfl*').mouseleave(function(e) {
	$('.foty').fadeOut(0);
	$('.activoverfl').removeClass('activoverfl2');
});


$('.terg-hdmgmenu').mouseover(function(){
	//$(this).addClass('activoverfl2');
	$('.hdmgmenu').fadeIn(0);
});

$('.terg-hdmgmenu*').mouseleave(function(e) {
	$('.hdmgmenu').fadeOut(0);
	//$('.activoverfl').removeClass('activoverfl2');
});



/*$(document).dblclick(function(){
	$('#fgq').height();
});*/

/*$('#fgq').mouseenter(function(event){
	event.stopImmediatePropagation();
	//alert($(this).width());
});
*/

// header3-t-h hdmgmenu

function setmegamenupos(){
var hdmnpos1=$('.header3-t-h').first();
var hdmnpos2=hdmnpos1.offset().top;
var hdmnpos3=hdmnpos2+hdmnpos1.height()+20;
var hdmnpos4=hdmnpos1.offset().left;
$('.hdmgmenu').css({'top':hdmnpos3+'px','left':hdmnpos4+'px'});

//alert(hdmnpos2+'---'+hdmnpos3);
//var hdmnpos4=$('.header3-t-h').first().offset();
//var hdmnpos1=$('.header3-t-h').first().offset();
//var hdmnpos1=$('.header3-t-h').first().offset();

}


function setsortmenupos(){
	//$('.sortmune').mouseenter(function(e) {
		var hdmnpos1=$('.sortmune').parent();
		var hdmnpos2=hdmnpos1.offset().top;
		var hdmnpos3=hdmnpos2+hdmnpos1.height()+20;
		var hdmnpos4=hdmnpos1.offset().left;
		var hdmnpos5=hdmnpos1.width();
		//$('.sortmune').width($('.sortmune').parent().width());
		$('.sortmune ul li').width($('.sortmune').parent().width());
		$('.sortmune').css({'top':hdmnpos1+'px','left':hdmnpos4+'px','margin':'0'});
		
		//alert(hdmnpos2+'---'+hdmnpos3);
		//var hdmnpos4=$('.header3-t-h').first().offset();
		//var hdmnpos1=$('.header3-t-h').first().offset();
		//var hdmnpos1=$('.header3-t-h').first().offset();
   // });

//alert($('.header3-t-h').width()+'-----'+$('.sortmune').width());
}

function header1navicontrol(){
	if($(window).width()<768){
		header1navresize1=$('.nav.call-media-query1').width();
		header1navresize2=$('.nav.call-media-query1').parent().width();
		header1navresize3=header1navresize2-header1navresize1;
		header1navresize4=header1navresize3/2;
		$('.nav.call-media-query1').css({'margin-left':header1navresize4+'px'});
	}else{
		$('.nav.call-media-query1').css({'margin-left':'0'});
	}
}


/////////////////////// header search start ////////////////////


//$('.mtre')

//function searchcontroling(){
//$('.tmpsearch').css({'right':'0'});
//function headersearchcon(){
	
var header1search=function(){	
$('#appendedInputButton').width();
ertwwi10=$('.searchareain').parent('li').width();
$('.tmpsearch').css({'width':'0','opacity':'1','z-index':'10'});


	//  width:0; overflow:hidden;
	// $(document).ready(function() {
	$('.searchareain').mouseenter(function(event) {
		event.stopImmediatePropagation();
		//$('.tmpsearch').css({'width':'0','opacity':'1','z-index':'10'});


		if($(this).parent().hasClass('bloksearch')){
			return false;
		}else{
			$(this).parent().addClass('bloksearch');
			//$('.searchareain2').fadeOut();
			$('.tmpsearch').css({'width':'0','opacity':'1','padding-left':'0','padding-right':'0','padding-bottom':'0'});
			$('.searchareain').parent('li').animate({
				width: $('#appendedInputButton').width()+55,/* right: 0,*/ opacity: 1
				}, 100, "linear", function() {
				//alert("all done");
			});	
			$('.tmpsearch').animate({
				width: $('#appendedInputButton').width()+53,/* right: 0,*/ opacity: 1
				}, 100, "linear", function() {
				//alert("all done");
			});
			
			}
	
	/*$("#left").click(function(){
	$(".block").animate({"left": "-=50px"}, "slow");
	});*/
	
	});


	$('.searchareain').mouseleave(function(event) {
		event.stopImmediatePropagation();
		if($(this).parent().hasClass('bloksearch')){
			
			$('.searchareain').parent('li').animate({
				width: 30,/* right: 0,*/ opacity: 1
				}, 100, "linear", function() {
				//alert("all done");
			});	

			
				$('.tmpsearch').animate({
				width: 0, opacity: 1
				}, 100, "linear", function() {
				//alert("all done");
				$('.tmpsearch').css({'padding-left':'0','padding-right':'0','padding-bottom':'0'});
						//$('.searchareain2').fadeIn();
						$('.searchareain').parent().removeClass('bloksearch');
				});
			}
	});
	}
	
	
	var header1search2=function(){
ertwwi=$('.tmpsearch').width();
$('.tmpsearch').css({'width':'0','opacity':'1','z-index':'10'});
$('.searchareain').parent('li').width(30);

	//  width:0; overflow:hidden;
	// $(document).ready(function() {
	$('.searchareain').mouseenter(function(event) {
		event.stopImmediatePropagation();
		$('.searchareain').parent('li').width(30);
		$(this).width(30);


		if($(this).parent().hasClass('bloksearch')){
			return false;
		}else{
			$(this).parent().addClass('bloksearch');
			//$('.searchareain2').fadeOut();
			$('.tmpsearch').css({'width':'0','opacity':'1','padding-left':'10px','padding-right':'10px','padding-bottom':'0'});
			$('.tmpsearch').animate({
				width: ertwwi,/* right: 0,*/ opacity: 1
				}, 100, "linear", function() {
				//alert("all done");
			});		}
	
	/*$("#left").click(function(){
	$(".block").animate({"left": "-=50px"}, "slow");
	});*/
	
	});


	$('.searchareain').mouseleave(function(event) {
		event.stopImmediatePropagation();
		if($(this).parent().hasClass('bloksearch')){
			
				$('.tmpsearch').animate({
				width: 0, opacity: 1
				}, 100, "linear", function() {
				//alert("all done");
				$('.tmpsearch').css({'padding-left':'0','padding-right':'0','padding-bottom':'0'});
						//$('.searchareain2').fadeIn();
						$('.searchareain').parent().removeClass('bloksearch');
				});
			}
	});
	}

if($(window).width()<768){
	header1search2();
}else{
	header1search();	
}

$(window).resize(function(event) {
	event.stopImmediatePropagation();
	if($(window).width()<768){
		header1search2();
		//header1search=null;
	}else{
		header1search();	
	}
});
   // });

//}
//}

/////////////////////// header search closed ////////////////////

	setmegamenupos();
	setsortmenupos();
	header1navicontrol();
	//searchcontroling();
	$(window).resize(function(){
		setmegamenupos();
		setsortmenupos();
		header1navicontrol();
		//searchcontroling();
	});



//////////////////////////////////////

$('.sort-menu-parent*').mouseover(function(event) {
	event.stopImmediatePropagation();
	$(this).children('.sortmune').slideDown(200);
	$(this).children('.sortmune').addClass('showandwait');
    
});

$('.sortmune*').mouseover(function(event) {
	event.stopImmediatePropagation();
	//$('#ptab2').attr('class','');
	$('.sortmune').removeClass('showandwait');
});

$('.sort-menu-parent').mouseleave(function(event) {
	event.stopImmediatePropagation();
	$('.sortmune').slideUp(200);
	/*setTimeout(function(){
		if($(this).children('.sortmune').hasClass('showandwait')){
				$('.sortmune').slideUp(200);
			}
		}, 100);*/
	//$('.showandwait').delay(1000).slideUp(200);
});

$('.sortmune*').mouseleave(function(event) {
	event.stopImmediatePropagation();
	$(this).slideUp(200);
    
});
///////////////////////////////////////////////////////
//headersearchcon();