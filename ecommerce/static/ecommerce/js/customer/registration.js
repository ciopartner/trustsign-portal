function RegistrationForm($obj, settings){

    // Private Variables
    var self = this;
    var loading = false;
    var CNPJNotFoundHTML = "<div class=\"error tm10\"  id=\"invalidCNPJ\"><span class=\"help-block error\"><i class=\"icon-exclamation-sign\"></i>Não foi possível localizar o CNPJ.</span></div>";
    var invalidPhone = "<div class=\"error tm10\" id=\"invalidPhone\"><span class=\"help-block\"><i class=\"icon-exclamation-sign\"></i>Telefone inválido. Apenas telefones fixos.</span></div>";
    var invalidEmail = "<div class=\"error tm10\" id=\"invalidEmail\"><span class=\"help-block\"><i class=\"icon-exclamation-sign\"></i>Use apenas email corporativo.</span></div>";
    var emailBlackList = new Array('gmail', 'yahoo', 'hotmail', 'outlook', 'ymail');

    settings = settings || {};
    var $cnpj = settings.cnpj || $obj.find('#id_registration-cnpj');
    var $phone = settings.phone || $obj.find("#id_registration-telefone_principal");
    var $email = settings.email || $obj.find("#id_registration-email");

    /**
     * Oculta campos desativos
     */
    self.hideDisableFields = function(){
        $obj.find("input[disabled]").parents('.control-group').hide();
    }

    /**
     * Exibe campos desativos
     */
    self.showDisableFields = function(){
        $obj.find("input[disabled]").parents('.control-group').show();
    }

    /**
     * Função de retorno da função getCNPJData
     */
    var CPNJCallback = function(data){

        for(field in data)
            if(field !== 'cnpj')
                $("#id_registration-" + field).val(data[field]);

        $("#invalidCPNJ").remove();
        self.showDisableFields();
        loading = false;
    }

    /**
     * Função de retorno da função getCNPJData em caso de erro.
     */
    var CPNJFailCallback = function(){
        $cnpj.after(CNPJNotFoundHTML);
        loading = false;
    }

    /**
     * Obtém CNPJ
     */
    self.getCPNJData = function(){
        var xhr = $.post(url_ecommerce + 'ajax/get-cnpj-data/', { cnpj : $cnpj.val() }, CPNJCallback);
        xhr.fail(CPNJFailCallback);
    }

    /**
     * Valida número de telefone
     */
    self.validadePhone = function(){
        var val = $phone.val();

        if(parseInt(val[5]) < 2 || parseInt(val[5]) > 5)
            $phone.after(invalidPhone);
        else
            $("#invalidPhone").remove();
    }

    /**
     * Valida email
     */
    self.validateEmail = function(){
        var val = $email.val();
        var domain = val.split('@')[1] || "";

        console.log(domain);

        if(domain.length){
            var block;
            $("#invalidEmail").remove();
            for(i in emailBlackList){

                if(domain.indexOf(emailBlackList[i]) >= 0){
                    $email.after(invalidEmail);
                    return;
                }
            }
        }
    }

    // --------------------------------------------
    // Constructor
    // --------------------------------------------

    $cnpj.mask("99.999.999/9999-99").mask("99.999.999/9999-99", {
        completed : self.getCPNJData
    });

    $phone.mask("(99) 9999-9999", {
        completed: self.validadePhone
    });

    console.log($email);
    $email.on('keydown keyup blur', self.validateEmail);


    self.hideDisableFields();

}

$(function(){
    new RegistrationForm($("#register_form"));
    new RegistrationForm($("#profile_form"),{
        phone : $("#id_callback_telefone_principal")
    });
});