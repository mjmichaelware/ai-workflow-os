
// AIWOS_FINAL_PROOF_DASHBOARD_V1
window.AIWOS_FINAL_PROOF_DASHBOARD_V1=true;

async function loadFinalProofDashboard(){
  const response=await fetch("/assets/final-proof-dashboard.data.json",{cache:"no-store"});
  return await response.json();
}

function proofCard(item){
  return `<article class="aiwos-proof-card">
    <span class="aiwos-proof-ok">${item.status}</span>
    <b>${item.label}</b>
    <p>${item.id}</p>
    <code>${item.artifact}</code>
  </article>`;
}

async function drawFinalProofDashboard(){
  const data=await loadFinalProofDashboard();
  const screen=document.getElementById("screen");
  if(!screen)return;
  screen.innerHTML=`<section class="aiwos-proof-dashboard">
    <article class="aiwos-proof-hero">
      <div class="aiwos-orbit"></div>
      <span class="aiwos-proof-ok">proof dashboard online</span>
      <h3>Everything routes through proof.</h3>
      <p>Visual layer, endpoint graph, generated app shell, recursive child-builder, Android wrapper scaffold, and capability matrix are visible as one local-first operator surface.</p>
    </article>
    <div class="aiwos-proof-grid">${data.proofs.map(proofCard).join("")}</div>
  </section>`;
}

document.addEventListener("click",event=>{
  const button=event.target.closest("[data-tab]");
  if(button&&button.dataset.tab==="proof"){
    setTimeout(()=>drawFinalProofDashboard().catch(error=>{
      const screen=document.getElementById("screen");
      if(screen)screen.innerHTML=`<article class="card full"><div class="label">Proof dashboard failed</div><pre>${error.message}</pre></article>`;
    }),0);
  }
});
