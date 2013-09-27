$(document).ready(function () {
    var $qtd_carrinho = $('#qtd_carrinho');

    function add_product(product_code, line, term, quantity){

        function add_success(data){
            $qtd_carrinho.text(parseInt($qtd_carrinho.text()) + 1);
            alert('funcionou');
        }

        function add_fail(data){
            console.log(data);
            alert('falhou');
        }

        quantity = typeof quantity !== 'undefined' ? quantity : 1;
        $.post(
            '/ajax/adicionar-produto/',
            {product_code: product_code, quantity:quantity, line: line, term: term},
            add_success,
            'json'
        ).fail(add_fail);
    }

    $('#add-ssl-basic-1year').click(function(){
        add_product('ssl', 'basic', '1year');
        return false;
    });
});