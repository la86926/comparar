from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# 1) Make the existing counter cleaner but much more visible.
old_counter_css='  .counter{min-width:105px;text-align:center;font-size:12.5px;font-weight:650}\n'
new_counter_css='''  .counter{\n    min-width:64px;height:34px;padding:0 12px;\n    display:grid;place-items:center;\n    border:1px solid rgba(0,113,227,.16);\n    border-radius:999px;\n    background:rgba(0,113,227,.085);\n    color:var(--blue);\n    text-align:center;\n    font-size:13px;font-weight:700;letter-spacing:-.02em;\n    box-shadow:inset 0 1px 0 rgba(255,255,255,.8);\n    transition:background .18s ease,transform .18s ease;\n  }\n  .counter.counter-pop{animation:counterPop .24s ease}\n  @keyframes counterPop{50%{transform:scale(1.06)}}\n'''
if old_counter_css not in s:
    raise RuntimeError('counter CSS anchor not found')
s=s.replace(old_counter_css,new_counter_css,1)

# 2) Add adaptive debounce + worker-backed word diff helpers.
old_schedule='''function scheduleCompare(delay=320){\n  clearTimeout(compareTimer);\n  compareTimer=setTimeout(()=>compareNow(false),delay);\n}\n'''
new_schedule='''function currentTextSize(){\n  let total=0;\n  ["A","B"].forEach(doc=>{\n    if(state[doc].mode==="text") total+=document.getElementById("text"+doc).value.length;\n  });\n  return total;\n}\n\nfunction scheduleCompare(delay){\n  clearTimeout(compareTimer);\n  if(delay==null){\n    const total=currentTextSize();\n    delay=total>150000?1100:total>50000?650:320;\n  }\n  compareTimer=setTimeout(()=>compareNow(false),delay);\n}\n\nlet activeDiffWorker=null;\nfunction diffWordsAsync(txtA,txtB){\n  const total=txtA.length+txtB.length;\n  if(total<30000||typeof Worker==="undefined") return Promise.resolve(Diff.diffWords(txtA,txtB));\n\n  if(activeDiffWorker){\n    activeDiffWorker.terminate();\n    activeDiffWorker=null;\n  }\n\n  return new Promise((resolve,reject)=>{\n    const source=`\n      self.importScripts("https://cdnjs.cloudflare.com/ajax/libs/jsdiff/5.1.0/diff.min.js");\n      self.onmessage=function(e){\n        try{\n          const parts=Diff.diffWords(e.data.a,e.data.b);\n          self.postMessage({ok:true,parts:parts});\n        }catch(err){\n          self.postMessage({ok:false,error:err&&err.message?err.message:String(err)});\n        }\n      };\n    `;\n    const url=URL.createObjectURL(new Blob([source],{type:"text/javascript"}));\n    const worker=new Worker(url);\n    activeDiffWorker=worker;\n    URL.revokeObjectURL(url);\n\n    const finish=()=>{\n      if(activeDiffWorker===worker) activeDiffWorker=null;\n      worker.terminate();\n    };\n    worker.onmessage=e=>{\n      const data=e.data||{};\n      finish();\n      if(data.ok) resolve(data.parts);\n      else reject(new Error(data.error||"No se pudo comparar el texto."));\n    };\n    worker.onerror=e=>{\n      finish();\n      reject(new Error(e.message||"No se pudo procesar el texto grande."));\n    };\n    worker.postMessage({a:txtA,b:txtB});\n  });\n}\n'''
if old_schedule not in s:
    raise RuntimeError('scheduleCompare anchor not found')
s=s.replace(old_schedule,new_schedule,1)

# 3) Run the expensive diff outside the UI thread for large texts.
old_diff='''    const parts=Diff.diffWords(txtA,txtB);\n    let hU="",hL="",hR="",nAdd=0,nDel=0,id=0,i=0;\n'''
new_diff='''    const totalChars=txtA.length+txtB.length;\n    if(totalChars>=30000){\n      document.getElementById("liveText").textContent="Analizando texto grande…";\n      document.getElementById("loadingText").textContent="Comparando sin bloquear la interfaz…";\n    }\n    const parts=await diffWordsAsync(txtA,txtB);\n    if(run!==compareRun) return;\n    document.getElementById("liveText").textContent="Comparación automática activada";\n    updateModeLabels();\n    await new Promise(resolve=>requestAnimationFrame(resolve));\n    let hU="",hL="",hR="",nAdd=0,nDel=0,id=0,i=0;\n'''
if old_diff not in s:
    raise RuntimeError('diffWords anchor not found')
s=s.replace(old_diff,new_diff,1)

# 4) Restore loading visibility after the async worker finishes rather than before it starts.
old_loading_hide='''    if(run!==compareRun) return;\n    loading.style.display="none";\n    document.getElementById("liveText").textContent="Comparación automática activada";\n\n    if(txtA==null||txtB==null||(!txtA.trim()&&!txtB.trim())){\n'''
new_loading_hide='''    if(run!==compareRun) return;\n\n    if(txtA==null||txtB==null||(!txtA.trim()&&!txtB.trim())){\n      loading.style.display="none";\n      document.getElementById("liveText").textContent="Comparación automática activada";\n'''
if old_loading_hide not in s:
    raise RuntimeError('loading state anchor not found')
s=s.replace(old_loading_hide,new_loading_hide,1)

# Hide loading after rendering the result.
old_card='''    card.style.display="block";\n    state.nChanges=id;state.current=-1;\n'''
new_card='''    loading.style.display="none";\n    document.getElementById("liveText").textContent="Comparación automática activada";\n    card.style.display="block";\n    state.nChanges=id;state.current=-1;\n'''
if old_card not in s:
    raise RuntimeError('card display anchor not found')
s=s.replace(old_card,new_card,1)

# 5) Compact 1/8 counter, but with accessible explanation and a subtle visual pulse.
old_update='''function updateCounter(){\n  const n=state.view==="pdf"?pdfState.groups.length:state.nChanges;\n  document.getElementById("counter").textContent=n?"Cambio "+(state.current+1)+" de "+n:"—";\n  document.getElementById("btnPrev").disabled=state.current<=0;\n  document.getElementById("btnNext").disabled=state.current>=n-1;\n}\n'''
new_update='''function updateCounter(){\n  const n=state.view==="pdf"?pdfState.groups.length:state.nChanges;\n  const counter=document.getElementById("counter");\n  counter.textContent=n?(state.current+1)+"/"+n:"—";\n  counter.title=n?"Cambio "+(state.current+1)+" de "+n:"Sin cambios";\n  counter.setAttribute("aria-label",counter.title);\n  counter.classList.remove("counter-pop");\n  void counter.offsetWidth;\n  if(n)counter.classList.add("counter-pop");\n  document.getElementById("btnPrev").disabled=state.current<=0;\n  document.getElementById("btnNext").disabled=state.current>=n-1;\n}\n'''
if old_update not in s:
    raise RuntimeError('updateCounter anchor not found')
s=s.replace(old_update,new_update,1)

# 6) Cancel any still-running large comparison on reset.
old_reset_start='''document.getElementById("btnReset").addEventListener("click",()=>{\n  clearTimeout(compareTimer);compareRun++;\n'''
new_reset_start='''document.getElementById("btnReset").addEventListener("click",()=>{\n  clearTimeout(compareTimer);compareRun++;\n  if(activeDiffWorker){activeDiffWorker.terminate();activeDiffWorker=null}\n'''
if old_reset_start not in s:
    raise RuntimeError('reset anchor not found')
s=s.replace(old_reset_start,new_reset_start,1)

p.write_text(s,encoding='utf-8')
print('Installed visible compact counter and large-text worker performance improvements')
