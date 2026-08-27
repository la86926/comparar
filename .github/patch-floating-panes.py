from pathlib import Path

path = Path("index.html")
s = path.read_text(encoding="utf-8")

css_start = s.index("  /* Floating compact editor */")
css_end = s.index("  @media(prefers-reduced-motion:reduce){", css_start)
new_css = '''  /* Floating compact editor */
  .floating-editor{
    position:fixed;
    inset:0;
    z-index:80;
    opacity:0;
    visibility:hidden;
    pointer-events:none;
    transition:opacity .2s ease,visibility .2s ease;
  }
  .floating-editor.visible{opacity:1;visibility:visible}
  .floating-pane{
    position:fixed;
    width:220px;
    padding:8px;
    border:1px solid rgba(0,0,0,.09);
    border-radius:18px;
    background:rgba(255,255,255,.86);
    backdrop-filter:blur(28px) saturate(1.35);
    -webkit-backdrop-filter:blur(28px) saturate(1.35);
    box-shadow:0 14px 42px rgba(0,0,0,.13),0 2px 8px rgba(0,0,0,.05);
    pointer-events:auto;
    opacity:0;
    transform:scale(.96) translateY(8px);
    transition:opacity .2s ease,transform .24s cubic-bezier(.2,.8,.2,1),box-shadow .18s ease;
  }
  .floating-editor.visible .floating-pane{opacity:1;transform:scale(1) translateY(0)}
  .floating-pane.pane-a{left:18px;bottom:18px}
  .floating-pane.pane-b{right:18px;bottom:18px}
  .floating-pane.dragging{transition:none;box-shadow:0 20px 55px rgba(0,0,0,.18),0 3px 10px rgba(0,0,0,.08)}
  .floating-drag{
    display:flex;align-items:center;gap:7px;min-height:28px;
    padding:3px 6px 7px;color:var(--muted);font-size:11.5px;font-weight:650;
    cursor:grab;user-select:none;-webkit-user-select:none;touch-action:none;
  }
  .floating-drag:active{cursor:grabbing}
  .floating-drag .grip{
    margin-left:auto;width:18px;height:12px;opacity:.42;
    background-image:radial-gradient(circle,#6e6e73 1px,transparent 1.2px);
    background-size:6px 6px;background-position:center;
  }
  .floating-pane textarea{
    min-height:52px;height:52px;max-height:52px;resize:none;overflow:auto;
    padding:8px 9px;border-radius:12px;background:rgba(248,248,250,.94);
    font-size:11.5px;line-height:1.35;
  }
  .floating-mini-actions{display:flex;justify-content:flex-end;margin-top:6px}
  .floating-mini-btn{
    border:0;min-height:26px;padding:5px 10px;border-radius:999px;
    background:rgba(0,0,0,.055);color:var(--ink);font-size:10.5px;font-weight:650;
    cursor:pointer;transition:transform .15s ease,background .15s ease;
  }
  .floating-mini-btn:hover{background:rgba(0,0,0,.09)}
  .floating-mini-btn:active{transform:scale(.96)}
  .floating-mini-btn.primary{background:var(--blue);color:#fff}
  .floating-mini-btn.primary:hover{background:var(--blue-hover)}

  @media(max-width:720px){
    .floating-pane{width:min(190px,calc(50vw - 14px));padding:7px;border-radius:16px}
    .floating-pane.pane-a{left:8px;bottom:8px}
    .floating-pane.pane-b{right:8px;bottom:8px}
    .floating-pane textarea{height:46px;min-height:46px;max-height:46px;font-size:11px}
    .floating-drag{font-size:10.5px;min-height:25px;padding:2px 5px 6px}
    .floating-mini-btn{min-height:24px;padding:4px 8px;font-size:10px}
  }

'''
s = s[:css_start] + new_css + s[css_end:]

html_start = s.index('<div class="floating-editor" id="floatingEditor"')
html_end = s.index('\n<script>', html_start)
new_html = '''<div class="floating-editor" id="floatingEditor" aria-label="Edición rápida para una nueva comparación">
  <section class="floating-pane pane-a" id="floatingPaneA" aria-label="Texto original flotante">
    <div class="floating-drag" data-pane="A" title="Arrastrar ventana">
      <span class="dot a"></span><span>Original</span><span class="grip" aria-hidden="true"></span>
    </div>
    <textarea id="floatingTextA" placeholder="Texto original…" spellcheck="true"></textarea>
    <div class="floating-mini-actions"><button class="floating-mini-btn" id="floatingReset">Limpiar</button></div>
  </section>

  <section class="floating-pane pane-b" id="floatingPaneB" aria-label="Texto modificado flotante">
    <div class="floating-drag" data-pane="B" title="Arrastrar ventana">
      <span class="dot b"></span><span>Modificado</span><span class="grip" aria-hidden="true"></span>
    </div>
    <textarea id="floatingTextB" placeholder="Texto modificado…" spellcheck="true"></textarea>
    <div class="floating-mini-actions"><button class="floating-mini-btn primary" id="floatingCompare">Comparar</button></div>
  </section>
</div>
'''
s = s[:html_start] + new_html + s[html_end:]

js_start = s.index("/* Editor flotante compacto: mantiene sincronizadas las cajas grandes y pequeñas */")
js_end = s.index("function contentLabel(doc){", js_start)
new_js = '''/* Editor flotante compacto: dos ventanas independientes, movibles y sincronizadas */
const floatingEditor=document.getElementById("floatingEditor");
const floatingTextA=document.getElementById("floatingTextA");
const floatingTextB=document.getElementById("floatingTextB");
const floatingPanes={A:document.getElementById("floatingPaneA"),B:document.getElementById("floatingPaneB")};

function syncFloatingFromMain(doc){
  const main=document.getElementById("text"+doc);
  const mini=doc==="A"?floatingTextA:floatingTextB;
  if(mini&&main&&mini.value!==main.value) mini.value=main.value;
}

function updateFloatingEditor(){
  if(!floatingEditor) return;
  const card=document.getElementById("resultCard");
  const grid=document.querySelector(".grid");
  const bothText=state.A.mode==="text"&&state.B.mode==="text";
  const hasResult=card&&getComputedStyle(card).display!=="none";
  const inputsPassed=grid&&grid.getBoundingClientRect().bottom<110;
  const show=!!(bothText&&hasResult&&inputsPassed);
  floatingEditor.classList.toggle("visible",show);
  if(show){syncFloatingFromMain("A");syncFloatingFromMain("B")}
}

function pushFloatingToMain(doc,mini){
  const main=document.getElementById("text"+doc);
  if(!main||main.value===mini.value) return;
  main.value=mini.value;
  main.dispatchEvent(new Event("input",{bubbles:true}));
}

function clampPanePosition(pane,x,y){
  const gap=8;
  const maxX=Math.max(gap,window.innerWidth-pane.offsetWidth-gap);
  const maxY=Math.max(gap,window.innerHeight-pane.offsetHeight-gap);
  return{x:Math.min(Math.max(gap,x),maxX),y:Math.min(Math.max(gap,y),maxY)};
}

function setFloatingPanePosition(doc,x,y,save=true){
  const pane=floatingPanes[doc];
  if(!pane)return;
  const p=clampPanePosition(pane,x,y);
  pane.style.left=p.x+"px";pane.style.top=p.y+"px";
  pane.style.right="auto";pane.style.bottom="auto";
  if(save){try{localStorage.setItem("comparar-floating-pane-"+doc,JSON.stringify(p))}catch(e){}}
}

function restoreFloatingPanePositions(){
  ["A","B"].forEach(doc=>{
    try{
      const raw=localStorage.getItem("comparar-floating-pane-"+doc);
      if(!raw)return;
      const p=JSON.parse(raw);
      if(Number.isFinite(p.x)&&Number.isFinite(p.y)) setFloatingPanePosition(doc,p.x,p.y,false);
    }catch(e){}
  });
}

function keepFloatingPanesInViewport(){
  ["A","B"].forEach(doc=>{
    const pane=floatingPanes[doc];
    if(!pane||!pane.style.left)return;
    const r=pane.getBoundingClientRect();
    setFloatingPanePosition(doc,r.left,r.top,false);
  });
}

document.querySelectorAll(".floating-drag").forEach(handle=>{
  handle.addEventListener("pointerdown",e=>{
    const doc=handle.dataset.pane,pane=floatingPanes[doc];
    if(!pane)return;
    const r=pane.getBoundingClientRect();
    const offsetX=e.clientX-r.left,offsetY=e.clientY-r.top;
    pane.classList.add("dragging");
    handle.setPointerCapture(e.pointerId);
    const move=ev=>setFloatingPanePosition(doc,ev.clientX-offsetX,ev.clientY-offsetY,false);
    const end=ev=>{
      handle.removeEventListener("pointermove",move);
      handle.removeEventListener("pointerup",end);
      handle.removeEventListener("pointercancel",end);
      pane.classList.remove("dragging");
      const rr=pane.getBoundingClientRect();
      setFloatingPanePosition(doc,rr.left,rr.top,true);
      try{handle.releasePointerCapture(ev.pointerId)}catch(err){}
    };
    handle.addEventListener("pointermove",move);
    handle.addEventListener("pointerup",end);
    handle.addEventListener("pointercancel",end);
    e.preventDefault();
  });
});

floatingTextA.addEventListener("input",()=>pushFloatingToMain("A",floatingTextA));
floatingTextB.addEventListener("input",()=>pushFloatingToMain("B",floatingTextB));
document.getElementById("floatingCompare").addEventListener("click",()=>compareNow(false));
document.getElementById("floatingReset").addEventListener("click",()=>document.getElementById("btnReset").click());
window.addEventListener("scroll",updateFloatingEditor,{passive:true});
window.addEventListener("resize",()=>{updateFloatingEditor();keepFloatingPanesInViewport()});
restoreFloatingPanePositions();

'''
s = s[:js_start] + new_js + s[js_end:]

path.write_text(s, encoding="utf-8")
print("Converted compact bar into two draggable floating panes")
