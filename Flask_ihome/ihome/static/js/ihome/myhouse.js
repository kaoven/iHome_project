
$(document).ready(function(){
    $.get("/api/v1.0/user/auth",function (resp) {
        if (resp.errcode="4003"){
            // 表示用户用户已完成实名认证
           $(".auth-warn").hide();
        }else if(resp.errcode="4002"){
            // 表示用户未完成实名认证
            $(".auth-warn").show();
            //　隐藏发布新房源的标签
            $('#houses-list').hide()
        }else {
            alert(resp.errmsg)
        }
    },"json");
})