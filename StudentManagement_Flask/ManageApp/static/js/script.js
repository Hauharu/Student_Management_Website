/***************************************************** Hover alert ****************************************************/
   $(document).ready(function() {
    a = document.getElementById('alert')
    $(a).mouseenter(function() {
        $(this).stop().animate({opacity:'100'})
        $(this).toggleClass('shadow-box')
    })
    $(a).mouseleave(function() {
        $(this).fadeOut(3000)
        $(this).toggleClass('shadow-box')
    })
/**********************************************************************************************************************/


/*************************************************** Back to top ******************************************************/
    //Check to see if the window is top if not then display button
    $(window).scroll(function(){
        if ($(this).scrollTop() > 100) {
            $('.scrollToTop').fadeIn(0);
        } else {
            $('.scrollToTop').fadeOut();
        }
    });

    //Click event to scroll to top
    $('.scrollToTop').click(function(){
        $('html, body').animate({scrollTop : 0},800);
        return false;
    });
/**********************************************************************************************************************/


/************************************************* Check confirm password *********************************************/

    var checkAndChange = function(passOne, passTwo) {
        if(passOne.length > 2) {
            $("#n-passwordHelp").css('opacity', '0')
            if($("#c-password").hasClass("is-invalid")) {
                if(passOne == passTwo) {
                    $("#c-password").removeClass("is-invalid").addClass("is-valid");
                    $("#n-password").removeClass("is-invalid").addClass("is-valid");
                    $("#c-passwordHelp").css('opacity', '0')
                }
            }
            else {
                if(passOne != passTwo){
                    $("#c-password").removeClass("is-valid").addClass("is-invalid");
                    $("#n-password").removeClass("is-valid").addClass("is-invalid");
                    $("#c-passwordHelp").css('opacity', '1')
                }
            }
        }
        else {
            $("#n-passwordHelp").css('opacity', '1')
        }
    }

  $("input[type=password]").keyup(function(){
    var newPassOne = $("#n-password").val();
    var newPassTwo = $("#c-password").val();

    passOne = newPassOne;
    passTwo = newPassTwo;

    checkAndChange(passOne, passTwo);
  });

})
/**********************************************************************************************************************/


/*****************************************Hiện thị thời gian và giờ hiện tại*******************************************/
// Hiển thị thời gian thực
function updateTime() {
    const now = new Date();
    const dateOptions = {
    weekday: 'long', // Hiển thị Thứ
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
};
    const timeOptions = {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false // 24 giờ
};
    // Định dạng ngày và giờ
    const dateString = now.toLocaleDateString('vi-VN', dateOptions);
    const timeString = now.toLocaleTimeString('vi-VN', timeOptions);

    // Kết hợp định dạng
    document.getElementById('current-time').textContent = `${dateString} ${timeString}`;
}

// Cập nhật thời gian mỗi giây
setInterval(updateTime, 1000);
updateTime();
/**********************************************************************************************************************/


 /*****************************************Hiện thị mật khẩu khi nhập password ****************************************/
    function showPassword() {
      var x = document.getElementById("password");
      if (x.type === "password") {
        x.type = "text";
      } else {
        x.type = "password";
      }
    }
 /**********************************************************************************************************************/


 /*************************** Nhấn vào ảnh hiện My profile và Change password *****************************************/
document.getElementById('navbarDropdownMenuAvatar').addEventListener('click', function() {
    console.log('Dropdown clicked!');
});
