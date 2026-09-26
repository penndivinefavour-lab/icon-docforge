(function () {
  const id='csv-xlsx';
  // Client-side conversion using xlsx.js library loaded in vendor/
  function render(){
    const w=document.createElement('div');
    w.innerHTML=`<div class="tool-section"><h3>Convert CSV ↔ XLSX</h3>
      <div class="drop-zone" id="drop"><div class="drop-zone-icon">📊</div><div class="drop-zone-text">Tap to select CSV or XLSX file</div>
      <input type="file" id="file" accept=".csv,.xlsx,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" style="display:none"></div>
      <div class="field" style="margin-top:12px"><label>Conversion</label>
      <select id="direction" class="input"><option value="csv2xlsx">CSV → XLSX</option><option value="xlsx2csv">XLSX → CSV</option></select></div>
      <button class="btn btn-primary btn-block" id="go" disabled>Convert</button>
      <div id="result" style="margin-top:16px"></div></div>`;
    return w;
  }
  async function onMount(root){
    let file=null;
    const input=root.querySelector('#file'), go=root.querySelector('#go');
    input.onchange=()=>{file=input.files[0];go.disabled=!file};
    root.querySelector('#drop').onclick=()=>input.click();
    go.onclick=async()=>{
      go.disabled=true;go.textContent='Converting...';
      try{
        const direction=root.querySelector('#direction').value;
        const bytes=new Uint8Array(await file.arrayBuffer());
        let outName='',outMime='';
        if(direction==='csv2xlsx'){
          const XLSX=window.XLSX;
          const wb=XLSX.read(bytes,{type:'array'});
          const out=XLSX.write(wb,{bookType:'xlsx',type:'array'});
          outName=file.name.replace(/\.csv$/i,'')+'.xlsx';
          outMime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
          const saved=DFRuntime.saveBytes(out,outName,outMime);
          DFRuntime.resultView(root,saved.name,'Spreadsheet',
            ()=>window.AndroidBridge&&AndroidBridge.openFile(saved.uri,saved.mime),
            ()=>window.AndroidBridge&&AndroidBridge.shareFile(saved.uri,saved.mime));
        }else{
          const XLSX=window.XLSX;
          const wb=XLSX.read(bytes,{type:'array'});
          const ws=wb.Sheets[wb.SheetNames[0]];
          const csv=XLSX.utils.sheet_to_csv(ws);
          outName=file.name.replace(/\.xlsx$/i,'')+'.csv';
          outMime='text/csv';
          const saved=DFRuntime.saveBytes(new TextEncoder().encode(csv),outName,outMime);
          DFRuntime.resultView(root,saved.name,'CSV file',
            ()=>window.AndroidBridge&&AndroidBridge.openFile(saved.uri,saved.mime),
            ()=>window.AndroidBridge&&AndroidBridge.shareFile(saved.uri,saved.mime));
        }
        window.App.toast('Conversion complete','success');
      }catch(e){window.App.toast(e.message,'error');}
      finally{go.disabled=false;go.textContent='Convert';}
    };
  }
  window.DFRegistry=window.DFRegistry||{};window.DFRegistry[id]={id,name:'CSV ↔ XLSX',render,onMount};
})();
