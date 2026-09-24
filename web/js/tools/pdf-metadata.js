(function () {
  const id = 'pdf-metadata';
  function render() {
    const w = document.createElement('div');
    w.innerHTML = `<div class="tool-section"><h3>PDF Info</h3><input type="file" id="file" accept=".pdf" class="input"/>
      <button class="btn btn-primary" id="info-btn" style="margin-top:12px">Read Metadata</button></div>
      <div id="result" style="margin-top:16px"></div></div>`;
    return w;
  }
  function onMount(root) {
    root.querySelector('#info-btn').onclick = async () => {
      const file = root.querySelector('#file').files[0];
      if (!file) { window.App.toast('Select a PDF', 'error'); return; }
      const formData = new FormData(); formData.append('input', file);
      try {
        const resp = await fetch('http://127.0.0.1:8765/api/pdf-metadata', { method: 'POST', body: formData });
        const data = await resp.json();
        if (data.success) {
          let html = '<div class="output-area">';
          for (const [k,v] of Object.entries(data.metadata||{})) html += `<strong>${k}:</strong> ${v}<br>`;
          html += '</div>';
          root.querySelector('#result').innerHTML = html;
        } else { root.querySelector('#result').innerHTML = `<p style="color:var(--error)">${data.error}</p>`; }
      } catch(e) { root.querySelector('#result').innerHTML = '<p style="color:var(--error)">Engine offline</p>'; }
    };
  }
  if (!window.DFRegistry) window.DFRegistry = {};
  window.DFRegistry[id] = { id, name: 'PDF Info', desc: 'View metadata', icon: 'ℹ️📄', category: 'pdf', render, onMount };
})();
