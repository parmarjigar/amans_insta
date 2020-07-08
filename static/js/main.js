$(document).ready(function() {
    $("#upload_file").click(function(e) {
        var form = $('#custom-form')[0];
        var data = new FormData(form);
        $.ajax({
            type: "POST",
            url: '/upload/',
            data: data,
            processData: false,
            contentType: false,
            cache: false,
            timeout: 600000,
            enctype: 'multipart/form-data',
            success: function(response, textStatus, xhr) {
                console.log(xhr.status)
                form.reset();
                alert(response);
            },
            error: function(e, textStatus, xhr) {
                alert(e.responseText)
            }
        });
        e.preventDefault();
    });

    $("#search_image").click(function(e) {
        var form = $('#search_form')[0];
        var data = new FormData(form);
        $.ajax({
            type: "POST",
            url: '/search/',
            data: data,
            processData: false,
            contentType: false,
            cache: false,
            timeout: 600000,
            success: function(response, textStatus, xhr) {
                view_div = document.getElementById('view_image')
                $('#view_image').empty();
                var img_ele = document.createElement("IMG")
                img_ele.setAttribute("src", 'data:image/jpeg;base64,'+response['image_data'])
                view_div.appendChild(img_ele)
            },
            error: function(e, textStatus, xhr) {
                alert(e.responseText)
            }
        });
        e.preventDefault();
    });
})