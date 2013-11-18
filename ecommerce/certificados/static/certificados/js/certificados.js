if (typeof String.prototype.startsWith != 'function') {
    String.prototype.startsWith = function (str){
        return this.lastIndexOf(str, 0) === 0
    };
}

$(document).ready(function () {

    var count = 0;
    var fqdn = '';

    var $window = $('#windowEscolheEmail'),
        $campo_emails= $('#lista-fqdns').find('input[type=hidden]');
    var $windowModel = $('#windowEscolheEmail .modal-body');
    var $form = $('form.emissao');

    function next_email(){
        count = (count + 1) % $windowModel.length;
        atualiza_fqdn();
        atualiza_window();
    }

    function prev_email(){
        count = (count - 1) % $windowModel.length;
        atualiza_fqdn();
        atualiza_window();
    }


    function atualiza_fqdn(){
        fqdn = $windowModel.eq(count).data('fqdn');
    }

    function atualiza_window(){
        $windowModel.addClass('hidden');
        $('#windowEscolheEmail .modal-body[data-fqdn="' + fqdn + '"]').removeClass('hidden');
    }

    function completo(){
        var lista = $campo_emails.val().split(' ');

        for(var i=0; i < lista.length; i++)
            if(lista[i].length == 0)
                return false;

        return true;
    }

    function atualizar_tabela(){
        var lista = $campo_emails.val().split(' ');

        for(var i=0; i < lista.length; i++){

            var val = lista[i];
            var $tr = $('.fqdn-table tr').eq(i + 1);
            var fqdn = $tr.data('fqdn');

            $tr.find('span').text(val);
            $('#windowEscolheEmail .modal-body[data-fqdn="' + fqdn + '"]').find('input[value="' + val + '"]');
        }
    }

    $window.find('input[type=radio]').click(function(){
        var i = $('.fqdn-table tr[data-fqdn="' + fqdn + '"]').index() - 1;
        var lista = $campo_emails.val().split(' ');

        lista[i] = $(this).parent().find('span').text().trim();
        $campo_emails.val(lista.join(' '));

        atualizar_tabela();
    });


    $window.find('.prev-icon').click(function(){
        prev_email();
    });

    $window.find('.next-icon').click(function(){
        next_email();
    });

    $(".fqdn-table a").click(function(e){
       fqdn = $(this).data('fqdn');
       atualiza_window();
    });

    $form.submit(function(e){

        if(!completo()){
            e.preventDefault();
            alert('Escolha todos os emails.');
        }

    });

    atualizar_tabela();
});

