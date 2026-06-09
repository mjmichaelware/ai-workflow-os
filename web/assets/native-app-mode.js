
// AIWOS_NATIVE_APP_MODE_V1
window.AIWOS_NATIVE_APP_MODE_V1=true;

function syncNativeAppMode(){
  const standalone=window.matchMedia("(display-mode: standalone)").matches || navigator.standalone===true;
  document.documentElement.classList.toggle("standalone-app",standalone);
  document.documentElement.classList.toggle("browser-tab",!standalone);
  const install=document.getElementById("install-app");
  if(install && standalone){
    install.textContent="Installed";
    install.disabled=true;
  }
}
window.addEventListener("load",syncNativeAppMode);
window.matchMedia("(display-mode: standalone)").addEventListener?.("change",syncNativeAppMode);
