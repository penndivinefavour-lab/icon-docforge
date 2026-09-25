(function () {
  const API_BASE = window.App && window.App.apiBase;

  async function api(path, options) {
    if (!API_BASE) throw new Error('This workflow requires the Termux/Python engine and is unavailable in the Android APK.');
    const response = await fetch(API_BASE.replace(/\/$/, '') + path, options);
    const data = await response.json();
    if (!response.ok || data.success === false) throw new Error(data.error || 'Conversion failed');
    return data;
  }

  function resultView(root, name, size, onOpen, onShare) {
    const box = document.createElement('div');
    box.className = 'output-file';
    box.innerHTML = `<div class="output-file-name">📄 ${name}</div><div class="output-file-info">${size || ''}</div><div style="display:flex;gap:8px;margin-top:12px"><button class="btn btn-gold" id="open-output">Open</button><button class="btn btn-secondary" id="share-output">Share</button></div>`;
    box.querySelector('#open-output').onclick = onOpen;
    box.querySelector('#share-output').onclick = onShare;
    root.querySelector('#result').appendChild(box);
  }

  function saveBytes(bytes, name, mime) {
    if (window.AndroidBridge && AndroidBridge.saveFile) {
      let binary = '';
      const chunk = 0x8000;
      for (let i = 0; i < bytes.length; i += chunk) binary += String.fromCharCode.apply(null, bytes.subarray(i, i + chunk));
      const uri = AndroidBridge.saveFile(name, mime, btoa(binary));
      if (!uri) throw new Error('Android could not save the generated output file.');
      return { name, uri, mime };
    }
    const blob = new Blob([bytes], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = name; a.click();
    setTimeout(() => URL.revokeObjectURL(url), 30000);
    return { name, uri: url, mime };
  }

  window.DFRuntime = { api, resultView, saveBytes };
})();
