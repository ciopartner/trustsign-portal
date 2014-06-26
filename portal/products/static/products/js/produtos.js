$(document).ready(function () {
    var $qtd_carrinho = $('#qtd_carrinho');
    var $message = $("#comprar-message");

    /**
     *
     * @param product_code Código do produto
     * @param line Linha
     * @param term Termo
     * @param quantity Quantidade
     * @param show_additional Se deve exibir box para produtos adicionais
     * @param additional_code Código do produto adicional
     * @param additional_price Preço do produto adicional
     */
    function add_product(product_code, line, term, quantity, show_additional, additional_code, additional_price){

        show_additional = (show_additional == 'true') || show_additional ? true : false;

        function add_success(data){
            $qtd_carrinho.text(parseInt($qtd_carrinho.text()) + 1);
            //location.href = url_ecommerce + 'basket/';
            $message.append("<div class=\"alert alert-success\"><button type=\"button\" class=\"close\" data-dismiss=\"alert\">×</button>Foi adicionado ao seu carrinho " + quantity + " ite" + (quantity > 1 ? "ns" : "m") +  ". <a href='" + url_ecommerce + "basket'>Clique aqui</a> para visualizá-lo.</div>");
        }

        function add_additional_success(data){
            $qtd_carrinho.text(parseInt($qtd_carrinho.text()) + 1);
            $("#form-confirm-buy").after("<div class=\"alert alert-success pull-right\" style=\"width: 486px\"><button type=\"button\" class=\"close\" data-dismiss=\"alert\">×</button>Foi adicionado ao seu carrinho " + quantity + " ite" + (quantity > 1 ? "ns" : "m") +  ". <a href='" + url_ecommerce + "basket'>Clique aqui</a> para visualizá-lo.</div><div class=\"clearfix\"></div>");
        }

        function add_fail(data){
            $message.html("<div class=\"alert alert-error\"><button type=\"button\" class=\"close\" data-dismiss=\"alert\">×</button>Não foi possível adicionar o produto ao carrinho.</div>");
            console.log(data);
        }

        function show_buy_info(){
            var form = $("#form-confirm-buy");

            form.hide();
            form.removeClass('hidden');
            form.slideDown(200);

            form.find('.line').text(line);
            form.find('.term').text(term.replace('year', ' ano'));
            form.find('.price').text(additional_price);

            product_code = additional_code;

            var $btn_buy = $("#btn-confirm-buy");
            $btn_buy.off();
            $btn_buy.on('click', function(e){
                e.preventDefault();

                var qtd = form.find('[name=qtd]').val();
                quantity = form.find('[name=num_domains]').val();

                do_post(add_additional_success);
            });
        }

        function hide_buy_info(){
            var form = $("#form-confirm-buy");

            form.hide();
            form.addClass('hidden');

        }

        function do_post(callback){

            callback = callback ? callback : add_success;

            $.ajax({
                type: 'POST',
                dataType: 'json',
                url: url_ecommerce + 'ajax/adicionar-produto/',
                data: {product_code: product_code, quantity:quantity, line: line, term: term},
                success: callback,
                error: add_fail
            });
        }

        quantity = typeof quantity !== 'undefined' ? quantity : 1;

        do_post();

        if(show_additional) show_buy_info();
        else hide_buy_info();
    }

    $('#add-ssl-basic-1year').click(function(){
        add_product('ssl', 'basic', '1year');
        return false;
    });

    $("[data-comprar-produto]").click(function(e){

        e.preventDefault();

        var product_code = $(this).data('comprar-produto');
        var line = $(this).data('line');
        var term = $(this).data('term');
        var qtd = 1;
        var additional = $(this).data('additional');
        var additional_code = $(this).data('additional-product-code');
        var additional_price = $(this).data('additional-price');

        add_product(product_code, line, term, qtd, additional, additional_code, additional_price);

    });
	
	// ssltab max-height 10 tr
	
	$.each($('.ssltab-wrap').find('.ssltab'), function() {
		var head_height = $(this).find('thead').height();
			max_height = head_height;
			
			$.each($(this).find('tbody tr'), function() {
				if ($(this).index() < 10) {		
					max_height += $(this).outerHeight();					
				} else {
					return false;
				}
			});
			
			$(this).parent().css('max-height', max_height + 'px')
			
	})
	
	// collapse table
	$('.ssltab-wrap').find('.expandir-tabela').click(function() {
		var tgt = $(this).parent();
		tgt.removeClass('comprimir');
		tgt.css('max-height', '9999px')
		$(this).hide();
	});
	
});