(function() {

    $('.activoverfl').mouseover(function () {
        $(this).addClass('activoverfl2');
        $('.foty').fadeIn(0);
    });

    $('.activoverfl*').mouseleave(function (e) {
        $('.foty').fadeOut(0);
        $('.activoverfl').removeClass('activoverfl2');
    });

    $('.sortmune li').click(function(){
        window.location = $(this).find('a').attr('href');
    });

    $("[rel=tooltip]").tooltip({ placement: 'bottom'});

}).call(this);

function abreVideo(link){
    $('#modal-video').find('.youtube-player').attr('src', link);
}