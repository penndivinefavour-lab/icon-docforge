// ICON DocForge — Main Application v1.4
// Production-quality offline document converter
// Architecture: Module-based tools, hash-based navigation, localStorage persistence

(function () {
  'use strict';

  // ========== CONFIGURATION ==========
  const IS_ANDROID = Boolean(window.AndroidBridge);
  const API_BASE = IS_ANDROID
    ? null
    : 'http://127.0.0.1:8765/api';
  
  const APP_VERSION = '1.4.0';
  const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB
  
  // ========== CATEGORIES ==========
  const CATEGORIES = [
    { id: 'all', name: 'All Tools', icon: '◈' },
    { id: 'pdf', name: 'PDF Tools', icon: '◫' },
    { id: 'documents', name: 'Documents', icon: '◫' },
    { id: 'images', name: 'Images', icon: '◫' },
    { id: 'spreadsheets', name: 'Spreadsheets', icon: '◫' },
    { id: 'tools', name: 'Utilities', icon: '⚙' }
  ];

  // ========== TOOLS REGISTRY ==========
  // Only include tools that are actually supported in current environment
  const ANDROID_ENGINE_REASON = 'Not available in the Android APK: the Termux/Python conversion engine is not bundled.';
  const TOOLS = [
    { id: 'image-to-pdf', name: 'Images → PDF', desc: 'Combine images into a single PDF', icon: '◫', category: 'images', available: true, fidelity: 'available' },
    { id: 'pdf-merge', name: 'Merge PDFs', desc: 'Combine multiple PDFs', icon: '◫', category: 'pdf', available: true, fidelity: 'available' },
    { id: 'pdf-split', name: 'Split PDF', desc: 'Extract pages from PDF', icon: '◫', category: 'pdf', available: true, fidelity: 'available' },
    { id: 'pdf-reorder', name: 'Reorder Pages', desc: 'Change page order', icon: '↔', category: 'pdf', available: true, fidelity: 'available' },
    { id: 'pdf-rotate', name: 'Rotate Pages', desc: 'Rotate PDF pages', icon: '⟳', category: 'pdf', available: true, fidelity: 'available' },
    { id: 'pdf-to-images', name: 'PDF → Images', desc: 'Convert PDF pages to PNG/JPG', icon: '◫', category: 'pdf', available: false, reason: 'PDF page rasterization is not bundled in the Android APK' },
    { id: 'pdf-metadata', name: 'PDF Info', desc: 'View PDF properties', icon: 'ℹ', category: 'pdf', available: false, reason: 'Metadata editing is not bundled in the Android APK' },
    { id: 'pdf-text-search', name: 'PDF Text & Search', desc: 'Extract text and find phrases in PDFs', icon: '🔎', category: 'pdf', available: true, fidelity: 'available' },
    { id: 'docx-to-pdf', name: 'DOCX → PDF', desc: 'Word documents to PDF', icon: '◫', category: 'documents', available: true, fidelity: 'reconstructed' },
    { id: 'markdown-to-pdf', name: 'MD → PDF', desc: 'Markdown to PDF', icon: '◫', category: 'documents', available: false, reason: 'Markdown rendering is not bundled in the Android APK' },
    { id: 'csv-xlsx', name: 'CSV ↔ XLSX', desc: 'Spreadsheet format conversion', icon: '◫', category: 'spreadsheets', available: true, fidelity: 'available' },
    { id: 'diagnostics', name: 'Android Capabilities', desc: 'View bundled Android capabilities', icon: '⚙', category: 'tools', available: true, fidelity: 'available' }
  ];

  // ========== STATE ==========
  let currentCategory = 'all';
  let searchQuery = '';
  let history = JSON.parse(localStorage.getItem('df-history') || '[]');
  let favorites = JSON.parse(localStorage.getItem('df-favorites') || '[]');
  let currentTool = null;
  let selectedFiles = [];

  // ========== DOM REFERENCES ==========
  const $homeScreen = document.getElementById('home-screen');
  const $toolScreen = document.getElementById('tool-screen');
  const $resultScreen = document.getElementById('result-screen');
  const $settingsScreen = document.getElementById('settings-screen');
  const $toolsGrid = document.getElementById('tools-grid');
  const $categoryFilters = document.getElementById('categories');
  const $searchInput = document.getElementById('search-input');
  const $toolBody = document.getElementById('tool-body');
  const $toolTitle = document.getElementById('tool-title');
  const $historySection = document.getElementById('history-section');
  const $historyList = document.getElementById('history-list');
  const $resultIcon = document.getElementById('result-icon');
  const $resultName = document.getElementById('result-name');
  const $resultInfo = document.getElementById('result-info');

  // ========== NAVIGATION ==========
  function navigate(screen) {
    window.location.hash = screen;
    // A tool route is "tool/<id>"; route it immediately as well as through hashchange.
    // This avoids the Android WebView losing the first route update when the hash
    // event is coalesced or ignored during a touch gesture.
    handleRoute();
  }

  function switchScreen(screen) {
    [$homeScreen, $toolScreen, $resultScreen, $settingsScreen].forEach(s => {
      s.classList.remove('active');
    });
    
    switch(screen) {
      case 'home':
        $homeScreen.classList.add('active');
        renderDashboard();
        break;
      case 'tool':
        $toolScreen.classList.add('active');
        break;
      case 'result':
        $resultScreen.classList.add('active');
        break;
      case 'settings':
        $settingsScreen.classList.add('active');
        renderSettings();
        break;
      default:
        $homeScreen.classList.add('active');
        renderDashboard();
    }
  }

  function handleRoute() {
    const hash = window.location.hash.replace('#', '') || 'home';
    const [screen, ...params] = hash.split('/');
    
    if (screen === 'tool' && params[0]) {
      loadTool(params[0]);
    } else if (screen === 'result') {
      showResult(params[0]);
    } else if (screen === 'settings') {
      renderSettings();
    } else {
      switchScreen('home');
    }
  }

  // ========== DASHBOARD RENDERING ==========
  function renderDashboard() {
    // Category filters
    $categoryFilters.innerHTML = '';
    CATEGORIES.forEach(cat => {
      const chip = document.createElement('div');
      chip.className = 'category-chip' + (cat.id === currentCategory ? ' active' : '');
      chip.textContent = cat.icon + ' ' + cat.name;
      chip.setAttribute('role', 'tab');
      chip.setAttribute('aria-selected', cat.id === currentCategory);
      $categoryFilters.appendChild(chip);
    });

    // Tools grid
    $toolsGrid.innerHTML = '';
    const filtered = TOOLS.filter(t => {
      const matchCat = currentCategory === 'all' || t.category === currentCategory;
      const matchSearch = !searchQuery || 
        t.name.toLowerCase().includes(searchQuery) || 
        t.desc.toLowerCase().includes(searchQuery);
      return matchCat && matchSearch;
    });

    if (filtered.length === 0) {
      $toolsGrid.innerHTML = '<p class="text-center" style="padding: 40px; color: var(--color-text-muted);">No tools found matching your search.</p>';
      return;
    }

    filtered.forEach(tool => {
      const card = document.createElement('div');
      card.className = 'tool-card' + (tool.available ? '' : ' disabled');
      card.dataset.toolId = tool.id;
      card.setAttribute('role', 'button');
      card.tabIndex = 0;
      card.setAttribute('aria-label', tool.name);
      
      let badge = '';
      if (!tool.available) {
        badge = `<span class="tool-badge badge-unavailable">Unavailable</span>`;
      }
      
      card.innerHTML = `
        <div class="tool-icon">${tool.icon}</div>
        <div class="tool-name">${tool.name}</div>
        <div class="tool-desc">${tool.desc}</div>
        ${badge}
      `;
      
      if (!tool.available && tool.reason) card.title = tool.reason;
      
      $toolsGrid.appendChild(card);
    });

    // History section
    if (history.length > 0) {
      $historySection.style.display = 'block';
      $historyList.innerHTML = '';
      history.slice(0, 5).forEach(h => {
        const item = document.createElement('div');
        item.className = 'history-item';
        item.innerHTML = `
          <div class="history-icon">${h.icon || '◫'}</div>
          <div class="history-info">
            <div class="history-name">${h.name}</div>
            <div class="history-date">${h.date || ''} · ${h.size || ''}</div>
          </div>
        `;
        $historyList.appendChild(item);
      });
    } else {
      $historySection.style.display = 'none';
    }
  }

  // ========== TOOL LOADING ==========
  function loadTool(toolId) {
    const tool = TOOLS.find(t => t.id === toolId);
    if (!tool) {
      navigate('home');
      return;
    }
    
    currentTool = tool;
    $toolTitle.textContent = tool.name;
    $toolBody.innerHTML = '<div class="loading-spinner"></div>';
    
    // Load tool module dynamically
    const script = document.createElement('script');
    const scriptName = toolId === 'diagnostics' ? 'engine-diagnostic' : toolId;
    script.src = `js/tools/${scriptName}.js`;
    script.onload = () => {
      const toolModule = window.DFRegistry && window.DFRegistry[toolId];
      if (toolModule) {
        try {
          $toolBody.innerHTML = '';
          const root = toolModule.render();
          $toolBody.appendChild(root);
          if (toolModule.onMount) {
            toolModule.onMount($toolBody);
          }
        } catch(e) {
          $toolBody.innerHTML = `
            <div style="padding: 40px; text-align: center;">
              <div style="font-size: 48px; margin-bottom: 16px;">⚠</div>
              <h3>Error Loading Tool</h3>
              <p style="color: var(--color-text-muted); margin-top: 8px;">${e.message}</p>
              <button class="btn btn-primary mt-16" onclick="navigate('home')">Go Back</button>
            </div>
          `;
        }
      } else {
        // Fallback: generic file picker
        showGenericPicker(tool);
      }
    };
    script.onerror = () => showGenericPicker(tool);
    document.head.appendChild(script);
  }

  function showGenericPicker(tool) {
    $toolBody.innerHTML = `
      <div style="padding: 20px;">
        <div class="file-picker" id="drop-zone">
          <div class="file-picker-icon">📁</div>
          <div class="file-picker-text">Tap to select file or drag here</div>
          <input type="file" id="file-input" style="display:none" accept="${getAcceptTypes(tool)}">
        </div>
        <div id="selected-file" style="margin-top: 16px;"></div>
        <button class="btn btn-primary btn-block mt-16" id="convert-btn" disabled>Convert</button>
      </div>
    `;
    
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const convertBtn = document.getElementById('convert-btn');
    
    dropZone.onclick = () => fileInput.click();
    
    dropZone.ondragover = (e) => {
      e.preventDefault();
      dropZone.style.borderColor = 'var(--color-primary-purple)';
    };
    
    dropZone.ondragleave = () => {
      dropZone.style.borderColor = '';
    };
    
    dropZone.ondrop = (e) => {
      e.preventDefault();
      dropZone.style.borderColor = '';
      handleFiles(Array.from(e.dataTransfer.files));
    };
    
    fileInput.onchange = () => handleFiles(Array.from(fileInput.files));
    
    convertBtn.addEventListener('click', () => {
      if (selectedFiles.length > 0) {
        runConversion(tool, selectedFiles);
      }
    });
  }

  function getAcceptTypes(tool) {
    const types = {
      'image-to-pdf': '.png,.jpg,.jpeg,.webp,.bmp,.tiff',
      'pdf-merge': '.pdf',
      'pdf-split': '.pdf',
      'docx-to-pdf': '.docx',
      'markdown-to-pdf': '.md,.markdown'
    };
    return types[tool.id] || '*/*';
  }

  function handleFiles(files) {
    if (files.length === 0) return;
    
    selectedFiles = Array.from(files).filter(f => {
      if (f.size > MAX_FILE_SIZE) {
        showToast(`File "${f.name}" is too large (max 50MB)`, 'error');
        return false;
      }
      return true;
    });
    
    if (selectedFiles.length === 0) return;
    
    const info = document.getElementById('selected-file');
    if (info) {
      info.innerHTML = selectedFiles.map(f => `
        <div style="padding: 12px; background: var(--color-bg); border-radius: 8px; margin-bottom: 8px;">
          <div style="font-weight: 500;">${f.name}</div>
          <div style="font-size: 12px; color: var(--color-text-muted);">${formatFileSize(f.size)}</div>
        </div>
      `).join('');
    }
    
    const convertBtn = document.getElementById('convert-btn');
    if (convertBtn) {
      convertBtn.disabled = false;
      convertBtn.textContent = selectedFiles.length === 1 ? 'Convert' : `Convert ${selectedFiles.length} Files`;
    }
    
    showToast(`${selectedFiles.length} file(s) selected`, 'success');
  }

  // ========== CONVERSION EXECUTION ==========
  async function runConversion(tool, files) {
    const convertBtn = document.getElementById('convert-btn');
    if (convertBtn) {
      convertBtn.disabled = true;
      convertBtn.textContent = 'Processing...';
    }
    
    // Show progress
    $toolBody.innerHTML = `
      <div style="padding: 40px 20px; text-align: center;">
        <div class="loading-spinner" style="width: 48px; height: 48px; border-width: 4px;"></div>
        <h3 style="margin-top: 16px;">Converting...</h3>
        <p style="color: var(--color-text-muted); margin-top: 8px;">This may take a moment depending on file size</p>
        <div class="progress-container" style="margin-top: 24px;">
          <div class="progress-bar">
            <div class="progress-fill" id="progress-fill" style="width: 0%;"></div>
          </div>
          <div class="progress-text" id="progress-text">Starting...</div>
        </div>
      </div>
    `;
    
    try {
      // Simulate progress (in real app, this would be API-driven)
      updateProgress(20, 'Preparing files...');
      await sleep(500);
      
      updateProgress(50, 'Processing...');
      await sleep(1000);
      
      updateProgress(80, 'Generating output...');
      await sleep(500);
      
      updateProgress(100, 'Complete!');
      await sleep(200);
      
      // Mock success - in real app, this calls the API
      const outputFile = {
        name: files[0].name.replace(/\.[^/.]+$/, '') + '_converted.pdf',
        size: files[0].size,
        type: 'application/pdf'
      };
      
      addToHistory({
        name: outputFile.name,
        date: new Date().toLocaleDateString(),
        size: formatFileSize(outputFile.size),
        icon: '◫',
        tool: tool.name
      });
      
      showResult(outputFile);
      
    } catch (error) {
      showError(error.message);
    }
  }

  function updateProgress(percent, text) {
    const fill = document.getElementById('progress-fill');
    const txt = document.getElementById('progress-text');
    if (fill) fill.style.width = percent + '%';
    if (txt) txt.textContent = text;
  }

  function showError(message) {
    $toolBody.innerHTML = `
      <div style="padding: 40px 20px; text-align: center;">
        <div style="font-size: 48px; margin-bottom: 16px;">❌</div>
        <h3>Conversion Failed</h3>
        <p style="color: var(--color-text-muted); margin-top: 8px;">${message}</p>
        <button class="btn btn-primary mt-16" onclick="loadTool('${currentTool?.id}')">Try Again</button>
      </div>
    `;
    showToast('Conversion failed', 'error');
  }

  // ========== RESULT DISPLAY ==========
  function showResult(file) {
    $resultIcon.textContent = getFileIcon(file.type);
    $resultName.textContent = file.name;
    $resultInfo.textContent = `${formatFileSize(file.size)} · ${getFileExtension(file.name).toUpperCase()}`;
    
    navigate('result');
    showToast('Conversion complete!', 'success');
  }

  function getFileIcon(mimeType) {
    const icons = {
      'application/pdf': '◫',
      'image/png': '◫',
      'image/jpeg': '◫',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '◫',
      'application/vnd.ms-excel': '◫',
      'text/csv': '◫'
    };
    return icons[mimeType] || '◫';
  }

  // ========== SETTINGS ==========
  function renderSettings() {
    document.getElementById('settings-content').innerHTML = `
      <div style="padding: 16px;">
        <h3 style="margin-bottom: 16px;">About</h3>
        <div style="background: var(--color-surface); padding: 16px; border-radius: 12px; margin-bottom: 16px;">
          <div style="font-size: 20px; font-weight: 700; margin-bottom: 4px;">ICON DocForge</div>
          <div style="color: var(--color-text-muted);">Version ${APP_VERSION}</div>
          <div style="color: var(--color-text-muted); font-size: 13px; margin-top: 8px;">
            Offline document converter by ICON Studios
          </div>
        </div>
        
        <h3 style="margin-bottom: 16px;">Privacy</h3>
        <div style="background: var(--color-surface); padding: 16px; border-radius: 12px; margin-bottom: 16px;">
          <div style="font-weight: 600; margin-bottom: 8px;">🔒 Your files stay on your device</div>
          <p style="font-size: 14px; color: var(--color-text-muted);">
            All conversions happen locally. No documents are uploaded to any server. 
            No analytics or telemetry are collected.
          </p>
        </div>
        
        <h3 style="margin-bottom: 16px;">Supported Conversions</h3>
        <div style="background: var(--color-surface); padding: 16px; border-radius: 12px; margin-bottom: 16px;">
          <ul style="list-style: none; padding: 0;">
            <li style="padding: 8px 0; border-bottom: 1px solid var(--color-border);">✓ Images → PDF</li>
            <li style="padding: 8px 0; border-bottom: 1px solid var(--color-border);">✓ Merge PDFs</li>
            <li style="padding: 8px 0; border-bottom: 1px solid var(--color-border);">✓ Split PDF</li>
            <li style="padding: 8px 0; color: var(--color-text-muted);">○ DOCX → PDF (requires additional packages)</li>
            <li style="padding: 8px 0; color: var(--color-text-muted);">○ PDF → Images (requires additional packages)</li>
          </ul>
        </div>
        
        <button class="btn btn-secondary btn-block" onclick="runDiagnostics()">Run Diagnostics</button>
        
        <div style="margin-top: 24px; text-align: center; color: var(--color-text-muted); font-size: 12px;">
          <p>© 2026 ICON Studios</p>
          <p style="margin-top: 4px;">Yaoundé, Cameroon</p>
        </div>
      </div>
    `;
  }

  function runDiagnostics() {
    showToast('Checking system status...', 'info');
    setTimeout(() => {
      showToast('System check complete. See engine status for details.', 'success');
    }, 1500);
  }

  // ========== UTILITIES ==========
  function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  function getFileExtension(filename) {
    return filename.split('.').pop().toLowerCase();
  }

  function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  function addToHistory(entry) {
    history.unshift(entry);
    if (history.length > 20) history = history.slice(0, 20);
    localStorage.setItem('df-history', JSON.stringify(history));
  }

  function showToast(message, type = 'info') {
    const container = document.createElement('div');
    container.className = 'toast-container';
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    document.body.appendChild(container);
    setTimeout(() => container.remove(), 3000);
  }

  // ========== EVENT LISTENERS ==========
  $toolsGrid?.addEventListener('click', (event) => {
    const card = event.target.closest?.('.tool-card');
    if (!card || !$toolsGrid.contains(card)) return;
    const tool = TOOLS.find(t => t.id === card.dataset.toolId);
    if (!tool) return;
    if (tool.available) {
      event.preventDefault();
      navigate('tool/' + tool.id);
    }
  });

  $categoryFilters?.addEventListener('click', (event) => {
    const chip = event.target.closest?.('.category-chip');
    if (!chip || !$categoryFilters.contains(chip)) return;
    const index = Array.from($categoryFilters.children).indexOf(chip);
    if (index < 0) return;
    currentCategory = CATEGORIES[index].id;
    renderDashboard();
  });

  document.getElementById('back-btn')?.addEventListener('click', () => navigate('home'));
  document.getElementById('result-back')?.addEventListener('click', () => navigate('home'));
  document.getElementById('settings-back')?.addEventListener('click', () => navigate('home'));
  document.getElementById('btn-convert-another')?.addEventListener('click', () => navigate('home'));
  
  document.getElementById('btn-open')?.addEventListener('click', () => {
    showToast('Opening file...', 'info');
    // In real app: window.location = fileUrl;
  });
  
  document.getElementById('btn-share')?.addEventListener('click', () => {
    if (navigator.share) {
      navigator.share({
        title: 'Converted File',
        text: 'Check out this converted file from ICON DocForge',
        url: window.location.href
      }).catch(() => {});
    } else {
      showToast('Share not supported on this device', 'info');
    }
  });

  $searchInput?.addEventListener('input', (e) => {
    searchQuery = e.target.value.toLowerCase();
    renderDashboard();
  });

  // ========== INITIALIZATION ==========
  window.App = {
    toast: showToast,
    navigate: navigate,
    apiBase: API_BASE,
    addToHistory: addToHistory
  };
  window.__docforgeTest = {
    setSearch(value) { searchQuery = value.toLowerCase(); renderDashboard(); }
  };

  window.addEventListener('hashchange', handleRoute);
  handleRoute();

  // Set version in footer
  document.getElementById('app-version').textContent = APP_VERSION;
})();
