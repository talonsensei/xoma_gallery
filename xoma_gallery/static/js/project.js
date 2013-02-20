$(document).ready(function(){
   $(".star").mouseover(function(event) {
       lightStars(event.target);
   }),
   $(".star").mouseout(function(event) {
       dimStars(event.target);
   }),
   $(".star").click(function(event) {
       ratePhoto(event.target);
   })
 });

function lightStars(domElement) {
    $(domElement).addClass("on");
    $(domElement).removeClass("off");
    $(domElement).prevAll().addClass("on");
    $(domElement).prevAll().removeClass("off");
}

function dimStars(domElement) {
    $(domElement).addClass("off");
    $(domElement).removeClass("on");
    $(domElement).prevAll().addClass("off");
    $(domElement).prevAll().removeClass("on");
}

function ratePhoto(domElement) {
    var matches_array = $(domElement).attr("id").match(/(\d+)-star(\d+)$/);
    var entry_id = matches_array[1];
    var rating = matches_array[2];
    
    $("#ratingArea" + entry_id).hide('normal');
    $.post("/contest/rate/" + entry_id + "/", { rating: rating });
    $("#happyArea" + entry_id + " .score").html(rating);
    $("#happyArea" + entry_id).show('normal');
}