function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    // $('.popup_con').fadeIn('fast');
    // $('.popup_con').fadeOut('fast');
    // 向后端发送请求，获取城区信息
    $.get("/api/v1.0/area_info", function (resp) {
        if (resp.errcode == "0"){
            var areas_html = template("area-html",{areas:resp.data.areas})
            $('#area-id').html(areas_html)
        }else {
            alert(resp.errmsg)
        }
    },"json")

    $('#form-house-info').submit(function (e) {
        e.preventDefault();

        //　收集表单数据
        var data = {};
        $('#form-house-info').serializeArray().map(function (x) {data[x.name]=x.value })
        var facility = [];
        $(':checked[name=facility]').each(function (index,x) {
            facility[index] = x.value
        });

        data.facility = facility;
        $.ajax({
          url:'/api/v1.0/houses/info',
          type:'post',
          data:JSON.stringify(data),
          contentType:'application/json',
          dataType:"json",
          headers:{
              "X-CSRFToken":getCookie("csrf_token")
          },
          success:function (resp) {
              if (resp.errcode == '4101'){
                  // 用户未登录
                  location.href='/login'
              }else if (resp.errcode == "0"){
                  $('#house-id').value(resp.data.house_id);
                  $('#form-house-info').hide();
                  $('#form-house-image').show();
              }else if(resp.errcode == "4003"){
                  $('.error-msg').show()
              }else {
                  alert(resp.errmsg)
              }
          }
        })
    })

})

