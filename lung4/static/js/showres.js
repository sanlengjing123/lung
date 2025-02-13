
$('.btn').click(function () {
    var FormDataObj = new FormData()  //新建一个FormData对象
    var myfile = $('#mf')[0].files[0]  //获取文件对象
    FormDataObj.append('myfile', myfile)

    $.ajax({
        url: '/upload_discriminate/',
        method: 'POST',
        processData: false,
        contentType: false,
        data: FormDataObj,
        success: function (data) {
            if (data.status === 200) {
                alert("分类成功！")
                document.getElementById("img").src = data.img_path
                document.getElementById("Cla_result").style.backgroundColor = "#FFAD60"
                document.getElementById("Cla_result").placeholder = "模型分类结果为:  " + data.Cla_result
            }
            else {
                alert("上传失败！")
                location.href = '/index/'
            }
        }
    })
})