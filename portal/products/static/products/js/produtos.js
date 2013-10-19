$(document).ready(function () {
    var $qtd_carrinho = $('#qtd_carrinho');
    var $message = $("#comprar-message");

    function add_product(product_code, line, term, quantity){

        function add_success(data){
            $qtd_carrinho.text(parseInt($qtd_carrinho.text()) + 1);
            location.href = url_ecommerce + 'basket/';
        }

        function add_fail(data){
            $message.html("<div class=\"alert alert-error\"><button type=\"button\" class=\"close\" data-dismiss=\"alert\">×</button>Não foi possível adicionar o produto ao carrinho.</div>");
            console.log(data);
        }

        quantity = typeof quantity !== 'undefined' ? quantity : 1;

        $.ajax({
            type: 'POST',
            dataType: 'json',
            url: url_ecommerce + 'ajax/adicionar-produto/',
            data: {product_code: product_code, quantity:quantity, line: line, term: term},
            success: add_success,
            error: add_fail
        });
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