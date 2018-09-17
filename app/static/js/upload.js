// List of pending files to handle when the Upload button is finally clicked.
var PENDING_FILES  = [];

$(document).ready(function() {
    // Set up the drag/drop zone.
    initDropbox();

    // Set up the handler for the file input box.
    $("#file-picker").on("change", function() {
        addFiles(this.files);
    });
    

    // Handle the submit button.
    $("#upload-button").on("click", function(e) {
        // If the user has JS disabled, none of this code is running but the
        // file multi-upload input box should still work. In this case they'll
        // just POST to the upload endpoint directly. However, with JS we'll do
        // the POST using ajax and then redirect them ourself when done.
        e.preventDefault();
		if (PENDING_FILES.length == 0) {
			window.close();
		}
        doUpload();
    });
});

function initDropbox() {
    var $dropbox = $("#dropbox");

    // On drag enter...
    $dropbox.on("dragenter", function(e) {
        e.stopPropagation();
        e.preventDefault();
        $(this).addClass("active");
    });
    
    $dropbox.on("dragleave", function(e) {
        e.stopPropagation();
        e.preventDefault();
        $(this).removeClass("active");
    });

    // On drag over...
    $dropbox.on("dragover", function(e) {
        e.stopPropagation();
        e.preventDefault();
    });

    // On drop...
    $dropbox.on("drop", function(e) {
        e.preventDefault();
        $(this).removeClass("active");

        // Get the files.
        var files = e.originalEvent.dataTransfer.files;
        addFiles(files);
    });

    // If the files are dropped outside of the drop zone, the browser will
    // redirect to show the files in the window. To avoid that we can prevent
    // the 'drop' event on the document.
    function stopDefault(e) {
        e.stopPropagation();
        e.preventDefault();
    }
    $(document).on("dragenter", stopDefault);
    $(document).on("dragover", stopDefault);
    $(document).on("drop", stopDefault);
}

function addFiles(files) {
    var $selected = $('#selected-files');
    var get_file_str = function() {
        var file_str = PENDING_FILES.length > 1 ? ' files':' file';
        return PENDING_FILES.length + file_str + ' selected'
    }

    // Add them to the pending files list.
    for (var i = 0; i < files.length; i++) {
        PENDING_FILES.push(files[i]);

        // Append files to show on page
        var li_file = $('<li/>', {
            class: 'list-group-item d-flex justify-content-between align-items-center',
            text: files[i].name}).appendTo($selected);
        var del_file = $('<button/>', {
            type: 'button',
            class: 'ml-auto btn btn-sm btn-danger',
            html: '&times;'}).appendTo(li_file);
        del_file.on('click', function() {
            PENDING_FILES.splice($(this).parent().index(), 1);
            $(this).parent().remove();
            $("#file-number").text(get_file_str());
        });
    }
    $("#file-number").text(get_file_str());
}

function doUpload() {
    $("#progress").show();
    var $progressBar   = $("#progress-bar");
    var $completion = $("#completion");

    // Gray out the form.
    $("#upload-form :input").attr("disabled", "disabled");

    // Initialize the progress bar.
    $progressBar.css({"width": "0%"});

    // Collect the form data.
    // fd = collectFormData();
    var fd = new FormData();

    // Attach the files.
    for (var i = 0; i < PENDING_FILES.length; i++) {
        // Collect the other form data.
        fd.append("file", PENDING_FILES[i]);
    }

    fd.append('page_id', page_id);

    var xhr = $.ajax({
        xhr: function() {
            var xhrobj = $.ajaxSettings.xhr();
            if (xhrobj.upload) {
                xhrobj.upload.addEventListener("progress", function(event) {
                    var percent = 0;
                    var position = event.loaded || event.position;
                    var total    = event.total;
                    if (event.lengthComputable) {
                        percent = Math.ceil(position / total * 100);
                    }

                    // Set the progress bar.
                    $progressBar.css({"width": percent + "%"});
                    $completion.text(percent + "%");
                }, false)
            }
            return xhrobj;
        },
        url: '/do-upload/' + wiki_group,
        method: "POST",
        contentType: false,
        processData: false,
        cache: false,
        data: fd,
        success: function(data) {
            $progressBar.css({"width": "100%"});
            opener.location.reload();
            window.close();
        },
    });
}