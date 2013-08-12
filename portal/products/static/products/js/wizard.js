$(function(){

$(".result").hide();

    $('#myTab a').addClass("disabled");

    $('a[data-toggle="tab"]').on('shown', function (e) {
    $(this).removeClass("hidden");
    $($(e.relatedTarget).attr('href')).find(".result").hide();
    $(this).parent().find(".circle").addClass("wizard-active");
    $(this).parent().find(".line").addClass("wizard-active");
    $(this).parent().nextAll().find("a").addClass("hidden");
    $(this).parent().nextAll().find(".answer").text("");
    $(this).parent().nextAll().find(".circle,.line").removeClass("wizard-active");
    });


 
$(".answer-button").click(function(){
	if($(this).val()=="yes"){
		$("li.active").find(".answer").text($(this).val());
		var next = $(this).parent().parent().attr("data-answer-yes");
		var type = $(this).parent().parent().attr("data-answer-yes-type");
		if(type=="result"){
    			$(next).slideToggle();
		}if(type=="tab"){
    			$('#myTab a[href="'+next+'"]').tab('show');
    
		}if(type=="question"){
		}


	}else{
		$("li.active").find(".answer").text($(this).val());
		var next = $(this).parent().parent().attr("data-answer-no");
		var type = $(this).parent().parent().attr("data-answer-no-type");
		if(type=="result"){
    			$(next).slideToggle();
		}if(type=="tab"){
    			$('#myTab a[href="'+next+'"]').tab('show');

		}if(type=="question"){
			var dep =  $(this).parent().parent().attr("data-answer-no-dependent");
			if($(dep).find(".answer").text()=="no"){
    				$('#myTab a[href="#step-5"]').tab('show');
			}else{
    				$('#myTab a[href="#finish"]').tab('show');
			}	
		}		

	}
});


});


