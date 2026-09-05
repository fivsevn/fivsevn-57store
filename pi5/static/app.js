"use strict";

const elements = {
  connection: document.querySelector("#connection-state"),
  hostname: document.querySelector("#hostname"),
  ip: document.querySelector("#ip"),
  systemUptime: document.querySelector("#system-uptime"),
  appUptime: document.querySelector("#app-uptime"),
  diskValue: document.querySelector("#disk-value"),
  diskMeter: document.querySelector("#disk-meter"),
  diskMeterRoot: document.querySelector(".meter"),
  lastEventTime: document.querySelector("#last-event-time"),
  lastEventMessage: document.querySelector("#last-event-message"),
  events: document.querySelector("#events"),
  eventCount: document.querySelector("#event-count"),
  version: document.querySelector("#version"),
  clock: document.querySelector("#clock"),
};

function duration(totalSeconds) {
  const seconds = Math.max(0, Math.floor(Number(totalSeconds) || 0));
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const tail = `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}`;
  return days ? `${String(days).padStart(2, "0")}D ${tail}` : `${tail}:${String(seconds % 60).padStart(2, "0")}`;
}

function bytes(value) {
  const units = ["B", "KB", "MB", "GB", "TB"];
  let amount = Number(value) || 0;
  let unit = 0;
  while (amount >= 1024 && unit < units.length - 1) {
    amount /= 1024;
    unit += 1;
  }
  return `${amount.toFixed(unit < 3 ? 0 : 1)} ${units[unit]}`;
}

function timestamp(value) {
  if (!value) return "NO SIGNAL";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toISOString().replace("T", " ").replace(".000Z", " UTC");
}

function setConnection(online) {
  elements.connection.classList.toggle("is-online", online);
  elements.connection.classList.toggle("is-offline", !online);
  elements.connection.querySelector(".status__label").textContent = online ? "ONLINE" : "OFFLINE";
}

function renderStatus(status) {
  setConnection(Boolean(status.online));
  elements.hostname.textContent = status.hostname || "UNAVAILABLE";
  elements.ip.textContent = status.ip || "UNAVAILABLE";
  elements.systemUptime.textContent = duration(status.system_uptime_seconds);
  elements.appUptime.textContent = duration(status.application_uptime_seconds);
  const percent = Math.max(0, Math.min(100, Number(status.disk?.percent) || 0));
  elements.diskValue.textContent = `${percent.toFixed(1)}% / ${bytes(status.disk?.total_bytes)}`;
  elements.diskMeter.style.width = `${percent}%`;
  elements.diskMeterRoot.setAttribute("aria-valuenow", String(percent));
  elements.version.textContent = `MIRROR v${status.version || "0.1"} / RUN ${String(status.start_count || 0).padStart(4, "0")}`;
  if (status.last_event) {
    elements.lastEventTime.textContent = timestamp(status.last_event.created_at);
    elements.lastEventMessage.textContent = status.last_event.message;
  }
}

function renderEvents(events) {
  elements.events.replaceChildren();
  elements.eventCount.textContent = `${String(events.length).padStart(2, "0")} RECORDS`;
  if (!events.length) {
    const item = document.createElement("li");
    item.className = "events__empty";
    item.textContent = "NO PERSISTENT EVENTS";
    elements.events.append(item);
    return;
  }
  for (const event of events) {
    const item = document.createElement("li");
    item.className = "event";
    item.dataset.level = event.level;

    const time = document.createElement("span");
    time.className = "event__time";
    time.textContent = timestamp(event.created_at);

    const source = document.createElement("span");
    source.className = "event__source";
    source.textContent = String(event.source || "UNKNOWN").toUpperCase();

    const message = document.createElement("span");
    message.className = "event__message";
    message.textContent = event.message;
    item.append(time, source, message);
    elements.events.append(item);
  }
}

async function refresh() {
  try {
    const [statusResponse, eventsResponse] = await Promise.all([
      fetch("/api/status", { cache: "no-store" }),
      fetch("/api/events?limit=8", { cache: "no-store" }),
    ]);
    if (!statusResponse.ok || !eventsResponse.ok) throw new Error("node response error");
    const status = await statusResponse.json();
    const eventPayload = await eventsResponse.json();
    renderStatus(status);
    renderEvents(eventPayload.events || []);
  } catch (_error) {
    setConnection(false);
  }
}

function tickClock() {
  elements.clock.textContent = new Date().toISOString().replace("T", " ").replace(".000Z", " UTC");
}

tickClock();
refresh();
setInterval(tickClock, 1000);
setInterval(refresh, 5000);
