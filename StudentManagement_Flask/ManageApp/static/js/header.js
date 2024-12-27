/*Làm nổi bật mục của menu tương ứng với url hiện tại và cập nhật trạng thái của mục khi người dùng nhấn vào mục khác của menu */

$(document).ready(function() {
    var main_route = (window.location.pathname.split("/")[1]);
    $('.main').removeClass('active');
    $('#nav_' + main_route).addClass('active');
    $(document).on('click', '.main', function (e) {
    $('.main').removeClass('active');
    $('#nav_' + main_route).addClass('active');
    })
})