
// AIWOS_MOBILE_COMMAND_V7_JS
window.AIWOS_MOBILE_COMMAND_V7_JS=true;

function allTabsForMobile(){
  if(typeof NAV !== "undefined" && Array.isArray(NAV))return NAV;
  return [
    {id:"overview",label:"Overview",hint:"System state"},
    {id:"build",label:"Build",hint:"Create apps"},
    {id:"apps",label:"Apps",hint:"Generated apps"},
    {id:"graph",label:"Graph",hint:"Endpoint graph"},
    {id:"proof",label:"Proof",hint:"Proof dashboard"},
    {id:"runtime",label:"Runtime",hint:"Logs and state"},
    {id:"tools",label:"Tools",hint:"Capabilities"},
    {id:"security",label:"Security",hint:"Safety"},
    {id:"research",label:"Research",hint:"Signals"},
    {id:"deploy",label:"Deploy",hint:"Exports"},
    {id:"about",label:"About",hint:"Project"},
    {id:"privacy",label:"Privacy",hint:"Privacy"},
    {id:"license",label:"License",hint:"License"}
  ];
}

function selectTabFromMobile(id){
  const direct=document.querySelector(`[data-tab="${id}"]`);
  if(direct){direct.click();return;}
  const allButtons=[...document.querySelectorAll("button")];
  const wanted=allTabsForMobile().find(item=>item.id===id);
  const label=(wanted?.label||id).toLowerCase();
  const byText=allButtons.find(button=>(button.textContent||"").trim().toLowerCase()===label);
  if(byText){byText.click();return;}
  document.dispatchEvent(new CustomEvent("aiwos-mobile-tab",{detail:{id}}));
}

function buildMobileCommandMenu(){
  if(document.getElementById("mobile-command-sheet"))return;
  const actions=document.querySelector(".top-actions") || document.body;
  const button=document.createElement("button");
  button.id="mobile-command-toggle";
  button.className="mobile-menu-toggle";
  button.type="button";
  button.innerHTML="<span>Menu</span>";
  actions.prepend(button);

  const overlay=document.createElement("div");
  overlay.id="mobile-command-overlay";
  overlay.className="mobile-menu-overlay";

  const sheet=document.createElement("section");
  sheet.id="mobile-command-sheet";
  sheet.className="mobile-menu-sheet";
  sheet.innerHTML=`<div class="mobile-menu-head"><b>AI Workflow OS command menu</b><button class="mobile-menu-close" type="button">Close</button></div><div class="mobile-menu-grid"></div>`;
  document.body.appendChild(overlay);
  document.body.appendChild(sheet);

  function currentTab(){
    return document.querySelector("[data-tab].active")?.dataset.tab || document.querySelector("button.active")?.textContent?.trim()?.toLowerCase() || "overview";
  }
  function draw(){
    const active=currentTab();
    const grid=sheet.querySelector(".mobile-menu-grid");
    grid.innerHTML=allTabsForMobile().map(item=>`<button class="mobile-menu-item ${item.id===active||item.label.toLowerCase()===active?"active":""}" type="button" data-mobile-tab="${item.id}"><b>${item.label}</b><small>${item.hint||"Open surface"}</small></button>`).join("");
  }
  function open(){
    draw();
    overlay.classList.add("open");
    sheet.classList.add("open");
    button.setAttribute("aria-expanded","true");
  }
  function close(){
    overlay.classList.remove("open");
    sheet.classList.remove("open");
    button.setAttribute("aria-expanded","false");
  }

  button.addEventListener("click",open);
  overlay.addEventListener("click",close);
  sheet.querySelector(".mobile-menu-close").addEventListener("click",close);
  sheet.addEventListener("click",event=>{
    const item=event.target.closest("[data-mobile-tab]");
    if(!item)return;
    selectTabFromMobile(item.dataset.mobileTab);
    close();
  });
  document.addEventListener("click",event=>{
    if(event.target.closest("button"))setTimeout(draw,20);
  });
}

window.addEventListener("load",buildMobileCommandMenu);
