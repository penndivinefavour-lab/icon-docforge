(function () {
  const id = 'image-to-pdf';

  function render() {
    const wrap = document.createElement('div');
    wrap.innerHTML = `
      <div class="tool-section">
        <h3>Select Images</h3>
        <div class="drop-zone" id="img-drop">
          <div class="drop-zone-icon">🖼</div>
          <div class="drop-zone-text">Drop images here (PNG, JPG, WebP)</div>
          <input type="file" id="img-input" accept="image/*" multiple style="display:none"/>
          <p style="font-size:12px;color:var(--text-muted);margin-top:8px" id="img-count">0 images selected</p>
        </div>
      </div>
      <div class="tool-section">
        <h3>Page Settings</h3>
        <div class="field">
          <label>Page Size</label>
          <select id="page-size">
            <option value="A4">A4</option>
            <option value="Letter">Letter</option>
            <option value="original">Original Image Size</option>
          </select>
        </div>
        <div class="field">
          <label>Orientation</label>
          <select id="orientation">
            <option value="portrait">Portrait</option>
            <option value="landscape">Landscape</option>
            <option value="auto">Auto (per image)</option>
          </select>
        </div>
        <div class="field">
          <label>Margins (mm)</label>
          <input type="number" id="margins" value="10" min="0" max="50"/>
        </div>
        <div class="field">
          <label>Image Quality (%)</label>
          <input type="range" id="quality" min="10" max="100" value="85"/>
          <span id="quality-val">85%</span>
        </div>
        <div class="field">
          <label><input type="checkbox" id="add-page-numbers" checked/> Add page numbers</label>
        </div>
        <div class="field">
          <label><input type="checkbox" id="add-cover"/> Add cover page</label>
        </div>
      </div>
      <div class="tool-section">
        <h3>Preview</h3>
        <div id="preview-list" style="max-height:200px;overflow-y:auto"></div>
      </div>
      <button class="btn btn-primary btn-block" id="convert-btn">Generate PDF</button>
      <div id="result-area" style="margin-top:16px"></div>
    `;
    return wrap;
  }

  function onMount(root) {
    let selectedFiles = [];
    const dropZone = root.querySelector('#img-drop');
    const fileInput = root.querySelector('#img-input');
    const quality = root.querySelector('#quality');
    const qualityVal = root.querySelector('#quality-val');
    const previewList = root.querySelector('#preview-list');
    const convertBtn = root.querySelector('#convert-btn');
    const resultArea = root.querySelector('#result-area');

    quality.oninput = () => { qualityVal.textContent = quality.value + '%'; };

    dropZone.onclick = () => fileInput.click();
    dropZone.ondragover = (e) => { e.preventDefault(); dropZone.classList.add('dragover'); };
    dropZone.ondragleave = () => dropZone.classList.remove('dragover');
    dropZone.ondrop = (e) => {
      e.preventDefault(); dropZone.classList.remove('dragover');
      selectedFiles = Array.from(e.dataTransfer.files).filter(f => f.type.startsWith('image/'));
      updatePreview();
    };
    fileInput.onchange = () => {
      selectedFiles = Array.from(fileInput.files).filter(f => f.type.startsWith('image/'));
      updatePreview();
    };

    function updatePreview() {
      root.querySelector('#img-count').textContent = selectedFiles.length + ' image(s) selected';
      previewList.innerHTML = '';
      selectedFiles.forEach((f, i) => {
        const div = document.createElement('div');
        div.style.cssText = 'display:flex;align-items:center;gap:8px;padding:8px;background:var(--bg);border-radius:6px;margin-bottom:4px;';
        div.innerHTML = `<span>${i+1}.</span><span>${f.name}</span><span style="color:var(--text-muted);font-size:12px">${(f.size/1024).toFixed(0)}KB</span>`;
        previewList.appendChild(div);
      });
    }

    convertBtn.onclick = async () => {
      if (selectedFiles.length === 0) { window.App.toast('Select at least one image', 'error'); return; }
      convertBtn.disabled = true;
      convertBtn.textContent = 'Converting…';
      resultArea.innerHTML = '<div class="progress-bar"><div class="progress-fill" style="width:30%"></div></div><p class="progress-text">Converting…</p>';

      // Create FormData
      const formData = new FormData();
      selectedFiles.forEach(f => formData.append('images', f));
      formData.append('page_size', root.querySelector('#page-size').value);
      formData.append('orientation', root.querySelector('#orientation').value);
      formData.append('margins', root.querySelector('#margins').value);
      formData.append('quality', quality.value);
      formData.append('add_page_numbers', root.querySelector('#add-page-numbers').checked);
      formData.append('add_cover', root.querySelector('#add-cover').checked);

      try {
        const resp = await fetch('http://127.0.0.1:8765/api/images-to-pdf', {
          method: 'POST', body: formData
        });
        const data = await resp.json();
        if (data.success) {
          resultArea.innerHTML = `
            <div class="output-file">
              <div class="output-file-name">📄 ${data.output.split('/').pop()}</div>
              <button class="btn btn-gold" id="download-btn">Download</button>
              <button class="btn btn-secondary" id="share-btn">Share</button>
            </div>
            <p style="font-size:12px;color:var(--text-muted);margin-top:4px">${data.size} bytes, ${data.pages} pages</p>
          `;
          document.getElementById('download-btn').onclick = () => window.open(data.output);
          window.App.toast('PDF generated successfully!', 'success');
          window.App.addToHistory({ name: 'Images → PDF', icon: '🖼', date: new Date().toLocaleDateString() });
        } else {
          resultArea.innerHTML = `<p style="color:var(--error)">Error: ${data.error}</p>`;
          window.App.toast('Conversion failed', 'error');
        }
      } catch(e) {
        resultArea.innerHTML = `<p style="color:var(--error)">Engine offline — start conversion service</p>`;
        window.App.toast('Engine not available', 'error');
      }
      convertBtn.disabled = false;
      convertBtn.textContent = 'Generate PDF';
    };
  }

  if (!window.DFRegistry) window.DFRegistry = {};
  window.DFRegistry[id] = { id, name: 'Images → PDF', desc: 'Create PDF from images', icon: '🖼', category: 'images', render, onMount };
})();
