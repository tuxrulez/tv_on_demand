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
                method: 'get',
                dataType: 'html',
                url: url,
                success: function(result){
                    $('#content').html(result);
                }            
            });
        }
    });   
    
});

