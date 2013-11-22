$.fn.quantityForm = function(){

    var self = $(this);
    var total_itens = 0;
    var $basket_itens = $('#qtd_carrinho');


    self.atualiza_itens_basket = function(){
        $basket_itens.text(total_itens);
    };

    this.each(function(){
        var self = $(this);

        var $field = self.find('.field-quantity input[type=text]');
        var $price = self.find("input[name=line_price]");
        var $total = self.find('.price_total');

        var currentValue = $field.val();
        var linePrice;

        /**
         * Format the output number
         */
        self.formatNumber = function(num){
            return ("" + num).replace(/(\d)(?=(\d\d\d)+(?!\d))/g, function($1) { return $1 + "." });
        };

        /**
         * Refresh
         */
        self.refresh = function(){
            linePrice = self.getPrice() * self.getQuantity();

            var total = self.formatNumber(("R$ " + linePrice.toFixed(2)).replace('.',','));
            $total.text(total);
        };

        /**
         * Get product price
         */
        self.getPrice = function(){
            return parseFloat($price.val().replace(",","."));
        };

        /**
         * Get product qtd
         */
        self.getQuantity = function(){
            var quantity = parseInt($field.val());
            if (isNaN(quantity) || quantity < 0)
                return 0;
            return quantity
        };


        /**
         * Change event
         */
        self.changeEvent = function(e){
            if(currentValue != $(this).val())
                self.refresh();
        };


        // --------------------------------------------
        // Constructor
        // --------------------------------------------

//        $field.on('keyup keydown', self.changeEvent);
        //$field.tooltip({ title : "Aperte enter para confirmar.", placement : 'bottom', trigger : 'focus' });
        total_itens += self.getQuantity();
        self.refresh();

        return self;
    });

    self.atualiza_itens_basket();
};


$(document).ready(function(){
    $(".basket-items").quantityForm();

    $(document).ajaxStop(function(){
        $(".basket-items").quantityForm();
    });
});