$(document).ready(function (e) {
    var tabs = $('.tabs-melhor-solucao'),
        p1 = tabs.find('.pergunta-1'),
        p2 = tabs.find('.pergunta-2'),
        p3 = tabs.find('.pergunta-3'),
        p4 = tabs.find('.pergunta-4'),
        p5 = tabs.find('.pergunta-5'),
        pfinal = tabs.find('.pergunta-final'),
        tp1 = tabs.find('#tab-pergunta-1'),
        tp2 = tabs.find('#tab-pergunta-2'),
        tp3 = tabs.find('#tab-pergunta-3'),
        tp4 = tabs.find('#tab-pergunta-4'),
        tp5 = tabs.find('#tab-pergunta-5'),
        ul_perguntas = $('ul.perguntas');

    p1.find('a').tab('show');

    $('a[data-toggle="tab"]').on('shown', function (e) {
        var tab_atual = $(e.target),
            //tab_anterior = $(e.relatedTarget),
            tab_id = tab_atual.attr('href'),
            tab_content = $(tab_id),
            i = parseInt(tab_id.slice(-1)),
            r;

        for (var j=1; j <= 5; j++){
            if (j>=i)
                tabs.find('.pergunta-'+j).find('span').text('');
            else{
                if (j == 1 && tab_id != '#tab-final')
                    r = 'SIM';
                else
                    r = 'NÃO';
                tabs.find('.pergunta-'+j).find('span').text(r);
            }
            ul_perguntas.removeClass('ativa-'+j);
        }
        if (i<=5)
            ul_perguntas.addClass('ativa-'+i);
        else
            ul_perguntas.addClass('ativa-5');

        tab_content.find('.pergunta').show();
        tab_content.find('.resposta').hide();
    });

    $('#btn-p1-sim').click(function(){
        p2.find('a').tab('show');
    });

    $('#btn-p1-nao').click(function(){
        pfinal.find('a').tab('show');
    });

    function exibe_resposta(tab, content){
        tab.find('span').text('SIM');
        content.find('.pergunta').hide();
        content.find('.resposta').show();
    }

    $('#btn-p2-sim').click(function(){
        exibe_resposta(p2,tp2);
    });
    $('#btn-p2-nao').click(function(){
        p3.find('a').tab('show');
    });

    $('#btn-p3-sim').click(function(){
        exibe_resposta(p3,tp3);
    });
    $('#btn-p3-nao').click(function(){
        p4.find('a').tab('show');
    });

    $('#btn-p4-sim').click(function(){
        exibe_resposta(p4,tp4);
    });
    $('#btn-p4-nao').click(function(){
        p5.find('a').tab('show');
    });

    $('#btn-p5-sim').click(function(){
        exibe_resposta(p5,tp5);
    });
    $('#btn-p5-nao').click(function(){
        pfinal.find('a').tab('show');
    });
});