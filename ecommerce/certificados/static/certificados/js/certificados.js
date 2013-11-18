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
        if ($(this).parent().parent().parent().index() > 4){
            alert("Preferencialmente escolha um dos 5 primeiros e-mails oferecidos. Caso escolha outro e-mail, " +
                "considere que o processo de emissão pode demorar até 1 dia útil a mais que o convencional.")
        }
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
            alert('É necessário fornecer um e-mail de validação para cada domínio da CSR');
        }

    });

    atualizar_tabela();
});

