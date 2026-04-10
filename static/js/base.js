document.addEventListener("DOMContentLoaded", function () {
    const badge = document.getElementById("ouvidoriaBadge");

    if (!badge) return;

    let isDragging = false;
    let offsetX, offsetY;

    badge.addEventListener("mousedown", function (e) {
        isDragging = true;

        offsetX = e.clientX - badge.getBoundingClientRect().left;
        offsetY = e.clientY - badge.getBoundingClientRect().top;

        badge.style.cursor = "grabbing";
    });

    document.addEventListener("mousemove", function (e) {
        if (!isDragging) return;

        badge.style.left = (e.clientX - offsetX) + "px";
        badge.style.top = (e.clientY - offsetY) + "px";

        badge.style.right = "auto"; // 🔥 importante
    });

    document.addEventListener("mouseup", function () {
        isDragging = false;
        badge.style.cursor = "pointer";
    });
});
