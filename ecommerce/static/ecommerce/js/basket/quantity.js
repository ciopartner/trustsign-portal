$.fn.quantityForm = function(){

    this.each(function(){
        var self = $(this);

        var $field = self.find('.field-quantity input[type=text]');
        var $price = self.find("input[name=line_price]");
        var $total = self.find('.price_total');

        var currentValue = $field.val();
        var linePrice;


        /**
         * Refresh
         */
        self.refresh = function(){
            linePrice = self.getPrice() * self.getQuantity();

            var total = ("R$ " + linePrice.toFixed(2)).replace('.',',');
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
            return $field.val();
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
        $field.on('keyup keydown', self.changeEvent);
        //$field.tooltip({ title : "Aperte enter para confirmar.", placement : 'bottom', trigger : 'focus' });
        self.refresh();

        return self;
    });

};


$(document).ready(function(){
    $(".basket-items").quantityForm();
});