function saveCanvas(canvas, name) {
    var a = document.createElement('a');

    canvas.toBlob(function(blob) {
        a.href = window.URL.createObjectURL(blob);
    }, 'image/png');

    a.style = 'display: none';
    a.download = name;
    document.body.appendChild(a);
    a.click();

    setTimeout(function() {
        document.body.removeChild(a);
        window.URL.revokeObjectURL(a.href);
    }, 0);
}
