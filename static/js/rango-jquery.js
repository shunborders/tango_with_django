/**
 * Created by shun on 5/5/16.
 */

$('#likes').click(function(){
    var catid;
    catid = $(this).attr("data-catid");
    $.get('/rango/like_category/', {category_id: catid}, function(data){
               $('#like_count').html(data);
               $('#likes').hide();
    });
});

$(document).ready( function() {

    $("#about-btn").click( function(event) {
        alert("You clicked the button using JQuery!");
    });
});


