window.addEventListener("load", function () {
    const f = document.getElementById("myi");
    f.onload = function () {
        f.style.height = f.contentWindow.document.body.scrollHeight +50+ "px";
    };
});