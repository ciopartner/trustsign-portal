(function() {

    $('.activoverfl').mouseover(function () {
        $(this).addClass('activoverfl2');
        $('.foty').fadeIn(0);
    });

    $('.activoverfl*').mouseleave(function (e) {
        $('.foty').fadeOut(0);
        $('.activoverfl').removeClass('activoverfl2');
    });


    $('.terg-hdmgmenu').mouseover(function () {
        //$(this).addClass('activoverfl2');
        $('.hdmgmenu').fadeIn(0);
    });

    $('.terg-hdmgmenu').mouseleave(function (e) {
        $('.hdmgmenu').fadeOut(0);
        //$('.activoverfl').removeClass('activoverfl2');
    });

}).call(this);

function abreVideo(link){
    $('#modal-video').find('iframe').attr('src', link);
}