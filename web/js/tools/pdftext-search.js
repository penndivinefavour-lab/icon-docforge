(function () {
  const id = 'pdftext-search';
  const PDFJS = window.pdfjsLib;

  function render() {
    const wrap = document.createElement('div');
    wrap.innerHTML = `
      <div class="tool-section">
        <h3>Search PDF Text</h3>
        <div class="drop-zone" id="drop">
          <div class="drop-zone-icon">🔎</div>
          <div class="drop-zone-text">Tap to select a PDF</div>
          <input type="file" id="file" accept="application/pdf" style="display:none">
        </div>
      </div>
      <div class="tool-section">
        <h3>Search Term</h3>
        <div class="field">
          <input type="text" id="search-term" class="input" placeholder="Enter text to search">
        </div>
        <button class="btn btn-primary btn-block" id="search-btn" disabled>Search</button>
      </div>
      <div id="results" style="margin-top:16px"></div>
      <div id="result" style="margin-top:16px"></div>
    `;
    return wrap;
  }

  async function onMount(root) {
    let file = null;
    const input = root.querySelector('#file');
    const searchBtn = root.querySelector('#search-btn');
    const searchTerm = root.querySelector('#search-term');

    input.onchange = () => {
      file = input.files[0];
      searchBtn.disabled = !file;
    };
    root.querySelector('#drop').onclick = () => input.click();

    searchBtn.onclick = async () => {
      const term = searchTerm.value.trim();
      if (!file || !term) return;
      searchBtn.disabled = true;
      searchBtn.textContent = 'Searching...';
      try {
        const pdf = await PDFJS.getDocument({ data: await file.arrayBuffer() }).promise;
        let totalMatches = 0;
        const pageResults = [];

        for (let i = 1; i <= pdf.numPages; i++) {
          const page = await pdf.getPage(i);
          const text = await page.getTextContent();
          const pageText = text.items.map(item => item.str).join(' ');
          const matches = (pageText.toLowerCase().match(new RegExp(term.toLowerCase(), 'g')) || []).length;
          if (matches > 0) {
            totalMatches += matches;
            pageResults.push({ page: i, matches });
          }
        }

        const resultsDiv = root.querySelector('#results');
        if (pageResults.length === 0) {
          resultsDiv.innerHTML = '<p style="color:var(--color-text-muted)">No matches found</p>';
        } else {
          resultsDiv.innerHTML = `
            <div class="stat-box">
              <div class="stat-value">${totalMatches}</div>
              <div class="stat-label">matches across ${pageResults.length} page(s)</div>
            </div>
            <div style="margin-top:12px">
              ${pageResults.map(p => `<div class="history-item"><div class="history-icon">${p.page}</div><div class="history-info"><div class="history-name">Page ${p.page}</div><div class="history-date">${p.matches} match(es)</div></div></div>`).join('')}
            </div>
          `;
        }

        const outName = file.name.replace(/\.pdf$/i, '') + '-search-results.txt';
        const outText = `Search: "${term}"\nTotal matches: ${totalMatches}\nPages: ${pageResults.map(p => `Page ${p.page}: ${p.matches} match(es)`).join('\n')}\n`;
        const saved = DFRuntime.saveBytes(new TextEncoder().encode(outText), outName, 'text/plain');
        DFRuntime.resultView(root, saved.name, `${totalMatches} match(es)`,
          () => window.AndroidBridge && AndroidBridge.openFile(saved.uri, saved.mime),
          () => window.AndroidBridge && AndroidBridge.shareFile(saved.uri, saved.mime));
        window.App.toast(`${totalMatches} match(es) found`, 'success');
      } catch (e) {
        window.App.toast(e.message, 'error');
      } finally {
        searchBtn.disabled = false;
        searchBtn.textContent = 'Search';
      }
    };
  }

  window.DFRegistry = window.DFRegistry || {};
  window.DFRegistry[id] = { id, name: 'PDF Text & Search', render, onMount };
})();
