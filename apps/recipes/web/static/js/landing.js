const layer = document.getElementById("ingredient-layer");
const hero = document.getElementById("hero");

const kitchenItems = ["🥄", "🍳", "🍅", "🥕", "🥚", "🌶️"];

function random(min, max) {
  return Math.random() * (max - min) + min;
}

function makeFloatingItems() {
  const total = 26;

  for (let i = 0; i < total; i += 1) {
    const item = document.createElement("span");
    const symbol = kitchenItems[Math.floor(Math.random() * kitchenItems.length)];
    const size = random(22, 52);
    const x = random(-3, 96);
    const y = random(-5, 95);

    item.className = `floating-item ${size < 30 ? "tiny" : ""}`.trim();
    item.textContent = symbol;
    item.style.fontSize = `${size}px`;
    item.style.setProperty("--x", `${x}vw`);
    item.style.setProperty("--y", `${y}vh`);
    item.style.setProperty("--duration", `${random(6.5, 11.5)}s`);
    item.style.setProperty("--delay", `${random(-8, 0)}s`);

    layer.appendChild(item);
  }
}

function makeSpiceDots() {
  for (let i = 0; i < 40; i += 1) {
    const dot = document.createElement("span");
    const size = random(3, 8);
    dot.className = "spice-dot";
    dot.style.width = `${size}px`;
    dot.style.height = `${size}px`;
    dot.style.setProperty("--x", `${random(0, 100)}vw`);
    dot.style.setProperty("--y", `${random(0, 100)}vh`);
    dot.style.setProperty("--duration", `${random(7, 14)}s`);
    dot.style.animationDelay = `${random(-10, 0)}s`;
    layer.appendChild(dot);
  }
}

function parallaxOnPointer() {
  window.addEventListener("pointermove", (event) => {
    const x = (event.clientX / window.innerWidth - 0.5) * 12;
    const y = (event.clientY / window.innerHeight - 0.5) * 12;
    layer.style.transform = `translate(${x * -0.12}px, ${y * -0.12}px)`;
  });

  window.addEventListener("pointerleave", () => {
    layer.style.transform = "translate(0, 0)";
  });
}

makeFloatingItems();
makeSpiceDots();
parallaxOnPointer();
