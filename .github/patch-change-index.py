from pathlib import Path

path = Path("index.html")
s = path.read_text(encoding="utf-8")

if "/* Numbered change index */" in s:
    print("Numbered change index already installed")
    raise SystemExit(0)

css_anchor = '  .counter{min-width:105px;text-align:center;font-size:12.5px;font-weight:650}\n\n'
css = '''  .counter{min-width:72px;text-align:center;font-size:12.5px;font-weight:650}\n\n  /* Numbered change index */\n  .change-index{\n    flex-basis:100%;\n    display:none;\n    align-items:center;\n    gap:5px;\n    max-width:100%;\n    overflow-x:auto;\n    padding:4px 2px 1px;\n    scroll-behavior:smooth;\n    scrollbar-width:none;\n    -webkit-overflow-scrolling:touch;\n  }\n  .change-index::-webkit-scrollbar{display:none}\n  .change-index button{\n    flex:0 0 auto;\n    width:26px;height:26px;\n    display:grid;place-items:center;\n    border:0;border-radius:50%;\n    background:rgba(0,0,0,.055);\n    color:var(--muted);\n    font-size:11.5px;\n    font-weight:650;\n    cursor:pointer;\n    transition:background .16s ease,color .16s ease,transform .16s ease,box-shadow .16s ease;\n  }\n  .change-index button:hover{background:rgba(0,0,0,.09);color:var(--ink)}\n  .change-index button:active{transform:scale(.94)}\n  .change-index button.active{\n    background:#1d1d1f;\n    color:#fff;\n    box-shadow:0 2px 7px rgba(0,0,0,.16);\n  }\n  @media(max-width:650px){\n    .change-index{gap:4px;padding-top:3px}\n    .change-index button{width:24px;height:24px;font-size:10.5px}\n  }\n\n'''
if css_anchor not in s:
    raise RuntimeError("CSS anchor not found")
s = s.replace(css_anchor, css, 1)

html_anchor = '''      <div class="legend">\n        <span><span class="chip add"></span>Agregado</span>\n        <span><span class="chip del"></span>Eliminado</span>\n      </div>\n    </div>\n  </nav>'''
html_repl = '''      <div class="legend">\n        <span><span class="chip add"></span>Agregado</span>\n        <span><span class="chip del"></span>Eliminado</span>\n      </div>\n      <div class="change-index" id="changeIndex" aria-label="Navegación por cambios"></div>\n    </div>\n  </nav>'''
if html_anchor not in s:
    raise RuntimeError("HTML anchor not found")
s = s.replace(html_anchor, html_repl, 1)

js_anchor = 'function goTo(idx,keep){\n'
js = '''function renderChangeIndex(){\n  const box=document.getElementById("changeIndex");\n  if(!box)return;\n  const n=state.view==="pdf"?pdfState.groups.length:state.nChanges;\n  box.innerHTML="";\n  if(!n){box.style.display="none";return}\n  box.style.display="flex";\n  const frag=document.createDocumentFragment();\n  for(let i=0;i<n;i++){\n    const b=document.createElement("button");\n    b.type="button";\n    b.textContent=String(i+1);\n    b.dataset.index=String(i);\n    b.setAttribute("aria-label","Ir al cambio "+(i+1));\n    b.addEventListener("click",()=>goTo(i));\n    frag.appendChild(b);\n  }\n  box.appendChild(frag);\n  updateChangeIndexActive();\n}\n\nfunction updateChangeIndexActive(){\n  const box=document.getElementById("changeIndex");\n  if(!box)return;\n  const buttons=[...box.querySelectorAll("button")];\n  buttons.forEach((b,i)=>b.classList.toggle("active",i===state.current));\n  const active=buttons[state.current];\n  if(active&&box.clientWidth){\n    const target=active.offsetLeft-box.clientWidth/2+active.offsetWidth/2;\n    box.scrollTo({left:Math.max(0,target),behavior:"smooth"});\n  }\n}\n\nfunction goTo(idx,keep){\n'''
if js_anchor not in s:
    raise RuntimeError("goTo anchor not found")
s = s.replace(js_anchor, js, 1)

old_counter = '''function updateCounter(){\n  const n=state.view==="pdf"?pdfState.groups.length:state.nChanges;\n  document.getElementById("counter").textContent=n?"Cambio "+(state.current+1)+" de "+n:"—";\n  document.getElementById("btnPrev").disabled=state.current<=0;\n  document.getElementById("btnNext").disabled=state.current>=n-1;\n}'''
new_counter = '''function updateCounter(){\n  const n=state.view==="pdf"?pdfState.groups.length:state.nChanges;\n  document.getElementById("counter").textContent=n?(state.current+1)+" / "+n:"—";\n  document.getElementById("btnPrev").disabled=state.current<=0;\n  document.getElementById("btnNext").disabled=state.current>=n-1;\n  updateChangeIndexActive();\n}'''
if old_counter not in s:
    raise RuntimeError("counter anchor not found")
s = s.replace(old_counter, new_counter, 1)

old_result = '''    card.style.display="block";\n    state.nChanges=id;state.current=-1;\n    requestAnimationFrame(updateFloatingEditor);'''
new_result = '''    card.style.display="block";\n    state.nChanges=id;state.current=-1;\n    renderChangeIndex();\n    requestAnimationFrame(updateFloatingEditor);'''
if old_result not in s:
    raise RuntimeError("result anchor not found")
s = s.replace(old_result, new_result, 1)

old_view = '''  state.view=v;\n  const split=v==="split"||v==="sync";'''
new_view = '''  state.view=v;\n  renderChangeIndex();\n  const split=v==="split"||v==="sync";'''
if old_view not in s:
    raise RuntimeError("view anchor not found")
s = s.replace(old_view, new_view, 1)

old_pdf_end = '''  pdfState.built=true;pdfState.building=false;updateCounter();\n}'''
new_pdf_end = '''  pdfState.built=true;pdfState.building=false;renderChangeIndex();updateCounter();\n}'''
if old_pdf_end not in s:
    raise RuntimeError("PDF end anchor not found")
s = s.replace(old_pdf_end, new_pdf_end, 1)

old_clear = '''  state.nChanges=0;state.current=-1;\n  updateFloatingEditor();\n  return true;'''
new_clear = '''  state.nChanges=0;state.current=-1;\n  renderChangeIndex();\n  updateFloatingEditor();\n  return true;'''
if old_clear not in s:
    raise RuntimeError("clear anchor not found")
s = s.replace(old_clear, new_clear, 1)

old_reset = '''  state.nChanges=0;state.current=-1;state.view="sync";\n  pdfState.built=false;pdfState.ok=false;pdfState.groups=[];'''
new_reset = '''  state.nChanges=0;state.current=-1;state.view="sync";\n  pdfState.built=false;pdfState.ok=false;pdfState.groups=[];\n  renderChangeIndex();'''
if old_reset not in s:
    raise RuntimeError("reset anchor not found")
s = s.replace(old_reset, new_reset, 1)

path.write_text(s, encoding="utf-8")
print("Installed numbered change index")
