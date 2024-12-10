$(document).ready(function() {
    var main_route = (window.location.pathname.split("/")[1]);
    $('.main').removeClass('active');
    $('#nav_' + main_route).addClass('active');
    $(document).on('click', '.main', function (e) {
        $('.main').removeClass('active');
        $('#nav_' + main_route).addClass('active');
    })
})