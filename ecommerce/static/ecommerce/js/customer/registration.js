function RegistrationForm(obj, cnpj){

    // Private Variables
    var self = this;
    var loading = false;

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
    var getCPNJCallback = function(data){

        for(field in data)
            $("#id_registration-" + field).val(data[field]);


        self.showDisableFields();
        loading = false;
    }

    /**
     * Função de retorno da função getCNPJData em caso de erro.
     */
    var getCPNJFailCallback = function(){
        // Todo: Implementar metodo de erro.
        loading = false;
    }

    /**
     * Obtém CNPJ
     */
    self.getCPNJData = function(){
        var xhr = $.post(url_ecommerce + 'ajax/get-cnpj-data/', { cnpj : cnpj.val() }, getCPNJCallback);
        xhr.fail(getCPNJFailCallback);
    }

    // --------------------------------------------
    // Constructor
    // --------------------------------------------
    cnpj = cnpj || obj.find('#id_registration-cnpj');

    cnpj.on('keyup keydown', function(evt){

        if(!loading && cnpj.val().length == 14){
            self.getCPNJData();
            loading = true;
        }
    });

    self.hideDisableFields();

}