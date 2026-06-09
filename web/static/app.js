const $=id=>document.getElementById(id);
function pretty(x){return JSON.stringify(x,null,2)}
async function get(id,url){try{const r=await fetch(url);$(id).textContent=pretty(await r.json())}catch(e){$(id).textContent=String(e)}}
async function post(url,payload){const r=await fetch(url,{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify(payload)});return await r.json()}
function payload(){const name=$("appName").value.trim()||"generated-app";const target=$("target").value.trim()||("generated_apps/"+name);return {prompt:$("prompt").value,name,target,execute:$("execute").checked}}
async function show(promise){$("output").textContent="Working...";try{$("output").textContent=pretty(await promise)}catch(e){$("output").textContent=String(e)}}
$("researchBtn").onclick=()=>show(post("/api/research-graph",{prompt:$("prompt").value}));
$("planBtn").onclick=()=>show(post("/api/create-app",{...payload(),execute:false}));
$("createBtn").onclick=()=>show(post("/api/create-app",payload()));
$("selfBtn").onclick=()=>show(post("/api/self-bootstrap",{prompt:$("prompt").value}));
get("health","/api/health");get("tools","/api/tools");get("providers","/api/providers");get("runs","/api/runs");
