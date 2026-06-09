const $=id=>document.getElementById(id);
function pretty(x){return JSON.stringify(x,null,2)}
async function getJson(url){const r=await fetch(url+"?t="+Date.now(),{cache:"no-store"});return await r.json()}
async function post(url,payload){const r=await fetch(url+"?t="+Date.now(),{method:"POST",cache:"no-store",headers:{"content-type":"application/json","cache-control":"no-store"},body:JSON.stringify(payload)});return await r.json()}
async function show(label,promise){$("output").textContent=label+" working...";try{$("output").textContent=label+" result:\n"+pretty(await promise);refresh()}catch(e){$("output").textContent=label+" error:\n"+String(e)}}
function payload(){return {prompt:$("prompt").value,name:$("appName").value.trim()||"generated-app",execute:$("execute").checked}}
async function refresh(){try{$("health").textContent=pretty(await getJson("/api/health"));$("tools").textContent=pretty(await getJson("/api/tools"));$("android").textContent=pretty(await getJson("/api/android/status"));$("apps").textContent=pretty(await getJson("/api/generated-apps"))}catch(e){$("output").textContent=String(e)}}
$("researchBtn").onclick=()=>show("Research graph",post("/api/research-graph",{prompt:$("prompt").value}));
$("planBtn").onclick=()=>show("Plan app",post("/api/create-app",{...payload(),execute:false}));
$("createBtn").onclick=()=>show("Generate app",post("/api/create-app",payload()));
$("testBtn").onclick=()=>show("Test app",post("/api/test-app",{name:payload().name}));
$("exportBtn").onclick=()=>show("Export to Downloads",post("/api/export-app-downloads",{name:payload().name}));
$("androidBtn").onclick=()=>show("Native Android target",post("/api/android/native-target",payload()));
$("selfBtn").onclick=()=>show("Self bootstrap",post("/api/self-bootstrap",{prompt:$("prompt").value}));
if("serviceWorker" in navigator){navigator.serviceWorker.getRegistrations().then(rs=>rs.forEach(r=>r.unregister())).catch(()=>{})}
refresh();
