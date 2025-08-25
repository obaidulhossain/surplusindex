document.addEventListener("DOMContentLoaded", function () {
    let modal = document.createElement("div");
    modal.id = "media-picker-modal";
    modal.style.cssText = `
        display: none;
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background: rgba(0,0,0,0.6);
        z-index: 9999;
        justify-content: center;
        align-items: center;
    `;
    modal.innerHTML = `
        <div style="background: white; width: 80%; height: 80%; border-radius: 8px; overflow: hidden; position: relative;">
            <iframe id="media-picker-iframe" src="" style="width:100%; height:100%; border:none;"></iframe>
            <button id="media-picker-close" style="position:absolute; top:10px; right:10px;">❌</button>
        </div>
    `;
    document.body.appendChild(modal);

    let iframe = modal.querySelector("#media-picker-iframe");
    let closeBtn = modal.querySelector("#media-picker-close");
    let currentTargetInput = null;  // Keep track of which input to fill

    closeBtn.addEventListener("click", function () {
        modal.style.display = "none";
    });

    window.addEventListener("message", function (event) {
        if (event.data && event.data.mediaUrl) {
            if (currentTargetInput) {
                currentTargetInput.value = event.data.mediaUrl;
            }
            modal.style.display = "none";
        }
    });

    document.querySelectorAll("[data-media-picker]").forEach(function (el) {
        el.addEventListener("click", function () {
            let targetInputSelector = el.getAttribute("data-target");
            currentTargetInput = document.querySelector(targetInputSelector);
            iframe.src = "/media-manager/";
            modal.style.display = "flex";
        });
    });
});
