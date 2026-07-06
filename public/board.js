function renderCards(data) {
  const container = document.getElementById('activity-grid');
  container.innerHTML = data.map(item => {
    const buttonsHTML = item.buttons.map(btn => `
      <a href="${btn.url}" class="inline-flex items-center gap-2 bg-white/40 hover:bg-white/80 border border-white/40 px-4 py-2 rounded-xl text-sm font-semibold text-neutral-800 transition-all active:scale-95">
        <i class="fa-solid ${btn.icon} text-primaryGreen"></i> ${btn.label}
      </a>
    `).join('');

    return `
    <div class="group bg-white/50 hover:bg-white/70 border border-white/20 p-6 rounded-[2rem] transition-all duration-300 shadow-sm">
      <div class="${item.badgeClass} text-[10px] font-bold px-3 py-1 rounded-full w-fit mb-4">
        ${item.category}
      </div>
            
      <h3 class="text-neutral-800 font-playfair text-2xl mb-2">${item.title}</h3>
        <p class="text-neutral-600 text-sm leading-relaxed mb-6">
          ${item.description}
        </p>

        <div class="flex flex-wrap gap-3">
          ${buttonsHTML}
        </div>
      </div>`;
    }
  ).join('');
}

getJSON("/boarddata.json").then((data) => renderCards(data));