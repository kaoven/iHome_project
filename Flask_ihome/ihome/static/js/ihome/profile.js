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

   $("#form-avatar").submit(function (e) {
       e.preventDefault()
       // 利用jquery扩展jquery.form.min.js向后端发送表单数据，补充回调函数
       $('#form-avatar').ajaxSubmit({
           url:"/api/v1.0/users/avatars",
           type:"post",
           dataType:"json",
           headers:{
               "X-CSRFToken":getCookie("csrf_token")
           },
           success:function (resp) {
               if (resp.errcode == "4101"){
                   //　用户未登录
                   location.href = "/login";
               } else if(resp.errcode == "0"){
                   image_url = resp.data.avatar_url
                   $('#user-avatar').attr("src",image_url);
               } else {
                   alert(resp.errmsg);
               }
           }
       })
   })
    // 更改用户名
    $('#form-name').submit(function (e) {
        e.preventDefault()
        // 利用jquery扩展jquery.form.min.js向后端发送表单数据，补充回调函数
     $('#form-name').ajaxSubmit({
         url:"/api/v1.0/users/username",
         type:"post",
         dataType:"json",
         headers:{
               "X-CSRFToken":getCookie("csrf_token")
           },
         success:function (resp) {
             if (resp.errcode == "4003"){
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

