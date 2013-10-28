$(document).ready(function (e) {
    var tab = $('#tab-ssl-converter');
    var tipo_converter =  tab.find('#id_tipo_para_converter'),
        tipo_atual = tab.find('#id_tipo_atual'),
        tr_pfx_password = tab.find('#id_pfx_password').parent().parent(),
        tr_privatekey = tab.find('#id_private_key').parent().parent();
    tr_pfx_password.hide();
    tr_privatekey.hide();
    tipo_converter.change(function(){
        if (tipo_converter.val() == '4')
            tr_privatekey.show();
        else
            tr_privatekey.hide();
        if (tipo_converter.val() == '4' || tipo_atual.val() == '4')
            tr_pfx_password.show();
        else
            tr_pfx_password.hide();
    });
    tipo_atual.change(function(){
        if (tipo_converter.val() == '4' || tipo_atual.val() == '4')
            tr_pfx_password.show();
        else
            tr_pfx_password.hide();
    });
});