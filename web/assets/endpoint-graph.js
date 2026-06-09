
// AIWOS_ENDPOINT_GRAPH_V1
window.AIWOS_ENDPOINT_GRAPH_V1=true;
async function loadEndpointGraphData(){
  const response=await fetch("/assets/endpoint-graph.data.json",{cache:"no-store"});
  return await response.json();
}
function renderEndpointGraphMap(data){
  const byId={};
  data.nodes.forEach(node=>byId[node.id]=node);
  const edges=data.edges.map(edge=>{
    const a=byId[edge[0]],b=byId[edge[1]];
    if(!a||!b)return "";
    const dx=b.x-a.x,dy=b.y-a.y;
    const length=Math.sqrt(dx*dx+dy*dy);
    const angle=Math.atan2(dy,dx)*180/Math.PI;
    return `<div class="aiwos-edge" style="left:${a.x}%;top:${a.y}%;width:${length}%;transform:rotate(${angle}deg)"></div>`;
  }).join("");
  const nodes=data.nodes.map(node=>`<div class="aiwos-graph-node" style="left:${node.x}%;top:${node.y}%"><strong>${node.label}</strong><small>${node.kind}</small><small>${node.endpoint}</small></div>`).join("");
  return `<div class="aiwos-graph-map">${edges}${nodes}</div>`;
}
async function drawEndpointGraph(){
  const data=await loadEndpointGraphData();
  const screen=document.getElementById("screen");
  if(!screen)return;
  screen.innerHTML=`<section class="aiwos-command-deck">
    <article class="aiwos-graph-panel">
      <div class="label">Endpoint graph</div>
      <h3>Every data point becomes a reachable node.</h3>
      <p>Local endpoints, proof scripts, generated apps, context packets, and research signals are rendered as a single operator map.</p>
      ${renderEndpointGraphMap(data)}
    </article>
    ${data.nodes.map(node=>`<article class="aiwos-node-card"><b>${node.label}</b><span>${node.kind}</span><code>${node.endpoint}</code></article>`).join("")}
  </section>`;
}
document.addEventListener("click",event=>{
  const button=event.target.closest("[data-tab]");
  if(button&&button.dataset.tab==="graph"){
    setTimeout(()=>drawEndpointGraph().catch(error=>{
      const screen=document.getElementById("screen");
      if(screen)screen.innerHTML=`<article class="card full"><div class="label">Graph failed</div><pre>${error.message}</pre></article>`;
    }),0);
  }
});
window.addEventListener("load",()=>{
  if(document.querySelector("[data-tab=graph].active"))drawEndpointGraph().catch(()=>{});
});
