(() => {
  const uploadZone   = document.getElementById("upload-zone");
  const fileInput    = document.getElementById("file-input");
  const editor       = document.getElementById("editor");
  const imageCanvas  = document.getElementById("image-canvas");
  const maskCanvas   = document.getElementById("mask-canvas");
  const canvasWrap   = document.getElementById("canvas-wrap");
  const brushCursor  = document.getElementById("brush-cursor");
  const brushSlider  = document.getElementById("brush-size");
  const brushDisplay = document.getElementById("brush-size-display");
  const btnClearMask = document.getElementById("btn-clear-mask");
  const btnRemove    = document.getElementById("btn-remove");
  const btnReset     = document.getElementById("btn-reset");
  const resultSection = document.getElementById("result-section");
  const originalImg  = document.getElementById("original-img");
  const resultImg    = document.getElementById("result-img");
  const downloadLink = document.getElementById("download-link");
  const loading      = document.getElementById("loading");
  const errorBanner  = document.getElementById("error-banner");

  const imgCtx  = imageCanvas.getContext("2d");
  const maskCtx = maskCanvas.getContext("2d");

  let brushSize = 40;
  let painting  = false;
  let originalDataURL = null;

  // ── Upload zone ──────────────────────────────────────────────────────────────
  uploadZone.addEventListener("click", () => fileInput.click());

  uploadZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    uploadZone.classList.add("drag-over");
  });

  uploadZone.addEventListener("dragleave", () => uploadZone.classList.remove("drag-over"));

  uploadZone.addEventListener("drop", (e) => {
    e.preventDefault();
    uploadZone.classList.remove("drag-over");
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith("image/")) loadImage(file);
  });

  fileInput.addEventListener("change", () => {
    if (fileInput.files[0]) loadImage(fileInput.files[0]);
  });

  function loadImage(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        // Scale down to max 1024px wide/tall to keep API payloads manageable
        const MAX = 1024;
        let w = img.naturalWidth;
        let h = img.naturalHeight;
        if (w > MAX || h > MAX) {
          const scale = Math.min(MAX / w, MAX / h);
          w = Math.round(w * scale);
          h = Math.round(h * scale);
        }

        imageCanvas.width  = w;
        imageCanvas.height = h;
        maskCanvas.width   = w;
        maskCanvas.height  = h;

        imgCtx.drawImage(img, 0, 0, w, h);
        clearMask();
        originalDataURL = imageCanvas.toDataURL("image/png");

        uploadZone.classList.add("hidden");
        editor.classList.remove("hidden");
        resultSection.classList.add("hidden");
        hideError();
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(file);
  }

  // ── Brush size ───────────────────────────────────────────────────────────────
  brushSlider.addEventListener("input", () => {
    brushSize = parseInt(brushSlider.value);
    brushDisplay.textContent = brushSize + "px";
    brushCursor.style.width  = brushSize + "px";
    brushCursor.style.height = brushSize + "px";
  });

  // ── Mask painting ────────────────────────────────────────────────────────────
  maskCtx.globalCompositeOperation = "source-over";
  maskCtx.fillStyle = "rgba(255, 40, 40, 0.55)";
  maskCtx.strokeStyle = "rgba(255, 40, 40, 0.55)";
  maskCtx.lineJoin = "round";
  maskCtx.lineCap  = "round";

  function getPos(e) {
    const rect = maskCanvas.getBoundingClientRect();
    const scaleX = maskCanvas.width  / rect.width;
    const scaleY = maskCanvas.height / rect.height;
    const src = e.touches ? e.touches[0] : e;
    return {
      x: (src.clientX - rect.left) * scaleX,
      y: (src.clientY - rect.top)  * scaleY,
    };
  }

  function startPaint(e) {
    e.preventDefault();
    painting = true;
    const pos = getPos(e);
    maskCtx.lineWidth = brushSize;
    maskCtx.beginPath();
    maskCtx.moveTo(pos.x, pos.y);
    maskCtx.lineTo(pos.x + 0.1, pos.y);
    maskCtx.stroke();
  }

  function continuePaint(e) {
    e.preventDefault();
    const rect = canvasWrap.getBoundingClientRect();
    const src = e.touches ? e.touches[0] : e;
    const cx = src.clientX - rect.left;
    const cy = src.clientY - rect.top;

    brushCursor.style.left = cx + "px";
    brushCursor.style.top  = cy + "px";

    if (!painting) return;
    const pos = getPos(e);
    maskCtx.lineWidth = brushSize;
    maskCtx.lineTo(pos.x, pos.y);
    maskCtx.stroke();
  }

  function stopPaint() {
    painting = false;
    maskCtx.beginPath();
  }

  canvasWrap.addEventListener("mousedown",  startPaint);
  canvasWrap.addEventListener("mousemove",  continuePaint);
  canvasWrap.addEventListener("mouseup",    stopPaint);
  canvasWrap.addEventListener("mouseleave", stopPaint);
  canvasWrap.addEventListener("touchstart", startPaint,    { passive: false });
  canvasWrap.addEventListener("touchmove",  continuePaint, { passive: false });
  canvasWrap.addEventListener("touchend",   stopPaint);

  // Show / hide brush cursor
  canvasWrap.addEventListener("mouseenter", () => {
    brushCursor.style.display = "block";
    brushCursor.style.width   = brushSize + "px";
    brushCursor.style.height  = brushSize + "px";
  });
  canvasWrap.addEventListener("mouseleave", () => {
    brushCursor.style.display = "none";
  });

  // ── Clear mask ───────────────────────────────────────────────────────────────
  function clearMask() {
    maskCtx.clearRect(0, 0, maskCanvas.width, maskCanvas.height);
  }
  btnClearMask.addEventListener("click", clearMask);

  // ── Reset to upload ──────────────────────────────────────────────────────────
  btnReset.addEventListener("click", () => {
    editor.classList.add("hidden");
    resultSection.classList.add("hidden");
    uploadZone.classList.remove("hidden");
    fileInput.value = "";
    originalDataURL = null;
    clearMask();
    hideError();
  });

  // ── Remove people ────────────────────────────────────────────────────────────
  btnRemove.addEventListener("click", async () => {
    // Build a binary mask: white = inpaint zone, black = keep
    const binaryMaskCanvas = document.createElement("canvas");
    binaryMaskCanvas.width  = maskCanvas.width;
    binaryMaskCanvas.height = maskCanvas.height;
    const bCtx = binaryMaskCanvas.getContext("2d");
    bCtx.fillStyle = "#000000";
    bCtx.fillRect(0, 0, binaryMaskCanvas.width, binaryMaskCanvas.height);

    // Convert painted (red) pixels to white
    const px = maskCtx.getImageData(0, 0, maskCanvas.width, maskCanvas.height);
    const out = bCtx.createImageData(maskCanvas.width, maskCanvas.height);
    for (let i = 0; i < px.data.length; i += 4) {
      const alpha = px.data[i + 3];
      const val   = alpha > 10 ? 255 : 0;
      out.data[i] = out.data[i + 1] = out.data[i + 2] = val;
      out.data[i + 3] = 255;
    }
    bCtx.putImageData(out, 0, 0);

    const maskDataURL  = binaryMaskCanvas.toDataURL("image/png");
    const imageDataURL = originalDataURL;

    hideError();
    setLoading(true);

    try {
      const resp = await fetch("/remove-people", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: imageDataURL, mask: maskDataURL }),
      });

      const data = await resp.json();

      if (!resp.ok || data.error) {
        showError(data.error || `Server error ${resp.status}`);
        return;
      }

      originalImg.src    = imageDataURL;
      resultImg.src      = data.result;
      downloadLink.href  = data.result;
      resultSection.classList.remove("hidden");
      resultSection.scrollIntoView({ behavior: "smooth" });
    } catch (err) {
      showError("Request failed: " + err.message);
    } finally {
      setLoading(false);
    }
  });

  // ── Helpers ──────────────────────────────────────────────────────────────────
  function setLoading(on) {
    loading.classList.toggle("hidden", !on);
    btnRemove.disabled = on;
  }

  function showError(msg) {
    errorBanner.textContent = "Error: " + msg;
    errorBanner.classList.remove("hidden");
  }

  function hideError() {
    errorBanner.classList.add("hidden");
    errorBanner.textContent = "";
  }
})();
