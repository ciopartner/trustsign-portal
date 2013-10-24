function RegistrationForm(obj, cnpj, phone){

    // Private Variables
    var self = this;
    var loading = false;
    var CNPJNotFoundHTML = "<div class=\"alert alert-error  pull-left tm10\"><button type=\"button\" class=\"close\" data-dismiss=\"alert\">×</button>Não foi possível localizar o CNPJ.</div>";
    var invalidPhone = "<div class=\"alert alert-error pull-left tm10\" ><button type=\"button\" class=\"close\" data-dismiss=\"alert\">×</button>Telefone inválido! Apenas telefones fixos.</div>";

    /**
     * Oculta campos desativos
     */
    self.hideDisableFields = function(){
        obj.find("input[disabled]").parents('.control-group').hide();
    }

    /**
     * Exibe campos desativos
     */
    self.showDisableFields = function(){
        obj.find("input[disabled]").parents('.control-group').show();
    }

    /**
     * Função de retorno da função getCNPJData
     */
    var CPNJCallback = function(data){

        for(field in data)
            $("#id_registration-" + field).val(data[field]);


        self.showDisableFields();
        loading = false;
    }

    /**
     * Função de retorno da função getCNPJData em caso de erro.
     */
    var CPNJFailCallback = function(){
        cnpj.after(CNPJNotFoundHTML);
        loading = false;
    }

    /**
     * Obtém CNPJ
     */
    self.getCPNJData = function(){
        var xhr = $.post(url_ecommerce + 'ajax/get-cnpj-data/', { cnpj : cnpj.val() }, CPNJCallback);
        xhr.fail(CPNJFailCallback);
    }

    self.validadePhone = function(){
        var val = phone.val();

        if(parseInt(val[5]) < 2 || parseInt(val[5]) > 5)
            phone.after(invalidPhone);
    }

    // --------------------------------------------
    // Constructor
    // --------------------------------------------
    cnpj = cnpj || obj.find('#id_registration-cnpj');
    phone = phone || obj.find("#id_registration-telefone_principal");

    //    cnpj.on('keyup keydown', function(){
    //
    //        if(!loading && cnpj.val().length == 14){
    //            self.getCPNJData();
    //            loading = true;
    //        }
    //    });

    cnpj.mask("99.999.999/9999-99").mask("99.999.999/9999-99", {
        completed : self.getCPNJData
    });

    phone.mask("(99) 9999-9999", {
        completed: self.validadePhone
    });


    self.hideDisableFields();

}

$(function(){
    new RegistrationForm($("#register_form"));
});