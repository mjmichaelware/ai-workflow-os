
// AIWOS_EDITORIAL_PAGES_V6
window.AIWOS_EDITORIAL_PAGES_V6=true;

async function loadEditorialData(){
  const response=await fetch("/assets/page-content-v2.data.json",{cache:"no-store"});
  if(!response.ok)throw new Error("page content unavailable");
  return await response.json();
}

function editorialCard(kind,item,index){
  return `<article class="editorial-card">
    <span>${kind} ${index+1}</span>
    <h4>${item.title}</h4>
    <p>${item.body}</p>
  </article>`;
}

async function drawEditorialPage(kind){
  const data=await loadEditorialData();
  const list=data[kind] || [];
  const title=data[kind+"_title"] || kind;
  const screen=document.getElementById("screen");
  if(!screen)return;
  const lead=list.slice(0,3);
  const rest=list.slice(3);
  screen.innerHTML=`<section class="editorial-page-v6">
    <article class="editorial-hero">
      <div class="editorial-rings"></div>
      <p class="eyebrow">${kind}</p>
      <h3>${title}</h3>
      <p>${list.length} unique sections loaded from decoupled local content. No repeated filler blocks.</p>
    </article>
    <div class="editorial-feature-row">${lead.map((item,index)=>editorialCard(kind,item,index)).join("")}</div>
    <div class="editorial-reading-grid">${rest.map((item,index)=>editorialCard(kind,item,index+3)).join("")}</div>
  </section>`;
}

document.addEventListener("click",event=>{
  const button=event.target.closest("[data-tab]");
  if(!button)return;
  const tab=button.dataset.tab;
  if(tab==="about"||tab==="privacy"||tab==="license"){
    setTimeout(()=>drawEditorialPage(tab).catch(error=>{
      const screen=document.getElementById("screen");
      if(screen)screen.innerHTML=`<article class="card full"><div class="label">Editorial page failed</div><pre>${error.message}</pre></article>`;
    }),60);
  }
});
