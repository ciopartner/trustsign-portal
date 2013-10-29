/*global $:false */
$(function(){
    'use strict';

    var $tags = $('.list-tags [name="tag[]"]');
    var $items = $('.list-tags .item');

    $tags.change(function(){
//        $items.hide(100);
        var $selected_tags = $('.list-tags [name="tag[]"]:checked');
        var tags = [];

        $selected_tags.each(function(){
            tags.push($(this).val());
        });

        $items.each(function(){
            var tagged = $(this).data('tags');

            for(var i =0; i < tagged.length; i++){
                for(var j =0 ; j < tags.length; j++){
                    if(tagged[i] == tags[j]){
                        return $(this).show(200);
                    }
                }
            }

            return $(this).hide(100);
        });

    });

    $tags.eq(0).change();
});