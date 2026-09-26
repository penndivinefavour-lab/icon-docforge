(function () {
  const id = 'image-to-pdf';
  const { PDFDocument } = window.PDFLib;
  function render() {
    const wrap = document.createElement('div');
    wrap.innerHTML = `<div class="tool-section"><h3>Select Images</h3><div class="drop-zone" id="drop"><div class="drop-zone-icon">🖼</div><div class="drop-zone-text">Tap to select PNG or JPEG images</div><input type="file" id="files" accept="image/png,image/jpeg" multiple style="display:none"></div><p id="count" class="tool-desc">0 images selected</p></div><button class="btn btn-primary btn-block" id="go" disabled>Generate PDF</button><div id="result" style="margin-top:16px"></div>`;
    return wrap;
  }
  async function onMount(root) {
    let files = [];
    const input = root.querySelector('#files'); const go = root.querySelector('#go');
    input.onchange = () => { files = Array.from(input.files); root.querySelector('#count').textContent = `${files.length} image(s) selected`; go.disabled = !files.length; };
    root.querySelector('#drop').onclick = () => input.click();
    go.onclick = async () => {
      go.disabled = true; go.textContent = 'Generating…';
      try {
        const doc = await PDFDocument.create();
        for (const file of files) doc.addPage([595.28, 841.89]);
        const pages = doc.getPages();
        for (let i=0; i<files.length; i++) {
          const bytes = new Uint8Array(await files[i].arrayBuffer());
          const image = bytes[0] === 0x89 ? await doc.embedPng(bytes) : await doc.embedJpg(bytes);
          const page = pages[i]; const size = page.getSize();
          const scale = Math.min(size.width / image.width, size.height / image.height);
          const w = image.width * scale, h = image.height * scale;
          page.drawImage(image, { x: (size.width-w)/2, y: (size.height-h)/2, width:w, height:h });
        }
        const out = await doc.save();
        const saved = DFRuntime.saveBytes(out, 'images-to-pdf.pdf', 'application/pdf');
                DFRuntime.resultView(root, saved.name, `${files.length} page(s)`,
                  () => window.AndroidBridge && AndroidBridge.openFile(saved.uri, saved.mime),
                  () => window.AndroidBridge && AndroidBridge.shareFile(saved.uri, saved.mime));
        window.App.toast('PDF generated', 'success');
      } catch (e) { window.App.toast(e.message, 'error'); } finally { go.disabled=false; go.textContent='Generate PDF'; }
    };
  }
  window.DFRegistry=window.DFRegistry||{}; window.DFRegistry[id]={id,name:'Images → PDF',render,onMount};
})();
