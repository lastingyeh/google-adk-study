document.addEventListener('DOMContentLoaded', () => {
  // Global state
  let learningData = [];
  const GROUP_SIZE = 20;

  // DOM Elements
  const container = document.getElementById('dashboard-container');
  const modal = document.getElementById('detail-modal');
  const modalTitle = document.getElementById('modal-title');
  const modalDescription = document.getElementById('modal-description');
  const modalDocsLinks = document.getElementById('modal-docs-links');
  const modalRefsLinks = document.getElementById('modal-refs-links');
  const modalDocsContainer = document.getElementById(
    'modal-docs-links-container'
  );
  const modalRefsContainer = document.getElementById(
    'modal-refs-links-container'
  );
  const searchInput = document.getElementById('search-input');
  const resetButton = document.getElementById('reset-button');
  const completedCountElement = document.getElementById('completed-count');
  const daysElement = document.getElementById('days');
  const cardViewBtn = document.getElementById('card-view-btn');
  const listViewBtn = document.getElementById('list-view-btn');

  // Main function to fetch data and initialize the app
  async function main() {
    try {
      const response = await fetch('data/learningData.json');
      if (!response.ok) throw new Error('Network response was not ok');
      learningData = await response.json();
      initializeApp();
    } catch (error) {
      console.error('Failed to load learning data:', error);
      container.innerHTML = '<p class="text-center text-red-400">Failed to load learning data. Please try again later.</p>';
    }
  }

  function initializeApp() {
    if (daysElement) {
      daysElement.textContent = `累積天數：${learningData.length} 天`;
    }

    const savedProgress = JSON.parse(localStorage.getItem('adkLearningProgress')) || {};
    learningData.forEach((day) => {
      if (savedProgress.hasOwnProperty(day.day)) {
        day.completed = savedProgress[day.day];
      }
    });

    updateCompletedCount();
    renderGroups();
    setupEventListeners();

    const savedViewMode = localStorage.getItem('adkViewMode');
    if (savedViewMode) {
      setView(savedViewMode);
    }
  }

  function updateCompletedCount() {
    const completedCount = learningData.filter((d) => d.completed).length;
    if (completedCountElement) {
      completedCountElement.textContent = `已完成：${completedCount} 天`;
    }
  }

  function createCard(day) {
    const isCompleted = day.completed;

    const card = document.createElement('div');
    card.className = `day-card bg-gray-800 p-5 rounded-lg transition-all duration-300 ease-in-out transform hover:-translate-y-1 card-shadow cursor-pointer flex flex-col justify-between ${
      isCompleted ? 'completed' : ''
    }`;
    card.dataset.day = day.day;

    const cardContent = document.createElement('div');
    cardContent.onclick = () => openModal(day.day);

    const cardHeader = document.createElement('div');
    cardHeader.className = 'flex justify-between items-center mb-3';
    const dayBadge = document.createElement('span');
    dayBadge.className =
      'bg-blue-500/10 text-blue-400 border border-blue-500/20 text-xs font-bold px-3 py-1 rounded-full backdrop-blur-sm';
    dayBadge.textContent = `Day ${day.day}`;
    cardHeader.appendChild(dayBadge);

    const title = document.createElement('h2');
    title.className = 'day-title text-lg font-semibold text-white mb-2';
    title.textContent = day.title;

    const description = document.createElement('p');
    description.className = 'text-sm text-gray-400 line-clamp-3';
    description.textContent = day.description;

    cardContent.appendChild(cardHeader);
    cardContent.appendChild(title);
    cardContent.appendChild(description);

    const labelsContainer = document.createElement('div');
    labelsContainer.className = 'mt-4 flex flex-wrap gap-2';
    if (day.labels && day.labels.length > 0) {
      day.labels.forEach((label) => {
        const labelBadge = document.createElement('span');
        labelBadge.className =
          'bg-gray-800/80 border border-gray-700 text-gray-400 text-xs font-medium px-2.5 py-1 rounded-full hover:border-gray-500 hover:text-gray-200 transition-colors';
        labelBadge.textContent = label;
        labelsContainer.appendChild(labelBadge);
      });
    }
    cardContent.appendChild(labelsContainer);

    const cardFooter = document.createElement('div');
    cardFooter.className =
      'mt-4 pt-4 border-t border-gray-700 flex items-center justify-end';

    const completionContainer = document.createElement('div');
    completionContainer.className = 'flex items-center gap-2';

    const completionText = document.createElement('span');
    completionText.className = 'text-sm text-gray-400';
    completionText.textContent = '已完成';

    const checkboxLabel = document.createElement('label');
    checkboxLabel.className = 'google-switch';

    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.checked = isCompleted;
    checkbox.onchange = (e) => {
      e.stopPropagation();
      toggleComplete(day.day, e.target.checked);
    };

    const slider = document.createElement('span');
    slider.className = 'slider';

    checkboxLabel.appendChild(checkbox);
    checkboxLabel.appendChild(slider);

    completionContainer.appendChild(completionText);
    completionContainer.appendChild(checkboxLabel);

    cardFooter.appendChild(completionContainer);

    card.appendChild(cardContent);
    card.appendChild(cardFooter);

    return card;
  }

  function createGridElement() {
    const el = document.createElement('div');
    el.className = 'dashboard-grid grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 md:gap-6';

    if (localStorage.getItem('adkViewMode') === 'list') {
      el.classList.add('list-view');
    }
    return el;
  }

  function renderGroups() {
    container.innerHTML = '';

    const groups = [];
    for (let i = 0; i < learningData.length; i += GROUP_SIZE) {
      groups.push(learningData.slice(i, i + GROUP_SIZE));
    }

    groups.forEach((groupItems, index) => {
      const groupStart = index * GROUP_SIZE + 1;
      const groupEnd = Math.min((index + 1) * GROUP_SIZE, learningData.length);

      const groupContainer = document.createElement('div');
      groupContainer.className = 'group-section bg-[#1e293b] rounded-2xl border border-gray-700/50 overflow-hidden shadow-lg transition-all duration-300 hover:border-gray-600';

      const header = document.createElement('button');
      header.className = 'w-full flex items-center justify-between p-5 bg-[#1e293b] hover:bg-[#2d3748] transition-all duration-300 group-header focus:outline-none relative';

      const completedInGroup = groupItems.filter(d => d.completed).length;
      const totalInGroup = groupItems.length;
      const progressPercent = totalInGroup > 0 ? Math.round((completedInGroup / totalInGroup) * 100) : 0;

      header.innerHTML = `
          <div class="flex items-center gap-4">
              <div class="flex items-center justify-center w-10 h-10 rounded-full bg-blue-500/10 text-blue-400 ring-1 ring-blue-500/20 shadow-[0_0_10px_rgba(59,130,246,0.1)]">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                     <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                  </svg>
              </div>
              <div class="text-left">
                  <h3 class="text-lg font-bold text-gray-100 tracking-tight group-hover:text-blue-400 transition-colors">Day ${groupStart} - ${groupEnd}</h3>
                  <div class="flex items-center gap-2 mt-1">
                       <div class="h-1.5 w-24 bg-gray-700 rounded-full overflow-hidden">
                           <div class="h-full bg-gradient-to-r from-blue-400 to-blue-500 rounded-full" style="width: ${progressPercent}%"></div>
                       </div>
                       <span class="text-xs text-gray-400 font-medium">${progressPercent}% 完成</span>
                  </div>
              </div>
          </div>
          <div class="flex items-center justify-center w-8 h-8 rounded-full bg-gray-800 border border-gray-700 text-gray-400 transition-all duration-300 group-hover:border-gray-500 group-hover:text-white icon-container">
              <svg class="w-5 h-5 transform transition-transform duration-300 rotate-180" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
              </svg>
          </div>
      `;

      const contentWrapper = document.createElement('div');
      contentWrapper.className = 'group-content collapsed';
      let isOpen = false;

      header.onclick = () => {
          isOpen = !isOpen;
          const icon = header.querySelector('.icon-container svg');

          header.classList.toggle('is-open', isOpen);
          contentWrapper.classList.toggle('collapsed', !isOpen);

          if (icon) {
            icon.classList.toggle('rotate-180', !isOpen);
          }
      };

      const grid = createGridElement();
      groupItems.forEach(day => {
          const card = createCard(day);
          grid.appendChild(card);
      });
      const gridPadding = document.createElement('div');
      gridPadding.className = 'p-4 md:p-6';
      gridPadding.appendChild(grid);

      contentWrapper.appendChild(gridPadding);
      groupContainer.appendChild(header);
      groupContainer.appendChild(contentWrapper);
      container.appendChild(groupContainer);
    });
  }

  function openModal(dayNum) {
    const dayData = learningData.find((d) => d.day === dayNum);
    if (!dayData) return;

    modalTitle.textContent = `Day ${dayData.day}: ${dayData.title}`;
    modalDescription.textContent = dayData.description;

    modalDocsLinks.innerHTML = '';
    modalRefsLinks.innerHTML = '';

    if (dayData.docs && dayData.docs.length > 0) {
      modalDocsContainer.style.display = 'block';
      dayData.docs.forEach((link) => {
        const li = document.createElement('li');
        const a = document.createElement('a');
        a.href = link.url;
        a.textContent = link.text;
        a.target = '_blank';
        a.rel = 'noopener noreferrer';
        a.className = 'text-blue-400 hover:text-blue-300 hover:underline';
        li.appendChild(a);
        modalDocsLinks.appendChild(li);
      });
    } else {
      modalDocsContainer.style.display = 'none';
    }

    if (dayData.refs && dayData.refs.length > 0) {
      modalRefsContainer.style.display = 'block';
      dayData.refs.forEach((link) => {
        const li = document.createElement('li');
        const a = document.createElement('a');
        a.href = link.url;
        a.textContent = link.text;
        a.target = '_blank';
        a.rel = 'noopener noreferrer';
        a.className =
          'text-purple-400 hover:text-purple-300 hover:underline';
        li.appendChild(a);
        modalRefsLinks.appendChild(li);
      });
    } else {
      modalRefsContainer.style.display = 'none';
    }

    modal.classList.add('flex');
    document.body.style.overflow = 'hidden';
  }

  function closeModal() {
    modal.classList.remove('flex');
    document.body.style.overflow = 'auto';
  }

  function updateGroupProgress(groupIndex) {
    const startIdx = groupIndex * GROUP_SIZE;
    const endIdx = Math.min(startIdx + GROUP_SIZE, learningData.length);
    const groupItems = learningData.slice(startIdx, endIdx);
    const completedInGroup = groupItems.filter(d => d.completed).length;
    const totalInGroup = groupItems.length;
    if (totalInGroup === 0) return;
    const progressPercent = Math.round((completedInGroup / totalInGroup) * 100);
    const groups = document.querySelectorAll('.group-section');
    const groupElement = groups[groupIndex];
    if (groupElement) {
         const header = groupElement.querySelector('.group-header');
         if (header) {
             const progressBar = header.querySelector('.h-full.bg-gradient-to-r');
             const progressText = header.querySelector('.text-xs.text-gray-400.font-medium');
             if (progressBar) progressBar.style.width = `${progressPercent}%`;
             if (progressText) progressText.textContent = `${progressPercent}% 完成`;
         }
    }
  }

  function toggleComplete(dayNum, isCompleted) {
    const card = document.querySelector(`.day-card[data-day='${dayNum}']`);
    if (card) {
      card.classList.toggle('completed', isCompleted);
    }
    const dataIndex = learningData.findIndex((d) => d.day === dayNum);
    if (dataIndex !== -1) {
      learningData[dataIndex].completed = isCompleted;
      updateCompletedCount();
      const groupIndex = Math.floor(dataIndex / GROUP_SIZE);
      updateGroupProgress(groupIndex);
    }
    const progressToSave = {};
    learningData.forEach((d) => {
      progressToSave[d.day] = d.completed;
    });
    localStorage.setItem(
      'adkLearningProgress',
      JSON.stringify(progressToSave)
    );
  }

  function showAllCards() {
    const cards = document.querySelectorAll('.day-card');
    cards.forEach((card) => {
      card.style.display = 'flex';
    });
    const groups = document.querySelectorAll('.group-section');
    groups.forEach(group => {
         group.style.display = 'block';
    });
  }

  function filterCards(searchTerm) {
    const lowerCaseSearchTerm = searchTerm.toLowerCase();
    const isSearching = searchTerm.length >= 2;
    const groups = document.querySelectorAll('.group-section');
    groups.forEach(group => {
        let hasVisibleCards = false;
        const cards = group.querySelectorAll('.day-card');
        cards.forEach(card => {
            const title = card.querySelector('.day-title').textContent.toLowerCase();
            const description = card.querySelector('p').textContent.toLowerCase();
            const labels = Array.from(card.querySelectorAll('.bg-gray-700, .bg-gray-800\\/80')).map(
                (label) => label.textContent.toLowerCase()
            );
            if (
                title.includes(lowerCaseSearchTerm) ||
                description.includes(lowerCaseSearchTerm) ||
                labels.some((label) => label.includes(lowerCaseSearchTerm))
            ) {
                card.style.display = 'flex';
                hasVisibleCards = true;
            } else {
                card.style.display = 'none';
            }
        });
        if (isSearching) {
             group.style.display = hasVisibleCards ? 'block' : 'none';
             if (hasVisibleCards) {
                 const content = group.querySelector('.group-content');
                 const icon = group.querySelector('.icon-container svg');
                 content.classList.remove('collapsed');
                 if (icon) icon.classList.remove('rotate-180');
             }
        } else {
            group.style.display = hasVisibleCards ? 'block' : 'none';
        }
    });
  }

  function setView(mode) {
    const grids = document.querySelectorAll('.dashboard-grid');
    grids.forEach(grid => {
        grid.classList.toggle('list-view', mode === 'list');
    });

    if (listViewBtn && cardViewBtn) {
        listViewBtn.classList.toggle('text-blue-400', mode === 'list');
        listViewBtn.classList.toggle('bg-blue-500/10', mode === 'list');
        listViewBtn.classList.toggle('text-gray-500', mode !== 'list');
        cardViewBtn.classList.toggle('text-blue-400', mode !== 'list');
        cardViewBtn.classList.toggle('bg-blue-500/10', mode !== 'list');
        cardViewBtn.classList.toggle('text-gray-500', mode === 'list');
    }

    localStorage.setItem('adkViewMode', mode);
  }

  function setupEventListeners() {
    modal.addEventListener('click', (event) => {
      if (event.target === modal) {
        closeModal();
      }
    });

    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') {
        closeModal();
      }
    });

    searchInput.addEventListener('input', () => {
      const searchTerm = searchInput.value.trim();
      if (searchTerm.length >= 2) {
        filterCards(searchTerm);
      } else {
        showAllCards();
      }
    });

    resetButton.addEventListener('click', () => {
      searchInput.value = '';
      showAllCards();
    });

    cardViewBtn.addEventListener('click', () => setView('card'));
    listViewBtn.addEventListener('click', () => setView('list'));
  }

  // Start the app
  main();
});
