function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function () {
    $.get("/api/v1.0/user/auth",function (resp) {
        if (resp.errcode="4003"){
            $('#real-name').val(resp.data.real_name);
            $('#id-card').val(resp.data.id_card);
            //　给input添加disabled属性，禁止用户修改
            $('#real-name').prop("disabled",true);
            $('#id-card').prop("disabled",true);
            // 隐藏提交按钮
            $('#form-auth>input[type=submit]').hide()
        }else {
            alert(resp.errmsg)
        }
    },"json");

    $("#form-auth").submit(function (e) {
        e.preventDefault()
     $("#form-auth").ajaxSubmit({
         url:"/api/v1.0/users/auth",
         type:"post",
         dataType:"json",
         headers:{
             "X-CSRFToken":getCookie("csrf_token")
         },
         success:function (resp) {
             if (resp.errcode == "4103"){
                 $('.error-msg').show()
             }else if(resp.errcode == "0"){
                 showSuccessMsg()
             }else {
                 alert(resp.errmsg)
             }
         }
     })
    })
})