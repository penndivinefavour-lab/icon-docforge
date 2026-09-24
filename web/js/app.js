// ICON DocForge - Main Application v1.0
// Architecture: Each tool is a self-contained IIFE module registered to window.DFRegistry
// Routing via hash-based navigation
// API communicates with conversion engine on localhost:8765

(function () {
  'use strict';

  const API_BASE = 'http://127.0.0.1:8765/api';

  // --- Categories ---
  const CATEGORIES = [
    { id: 'all', name: 'All', icon: '◯' },
    { id: 'documents', name: 'Documents', icon: '📄' },
    { id: 'pdf', name: 'PDF', icon: '📑' },
    { id: 'presentations', name: 'Presentations', icon: '📊' },
    { id: 'images', name: 'Images', icon: '🖼' },
    { id: 'spreadsheets', name: 'Spreadsheets', icon: '📊' },
    { id: 'tools', name: 'Tools', icon: '🔧' }
  ];

  // --- Tools Registry ---
  const TOOLS = [
    { id: 'dashboard', name: 'Dashboard', desc: 'Overview & stats', icon: '🏠', category: 'all', tag: 'Home' },
    { id: 'image-to-pdf', name: 'Images → PDF', desc: 'Create PDF from images', icon: '🖼→📄', category: 'images', tag: 'Images' },
    { id: 'pdf-merge', name: 'PDF Merge', desc: 'Combine PDFs', icon: '📄+📄→📄', category: 'pdf', tag: 'PDF' },
    { id: 'pdf-split', name: 'PDF Split', desc: 'Extract pages', icon: '📄→📄+📄', category: 'pdf', tag: 'PDF' },
    { id: 'pdf-rotate', name: 'PDF Rotate', desc: 'Rotate pages', icon: '🔄📄', category: 'pdf', tag: 'PDF' },
    { id: 'pdf-to-images', name: 'PDF → Images', desc: 'Extract as images', icon: '📄→🖼', category: 'pdf', tag: 'PDF' },
    { id: 'pdf-metadata', name: 'PDF Info', desc: 'View/edit metadata', icon: 'ℹ️📄', category: 'pdf', tag: 'PDF' },
    { id: 'docx-to-pdf', name: 'DOCX → PDF', desc: 'Word docs to PDF', icon: '📝→📄', category: 'documents', tag: 'Documents' },
    { id: 'markdown-to-pdf', name: 'MD → PDF', desc: 'Markdown to PDF', icon: '📝→📄', category: 'documents', tag: 'Documents' },
    { id: 'csv-xlsx', name: 'CSV ↔ XLSX', desc: 'Spreadsheet convert', icon: '📊↔📊', category: 'spreadsheets', tag: 'Spreadsheets' },
    { id: 'docx-odt', name: 'DOCX ↔ ODT', desc: 'Office format convert', icon: '📝↔📝', category: 'documents', tag: 'Documents' },
    { id: 'diagnostics', name: 'Diagnostics', desc: 'Engine health check', icon: '🔧', category: 'tools', tag: 'Tools' },
  ];

  // --- State ---
  let currentCategory = 'all';
  let searchQuery = '';
  let history = JSON.parse(localStorage.getItem('df-history') || '[]');
  let favorites = JSON.parse(localStorage.getItem('df-favorites') || '[]');

  // --- DOM ---
  const $homeScreen = document.getElementById('home-screen');
  const $toolScreen = document.getElementById('tool-screen');
  const $detailScreen = document.getElementById('detail-screen');
  const $toolsGrid = document.getElementById('tools-grid');
  const $categoryFilters = document.getElementById('category-filters');
  const $searchInput = document.getElementById('search-input');

  // --- Navigation ---
  function navigate(screen) {
    window.location.hash = screen;
  }

  function handleRoute() {
    const hash = window.location.hash.replace('#', '') || 'dashboard';
    const [screen, toolId] = hash.split('/');

    $homeScreen.classList.remove('active');
    $toolScreen.classList.remove('active');
    $detailScreen.classList.remove('active');

    if (screen === 'tool' && toolId) {
      $toolScreen.classList.add('active');
      loadTool(toolId);
    } else if (screen === 'detail') {
      $detailScreen.classList.add('active');
    } else {
      $homeScreen.classList.add('active');
      renderDashboard();
    }
  }

  // --- Render Dashboard ---
  function renderDashboard() {
    // Category filters
    $categoryFilters.innerHTML = '';
    CATEGORIES.forEach(cat => {
      const chip = document.createElement('div');
      chip.className = 'cat-chip' + (cat.id === currentCategory ? ' active' : '');
      chip.textContent = cat.icon + ' ' + cat.name;
      chip.setAttribute('role', 'tab');
      chip.onclick = () => { currentCategory = cat.id; renderDashboard(); };
      $categoryFilters.appendChild(chip);
    });

    // Tools grid
    $toolsGrid.innerHTML = '';
    const filtered = TOOLS.filter(t => {
      const matchCat = currentCategory === 'all' || t.category === currentCategory;
      const matchSearch = !searchQuery || t.name.toLowerCase().includes(searchQuery) || t.desc.toLowerCase().includes(searchQuery);
      return matchCat && matchSearch;
    });

    filtered.forEach(tool => {
      const card = document.createElement('div');
      card.className = 'tool-card';
      card.innerHTML = `<div class="tool-card-icon">${tool.icon}</div><div class="tool-card-name">${tool.name}</div><div class="tool-card-desc">${tool.desc}</div>`;
      card.onclick = () => navigate('tool/' + tool.id);
      $toolsGrid.appendChild(card);
    });

    // Recent history
    if (history.length > 0) {
      const section = document.createElement('div');
      section.className = 'tool-section';
      section.innerHTML = '<h3>Recent Conversions</h3>';
      const grid = document.createElement('div');
      grid.style.cssText = 'display:grid;grid-template-columns:1fr;gap:8px;';
      history.slice(0, 5).forEach(h => {
        const item = document.createElement('div');
        item.className = 'history-item';
        item.innerHTML = `<div class="history-icon">${h.icon || '📄'}</div><div class="history-info"><div class="history-name">${h.name}</div><div class="history-date">${h.date || ''}</div></div>`;
        section.appendChild(item);
      });
      $toolsGrid.appendChild(section);
    }
  }

  // --- Load Tool ---
  function loadTool(toolId) {
    const tool = TOOLS.find(t => t.id === toolId);
    if (!tool) { navigate('dashboard'); return; }

    document.getElementById('tool-icon').textContent = tool.icon;
    document.getElementById('tool-title').textContent = tool.name;

    const toolBody = document.getElementById('tool-body');
    toolBody.innerHTML = '<div style="text-align:center;padding:40px"><div class="progress-bar"><div class="progress-fill" style="width:30%"></div></div><p class="progress-text">Loading ' + tool.name + '…</p></div>';

    // Dynamically load tool module
    const script = document.createElement('script');
    script.src = '/js/tools/' + toolId + '.js';
    script.onload = () => {
      if (window.DFRegistry && window.DFRegistry[toolId]) {
        try {
          const render = window.DFRegistry[toolId].render;
          const root = render();
          toolBody.innerHTML = '';
          toolBody.appendChild(root);
          if (window.DFRegistry[toolId].onMount) {
            window.DFRegistry[toolId].onMount(toolBody);
          }
        } catch(e) {
          toolBody.innerHTML = '<p class="tool-desc">Error loading tool: ' + e.message + '</p>';
        }
      } else {
        // Show placeholder if tool module not loaded yet
        showToolPlaceholder(toolId);
      }
    };
    script.onerror = () => showToolPlaceholder(toolId);
    document.head.appendChild(script);
  }

  function showToolPlaceholder(toolId) {
    const tool = TOOLS.find(t => t.id === toolId);
    const body = document.getElementById('tool-body');
    body.innerHTML = `
      <div class="tool-section">
        <h3>${tool ? tool.name : 'Tool'}</h3>
        <div class="drop-zone" id="drop-zone">
          <div class="drop-zone-icon">📁</div>
          <div class="drop-zone-text">Drop files here or tap to browse</div>
          <input type="file" id="file-input" style="display:none" multiple/>
        </div>
        <div style="margin-top:16px">
          <button class="btn btn-primary btn-block" id="convert-btn">Convert</button>
        </div>
        <p style="font-size:12px;color:var(--text-muted);margin-top:8px;text-align:center">
          🔒 All processing happens locally on your device
        </p>
      </div>
    `;
    // File picker
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    dropZone.onclick = () => fileInput.click();
    dropZone.ondragover = (e) => { e.preventDefault(); dropZone.classList.add('dragover'); };
    dropZone.ondragleave = () => dropZone.classList.remove('dragover');
    dropZone.ondrop = (e) => {
      e.preventDefault(); dropZone.classList.remove('dragover');
      const files = Array.from(e.dataTransfer.files);
      handleFiles(files);
    };
    fileInput.onchange = () => handleFiles(Array.from(fileInput.files));

    document.getElementById('convert-btn')?.addEventListener('click', () => {
      window.App.toast('Conversion started — check progress', 'info');
    });
  }

  function handleFiles(files) {
    if (files.length === 0) return;
    const names = files.map(f => f.name).join(', ');
    window.App.toast(`${files.length} file(s) selected`, 'success');
    const info = document.createElement('div');
    info.className = 'output-area';
    info.innerHTML = `<strong>Selected:</strong><br>${names}`;
    const dropZone = document.getElementById('drop-zone');
    if (dropZone) dropZone.after(info);
  }

  // --- API Communication ---
  async function apiCall(endpoint, data = null) {
    try {
      const opts = { method: 'POST', headers: { 'Content-Type': 'application/json' } };
      if (data) opts.body = JSON.stringify(data);
      const resp = await fetch(`${API_BASE}${endpoint}`, opts);
      return await resp.json();
    } catch(e) {
      return { success: false, error: 'Engine unavailable. Start the conversion service.' };
    }
  }

  // --- Toast ---
  function toast(msg, type = 'info') {
    const container = document.createElement('div');
    container.className = 'toast-container';
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = msg;
    container.appendChild(toast);
    document.body.appendChild(container);
    setTimeout(() => container.remove(), 3000);
  }

  // --- Back Button ---
  document.getElementById('back-btn')?.addEventListener('click', () => navigate('dashboard'));
  document.getElementById('detail-back')?.addEventListener('click', () => navigate('dashboard'));

  // --- Search ---
  $searchInput?.addEventListener('input', (e) => {
    searchQuery = e.target.value.toLowerCase();
    renderDashboard();
  });

  // --- History ---
  function addToHistory(entry) {
    history.unshift(entry);
    if (history.length > 20) history = history.slice(0, 20);
    localStorage.setItem('df-history', JSON.stringify(history));
  }

  // --- Init ---
  window.App = { toast, apiCall, addToHistory, navigate };

  window.addEventListener('hashchange', handleRoute);
  handleRoute();
})();
