const countElement = document.getElementById("ingredients-count");
const spiceLayer = document.getElementById("spice-layer");

function animateCount() {
  if (!countElement) return;
  const target = Number(countElement.dataset.target || 0);
  const durationMs = 900;
  const start = performance.now();

  function tick(now) {
    const progress = Math.min((now - start) / durationMs, 1);
    countElement.textContent = Math.floor(progress * target).toLocaleString("es-ES");
    if (progress < 1) requestAnimationFrame(tick);
  }

  requestAnimationFrame(tick);
}

function buildSpiceDots() {
  if (!spiceLayer) return;
  for (let i = 0; i < 28; i += 1) {
    const dot = document.createElement("span");
    const size = Math.random() * 6 + 3;
    dot.className = "spice-dot";
    dot.style.width = `${size}px`;
    dot.style.height = `${size}px`;
    dot.style.left = `${Math.random() * 100}vw`;
    dot.style.top = `${Math.random() * 100}vh`;
    spiceLayer.appendChild(dot);
  }
}

animateCount();
buildSpiceDots();
