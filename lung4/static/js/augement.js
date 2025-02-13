$(document).ready(function() {
    let uploadedImage = null;

    $('#fileInput').change(function() {
        uploadedImage = $('#fileInput')[0].files[0];
        if (uploadedImage) {
            let reader = new FileReader();
            reader.onload = function(e) {
                $('#img2').attr('src', e.target.result);
            }
            reader.readAsDataURL(uploadedImage);
        }
    });

    $('.augment-btn').click(function() {
        var action = $(this).data('action');
        if (!uploadedImage) {
            alert('请先选择文件');
            return;
        }

        var formDataObj = new FormData();
        formDataObj.append('myfile', uploadedImage);
        formDataObj.append('action', action);

        $.ajax({
            url: '/enhance_image/',
            method: 'POST',
            processData: false,
            contentType: false,
            data: formDataObj,
            success: function(data) {
                if (data.status === 200) {
                    alert("操作成功！");
                    $('#img2').attr('src', data.img_original_path);
                    $('#enhancedImg').attr('src', data.img_path);
                } else {
                    alert("上传失败");
                }
            },
            error: function() {
                alert("上传失败");
            }
        });
    });
});
