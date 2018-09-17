// List of pending files to handle when the Upload button is finally clicked.
var PENDING_FILES  = [];

$(document).ready(function() {
    // Set up the drag/drop zone.
    initDropbox();

    // Set up the handler for the file input box.
    $("#file-picker").on("change", function() {
        addFiles(this.files);
        doUpload();
    });
});

function initDropbox() {
    var $dropbox = $("#out");

    // On drag enter...
    $dropbox.on("dragenter", function(e) {
        e.stopPropagation();
        e.preventDefault();
    });

    $dropbox.on("dragleave", function(e) {
        e.stopPropagation();
        e.preventDefault();
    });

    // On drag over...
    $dropbox.on("dragover", function(e) {
        e.stopPropagation();
        e.preventDefault();
    });

    // On drop...
    $dropbox.on("drop", function(e) {
        e.preventDefault();
        var files = e.originalEvent.dataTransfer.files;
        
        if (confirm('Are you sure to upload?')) {
            addFiles(files);
            doUpload();
        }
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
    // Add them to the pending files list.
    for (var i = 0; i < files.length; i++) {
        PENDING_FILES.push(files[i]);
    }
}

function doUpload() {
    // Collect the form data.
    // fd = collectFormData();
    var fd = new FormData();

    // Attach the files.
    for (var i = 0; i < PENDING_FILES.length; i++) {
        // Collect the other form data.
        fd.append("file", PENDING_FILES[i]);
    }

    var xhr = $.ajax({
        xhr: function() {
            var xhrobj = $.ajaxSettings.xhr();
            return xhrobj;
        },
        url: '/do-upload/from-edit/' + wiki_group,
        method: "POST",
        contentType: false,
        processData: false,
        cache: false,
        data: fd,
        success: function(data) {
            PENDING_FILES.splice(0, PENDING_FILES.length);
            editor.replaceRange(data, CodeMirror.Pos(editor.lastLine()))
        },
    });
}