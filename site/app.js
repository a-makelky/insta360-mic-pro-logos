const grid = document.querySelector("#grid");
const searchInput = document.querySelector("#search");
const categorySelect = document.querySelector("#category");

let logos = [];

function option(label) {
  const el = document.createElement("option");
  el.value = label;
  el.textContent = label;
  return el;
}

function card(entry) {
  const article = document.createElement("article");
  article.className = "card";
  article.innerHTML = `
    <div class="preview">
      <div class="mic-screen">
        <img src="../${entry.files.color}" alt="${entry.name} color logo preview" loading="lazy" />
      </div>
    </div>
    <div class="card-body">
      <h2>${entry.name}</h2>
      <p class="meta">${entry.category} · 240 x 208 transparent PNG</p>
      <div class="downloads">
        <a href="../${entry.files.color}" download>Color</a>
        <a href="../${entry.files.mono}" download>High contrast</a>
      </div>
    </div>
  `;
  return article;
}

function render() {
  const query = searchInput.value.trim().toLowerCase();
  const category = categorySelect.value;
  const filtered = logos.filter((entry) => {
    const matchesQuery = !query || entry.name.toLowerCase().includes(query) || entry.slug.includes(query);
    const matchesCategory = !category || entry.category === category;
    return matchesQuery && matchesCategory;
  });

  grid.replaceChildren(...filtered.map(card));
}

async function init() {
  const response = await fetch("logos.json");
  logos = await response.json();
  const categories = [...new Set(logos.map((entry) => entry.category))].sort();
  categorySelect.append(...categories.map(option));
  searchInput.addEventListener("input", render);
  categorySelect.addEventListener("change", render);
  render();
}

init();
