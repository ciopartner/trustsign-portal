if (typeof String.prototype.startsWith != 'function') {
    String.prototype.startsWith = function (str){
        return this.lastIndexOf(str, 0) === 0
    };
}

$(document).ready(function () {
    var $window = $('#windowEscolheEmail'),
        $campo_emails= $('#lista-fqdns').find('input[type=hidden]'),
        email_atual='fqdn-0',
        total_fqdn=$('.fqdn-table tr').length - 1;

    function next_email(){
        var i = parseInt(email_atual.slice(5));
        i++;
        if (i < total_fqdn){
            email_atual = 'fqdn-' + i;
            atualiza_window()
        }
    }

    function prev_email(){
        var i = parseInt(email_atual.slice(5));
        i--;
        if (i >= 0){
            email_atual = 'fqdn-' + i;
            atualiza_window()
        }
    }

    function seleciona_email(){


        var i = parseInt(email_atual.slice(5)),
            email_selecionado = $campo_emails.val().split(' ')[i];
        if (email_selecionado.startsWith('admin@')){
            $window.find('#email1').attr('checked', true);
        } else if (email_selecionado.startsWith('administrator@')){
            $window.find('#email2').attr('checked', true);
        } else if (email_selecionado.startsWith('hostmaster@')){
            $window.find('#email3').attr('checked', true);
        } else if (email_selecionado.startsWith('postmaster@')){
            $window.find('#email4').attr('checked', true);
        } else if (email_selecionado.startsWith('webmaster@')){
            $window.find('#email5').attr('checked', true);
        }
    }

    function atualiza_window(){
        var $tr = $('#' + email_atual),
            dominio = $tr.find('td:first-child').text();

        if (dominio.startsWith('*.')){
            dominio = dominio.slice(2);
        }

        $window.find('.dominio').text(dominio);
        $window.find('label.email-1').text('admin@' + dominio);
        $window.find('label.email-2').text('administrator@' + dominio);
        $window.find('label.email-3').text('hostmaster@' + dominio);
        $window.find('label.email-4').text('postmaster@' + dominio);
        $window.find('label.email-5').text('webmaster@' + dominio);
        $window.find('input[type=radio]').attr('checked', false);
        seleciona_email()
    }

    $('.fqdn-table a').click(function(){
        email_atual = $(this).parent().parent().attr('id');
        atualiza_window()
    });

    $window.find('input[type=radio]').click(function(){
        var i = parseInt(email_atual.slice(5)),
            lista = $campo_emails.val().split(' '),
            $tr = $('#' + email_atual);

        lista[i]= $(this).parent().text();
        $campo_emails.val(lista.join(' '));

        $tr.find('span').text(lista[i])
    });

    $window.find('.prev-icon').click(function(){
        prev_email();
    });

    $window.find('.next-icon').click(function(){
        next_email();
    });
});

