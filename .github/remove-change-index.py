from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# Restore original counter CSS and remove numbered index CSS block.
start=s.index('  .counter{min-width:72px;text-align:center;font-size:12.5px;font-weight:650}')
end=s.index('  .viewtoggle{', start)
replacement='  .counter{min-width:105px;text-align:center;font-size:12.5px;font-weight:650}\n\n'
s=s[:start]+replacement+s[end:]

# Remove numbered index container.
s=s.replace('      <div class="change-index" id="changeIndex" aria-label="Navegación por cambios"></div>\n','',1)

# Remove helper functions.
js_start=s.index('function renderChangeIndex(){')
js_end=s.index('function goTo(idx,keep){', js_start)
s=s[:js_start]+s[js_end:]

# Restore old counter text and remove active-index update.
s=s.replace('  document.getElementById("counter").textContent=n?(state.current+1)+" / "+n:"—";\n  document.getElementById("btnPrev").disabled=state.current<=0;\n  document.getElementById("btnNext").disabled=state.current>=n-1;\n  updateChangeIndexActive();',
            '  document.getElementById("counter").textContent=n?"Cambio "+(state.current+1)+" de "+n:"—";\n  document.getElementById("btnPrev").disabled=state.current<=0;\n  document.getElementById("btnNext").disabled=state.current>=n-1;',1)

# Remove added render calls.
for snippet in [
    '    renderChangeIndex();\n',
    '  renderChangeIndex();\n',
    '  pdfState.built=true;pdfState.building=false;renderChangeIndex();updateCounter();'
]:
    if snippet == '  pdfState.built=true;pdfState.building=false;renderChangeIndex();updateCounter();':
        s=s.replace(snippet,'  pdfState.built=true;pdfState.building=false;updateCounter();',1)
    else:
        s=s.replace(snippet,'',1)

# Remove any remaining direct render calls safely.
s=s.replace('  renderChangeIndex();\n','')
s=s.replace('    renderChangeIndex();\n','')

p.write_text(s,encoding='utf-8')
print('Removed numbered change index and restored original navigation')
