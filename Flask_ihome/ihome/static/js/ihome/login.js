function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function() {
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
    });
    $(".form-login").submit(function(e){
        // 阻止表单的默认提交行为
        e.preventDefault();
        var mobile = $("#mobile").val();
        var password = $("#password").val();
        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        } 
        if (!password) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }

        var req_dict = {
            mobile:mobile,
            password:password
        }
        var reqJSONstr = JSON.stringify(req_dict)
        $.ajax({
            url:"/api/v1.0/sessions",
            type:"post",
            data:reqJSONstr,
            contentType:"application/json",
            dataType:"json",
            headers:{
                "X-CSRFToken":getCookie("csrf_token")
            },
            success:function (data) {
                if(data.errcode == "0"){
                    location.href = "/index"
                }else {
                    alert(data.errmsg);
                }
            }

        })
    });
})