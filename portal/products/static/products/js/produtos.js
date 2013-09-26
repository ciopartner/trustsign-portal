$(document).ready(function () {
    var $qtd_carrinho = $('#qtd_carrinho');

    function sucesso_add(data){
        $qtd_carrinho.text(parseInt($qtd_carrinho.text()) + 1);
        alert('funcionou');
    }

    function falhou_add(data){
        console.log(data);
        alert('falhou');
    }

    $('#add-ssl-basic-1year').click(function(){
        $.post(
            '/ajax/adicionar-produto/',
            {product_id:1, quantity:1, line:'basic', term:'1year'},
            sucesso_add,
            'json'
        ).fail(falhou_add);

        return false;
    });
});