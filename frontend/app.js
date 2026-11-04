"use strict";
// Clinton Auto Detailing booking flow: service -> day/time -> details -> confirmed.
// API is same-origin in production (the FastAPI app serves this page).
const API = "";
const state = { service: "Standard Detail", size: "sedan", date: null, slot: null, price: 250, hours: 4 };
const $ = (s) => document.querySelector(s);

function showStep(n) {
  document.querySelectorAll(".step").forEach((el) => el.classList.toggle("hidden", el.dataset.step !== String(n)));
  document.querySelectorAll(".steps-indicator li").forEach((li) => li.classList.toggle("active", li.dataset.ind === String(n)));
  if (n === 3) updateSummary();
  window.scrollTo({ top: document.querySelector("#book").offsetTop - 10, behavior: "smooth" });
}
function showError(msg) { const b = $("#errorBox"); b.textContent = msg; b.classList.remove("hidden"); }
function clearError() { $("#errorBox").classList.add("hidden"); }

async function refreshQuote() {
  try {
    const r = await fetch(API + "/api/v1/bookings/quote", { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ service_type: state.service, vehicle_size: state.size }) });
    if (!r.ok) return;
    const q = await r.json(); state.price = q.estimated_price; state.hours = q.estimated_duration_hours;
    $("#quoteLine").textContent = "Estimate: $" + q.estimated_price + " \u00B7 about " + q.estimated_duration_hours + " hrs \u00B7 No deposit";
  } catch (e) { /* keep the card price as the estimate if the API is unreachable */ }
}

document.querySelectorAll("#serviceCards .card").forEach((card) => {
  card.addEventListener("click", () => {
    document.querySelectorAll("#serviceCards .card").forEach((c) => c.classList.remove("selected"));
    card.classList.add("selected"); state.service = card.dataset.service; refreshQuote();
  });
});
$("#vehicleSize").addEventListener("change", (e) => { state.size = e.target.value; refreshQuote(); });

async function loadSlots() {
  const grid = $("#slotGrid"); const date = $("#bookDate").value;
  state.date = date; state.slot = null; $("#toStep3").disabled = true;
  if (!date) { grid.innerHTML = '<p class="muted">Pick a day to see open bay times.</p>'; return; }
  grid.innerHTML = '<p class="muted">Checking open bay times\u2026</p>';
  try {
    const r = await fetch(API + "/api/v1/bookings/availability?date=" + encodeURIComponent(date) + "&service_type=" + encodeURIComponent(state.service));
    const j = await r.json();
    grid.innerHTML = "";
    j.slots.forEach((s) => {
      const b = document.createElement("button"); b.type = "button"; b.className = "slot";
      const t = new Date(s.start); b.textContent = t.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
      b.disabled = !s.available;
      b.addEventListener("click", () => { document.querySelectorAll(".slot").forEach((x) => x.classList.remove("selected"));
        b.classList.add("selected"); state.slot = s.start; $("#toStep3").disabled = false; });
      grid.appendChild(b);
    });
    if (!j.slots.some((s) => s.available)) grid.innerHTML = '<p class="muted">That day is full for this service \u2014 try the next day, or text Court at 815-718-8936.</p>';
  } catch (e) {
    grid.innerHTML = '<p class="muted">Could not load times. Text Court at 815-718-8936 and we will get you booked.</p>';
  }
}
$("#bookDate").addEventListener("change", loadSlots);
(function initDate() { const d = new Date(); d.setDate(d.getDate() + 1);
  const iso = d.toISOString().slice(0, 10); const el = $("#bookDate"); el.min = new Date().toISOString().slice(0, 10); el.value = iso; })();

function updateSummary() {
  const when = state.slot ? new Date(state.slot).toLocaleString([], { weekday: "long", month: "long", day: "numeric", hour: "numeric", minute: "2-digit" }) : "";
  const label = document.querySelector("#serviceCards .card.selected strong").textContent;
  $("#summaryLine").textContent = label + " \u00B7 " + when + " \u00B7 Estimate $" + state.price + " \u00B7 No deposit";
}

document.querySelectorAll("[data-next]").forEach((b) => b.addEventListener("click", () => { clearError(); showStep(b.dataset.next); }));

$("#detailsForm").addEventListener("submit", async (e) => {
  e.preventDefault(); clearError();
  if (!state.slot) { showError("Please pick a day and time first."); showStep(2); return; }
  const fd = new FormData(e.target);
  const notes = [];
  if ($("#optPickup").checked) notes.push("Free pickup & delivery requested");
  if ($("#optPet").checked) notes.push("Pet hair");
  if ($("#optOdor").checked) notes.push("Odor cleanup");
  const body = { name: fd.get("name"), phone: fd.get("phone"), vehicle_year: parseInt(fd.get("vehicle_year"), 10),
    vehicle_make: fd.get("vehicle_make"), vehicle_model: fd.get("vehicle_model"), vehicle_size: state.size,
    service_type: state.service, scheduled_time: state.slot, source: "website", notes: notes.join("; ") || null };
  const btn = $("#confirmBtn"); btn.disabled = true; btn.textContent = "Locking your slot\u2026";
  try {
    const r = await fetch(API + "/api/v1/bookings/create-appointment", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    const j = await r.json();
    if (!r.ok) { showError(j.detail || "That time just filled. Please pick another slot."); btn.disabled = false; btn.textContent = "Lock My Bay Slot"; return; }
    const when = new Date(state.slot).toLocaleString([], { weekday: "long", month: "long", day: "numeric", hour: "numeric", minute: "2-digit" });
    $("#doneText").textContent = body.vehicle_year + " " + body.vehicle_make + " " + body.vehicle_model + " \u00B7 " + when +
      " \u00B7 715 Park Pl, Clinton, IA. " + (j.sms_sent ? "Your confirmation text is on its way." : "Court will text your confirmation shortly.");
    showStep("done");
  } catch (err) {
    showError("Something hiccuped. Text Court at 815-718-8936 and we will book you by hand.");
    btn.disabled = false; btn.textContent = "Lock My Bay Slot";
  }
});
refreshQuote(); loadSlots();
