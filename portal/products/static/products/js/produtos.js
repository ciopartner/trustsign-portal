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

        show_additional = show_additional == 'true' || show_additional ? true : false;

        function add_success(data){
            $qtd_carrinho.text(parseInt($qtd_carrinho.text()) + 1);
            //location.href = url_ecommerce + 'basket/';
            $message.html("<div class=\"alert alert-success\"><button type=\"button\" class=\"close\" data-dismiss=\"alert\">×</button>Foi adicionado ao seu carrinho " + quantity + " ite" + (quantity > 1 ? "ns" : "m") +  ". <a href='" + url_ecommerce + "basket'>Clique aqui</a> para visualizá-lo.</div>");
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

            $("#btn-confirm-buy").bind('click')
            $("#btn-confirm-buy").on('click', function(e){
                e.preventDefault();

                var qtd = form.find('[name=qtd]').val();
                quantity = form.find('[name=num_domains]').val();

                do_post();
            });
        }

        function do_post(){
            $.ajax({
                type: 'POST',
                dataType: 'json',
                url: url_ecommerce + 'ajax/adicionar-produto/',
                data: {product_code: product_code, quantity:quantity, line: line, term: term},
                success: add_success,
                error: add_fail
            });
        }

        quantity = typeof quantity !== 'undefined' ? quantity : 1;

        do_post();

        if(show_additional) show_buy_info();
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

});