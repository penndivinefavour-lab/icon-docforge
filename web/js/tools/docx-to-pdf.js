(function () {
  const id='docx-to-pdf';
  function render(){const w=document.createElement('div');w.innerHTML=`<div class="tool-section"><h3>Convert DOCX to PDF</h3><div class="drop-zone" id="drop"><div class="drop-zone-icon">📝</div><div class="drop-zone-text">Tap to select a DOCX file</div><input type="file" id="file" accept=".docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document" style="display:none"></div></div><div class="output-area" style="margin-top:12px">Fidelity note: text, headings, paragraphs, and basic formatting are reconstructed. Pixel-perfect Microsoft Word layout is not guaranteed.</div><button class="btn btn-primary btn-block" id="go" disabled>Convert to PDF</button><div id="result" style="margin-top:16px"></div>`;return w;}
  async function onMount(root){let file=null;const input=root.querySelector('#file'),go=root.querySelector('#go');
    input.onchange=()=>{file=input.files[0];go.disabled=!file};
    root.querySelector('#drop').onclick=()=>input.click();
    go.onclick=async()=>{go.disabled=true;go.textContent='Converting...';
      try{
        const result=await mammoth.convertToHtml({arrayBuffer:await file.arrayBuffer()});
        const holder=document.createElement('div');
        holder.innerHTML=result.value;
        holder.style.cssText='background:white;color:#111;padding:40px;width:700px;font-family:Arial,sans-serif';
        document.body.appendChild(holder);
        const canvas=await html2canvas(holder,{scale:1.5,backgroundColor:'#fff'});
        document.body.removeChild(holder);
        const {jsPDF}=window.jspdf;
        const pdf=new jsPDF({unit:'px',format:[canvas.width,canvas.height],orientation:canvas.width>canvas.height?'landscape':'portrait'});
        pdf.addImage(canvas.toDataURL('image/jpeg',0.95),'JPEG',0,0,canvas.width,canvas.height);
        const saved=DFRuntime.saveBytes(pdf.output('arraybuffer'),`${file.name.replace(/\.docx$/i,'')}.pdf`,'application/pdf');
        DFRuntime.resultView(root,saved.name,'Reconstructed document layout',
          ()=>window.AndroidBridge&&AndroidBridge.openFile(saved.uri,saved.mime),
          ()=>window.AndroidBridge&&AndroidBridge.shareFile(saved.uri,saved.mime));
      }catch(e){window.App.toast(e.message,'error');}
      finally{go.disabled=false;go.textContent='Convert to PDF';}
    };
  }
  window.DFRegistry=window.DFRegistry||{};window.DFRegistry[id]={id,name:'DOCX → PDF',render,onMount};
})();
