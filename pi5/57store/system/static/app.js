"use strict";
const $ = (id) => document.getElementById(id);
const local = ["localhost", "127.0.0.1", "[::1]"].includes(location.hostname);
let lastPosts = "", lastEvents = "", initialized = false, newestId = null;
let rotation = "auto";
try { rotation = localStorage.getItem("57store-rotation") || "auto"; } catch (_) {}
function rotate() {
  const portrait = window.innerHeight > window.innerWidth;
  const rotated = rotation === "clockwise" || (rotation === "auto" && local && portrait);
  $("terminal").classList.toggle("rotated", rotated);
  $("terminal").classList.toggle("compact", (rotated ? window.innerWidth : window.innerHeight) < 620);
  $("rotate").textContent = rotated ? "90° CW / TAP TO RESET" : "NORMAL / TAP TO ROTATE";
}
$("rotate").addEventListener("click", () => {
  rotation = $("terminal").classList.contains("rotated") ? "normal" : "clockwise";
  try { localStorage.setItem("57store-rotation", rotation); } catch (_) {}
  rotate();
});
window.addEventListener("resize", rotate);
rotate();
function timestamp(value) {
  if (!value) return "—";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "—" : new Intl.DateTimeFormat("sv-SE", {year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",hour12:false}).format(date);
}
function duration(seconds) {
  const n = Math.max(0, Math.floor(Number(seconds) || 0));
  return `${Math.floor(n/86400)}D ${String(Math.floor(n/3600)%24).padStart(2,"0")}:${String(Math.floor(n/60)%60).padStart(2,"0")}`;
}
const views = {home:"STORE",manager:"MANAGER",day:"五月七日 / DAY SHIFT",vacant:"OTHER STAFF",maxx:"MAXX / NIGHT SHIFT"};
function showView(name, updateHash = true) {
  if (!views[name]) name = "home";
  for (const view of document.querySelectorAll(".view")) view.hidden = view.id !== `view-${name}`;
  const parent = name;
  for (const button of document.querySelectorAll("[data-view]")) {
    const selected = button.closest("nav") ? button.dataset.view === parent : button.dataset.view === name;
    button.classList.toggle("active", selected);
    button.setAttribute("aria-pressed", String(selected));
  }
  $("page-name").textContent = views[name];
  $("view-"+name).scrollTop = 0;
  if (updateHash && location.hash !== "#"+name) location.hash = name;
}
for (const button of document.querySelectorAll("[data-view]")) button.addEventListener("click", () => showView(button.dataset.view));
window.addEventListener("hashchange", () => showView(location.hash.slice(1), false));
showView(location.hash.slice(1) || "home", false);
document.addEventListener("keydown", (event) => {
  if (event.altKey || event.ctrlKey || event.metaKey || /INPUT|TEXTAREA|SELECT/.test(event.target.tagName)) return;
  const name = {"1":"home","2":"manager","3":"day","4":"vacant","5":"maxx","Escape":"home"}[event.key];
  if (name) showView(name);
});
function postElement(post) {
  const li = document.createElement("li"); li.className = "post";
  const meta = document.createElement("div"); meta.className = "record-meta";
  const id = document.createElement("span"); id.textContent = `SYS / ${post.id}`;
  const time = document.createElement("time"); time.textContent = timestamp(post.published_at);
  const text = document.createElement("p"); text.textContent = post.content.length>160?post.content.slice(0,160)+"…":post.content;
  meta.append(id,time); li.append(meta,text); return li;
}
function renderFeed(data) {
  const sync = data.sync || {};
  const stale = sync.last_success && Date.now() - Date.parse(sync.last_success) > 180000;
  $("sync-state").textContent = sync.state === "online" && !stale ? "SYS / SYNCED / 60s" : sync.last_success ? "SYS / OFFLINE CACHE" : sync.state === "offline" ? "SYS / WAITING" : "SYS / RECEIVING";
  $("last-sync").textContent = sync.last_success ? `RECEIVED ${timestamp(sync.last_success)}` : "NOT SYNCED YET";
  $("maintenance-sync").textContent = timestamp(sync.last_success);
  $("record-count").textContent = `${String(data.count || 0).padStart(2,"0")} RECORDS`;
  const posts = data.posts || [], signature = JSON.stringify(posts);
  if (lastPosts === signature) return;
  lastPosts = signature;
  const latest = posts[0];
  if (latest) {
    $("latest-id").textContent = `SYS / ${latest.id}`;
    $("latest-time").textContent = timestamp(latest.published_at);
    $("latest-text").textContent = latest.content.length>280?latest.content.slice(0,280)+"…":latest.content;
    if (initialized && newestId !== latest.id) {
      $("latest").classList.remove("new-record");
      void $("latest").offsetWidth;
      $("latest").classList.add("new-record");
    }
    newestId = latest.id;
  }
  $("recent-posts").replaceChildren(...posts.slice(1,3).map(postElement));
  
  if (!posts.length) {
    $("latest-id").textContent = "SYS / —";
    $("latest-time").textContent = "—";
    $("latest-text").textContent = "No records received yet.";
    $("recent-posts").textContent = "No records received yet.";
    
  }
  initialized = true;
}
function renderStatus(data) {
  $("connection-state").textContent = data.online ? "STORE OPEN" : "OFFLINE";
  $("connection-state").classList.toggle("offline", !data.online);
  $("hostname").textContent = data.hostname;
  $("ip").textContent = data.ip;
  $("system-uptime").textContent = duration(data.system_uptime_seconds);
  $("app-uptime").textContent = `SHIFT ${duration(data.application_uptime_seconds)}`;
  $("disk-value").textContent = `${data.disk.percent}% / ${(data.disk.total_bytes/1073741824).toFixed(1)} GB`;
  $("version").textContent = `EDITION ${data.version} / SHIFT ${String(data.start_count).padStart(4,"0")}`;
}
function renderEvents(data) {
  const events = data.events || [], signature = JSON.stringify(events);
  if (lastEvents === signature) return;
  lastEvents = signature;
  $("local-events").replaceChildren(...events.slice(0,1).map(event => {
    const li = document.createElement("li"); li.className = "local-event";
    const time = document.createElement("time"); time.textContent = timestamp(event.created_at);
    const text = document.createElement("span"); text.textContent = event.message.replace(/SYSTEM ONLINE \/ SERVICE STARTED \/ RUN /g,"STORE OPEN / COUNTER READY / SHIFT ").replace(/SYSTEM OFFLINE/g,"COUNTER OFFLINE").replace(/SERVICE STOPPED/g,"COUNTER CLOSED");
    li.append(time,text); return li;
  }));
}
async function get(url) {
  const controller = new AbortController(), timer = setTimeout(() => controller.abort(), 8000);
  try {
    const response = await fetch(url, {cache:"no-store",signal:controller.signal});
    if (!response.ok) throw new Error("node unavailable");
    return await response.json();
  } finally { clearTimeout(timer); }
}
async function refresh() {
  const results = await Promise.allSettled([get("/api/status"), get("/api/sys"), get("/api/events?limit=8")]);
  if (results[0].status === "fulfilled") renderStatus(results[0].value);
  else { $("connection-state").textContent = "CONNECTION LOST"; $("connection-state").classList.add("offline"); }
  if (results[1].status === "fulfilled") renderFeed(results[1].value);
  else $("sync-state").textContent = "SYS / LOCAL SERVICE UNAVAILABLE";
  if (results[2].status === "fulfilled") renderEvents(results[2].value);
  setTimeout(refresh, 5000);
}
function clock() { $("clock").textContent = timestamp(new Date()); }
renderFeed({"posts":[{"id":4294,"published_at":"2026-08-04T16:56:04Z","modified_at":"2026-08-04T16:56:04Z","received_at":"2026-09-05T14:34:57Z","content":"buffer rail verified load distribution even\n缓冲轨 已验证 负载分布均衡","link":"https://fivsevn.com/2026/08/05/57storesys-2026-08-04-1656-d5498997d2af/"},{"id":4283,"published_at":"2026-07-26T19:04:42Z","modified_at":"2026-07-26T19:04:42Z","received_at":"2026-09-05T14:34:57Z","content":"input bank flushed trace residue\n输入库 已清理 痕迹残留轻微","link":"https://fivsevn.com/2026/07/27/57storesys-2026-07-26-1904-e54668d0f07a/"},{"id":4265,"published_at":"2026-07-18T00:57:04Z","modified_at":"2026-07-18T00:57:04Z","received_at":"2026-09-05T14:34:57Z","content":"sensor array settled slight offset\n传感器阵列 已稳定 轻微偏移","link":"https://fivsevn.com/2026/07/18/57storesys-2026-07-18-0057-bf4e71f94192/"},{"id":4174,"published_at":"2026-07-05T14:46:22Z","modified_at":"2026-07-05T14:46:22Z","received_at":"2026-09-05T14:34:57Z","content":"shelf map indexed residual mismatch\n货架图 已索引 残余失配轻微","link":"https://fivsevn.com/2026/07/05/57storesys-2026-07-05-1446-3434cf1d5a6a/"},{"id":4173,"published_at":"2026-07-05T14:45:48Z","modified_at":"2026-07-05T14:45:48Z","received_at":"2026-09-05T14:34:57Z","content":"firmware block recalibrated residual\n固件块 已重新校准 残余轻微","link":"https://fivsevn.com/2026/07/05/57storesys-2026-07-05-1445-edca7b4c920e/"},{"id":4172,"published_at":"2026-07-04T06:12:14Z","modified_at":"2026-07-04T06:12:14Z","received_at":"2026-09-05T14:34:57Z","content":"camera index recalibrated shallow jitter\n摄像索引 已重新校准 浅层抖动","link":"https://fivsevn.com/2026/07/04/57storesys-2026-07-04-0612-4be4fc6378e6/"},{"id":4129,"published_at":"2026-06-22T21:19:55Z","modified_at":"2026-06-22T21:19:55Z","received_at":"2026-09-05T14:34:57Z","content":"scan head aligned baseline scatter\n扫描头 已对齐 基线散布轻微","link":"https://fivsevn.com/2026/06/23/57storesys-2026-06-22-2119-78d054302e48/"},{"id":4087,"published_at":"2026-06-21T08:34:59Z","modified_at":"2026-06-21T08:34:59Z","received_at":"2026-09-05T14:34:57Z","content":"tag register cleared queue compression\n标签寄存器 已清除 队列压缩轻微","link":"https://fivsevn.com/2026/06/21/57storesys-2026-06-21-0834-e786718f7049/"}],"count":8,"sync":{"state":"online","last_success":"2026-09-05T17:50:10Z","last_attempt":"2026-09-05T17:50:10Z"},"interval":60});
clock(); setInterval(clock,1000); refresh();

const weatherURL = '/api/weather';
function validWeather(data) {
 const c=data?.current;
 return !!c && ['temperature_2m','relative_humidity_2m','apparent_temperature','precipitation','weather_code','wind_speed_10m','wind_direction_10m','wind_gusts_10m'].every(k=>typeof c[k]==='number' && Number.isFinite(c[k])) && Number.isFinite(Date.parse(c.time+'+08:00'));
}
function weatherName(code) {
 if(code===0)return 'CLEAR'; if(code<=3)return ['','MOSTLY CLEAR','PARTLY CLOUDY','OVERCAST'][code];
 if([45,48].includes(code))return 'FOG'; if(code>=51&&code<=57)return 'DRIZZLE';
 if(code>=61&&code<=67)return 'RAIN'; if(code>=71&&code<=77)return 'SNOW';
 if(code>=80&&code<=82)return 'SHOWERS'; if(code>=85&&code<=86)return 'SNOW SHOWERS';
 if(code>=95)return 'THUNDERSTORM';return 'UNKNOWN';
}
function beaufort(speed) {return [0.3,1.6,3.4,5.5,8,10.8,13.9,17.2,20.8,24.5,28.5,32.7].filter(x=>speed>=x).length;}
let weatherData=null;
function renderWeather(data,cached=false) {
 if(!validWeather(data))throw Error('Incomplete weather data');
 weatherData=data;
 const c=data.current;
 const old=Date.now()-Date.parse(c.time+'+08:00')>90*60*1000;
 $('weather-state').textContent=cached||old?'CACHED / RETRYING':'UPDATED / 15 MIN';
 $('weather-sky').textContent=weatherName(c.weather_code);
 $('weather-temp').textContent=c.temperature_2m.toFixed(1)+' °C';
 $('weather-feels').textContent=c.apparent_temperature.toFixed(1)+' °C';
 $('weather-humidity').textContent=c.relative_humidity_2m+'%';
 const dir=['N','NE','E','SE','S','SW','W','NW'][Math.round(c.wind_direction_10m/45)%8];
 $('weather-wind').textContent=dir+' '+c.wind_speed_10m.toFixed(1)+' m/s / BFT '+beaufort(c.wind_speed_10m);
 $('weather-gusts').textContent=c.wind_gusts_10m.toFixed(1)+' m/s';
 $('weather-rain').textContent=c.precipitation.toFixed(1)+' mm';
 $('weather-time').textContent=c.time.replace('T',' ')+' CST';
}
async function refreshWeather() {
 try {
  const delivery=await get(weatherURL);
  const data=delivery.value;
  renderWeather(data,delivery.state!=="online");
  try{localStorage.setItem('57store-outside',JSON.stringify(data));}catch(_){}
 }catch(_){if(weatherData)renderWeather(weatherData,true);else $('weather-state').textContent='UNAVAILABLE / RETRYING';}
 setTimeout(refreshWeather,60*1000);
}
try {const saved=JSON.parse(localStorage.getItem('57store-outside'));if(validWeather(saved))renderWeather(saved,true);}catch(_){}
refreshWeather();

async function refreshSignal(){
 try{
  const data=await get('/api/signal');
  if(data.value && typeof data.value.text==='string'){
   $('signal-text').textContent=data.value.text.length>300?data.value.text.slice(0,300)+'…':data.value.text;
   $('signal-date').textContent=data.value.date||'';
  }
  $('signal-state').textContent=(data.state==='online'?'SYNCED / 5 MIN':'LOCAL COPY / RETRYING')+(data.received_at?' / '+timestamp(data.received_at):'');
 }catch(_){$('signal-state').textContent='LOCAL COPY / RETRYING';}
 setTimeout(refreshSignal,60000);
}
refreshSignal();
