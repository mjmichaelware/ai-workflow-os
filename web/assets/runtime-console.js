
// AIWOS_RUNTIME_CONSOLE_V1
window.AIWOS_RUNTIME_CONSOLE_V1=true;

async function getJsonLocal(path){
  const response=await fetch(path,{cache:"no-store"});
  if(!response.ok)throw new Error(path+" returned "+response.status);
  return await response.json();
}

function terminalLine(label,value){
  const safe=String(value??"").replace(/[<>&]/g,ch=>({"<":"&lt;",">":"&gt;","&":"&amp;"}[ch]));
  return `<div class="terminal-line"><span>${label}</span><code>${safe}</code></div>`;
}

function renderRuntimePayload(payload){
  const proofCards=payload.proof_files.map(item=>`<article class="dense-tile ${item.exists?"ok":"warn"}"><b>${item.path.split("/").pop()}</b><span>${item.exists?"present":"missing"}</span><code>${item.path}</code></article>`).join("");
  const assetCards=payload.assets.map(item=>`<article class="dense-tile ${item.exists?"ok":"warn"}"><b>${item.path.split("/").pop()}</b><span>${item.exists?"served asset":"missing"}</span><code>${item.path}</code></article>`).join("");
  const appCards=(payload.generated_apps||[]).slice(0,18).map(app=>`<article class="dense-tile ok"><b>${app.name}</b><span>manifest:${app.manifest} web:${app.web} builder:${app.builder}</span><code>android:${app.android_wrapper} proof:${app.proof}</code></article>`).join("");
  return `<section class="runtime-console-view">
    <article class="runtime-hero">
      <div class="runtime-orb"></div>
      <p class="eyebrow">safe inline terminal</p>
      <h3>Runtime console, proof surface, export state, and endpoint telemetry.</h3>
      <p>This is a read-only operator terminal. It displays logs and proof state. It does not execute arbitrary browser-submitted shell commands.</p>
    </article>
    <article class="terminal-panel">
      ${terminalLine("branch",payload.branch)}
      ${terminalLine("git head",payload.git_head)}
      ${terminalLine("git status",payload.git_status || "clean")}
      ${terminalLine("keys printed",payload.safety.keys_printed)}
      ${terminalLine("broad permissions",payload.safety.broad_permissions)}
      ${terminalLine("browser shell execution",payload.safety.arbitrary_shell_from_browser)}
    </article>
    <div class="dense-section"><h4>Proof executors</h4><div class="dense-grid">${proofCards}</div></div>
    <div class="dense-section"><h4>Runtime assets</h4><div class="dense-grid">${assetCards}</div></div>
    <div class="dense-section"><h4>Generated applications</h4><div class="dense-grid">${appCards || "<article class='dense-tile warn'><b>No generated apps visible</b><span>Run a build proof to populate.</span></article>"}</div></div>
  </section>`;
}

async function drawRuntimeConsole(){
  const screen=document.getElementById("screen");
  if(!screen)return;
  const payload=await getJsonLocal("/api/runtime/console");
  screen.innerHTML=renderRuntimePayload(payload);
}

async function drawVerbosePage(kind){
  const data=await getJsonLocal("/assets/verbose-pages.data.json");
  const title=data[kind+"_title"] || kind;
  const blocks=data[kind] || [];
  const screen=document.getElementById("screen");
  if(!screen)return;
  screen.innerHTML=`<section class="verbose-page">
    <article class="verbose-hero"><p class="eyebrow">${kind}</p><h3>${title}</h3><p>${blocks.length} operating notes loaded from decoupled local copy data.</p></article>
    <div class="verbose-columns">${blocks.map((text,index)=>`<article class="verbose-card"><b>${kind.toUpperCase()} ${index+1}</b><p>${text}</p></article>`).join("")}</div>
  </section>`;
}

document.addEventListener("click",event=>{
  const button=event.target.closest("[data-tab]");
  if(!button)return;
  const tab=button.dataset.tab;
  if(tab==="runtime")setTimeout(()=>drawRuntimeConsole().catch(error=>{const screen=document.getElementById("screen");if(screen)screen.innerHTML=`<article class="card full"><div class="label">Runtime failed</div><pre>${error.message}</pre></article>`;}),0);
  if(tab==="about"||tab==="privacy"||tab==="license")setTimeout(()=>drawVerbosePage(tab).catch(()=>{}),0);
});
