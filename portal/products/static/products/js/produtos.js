$(document).ready(function () {
    var $qtd_carrinho = $('#qtd_carrinho');
    var $message = $("#comprar-message");

    function add_product(product_code, line, term, quantity, num_domains){

        num_domains = num_domains ? num_domains : 0;

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

            $("#btn-confirm-buy").bind('click')
            $("#btn-confirm-buy").on('click', function(e){
                e.preventDefault();

                var qtd = form.find('[name=qtd]').val();
                num_domains = form.find('[name=num_domains]').val();

                do_post();
            });
        }

        function do_post(){
            $.ajax({
                type: 'POST',
                dataType: 'json',
                url: url_ecommerce + 'ajax/adicionar-produto/',
                data: {product_code: product_code, quantity:quantity, line: line, term: term, num_domains : num_domains},
                success: add_success,
                error: add_fail
            });
        }

        quantity = typeof quantity !== 'undefined' ? quantity : 1;

        do_post();

        if($("#form-confirm-buy").length == 1){
            show_buy_info();
        }
    }

    $('#add-ssl-basic-1year').click(function(){
        add_product('ssl', 'basic', '1year');
        return false;
    });

    $("[data-comprar-produto]").click(function(e){
        e.preventDefault();
        add_product($(this).data('comprar-produto'),$(this).data('line'),$(this).data('term'));
    });

});