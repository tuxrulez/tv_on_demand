$(function(){ 
    
    // player
    var j_vlc = $('#vlc');
    var play = $('.controls .play');    
    play.live('click', function(evt){
        evt.preventDefault();
        var vlc = document.getElementById('vlc');
        if(vlc.playlist.isPlaying){
            return false;
        }
        vlc.playlist.play();
    }); 
    var stop = $('.controls .stop');
    stop.live('click', function(evt){
       evt.preventDefault();
       var vlc = document.getElementById('vlc');
       vlc.playlist.stop();
    });
    var pause = $('.controls .pause');
    pause.live('click', function(evt){
       evt.preventDefault();
       var vlc = document.getElementById('vlc');
       vlc.playlist.togglePause(); 
    });
    var fullscreen = $('.controls .fullscreen');
    fullscreen.live('click', function(evt){
       evt.preventDefault();
       var vlc = document.getElementById('vlc');
       vlc.video.toggleFullscreen(); 
    });    
   
   
    // nav
    var links = $('#content .menu a');    
    links.live('click', function(evt){
        evt.preventDefault();
        var self = $(this);
        var url = self.attr('href');
        var media_type = self.closest('ul').attr('class');
        
        // se for um video ele abre o colorbox
        if(media_type == 'video'){
            $.fn.colorbox({href:self.attr('href'), width:"80%", height:"90%", iframe:true, open:true});
    
        }else{
        // caso contrário ele carrega o conteúdo por ajax
            $.ajax({
                type: 'GET',
                dataType: 'html',
                url: url,
                success: function(result){
                    if(result == 'not_allowed'){
                        var re_id = RegExp(/\d+\b/);
                        var row_id = self.attr('href').match(re_id);
                        var login_url = '/admin/tv_on_demand/do-login/' + row_id;        
                        $.fn.colorbox({href:login_url, width:"30%", height:"50%", iframe:true, open:true}); 
                        
                    }else{                    
                        $('#content').html(result);
                    }
                }            
            });
        }
    }); 
    
    
    // login
    var login_btn = $('#login-send');
    login_btn.live('click', function(evt){
       evt.preventDefault();
       var self = $(this);
       var form = self.closest('form');
       var username = $('input[name=username]', form).val();
       var password = $('input[name=password]', form).val();
       var row_url = $('input[name=row_url]', form).val();
       var re_id = RegExp(/\d+\b/);
       var row_id = row_url.match(re_id);
       var redirect_url = '/admin/tv_on_demand/main/children/' + row_id + '/';
       
       $.ajax({
            type: 'POST',
            dataType: 'html',
            url: row_url,
            data: {username: username, password: password},
            success: function(result){
                var login_div = $('#login');
                
                if(result == 'login_true'){
                    login_div.html('<p>Permissão concedida. Por favor, retorne ao menu desejado e acesse nosso conteúdo.</p>');
                    
                }else{
                    login_div.html('<p>Desculpe, você não tem permissão para acessar esse conteúdo.</p>');
                }
            }
           
       });
        
    });
    
    
    //logout ( a cada 60 segundos o usuário é deslogado )
    var do_logout = function(){
        $.get('/admin/tv_on_demand/do-logout/');        
    }
    window.setInterval(do_logout, 60000);    
    
});

