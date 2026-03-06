document.addEventListener("DOMContentLoaded", () => {
  const card = document.querySelector(".placeholder-card");

  const actionInput = document.getElementById("action-search");
  const actionSelectedIdInput = document.getElementById("action-selected-id");
  const actionSuggestionsList = document.getElementById("action-suggestions");
  const actionImportZone = document.getElementById("action-import-zone");

  const durationValueInput = document.getElementById("action-duration-value");
  const durationUnitSelect = document.getElementById("action-duration-unit");

  const searchInput = document.getElementById("ingredient-search");
  const selectedIdInput = document.getElementById("ingredient-selected-id");
  const suggestionsList = document.getElementById("ingredient-suggestions");
  const importZone = document.getElementById("ingredient-import-zone");
  const participleInput = document.getElementById("participle-search");
  const participleSelectedIdInput = document.getElementById("participle-selected-id");
  const participleSuggestionsList = document.getElementById("participle-suggestions");
  const participleImportZone = document.getElementById("participle-import-zone");

  const qtyInput = document.getElementById("ingredient-qty");
  const unitSelect = document.getElementById("ingredient-unit");
  const unitSelectedIdInput = document.getElementById("ingredient-unit-selected-id");
  const unitSuggestionsList = document.getElementById("ingredient-unit-suggestions");
  const unitImportZone = document.getElementById("ingredient-unit-import-zone");

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

  if (
    !searchInput ||
    !suggestionsList ||
    !addBtn ||
    !actionInput ||
    !actionSuggestionsList ||
    !participleInput ||
    !participleSuggestionsList
  ) return;

  const suggestionsUrl = searchInput.dataset.suggestionsUrl;
  const importUrl = searchInput.dataset.importUrl;
  const unitSuggestionsUrl = unitSelect ? unitSelect.dataset.suggestionsUrl : "";
  const unitAddUrl = unitSelect ? unitSelect.dataset.addUrl : "";
  const actionSuggestionsUrl = actionInput.dataset.suggestionsUrl || "";
  const actionAddUrl = actionInput.dataset.addUrl || "";
  const participleSuggestionsUrl = participleInput.dataset.suggestionsUrl || "";
  const participleAddUrl = participleInput.dataset.addUrl || "";

  const csrfTokenFromTemplate = searchInput.dataset.csrfToken || "";

  let debounceTimer;
  let unitDebounceTimer;
  let actionDebounceTimer;
  let participleDebounceTimer;

  let currentResults = [];
  let currentUnitResults = [];
  let currentActionResults = [];
  let currentParticipleResults = [];

  let activeSuggestionIndex = -1;
  let activeUnitSuggestionIndex = -1;
  let activeActionSuggestionIndex = -1;
  let activeParticipleSuggestionIndex = -1;

  let lastRequestId = 0;
  let lastUnitRequestId = 0;
  let lastActionRequestId = 0;
  let lastParticipleRequestId = 0;

  function showMessage(text) {
    if (!builderMessage) return;
    builderMessage.textContent = text;
  }

  function hideSuggestions() {
    suggestionsList.hidden = true;
    suggestionsList.innerHTML = "";
    currentResults = [];
    activeSuggestionIndex = -1;
    searchInput.setAttribute("aria-expanded", "false");
  }

  function hideImportZone() {
    if (!importZone) return;
    importZone.hidden = true;
    importZone.innerHTML = "";
  }

  function hideUnitSuggestions() {
    if (!unitSuggestionsList || !unitSelect) return;
    unitSuggestionsList.hidden = true;
    unitSuggestionsList.innerHTML = "";
    currentUnitResults = [];
    activeUnitSuggestionIndex = -1;
    unitSelect.setAttribute("aria-expanded", "false");
  }

  function hideUnitImportZone() {
    if (!unitImportZone) return;
    unitImportZone.hidden = true;
    unitImportZone.innerHTML = "";
  }

  function hideActionSuggestions() {
    actionSuggestionsList.hidden = true;
    actionSuggestionsList.innerHTML = "";
    currentActionResults = [];
    activeActionSuggestionIndex = -1;
    actionInput.setAttribute("aria-expanded", "false");
  }

  function hideActionImportZone() {
    if (!actionImportZone) return;
    actionImportZone.hidden = true;
    actionImportZone.innerHTML = "";
  }

  function hideParticipleSuggestions() {
    if (!participleSuggestionsList) return;
    participleSuggestionsList.hidden = true;
    participleSuggestionsList.innerHTML = "";
    currentParticipleResults = [];
    activeParticipleSuggestionIndex = -1;
    participleInput.setAttribute("aria-expanded", "false");
  }

  function hideParticipleImportZone() {
    if (!participleImportZone) return;
    participleImportZone.hidden = true;
    participleImportZone.innerHTML = "";
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

  function macroEntries(payload) {
    const nutrients = payload.nutrients || {};
    const macroOrder = [
      [["energy_total", "energía, total"], "Energia (kcal)"],
      [["protein_total", "proteina, total"], "Proteina (g)"],
      [["grasa, total (lipidos totales)"], "Grasa total (g)"],
      [["carbohidratos"], "Carbohidratos (g)"],
      [["fibra, dietetica total"], "Fibra (g)"],
      [["sodio"], "Sodio (mg)"],
    ];

    const firstNutrientValue = (keys) => {
      for (const key of keys) {
        if (nutrients[key] !== undefined && nutrients[key] !== null && nutrients[key] !== "") {
          return nutrients[key];
        }
      }
      return null;
    };

    const out = [];
    for (const [keys, label] of macroOrder) {
      const payloadKey = keys.find(
        (key) => payload[key] !== undefined && payload[key] !== null && payload[key] !== ""
      );
      const payloadValue = payloadKey ? payload[payloadKey] : null;
      const nutrientValue = firstNutrientValue(keys);
      const value = payloadValue ?? nutrientValue;
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
    const nutrients = payload.nutrients || {};
    const macros = macroEntries(payload);
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

  async function showIngredientDetail(sourceId, ingredientName) {
    openModalBase(ingredientName, `ID fuente: ${sourceId}`);
    try {
      const response = await fetch(`/api/v1/ingredients/${sourceId}/`);
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

  function setActiveSuggestion(index) {
    const buttons = suggestionsList.querySelectorAll(".suggestion-btn");
    buttons.forEach((button, btnIndex) => {
      button.classList.toggle("active", btnIndex === index);
    });
    activeSuggestionIndex = index;
  }

  function setActiveUnitSuggestion(index) {
    if (!unitSuggestionsList) return;
    const buttons = unitSuggestionsList.querySelectorAll(".suggestion-btn");
    buttons.forEach((button, btnIndex) => {
      button.classList.toggle("active", btnIndex === index);
    });
    activeUnitSuggestionIndex = index;
  }

  function setActiveActionSuggestion(index) {
    const buttons = actionSuggestionsList.querySelectorAll(".suggestion-btn");
    buttons.forEach((button, btnIndex) => {
      button.classList.toggle("active", btnIndex === index);
    });
    activeActionSuggestionIndex = index;
  }

  function setActiveParticipleSuggestion(index) {
    const buttons = participleSuggestionsList.querySelectorAll(".suggestion-btn");
    buttons.forEach((button, btnIndex) => {
      button.classList.toggle("active", btnIndex === index);
    });
    activeParticipleSuggestionIndex = index;
  }

  function selectSuggestion(item) {
    searchInput.value = item.name;
    selectedIdInput.value = String(item.id);
    hideSuggestions();
    hideImportZone();
  }

  function selectUnitSuggestion(item) {
    if (!unitSelect || !unitSelectedIdInput) return;
    unitSelect.value = item.name;
    unitSelectedIdInput.value = String(item.id);
    hideUnitSuggestions();
    hideUnitImportZone();
  }

  function selectActionSuggestion(item) {
    actionInput.value = item.name;
    actionSelectedIdInput.value = String(item.id);
    hideActionSuggestions();
    hideActionImportZone();
  }

  function selectParticipleSuggestion(item) {
    participleInput.value = item.name;
    participleSelectedIdInput.value = String(item.id);
    hideParticipleSuggestions();
    hideParticipleImportZone();
  }

  function renderSuggestions(results) {
    suggestionsList.innerHTML = "";
    currentResults = results;
    activeSuggestionIndex = -1;
    hideImportZone();

    if (!searchInput.value.trim()) {
      hideSuggestions();
      return;
    }

    if (!results.length) {
      const li = document.createElement("li");
      li.className = "suggestion-empty";
      li.textContent = "No hay coincidencias locales";
      suggestionsList.appendChild(li);
      suggestionsList.hidden = false;
      searchInput.setAttribute("aria-expanded", "true");
      renderImportAction(searchInput.value.trim());
      return;
    }

    for (const [index, item] of results.entries()) {
      const li = document.createElement("li");
      const button = document.createElement("button");
      button.type = "button";
      button.className = "suggestion-btn";
      button.textContent = item.name;
      button.setAttribute("role", "option");
      button.addEventListener("click", () => selectSuggestion(item));
      button.addEventListener("mouseenter", () => setActiveSuggestion(index));
      li.appendChild(button);
      suggestionsList.appendChild(li);
    }

    suggestionsList.hidden = false;
    searchInput.setAttribute("aria-expanded", "true");
  }

  function renderUnitSuggestions(results) {
    if (!unitSuggestionsList || !unitSelect) return;
    unitSuggestionsList.innerHTML = "";
    currentUnitResults = results;
    activeUnitSuggestionIndex = -1;
    hideUnitImportZone();

    if (!unitSelect.value.trim()) {
      hideUnitSuggestions();
      return;
    }

    if (!results.length) {
      const li = document.createElement("li");
      li.className = "suggestion-empty";
      li.textContent = "No hay coincidencias locales";
      unitSuggestionsList.appendChild(li);
      unitSuggestionsList.hidden = false;
      unitSelect.setAttribute("aria-expanded", "true");
      renderUnitImportAction(unitSelect.value.trim());
      return;
    }

    for (const [index, item] of results.entries()) {
      const li = document.createElement("li");
      const button = document.createElement("button");
      button.type = "button";
      button.className = "suggestion-btn";
      button.textContent = item.name;
      button.setAttribute("role", "option");
      button.addEventListener("click", () => selectUnitSuggestion(item));
      button.addEventListener("mouseenter", () => setActiveUnitSuggestion(index));
      li.appendChild(button);
      unitSuggestionsList.appendChild(li);
    }

    unitSuggestionsList.hidden = false;
    unitSelect.setAttribute("aria-expanded", "true");
  }

  function renderActionSuggestions(results) {
    actionSuggestionsList.innerHTML = "";
    currentActionResults = results;
    activeActionSuggestionIndex = -1;
    hideActionImportZone();

    if (!actionInput.value.trim()) {
      hideActionSuggestions();
      return;
    }

    if (!results.length) {
      const li = document.createElement("li");
      li.className = "suggestion-empty";
      li.textContent = "No hay coincidencias locales";
      actionSuggestionsList.appendChild(li);
      actionSuggestionsList.hidden = false;
      actionInput.setAttribute("aria-expanded", "true");
      renderActionImportAction(actionInput.value.trim());
      return;
    }

    for (const [index, item] of results.entries()) {
      const li = document.createElement("li");
      const button = document.createElement("button");
      button.type = "button";
      button.className = "suggestion-btn";
      button.textContent = item.name;
      button.setAttribute("role", "option");
      button.addEventListener("click", () => selectActionSuggestion(item));
      button.addEventListener("mouseenter", () => setActiveActionSuggestion(index));
      li.appendChild(button);
      actionSuggestionsList.appendChild(li);
    }

    actionSuggestionsList.hidden = false;
    actionInput.setAttribute("aria-expanded", "true");
  }

  function renderParticipleSuggestions(results) {
    participleSuggestionsList.innerHTML = "";
    currentParticipleResults = results;
    activeParticipleSuggestionIndex = -1;
    hideParticipleImportZone();

    if (!participleInput.value.trim()) {
      hideParticipleSuggestions();
      return;
    }

    if (!results.length) {
      const li = document.createElement("li");
      li.className = "suggestion-empty";
      li.textContent = "No hay coincidencias locales";
      participleSuggestionsList.appendChild(li);
      participleSuggestionsList.hidden = false;
      participleInput.setAttribute("aria-expanded", "true");
      renderParticipleImportAction(participleInput.value.trim());
      return;
    }

    for (const [index, item] of results.entries()) {
      const li = document.createElement("li");
      const button = document.createElement("button");
      button.type = "button";
      button.className = "suggestion-btn";
      button.textContent = item.name;
      button.setAttribute("role", "option");
      button.addEventListener("click", () => selectParticipleSuggestion(item));
      button.addEventListener("mouseenter", () => setActiveParticipleSuggestion(index));
      li.appendChild(button);
      participleSuggestionsList.appendChild(li);
    }

    participleSuggestionsList.hidden = false;
    participleInput.setAttribute("aria-expanded", "true");
  }

  async function fetchSuggestions(term) {
    if (!term) {
      hideSuggestions();
      hideImportZone();
      return;
    }

    const requestId = ++lastRequestId;
    const response = await fetch(`${suggestionsUrl}?q=${encodeURIComponent(term)}`);
    if (!response.ok) {
      hideSuggestions();
      hideImportZone();
      return;
    }

    const payload = await response.json();
    if (requestId !== lastRequestId) return;
    renderSuggestions(Array.isArray(payload) ? payload.slice(0, 5) : []);
  }

  async function fetchUnitSuggestions(term) {
    if (!term || !unitSuggestionsUrl) {
      hideUnitSuggestions();
      hideUnitImportZone();
      return;
    }

    const requestId = ++lastUnitRequestId;
    const response = await fetch(`${unitSuggestionsUrl}?q=${encodeURIComponent(term)}`);
    if (!response.ok) {
      hideUnitSuggestions();
      hideUnitImportZone();
      return;
    }

    const payload = await response.json();
    if (requestId !== lastUnitRequestId) return;
    renderUnitSuggestions(Array.isArray(payload) ? payload.slice(0, 5) : []);
  }

  async function fetchActionSuggestions(term) {
    if (!term || !actionSuggestionsUrl) {
      hideActionSuggestions();
      hideActionImportZone();
      return;
    }

    const requestId = ++lastActionRequestId;
    const response = await fetch(`${actionSuggestionsUrl}?q=${encodeURIComponent(term)}`);
    if (!response.ok) {
      hideActionSuggestions();
      hideActionImportZone();
      return;
    }

    const payload = await response.json();
    if (requestId !== lastActionRequestId) return;
    renderActionSuggestions(Array.isArray(payload) ? payload.slice(0, 5) : []);
  }

  async function fetchParticipleSuggestions(term) {
    if (!term || !participleSuggestionsUrl) {
      hideParticipleSuggestions();
      hideParticipleImportZone();
      return;
    }

    const requestId = ++lastParticipleRequestId;
    const response = await fetch(`${participleSuggestionsUrl}?q=${encodeURIComponent(term)}`);
    if (!response.ok) {
      hideParticipleSuggestions();
      hideParticipleImportZone();
      return;
    }

    const payload = await response.json();
    if (requestId !== lastParticipleRequestId) return;
    renderParticipleSuggestions(Array.isArray(payload) ? payload.slice(0, 5) : []);
  }

  function getCookie(name) {
    const cookieValue = document.cookie
      .split(";")
      .map((item) => item.trim())
      .find((cookie) => cookie.startsWith(`${name}=`));

    if (!cookieValue) return "";
    return decodeURIComponent(cookieValue.split("=")[1]);
  }

  async function importIngredientFromApi(term, button) {
    if (!importUrl) return;

    button.disabled = true;
    const originalLabel = button.textContent;
    button.textContent = "Importando...";
    showMessage(`Importando "${term}" desde API USDA...`);

    try {
      const response = await fetch(importUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken") || csrfTokenFromTemplate,
        },
        body: JSON.stringify({ query: term }),
      });

      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.detail || "No se pudo importar el ingrediente");
      }

      const ingredient = payload.ingredient;
      if (!ingredient) throw new Error("Respuesta invalida del servidor");

      selectSuggestion({ id: ingredient.source_id, name: ingredient.name });
      showMessage(
        payload.status === "created"
          ? `Ingrediente importado: ${ingredient.name}`
          : `Ingrediente ya existente: ${ingredient.name}`
      );
      showIngredientDetail(ingredient.source_id, ingredient.name);
    } catch (error) {
      showMessage(error.message || "No se pudo importar desde API");
    } finally {
      button.disabled = false;
      button.textContent = originalLabel;
    }
  }

  function renderImportAction(term) {
    if (!importZone || !importUrl || !term) return;

    importZone.innerHTML = "";
    const label = document.createElement("span");
    label.className = "import-empty-label";
    label.textContent = "No hay coincidencias locales.";

    const button = document.createElement("button");
    button.type = "button";
    button.className = "import-api-btn";
    button.textContent = `Añadir "${term}" desde API`;
    button.addEventListener("click", () => importIngredientFromApi(term, button));

    importZone.appendChild(label);
    importZone.appendChild(button);
    importZone.hidden = false;
  }

  async function addCulinaryUnit(term, button) {
    if (!unitAddUrl || !unitSelectedIdInput) return;

    button.disabled = true;
    const original = button.textContent;
    button.textContent = "Guardando...";
    showMessage(`Añadiendo medida culinaria "${term}"...`);

    try {
      const response = await fetch(unitAddUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken") || csrfTokenFromTemplate,
        },
        body: JSON.stringify({ name: term }),
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.detail || "No se pudo añadir la medida culinaria");
      }

      const unit = payload.unit;
      if (!unit) throw new Error("Respuesta invalida del servidor");
      selectUnitSuggestion(unit);
      showMessage(
        payload.status === "created"
          ? `Medida culinaria añadida: ${unit.name}`
          : `Medida culinaria existente: ${unit.name}`
      );
    } catch (error) {
      showMessage(error.message || "No se pudo añadir la medida culinaria");
    } finally {
      button.disabled = false;
      button.textContent = original;
    }
  }

  async function addCulinaryAction(term, button) {
    if (!actionAddUrl || !actionSelectedIdInput) return;

    button.disabled = true;
    const original = button.textContent;
    button.textContent = "Guardando...";
    showMessage(`Añadiendo accion culinaria "${term}"...`);

    try {
      const response = await fetch(actionAddUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken") || csrfTokenFromTemplate,
        },
        body: JSON.stringify({ name: term }),
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.detail || "No se pudo añadir la accion culinaria");
      }

      const action = payload.action;
      if (!action) throw new Error("Respuesta invalida del servidor");
      selectActionSuggestion(action);
      showMessage(
        payload.status === "created"
          ? `Accion culinaria añadida: ${action.name}`
          : `Accion culinaria existente: ${action.name}`
      );
    } catch (error) {
      showMessage(error.message || "No se pudo añadir la accion culinaria");
    } finally {
      button.disabled = false;
      button.textContent = original;
    }
  }

  async function addCulinaryParticiple(term, button) {
    if (!participleAddUrl || !participleSelectedIdInput) return;

    button.disabled = true;
    const original = button.textContent;
    button.textContent = "Guardando...";
    showMessage(`Añadiendo participio "${term}"...`);

    try {
      const response = await fetch(participleAddUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken") || csrfTokenFromTemplate,
        },
        body: JSON.stringify({ name: term }),
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.detail || "No se pudo añadir el participio");
      }

      const participle = payload.participle;
      if (!participle) throw new Error("Respuesta invalida del servidor");
      selectParticipleSuggestion(participle);
      showMessage(
        payload.status === "created"
          ? `Participio añadido: ${participle.name}`
          : `Participio existente: ${participle.name}`
      );
    } catch (error) {
      showMessage(error.message || "No se pudo añadir el participio");
    } finally {
      button.disabled = false;
      button.textContent = original;
    }
  }

  function renderUnitImportAction(term) {
    if (!unitImportZone || !unitAddUrl || !term) return;
    unitImportZone.innerHTML = "";

    const label = document.createElement("span");
    label.className = "import-empty-label";
    label.textContent = "No hay medidas locales.";

    const button = document.createElement("button");
    button.type = "button";
    button.className = "import-api-btn";
    button.textContent = `Añadir medida culinaria "${term}"`;
    button.addEventListener("click", () => addCulinaryUnit(term, button));

    unitImportZone.appendChild(label);
    unitImportZone.appendChild(button);
    unitImportZone.hidden = false;
  }

  function renderActionImportAction(term) {
    if (!actionImportZone || !actionAddUrl || !term) return;
    actionImportZone.innerHTML = "";

    const label = document.createElement("span");
    label.className = "import-empty-label";
    label.textContent = "No hay acciones locales.";

    const button = document.createElement("button");
    button.type = "button";
    button.className = "import-api-btn";
    button.textContent = `Añadir accion culinaria "${term}"`;
    button.addEventListener("click", () => addCulinaryAction(term, button));

    actionImportZone.appendChild(label);
    actionImportZone.appendChild(button);
    actionImportZone.hidden = false;
  }

  function renderParticipleImportAction(term) {
    if (!participleImportZone || !participleAddUrl || !term) return;
    participleImportZone.innerHTML = "";

    const label = document.createElement("span");
    label.className = "import-empty-label";
    label.textContent = "No hay participios locales.";

    const button = document.createElement("button");
    button.type = "button";
    button.className = "import-api-btn";
    button.textContent = `Añadir participio "${term}"`;
    button.addEventListener("click", () => addCulinaryParticiple(term, button));

    participleImportZone.appendChild(label);
    participleImportZone.appendChild(button);
    participleImportZone.hidden = false;
  }

  function capitalizeFirst(value) {
    if (!value) return value;
    return value.charAt(0).toUpperCase() + value.slice(1);
  }

  function durationLabel(value, unit) {
    if (unit === "sg") {
      return value === 1 ? "segundo" : "segundos";
    }
    if (unit === "horas") {
      return value === 1 ? "hora" : "horas";
    }
    return value === 1 ? "minuto" : "minutos";
  }

  function singularizeUnit(unit) {
    const trimmed = (unit || "").trim();
    if (!trimmed) return trimmed;
    const lower = trimmed.toLowerCase();
    if (["ml", "cl", "dl", "l", "g", "kg", "mg"].includes(lower)) return trimmed;
    if (!lower.endsWith("s")) return trimmed;
    return trimmed.slice(0, -1);
  }

  function quantityWithUnit(qty, unit) {
    const qtyText = qty.toLocaleString("es-ES");
    const unitText = qty === 1 ? singularizeUnit(unit) : unit;
    return `${qtyText} ${unitText}`;
  }

  actionInput.addEventListener("input", () => {
    const term = actionInput.value.trim();
    actionSelectedIdInput.value = "";
    hideActionImportZone();

    clearTimeout(actionDebounceTimer);
    actionDebounceTimer = setTimeout(() => {
      fetchActionSuggestions(term);
    }, 220);
  });

  actionInput.addEventListener("focus", () => {
    const term = actionInput.value.trim();
    if (term) fetchActionSuggestions(term);
  });

  actionInput.addEventListener("keydown", (event) => {
    if (event.key === "ArrowDown") {
      if (!currentActionResults.length) return;
      event.preventDefault();
      const nextIndex =
        activeActionSuggestionIndex + 1 >= currentActionResults.length ? 0 : activeActionSuggestionIndex + 1;
      setActiveActionSuggestion(nextIndex);
      return;
    }

    if (event.key === "ArrowUp") {
      if (!currentActionResults.length) return;
      event.preventDefault();
      const prevIndex =
        activeActionSuggestionIndex - 1 < 0 ? currentActionResults.length - 1 : activeActionSuggestionIndex - 1;
      setActiveActionSuggestion(prevIndex);
      return;
    }

    if (event.key === "Enter") {
      if (!currentActionResults.length) return;
      event.preventDefault();
      const chosenIndex = activeActionSuggestionIndex >= 0 ? activeActionSuggestionIndex : 0;
      selectActionSuggestion(currentActionResults[chosenIndex]);
      return;
    }

    if (event.key === "Escape") hideActionSuggestions();
  });

  searchInput.addEventListener("input", () => {
    const term = searchInput.value.trim();
    selectedIdInput.value = "";
    hideImportZone();

    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      fetchSuggestions(term);
    }, 220);
  });

  searchInput.addEventListener("focus", () => {
    const term = searchInput.value.trim();
    if (term) fetchSuggestions(term);
  });

  searchInput.addEventListener("keydown", (event) => {
    if (event.key === "ArrowDown") {
      if (!currentResults.length) return;
      event.preventDefault();
      const nextIndex = activeSuggestionIndex + 1 >= currentResults.length ? 0 : activeSuggestionIndex + 1;
      setActiveSuggestion(nextIndex);
      return;
    }

    if (event.key === "ArrowUp") {
      if (!currentResults.length) return;
      event.preventDefault();
      const prevIndex = activeSuggestionIndex - 1 < 0 ? currentResults.length - 1 : activeSuggestionIndex - 1;
      setActiveSuggestion(prevIndex);
      return;
    }

    if (event.key === "Enter") {
      if (!currentResults.length) return;
      event.preventDefault();
      const chosenIndex = activeSuggestionIndex >= 0 ? activeSuggestionIndex : 0;
      selectSuggestion(currentResults[chosenIndex]);
      return;
    }

    if (event.key === "Escape") hideSuggestions();
  });

  participleInput.addEventListener("input", () => {
    const term = participleInput.value.trim();
    participleSelectedIdInput.value = "";
    hideParticipleImportZone();

    clearTimeout(participleDebounceTimer);
    participleDebounceTimer = setTimeout(() => {
      fetchParticipleSuggestions(term);
    }, 220);
  });

  participleInput.addEventListener("focus", () => {
    const term = participleInput.value.trim();
    if (term) fetchParticipleSuggestions(term);
  });

  participleInput.addEventListener("keydown", (event) => {
    if (event.key === "ArrowDown") {
      if (!currentParticipleResults.length) return;
      event.preventDefault();
      const nextIndex =
        activeParticipleSuggestionIndex + 1 >= currentParticipleResults.length
          ? 0
          : activeParticipleSuggestionIndex + 1;
      setActiveParticipleSuggestion(nextIndex);
      return;
    }

    if (event.key === "ArrowUp") {
      if (!currentParticipleResults.length) return;
      event.preventDefault();
      const prevIndex =
        activeParticipleSuggestionIndex - 1 < 0
          ? currentParticipleResults.length - 1
          : activeParticipleSuggestionIndex - 1;
      setActiveParticipleSuggestion(prevIndex);
      return;
    }

    if (event.key === "Enter") {
      if (!currentParticipleResults.length) return;
      event.preventDefault();
      const chosenIndex = activeParticipleSuggestionIndex >= 0 ? activeParticipleSuggestionIndex : 0;
      selectParticipleSuggestion(currentParticipleResults[chosenIndex]);
      return;
    }

    if (event.key === "Escape") hideParticipleSuggestions();
  });

  if (unitSelect) {
    unitSelect.addEventListener("input", () => {
      const term = unitSelect.value.trim();
      if (unitSelectedIdInput) unitSelectedIdInput.value = "";
      hideUnitImportZone();

      clearTimeout(unitDebounceTimer);
      unitDebounceTimer = setTimeout(() => {
        fetchUnitSuggestions(term);
      }, 220);
    });

    unitSelect.addEventListener("focus", () => {
      const term = unitSelect.value.trim();
      if (term) fetchUnitSuggestions(term);
    });

    unitSelect.addEventListener("keydown", (event) => {
      if (event.key === "ArrowDown") {
        if (!currentUnitResults.length) return;
        event.preventDefault();
        const nextIndex =
          activeUnitSuggestionIndex + 1 >= currentUnitResults.length ? 0 : activeUnitSuggestionIndex + 1;
        setActiveUnitSuggestion(nextIndex);
        return;
      }

      if (event.key === "ArrowUp") {
        if (!currentUnitResults.length) return;
        event.preventDefault();
        const prevIndex =
          activeUnitSuggestionIndex - 1 < 0 ? currentUnitResults.length - 1 : activeUnitSuggestionIndex - 1;
        setActiveUnitSuggestion(prevIndex);
        return;
      }

      if (event.key === "Enter") {
        if (!currentUnitResults.length) return;
        event.preventDefault();
        const chosenIndex = activeUnitSuggestionIndex >= 0 ? activeUnitSuggestionIndex : 0;
        selectUnitSuggestion(currentUnitResults[chosenIndex]);
        return;
      }

      if (event.key === "Escape") hideUnitSuggestions();
    });
  }

  if (qtyInput) {
    qtyInput.addEventListener("input", () => {
      const value = Number(qtyInput.value);
      if (!Number.isNaN(value) && value > 10000) {
        showMessage("La cantidad maxima permitida es 10000.");
      }
    });
  }

  document.addEventListener("click", (event) => {
    if (
      !suggestionsList.contains(event.target) &&
      event.target !== searchInput &&
      (!importZone || !importZone.contains(event.target))
    ) {
      hideSuggestions();
      hideImportZone();
    }

    if (
      unitSuggestionsList &&
      unitSelect &&
      !unitSuggestionsList.contains(event.target) &&
      event.target !== unitSelect &&
      (!unitImportZone || !unitImportZone.contains(event.target))
    ) {
      hideUnitSuggestions();
      hideUnitImportZone();
    }

    if (
      !actionSuggestionsList.contains(event.target) &&
      event.target !== actionInput &&
      (!actionImportZone || !actionImportZone.contains(event.target))
    ) {
      hideActionSuggestions();
      hideActionImportZone();
    }

    if (
      !participleSuggestionsList.contains(event.target) &&
      event.target !== participleInput &&
      (!participleImportZone || !participleImportZone.contains(event.target))
    ) {
      hideParticipleSuggestions();
      hideParticipleImportZone();
    }
  });

  addBtn.addEventListener("click", () => {
    const actionName = actionInput.value.trim();
    const actionId = actionSelectedIdInput.value.trim();
    const durationValueRaw = durationValueInput ? durationValueInput.value.trim() : "";
    const durationValue = Number(durationValueRaw);
    const durationUnit = durationUnitSelect ? durationUnitSelect.value : "sg";

    const ingredientName = searchInput.value.trim();
    const ingredientId = selectedIdInput.value.trim();
    const participleName = participleInput.value.trim();
    const participleId = participleSelectedIdInput.value.trim();
    const qtyRaw = qtyInput ? qtyInput.value.trim() : "";
    const qty = Number(qtyRaw);
    const unit = unitSelect ? unitSelect.value.trim() : "";
    const unitId = unitSelectedIdInput ? unitSelectedIdInput.value.trim() : "";

    if (!actionName || !actionId) {
      showMessage("Selecciona una accion culinaria desde las sugerencias.");
      return;
    }
    if (!durationValueRaw || Number.isNaN(durationValue) || durationValue < 0) {
      showMessage("Introduce una duracion valida para la accion.");
      return;
    }
    if (!ingredientName || !ingredientId) {
      showMessage("Selecciona un ingrediente desde las sugerencias.");
      return;
    }
    if (!participleName || !participleId) {
      showMessage("Selecciona un participio desde las sugerencias o añadelo.");
      return;
    }
    if (!qtyRaw || Number.isNaN(qty) || qty <= 0) {
      showMessage("Introduce una cantidad numerica valida.");
      return;
    }
    if (qty > 10000) {
      showMessage("La cantidad maxima permitida es 10000.");
      return;
    }
    if (!unit || !unitId) {
      showMessage("Selecciona una medida culinaria desde las sugerencias o añadela.");
      return;
    }

    const cardEl = document.createElement("article");
    cardEl.className = "ingredient-card entering";
    cardEl.dataset.sourceId = ingredientId;
    cardEl.dataset.ingredientName = ingredientName;

    const nameEl = document.createElement("span");
    nameEl.className = "name";
    const durationText = durationValue.toLocaleString("es-ES");
    const normalizedDurationUnit = durationLabel(durationValue, durationUnit);
    const quantityText = quantityWithUnit(qty, unit);
    nameEl.textContent = `${capitalizeFirst(actionName)} ${quantityText} de ${ingredientName} ${participleName} durante ${durationText} ${normalizedDurationUnit}.`;

    const actionsEl = document.createElement("div");
    actionsEl.className = "card-actions";

    const deleteBtn = document.createElement("button");
    deleteBtn.type = "button";
    deleteBtn.className = "info-btn";
    deleteBtn.textContent = "Eliminar paso";

    actionsEl.appendChild(deleteBtn);
    cardEl.appendChild(nameEl);
    cardEl.appendChild(actionsEl);
    pickedGrid.appendChild(cardEl);
    cardEl.addEventListener(
      "animationend",
      () => {
        cardEl.classList.remove("entering");
      },
      { once: true }
    );

    actionInput.value = "";
    actionSelectedIdInput.value = "";
    if (durationValueInput) durationValueInput.value = "";

    searchInput.value = "";
    selectedIdInput.value = "";
    participleInput.value = "";
    participleSelectedIdInput.value = "";
    if (qtyInput) qtyInput.value = "";
    if (unitSelect) unitSelect.value = "";
    if (unitSelectedIdInput) unitSelectedIdInput.value = "";

    hideActionSuggestions();
    hideSuggestions();
    hideParticipleSuggestions();
    hideUnitSuggestions();
    showMessage(`Paso añadido: ${actionName}`);
    actionInput.focus();
  });

  if (pickedGrid) {
    pickedGrid.addEventListener("click", (event) => {
      const target = event.target;
      if (!(target instanceof HTMLElement) || !target.classList.contains("info-btn")) return;
      const cardEl = target.closest(".ingredient-card");
      if (!cardEl) return;
      cardEl.remove();
      showMessage("Paso eliminado.");
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
