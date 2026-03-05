document.addEventListener("DOMContentLoaded", () => {
  const card = document.querySelector(".placeholder-card");
  const searchInput = document.getElementById("ingredient-search");
  const selectedIdInput = document.getElementById("ingredient-selected-id");
  const suggestionsList = document.getElementById("ingredient-suggestions");
  const qtyInput = document.getElementById("ingredient-qty");
  const unitSelect = document.getElementById("ingredient-unit");
  const addBtn = document.getElementById("add-ingredient-btn");
  const pickedGrid = document.getElementById("picked-ingredients");
  const builderMessage = document.getElementById("builder-message");
  const modal = document.getElementById("ingredient-modal");
  const modalCloseBtn = document.getElementById("modal-close-btn");
  const modalTitle = document.getElementById("modal-title");
  const modalSubtitle = document.getElementById("modal-subtitle");
  const modalLoading = document.getElementById("modal-loading");
  const modalContent = document.getElementById("modal-content");

  if (card) {
    card.animate(
      [
        { opacity: 0, transform: "translateY(12px)" },
        { opacity: 1, transform: "translateY(0)" },
      ],
      { duration: 420, easing: "ease-out", fill: "both" }
    );
  }

  if (!searchInput || !suggestionsList || !addBtn) return;

  const suggestionsUrl = searchInput.dataset.suggestionsUrl;
  let debounceTimer;
  let currentResults = [];

  function hideSuggestions() {
    suggestionsList.hidden = true;
    suggestionsList.innerHTML = "";
    currentResults = [];
  }

  function showMessage(text) {
    if (!builderMessage) return;
    builderMessage.textContent = text;
  }

  function normalizeLabel(key) {
    return key
      .replace(/_/g, " ")
      .replace(/\b\w/g, (m) => m.toUpperCase());
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function macroEntries(nutrients) {
    const macroOrder = [
      [["energy_kcal", "energía_kcal", "energia_kcal"], "Energia (kcal)"],
      [["protein_g", "proteína_g", "proteina_g"], "Proteina (g)"],
      [["fat_g", "grasa_lípida_total_g", "grasa_lipida_total_g"], "Grasa total (g)"],
      [["carbohydrate_g", "carbohidratos_por_diferencia_g"], "Carbohidratos (g)"],
      [["fiber_g", "fibra_total_dietaria_g"], "Fibra (g)"],
      [["sugars_g", "azúcares_totales_incl_nlea_g", "azucares_totales_incl_nlea_g"], "Azucares (g)"],
      [["sodium_mg", "sodio_na_mg"], "Sodio (mg)"],
    ];

    const firstValue = (keys) => {
      for (const key of keys) {
        if (nutrients[key] !== undefined && nutrients[key] !== null && nutrients[key] !== "") {
          return nutrients[key];
        }
      }
      return null;
    };

    const out = [];
    for (const [keys, label] of macroOrder) {
      const value = firstValue(keys);
      if (value === null) continue;
      out.push({ label, value, keys });
    }
    return out;
  }

  function microEntries(nutrients, macros) {
    const macroKeys = new Set();
    for (const macro of macros) {
      for (const key of macro.keys || []) macroKeys.add(key);
    }

    const keys = Object.keys(nutrients || {}).filter((k) => !macroKeys.has(k));
    keys.sort((a, b) => a.localeCompare(b));
    return keys.map((key) => ({
      label: normalizeLabel(key),
      value: nutrients[key],
    }));
  }

  function openModalBase(title, subtitle) {
    if (!modal || !modalTitle || !modalSubtitle || !modalLoading || !modalContent) return;
    modalTitle.textContent = title;
    modalSubtitle.textContent = subtitle;
    modalLoading.hidden = false;
    modalContent.hidden = true;
    modalContent.innerHTML = "";
    modal.hidden = false;
    document.body.style.overflow = "hidden";
  }

  function closeModal() {
    if (!modal) return;
    modal.hidden = true;
    document.body.style.overflow = "";
  }

  function renderIngredientDetail(payload) {
    if (!modalLoading || !modalContent) return;
    const nutrients = payload.nutrientes || {};
    const macros = macroEntries(nutrients);
    const micros = microEntries(nutrients, macros);

    const macroCards = macros.length
      ? macros
          .map(
            (item) => `
              <article class="macro-card">
                <span class="macro-name">${escapeHtml(item.label)}</span>
                <span class="macro-val">${escapeHtml(item.value)}</span>
              </article>
            `
          )
          .join("")
      : `<article class="macro-card"><span class="macro-name">Sin macros detectadas</span><span class="macro-val">-</span></article>`;

    const microPills = micros.length
      ? micros
          .map(
            (item) =>
              `<span class="micro-pill"><strong>${escapeHtml(item.label)}:</strong> ${escapeHtml(item.value)}</span>`
          )
          .join("")
      : `<span class="micro-pill"><strong>Info:</strong> sin micronutrientes cargados</span>`;

    modalContent.innerHTML = `
      <section class="macro-panel">
        <h4>Macros principales</h4>
        <div class="macro-grid">${macroCards}</div>
      </section>
      <section class="micro-panel">
        <h4>Micros y otros nutrientes</h4>
        <div class="micro-list">${microPills}</div>
      </section>
      <section class="raw-panel">
        <h4>Detalle tecnico (JSON)</h4>
        <pre class="raw-box">${escapeHtml(JSON.stringify(nutrients, null, 2))}</pre>
      </section>
    `;
    modalLoading.hidden = true;
    modalContent.hidden = false;
  }

  async function showIngredientDetail(fdcId, ingredientName) {
    openModalBase(ingredientName, `FDC ID: ${fdcId}`);
    try {
      const response = await fetch(`/api/v1/ingredients/${fdcId}/`);
      if (!response.ok) throw new Error("No se pudo cargar la informacion");
      const payload = await response.json();
      renderIngredientDetail(payload);
    } catch (error) {
      if (modalLoading) modalLoading.hidden = true;
      if (modalContent) {
        modalContent.hidden = false;
        modalContent.innerHTML = `<section class="raw-panel"><h4>Error</h4><p>No fue posible cargar el detalle del ingrediente.</p></section>`;
      }
    }
  }

  function renderSuggestions(results) {
    suggestionsList.innerHTML = "";
    currentResults = results;

    if (!results.length) {
      hideSuggestions();
      return;
    }

    for (const item of results) {
      const li = document.createElement("li");
      const button = document.createElement("button");
      button.type = "button";
      button.className = "suggestion-btn";
      button.textContent = item.alimento;
      button.dataset.fdcId = String(item.fdc_id);

      button.addEventListener("click", () => {
        searchInput.value = item.alimento;
        selectedIdInput.value = String(item.fdc_id);
        hideSuggestions();
      });

      li.appendChild(button);
      suggestionsList.appendChild(li);
    }

    suggestionsList.hidden = false;
  }

  async function fetchSuggestions(term) {
    if (!term) {
      hideSuggestions();
      return;
    }

    const url = `${suggestionsUrl}?q=${encodeURIComponent(term)}`;
    const response = await fetch(url);
    if (!response.ok) {
      hideSuggestions();
      return;
    }

    const payload = await response.json();
    renderSuggestions(Array.isArray(payload.results) ? payload.results : []);
  }

  searchInput.addEventListener("input", () => {
    const term = searchInput.value.trim();
    selectedIdInput.value = "";

    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      fetchSuggestions(term);
    }, 160);
  });

  searchInput.addEventListener("keydown", (event) => {
    if (event.key !== "Enter" || !currentResults.length) return;
    event.preventDefault();
    const first = currentResults[0];
    searchInput.value = first.alimento;
    selectedIdInput.value = String(first.fdc_id);
    hideSuggestions();
  });

  document.addEventListener("click", (event) => {
    if (!suggestionsList.contains(event.target) && event.target !== searchInput) {
      hideSuggestions();
    }
  });

  addBtn.addEventListener("click", () => {
    const ingredientName = searchInput.value.trim();
    const selectedId = selectedIdInput.value.trim();
    const qtyRaw = qtyInput ? qtyInput.value.trim() : "";
    const qty = Number(qtyRaw);
    const unit = unitSelect ? unitSelect.value : "";

    if (!ingredientName || !selectedId) {
      showMessage("Selecciona un ingrediente desde las sugerencias.");
      return;
    }
    if (!qtyRaw || Number.isNaN(qty) || qty <= 0) {
      showMessage("Introduce una cantidad numerica valida.");
      return;
    }

    const cardEl = document.createElement("article");
    cardEl.className = "ingredient-card entering";
    cardEl.dataset.fdcId = selectedId;
    cardEl.dataset.ingredientName = ingredientName;
    const nameEl = document.createElement("span");
    nameEl.className = "name";
    nameEl.textContent = ingredientName;
    const metaEl = document.createElement("span");
    metaEl.className = "meta";
    metaEl.textContent = `${qty.toLocaleString("es-ES")} ${unit}`;
    const actionsEl = document.createElement("div");
    actionsEl.className = "card-actions";
    const infoBtn = document.createElement("button");
    infoBtn.type = "button";
    infoBtn.className = "info-btn";
    infoBtn.textContent = "Ver info";
    actionsEl.appendChild(infoBtn);
    cardEl.appendChild(nameEl);
    cardEl.appendChild(metaEl);
    cardEl.appendChild(actionsEl);
    pickedGrid.appendChild(cardEl);
    cardEl.addEventListener("animationend", () => {
      cardEl.classList.remove("entering");
    }, { once: true });

    searchInput.value = "";
    selectedIdInput.value = "";
    if (qtyInput) qtyInput.value = "";
    showMessage(`Añadido: ${ingredientName}`);
    hideSuggestions();
    searchInput.focus();
  });

  if (pickedGrid) {
    pickedGrid.addEventListener("click", (event) => {
      const target = event.target;
      if (!(target instanceof HTMLElement) || !target.classList.contains("info-btn")) return;
      const cardEl = target.closest(".ingredient-card");
      if (!cardEl) return;
      const fdcId = cardEl.dataset.fdcId;
      const ingredientName = cardEl.dataset.ingredientName || "Ingrediente";
      if (!fdcId) return;
      showIngredientDetail(fdcId, ingredientName);
    });
  }

  if (modalCloseBtn) {
    modalCloseBtn.addEventListener("click", closeModal);
  }

  if (modal) {
    modal.addEventListener("click", (event) => {
      const target = event.target;
      if (target instanceof HTMLElement && target.dataset.closeModal === "true") {
        closeModal();
      }
    });
  }

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeModal();
  });
});
