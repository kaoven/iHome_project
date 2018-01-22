function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function logout() {
    $.ajax({
        url:"/api/v1.0/session",
        type:"delete",
        dataType:"json",
        headers:{
            "X-CSRFToken":getCookie("csrf_token")
        },
        success:function (data) {
            if (data.errcode == "0"){
                location.href = "/index"
            }
        }
    })
}

$(document).ready(function(){
    $.ajax({
        url:"/api/v1.0/users/userinfo",
        type:"get",
        dataType:"json",
        success:function (resp) {
            if (resp.errcode == "0"){
                $("#user-name").html(resp.data.username)
                $("#user-mobile").html(resp.data.mobile)
                $("#user-avatar").attr("src",resp.data.avatar_url)
            }else {
                alert(resp.errmsg)
            }
        }
    })
})