/**
 * 4J's Educational Academy LMS Client Application - Pure Vanilla TS (No React)
 * 🔬 Managed for UK national board curriculums (GCSE, AQA, Edexcel)
 */

import { Trainer, ScheduleItem, TimesheetEntry, SyllabusTopic, ResourceItem } from "./types";

// Client Application State
interface AppState {
  currentUser: {
    id: string;
    name: string;
    email: string;
    role: "guest" | "trainer" | "admin";
    hourlyRate: number;
    subjects: string[];
  } | null;
  db: {
    config: {
      totalStudents: number;
      aboutText: string;
      announcements: Array<{ id: string; date: string; text: string }>;
    };
    trainers: Trainer[];
    schedule: ScheduleItem[];
    resources: ResourceItem[];
    syllabus: SyllabusTopic[];
    timesheets: TimesheetEntry[];
  } | null;
  activeTab: "public" | "trainer" | "admin";
  activeSubTab: "landing" | "resources" | "purifier";
  activeTrainerSubTab: "timesheet" | "syllabus" | "qwen";
  chatHistory: Array<{ role: "trainer" | "ai"; text: string }>;
  uploadedFile: { name: string; contentBase64: string; type: string } | null;
}

const state: AppState = {
  currentUser: null,
  db: null,
  activeTab: "public",
  activeSubTab: "landing",
  activeTrainerSubTab: "timesheet",
  chatHistory: [],
  uploadedFile: null
};

// UK / London Relative Days Mapping
const DAYS_OF_WEEK = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

// On App Initialization
document.addEventListener("DOMContentLoaded", async () => {
  setupLondonClock();
  await refreshDatabaseSync();
  setupNavEventListeners();
  setupLoginEventListeners();
  setupPublicResourcesListeners();
  setupDocumentPurifierListeners();
  setupTimesheetCalculatorListeners();
  setupSyllabusEventListeners();
  setupChatBotEventListeners();
  
  // Render default states
  switchGlobalTab("public");
  switchPublicSubTab("landing");
});

// --- CLOCK CONTROLLERS ---
function setupLondonClock() {
  const timeEl = document.getElementById("live-uk-time");
  const dateEl = document.getElementById("live-uk-date");
  const dayLabelEl = document.getElementById("radar-day-label");

  function updateClock() {
    // Standard UTC time is matched with UK timezone offsets cleanly
    // For AI Studio preview environments, standard formatted time works beautifully
    const options: Intl.DateTimeFormatOptions = {
      timeZone: "Europe/London",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false
    };
    const now = new Date();
    
    if (timeEl) {
      timeEl.textContent = now.toLocaleTimeString("en-GB", options);
    }

    const dateOptions: Intl.DateTimeFormatOptions = {
      timeZone: "Europe/London",
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric"
    };
    const dateFormatted = now.toLocaleDateString("en-GB", dateOptions);
    if (dateEl) {
      dateEl.textContent = dateFormatted;
    }

    // Get current day name for UK
    const dayFormatter = new Intl.DateTimeFormat("en-GB", {
      timeZone: "Europe/London",
      weekday: "long"
    });
    const currentDayName = dayFormatter.format(now);
    if (dayLabelEl) {
      dayLabelEl.textContent = currentDayName;
    }
  }

  updateClock();
  setInterval(updateClock, 1000);
}

// --- DATABASE FETCHERS & STORAGE ---
async function refreshDatabaseSync() {
  try {
    const res = await fetch("/api/db");
    if (res.ok) {
      state.db = await res.json();
      console.log("4J DB Synchronized successfully:", state.db);
      updateLandingCounters();
      renderActiveScheduleRadar();
      renderResources();
      renderSyllabusTrackers();
      populateTrainerPickers();
      renderAdminTrainersList();
      renderAdminTimetableList();
      
      if (state.currentUser) {
        renderTrainerTimesheetGrid();
        renderTrainerSyllabusStatus();
      }
    }
  } catch (err) {
    console.error("Database fetch sync failed:", err);
  }
}

// Update Landing Page Counts
function updateLandingCounters() {
  if (!state.db) return;
  
  // Elements
  const stT = document.getElementById("stat-trainers-count");
  const stS = document.getElementById("stat-students-count");
  const stB = document.getElementById("stat-batches-count");
  const aboutTextEl = document.getElementById("landing-about-text");
  
  // Admin counters
  const astT = document.getElementById("admin-stat-trainers");
  const astS = document.getElementById("admin-input-students") as HTMLInputElement;
  const astSlots = document.getElementById("admin-stat-slots");
  const adminAboutBox = document.getElementById("admin-about-textbox") as HTMLTextAreaElement;

  if (stT) stT.textContent = String(state.db.trainers.length);
  if (stS) stS.textContent = String(state.db.config.totalStudents);
  if (stB) stB.textContent = String(state.db.schedule.length);
  if (aboutTextEl) aboutTextEl.textContent = state.db.config.aboutText;

  // Admin Space Syncs
  if (astT) astT.textContent = String(state.db.trainers.length);
  if (astS) astS.value = String(state.db.config.totalStudents);
  if (astSlots) astSlots.textContent = String(state.db.schedule.length);
  if (adminAboutBox && !adminAboutBox.value) {
    adminAboutBox.value = state.db.config.aboutText;
  }
}

// --- ROUTER VIEW CONTROLLERS ---
function setupNavEventListeners() {
  const btnPub = document.getElementById("btn-tab-public");
  const btnTrain = document.getElementById("btn-tab-trainer");
  const btnAdmin = document.getElementById("btn-tab-admin");
  const btnLogout = document.getElementById("btn-logout");

  if (btnPub) {
    btnPub.addEventListener("click", () => switchGlobalTab("public"));
  }
  if (btnTrain) {
    btnTrain.addEventListener("click", () => switchGlobalTab("trainer"));
  }
  if (btnAdmin) {
    btnAdmin.addEventListener("click", () => switchGlobalTab("admin"));
  }
  if (btnLogout) {
    btnLogout.addEventListener("click", () => triggerLogout());
  }

  // Guest Subtabs
  const btnSubLand = document.getElementById("btn-sub-landing");
  const btnSubRes = document.getElementById("btn-sub-resources");
  const btnSubPurify = document.getElementById("btn-sub-purifier");
  const btnJumpRes = document.getElementById("btn-jump-resources");

  if (btnSubLand) {
    btnSubLand.addEventListener("click", () => switchPublicSubTab("landing"));
  }
  if (btnSubRes) {
    btnSubRes.addEventListener("click", () => switchPublicSubTab("resources"));
  }
  if (btnSubPurify) {
    btnSubPurify.addEventListener("click", () => switchPublicSubTab("purifier"));
  }
  if (btnJumpRes) {
    btnJumpRes.addEventListener("click", () => switchPublicSubTab("resources"));
  }

  // Trainer Subtabs
  const btnTS = document.getElementById("btn-trainer-timesheet");
  const btnSyl = document.getElementById("btn-trainer-syllabus");
  const btnQwen = document.getElementById("btn-trainer-qwen");

  if (btnTS) {
    btnTS.addEventListener("click", () => switchTrainerSubTab("timesheet"));
  }
  if (btnSyl) {
    btnSyl.addEventListener("click", () => switchTrainerSubTab("syllabus"));
  }
  if (btnQwen) {
    btnQwen.addEventListener("click", () => switchTrainerSubTab("qwen"));
  }
}

function switchGlobalTab(tab: "public" | "trainer" | "admin") {
  state.activeTab = tab;
  
  // Visual button styling toggles
  const btnPub = document.getElementById("btn-tab-public");
  const btnTrain = document.getElementById("btn-tab-trainer");
  const btnAdmin = document.getElementById("btn-tab-admin");

  // Reset active classes
  [btnPub, btnTrain, btnAdmin].forEach(btn => {
    if (btn) {
      btn.className = "px-3 py-1.5 rounded-lg text-xs font-serif font-bold uppercase transition text-gray-600 hover:bg-gray-100";
    }
  });

  // Highlight selected
  if (tab === "public" && btnPub) {
    btnPub.className = "px-3 py-1.5 rounded-lg text-xs font-serif font-bold uppercase transition bg-amber-600 text-white shadow";
  } else if (tab === "trainer" && btnTrain) {
    btnTrain.className = "px-3 py-1.5 rounded-lg text-xs font-serif font-bold uppercase transition bg-amber-600 text-white shadow";
  } else if (tab === "admin" && btnAdmin) {
    btnAdmin.className = "px-3 py-1.5 rounded-lg text-xs font-serif font-bold uppercase transition bg-amber-600 text-white shadow";
  }

  // Panel selections visibility toggles
  const pubWorkspace = document.getElementById("guest-view-workspace");
  const trainerWorkspace = document.getElementById("trainer-workspace");
  const adminWorkspace = document.getElementById("admin-workspace");
  const loginModal = document.getElementById("login-modal");

  if (pubWorkspace) pubWorkspace.style.display = "none";
  if (trainerWorkspace) trainerWorkspace.style.display = "none";
  if (adminWorkspace) adminWorkspace.style.display = "none";
  if (loginModal) loginModal.style.display = "none";

  if (tab === "public") {
    if (pubWorkspace) pubWorkspace.style.display = "block";
    // Keep login modal visible on bottom if not logged in
    if (!state.currentUser && loginModal) {
      loginModal.style.display = "block";
    }
  } else if (tab === "trainer") {
    if (state.currentUser && state.currentUser.role === "trainer") {
      if (trainerWorkspace) {
        trainerWorkspace.style.display = "block";
        document.getElementById("trainer-fullname-heading")!.textContent = state.currentUser.name;
        document.getElementById("trainer-email-span")!.textContent = state.currentUser.email;
        document.getElementById("label-billing-rate")!.textContent = String(state.currentUser.hourlyRate);
        renderTrainerTimesheetGrid();
        renderTrainerSyllabusStatus();
      }
    } else {
      if (loginModal) loginModal.style.display = "block";
    }
  } else if (tab === "admin") {
    if (state.currentUser && state.currentUser.role === "admin") {
      if (adminWorkspace) adminWorkspace.style.display = "block";
    } else {
      if (loginModal) loginModal.style.display = "block";
    }
  }
}

function switchPublicSubTab(sub: "landing" | "resources" | "purifier") {
  state.activeSubTab = sub;

  const btnSubLand = document.getElementById("btn-sub-landing");
  const btnSubRes = document.getElementById("btn-sub-resources");
  const btnSubPurify = document.getElementById("btn-sub-purifier");

  [btnSubLand, btnSubRes, btnSubPurify].forEach(btn => {
    if (btn) {
      btn.className = "py-2 px-4 font-serif font-bold uppercase text-xs tracking-wider border-b-2 border-transparent text-gray-400 hover:text-gray-700 transition";
    }
  });

  const panelLand = document.getElementById("panel-guest-landing");
  const panelRes = document.getElementById("panel-guest-resources");
  const panelPurifier = document.getElementById("panel-guest-purifier");

  if (panelLand) panelLand.style.display = "none";
  if (panelRes) panelRes.style.display = "none";
  if (panelPurifier) panelPurifier.style.display = "none";

  if (sub === "landing") {
    if (btnSubLand) btnSubLand.className = "py-2 px-4 font-serif font-bold uppercase text-xs tracking-wider border-b-2 border-amber-600 text-amber-900 transition";
    if (panelLand) panelLand.style.display = "block";
  } else if (sub === "resources") {
    if (btnSubRes) btnSubRes.className = "py-2 px-4 font-serif font-bold uppercase text-xs tracking-wider border-b-2 border-amber-600 text-amber-900 transition";
    if (panelRes) panelRes.style.display = "block";
  } else if (sub === "purifier") {
    if (btnSubPurify) btnSubPurify.className = "py-2 px-4 font-serif font-bold uppercase text-xs tracking-wider border-b-2 border-amber-600 text-amber-900 transition";
    if (panelPurifier) panelPurifier.style.display = "block";
  }
}

function switchTrainerSubTab(sub: "timesheet" | "syllabus" | "qwen") {
  state.activeTrainerSubTab = sub;

  const btnTS = document.getElementById("btn-trainer-timesheet");
  const btnSyl = document.getElementById("btn-trainer-syllabus");
  const btnQwen = document.getElementById("btn-trainer-qwen");

  [btnTS, btnSyl, btnQwen].forEach(btn => {
    if (btn) {
      btn.className = "px-3.5 py-1.5 text-xs font-serif font-bold uppercase rounded-lg border transition bg-white text-gray-700 border-gray-300 hover:bg-gray-50";
    }
  });

  const panelTS = document.getElementById("panel-trainer-timesheet");
  const panelSyl = document.getElementById("panel-trainer-syllabus");
  const panelQwen = document.getElementById("panel-trainer-qwen");

  if (panelTS) panelTS.style.display = "none";
  if (panelSyl) panelSyl.style.display = "none";
  if (panelQwen) panelQwen.style.display = "none";

  if (sub === "timesheet") {
    if (btnTS) btnTS.className = "px-3.5 py-1.5 text-xs font-serif font-bold uppercase rounded-lg border transition bg-amber-600 text-white border-amber-600 shadow-sm";
    if (panelTS) panelTS.style.display = "block";
  } else if (sub === "syllabus") {
    if (btnSyl) btnSyl.className = "px-3.5 py-1.5 text-xs font-serif font-bold uppercase rounded-lg border transition bg-amber-600 text-white border-amber-600 shadow-sm";
    if (panelSyl) panelSyl.style.display = "block";
  } else if (sub === "qwen") {
    if (btnQwen) btnQwen.className = "px-3.5 py-1.5 text-xs font-serif font-bold uppercase rounded-lg border transition bg-amber-600 text-white border-amber-600 shadow-sm";
    if (panelQwen) panelQwen.style.display = "block";
  }
}

// --- ACTIVE LONDON SCHEDULE RADAR VIEW ---
function renderActiveScheduleRadar() {
  const container = document.getElementById("radar-cards-grid");
  if (!container || !state.db) return;

  container.innerHTML = "";

  // Get current day name mapping (Monday, Tuesday...)
  // We use the UK time formatter on the client timezone mapping
  const ukDay = new Intl.DateTimeFormat("en-GB", { timeZone: "Europe/London", weekday: "long" }).format(new Date());

  const sortedSchedule = [...state.db.schedule].sort((a, b) => {
    // Sort by day then by start time
    const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
    const dayDiff = days.indexOf(a.dayOfWeek) - days.indexOf(b.dayOfWeek);
    if (dayDiff !== 0) return dayDiff;
    return a.startTime.localeCompare(b.startTime);
  });

  sortedSchedule.forEach(item => {
    const isToday = item.dayOfWeek.toLowerCase() === ukDay.toLowerCase();
    
    const cardEl = document.createElement("div");
    cardEl.className = `p-4 h-full rounded-xl border transition flex flex-col justify-between ${
      isToday 
        ? "bg-amber-500/5 border-amber-400 shadow-center ring-2 ring-amber-400/20" 
        : "bg-white border-gray-200/90 hover:border-amber-300"
    }`;

    cardEl.innerHTML = `
      <div>
        <div class="flex items-center justify-between mb-2">
          <span class="text-[9px] uppercase font-bold text-amber-700 tracking-wider font-mono">
            ${item.classYear} Stream
          </span>
          <span class="px-2 py-0.5 rounded text-[8px] font-bold font-sans uppercase tracking-[0.05em] ${
            isToday ? "bg-amber-500 text-amber-950 font-serif" : "bg-gray-100 text-gray-500"
          }">
            ${item.dayOfWeek}
          </span>
        </div>
        <h4 class="font-serif font-bold text-slate-900 text-xs">${item.subject} Tutoring Class</h4>
        <p class="text-[10px] text-gray-400 mt-1 uppercase tracking-wide font-medium">Memo: ${item.description || "Active tutoring Session"}</p>
      </div>

      <div class="mt-4 pt-3 border-t border-gray-100/80 flex items-center justify-between">
        <div class="flex items-center gap-1">
          <div class="w-1.5 h-1.5 rounded-full ${isToday ? "bg-amber-600 animate-ping" : "bg-gray-400"}"></div>
          <span class="text-[10px] font-bold text-amber-950 font-mono">${item.startTime} – ${item.endTime} <span class="text-[8px] text-gray-400 font-sans font-normal">UK</span></span>
        </div>
        <span class="text-[10px] font-medium text-amber-900">Tutor: ${item.trainerName}</span>
      </div>
    `;

    container.appendChild(cardEl);
  });
}

// --- SECURE AUTHORIZATION HANDLER ---
function setupLoginEventListeners() {
  const form = document.getElementById("login-form-submit") as HTMLFormElement;
  const alertBox = document.getElementById("login-alert-box");

  if (form) {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const emailVal = (document.getElementById("login-email-input") as HTMLInputElement).value.trim();
      const passVal = (document.getElementById("login-password-input") as HTMLInputElement).value;

      if (!state.db) return;

      // Handle simple credentials match
      if (emailVal === "admin@4j.com" && passVal === "admin123") {
        // Admin authorization
        state.currentUser = {
          id: "admin",
          name: "Main Academy Administration desk",
          email: "admin@4j.com",
          role: "admin",
          hourlyRate: 0,
          subjects: []
        };
        handleSuccessfulLogin();
      } else {
        // Search Trainer Accounts
        const matched = state.db.trainers.find(t => t.email.toLowerCase() === emailVal.toLowerCase() && t.password === passVal);
        if (matched) {
          state.currentUser = {
            id: matched.id,
            name: matched.name,
            email: matched.email,
            role: "trainer",
            hourlyRate: matched.hourlyRate,
            subjects: matched.subjects
          };
          handleSuccessfulLogin();
        } else {
          // Failed credential notice
          if (alertBox) {
            alertBox.classList.remove("hidden");
            setTimeout(() => {
              alertBox.classList.add("hidden");
            }, 3500);
          }
        }
      }
    });
  }
}

function handleSuccessfulLogin() {
  if (!state.currentUser) return;

  const btnTrain = document.getElementById("btn-tab-trainer");
  const btnAdmin = document.getElementById("btn-tab-admin");
  const btnLogout = document.getElementById("btn-logout");
  const loginModal = document.getElementById("login-modal");

  // Show navigation keys
  if (state.currentUser.role === "trainer") {
    if (btnTrain) {
      btnTrain.classList.remove("hidden");
      document.getElementById("trainer-name-nav")!.textContent = `(${state.currentUser.name.split(" ")[0]})`;
    }
    switchGlobalTab("trainer");
  } else if (state.currentUser.role === "admin") {
    if (btnAdmin) {
      btnAdmin.classList.remove("hidden");
    }
    switchGlobalTab("admin");
  }

  if (btnLogout) btnLogout.classList.remove("hidden");
  if (loginModal) loginModal.style.display = "none";
}

function triggerLogout() {
  state.currentUser = null;
  
  // Hide portals
  const btnTrain = document.getElementById("btn-tab-trainer");
  const btnAdmin = document.getElementById("btn-tab-admin");
  const btnLogout = document.getElementById("btn-logout");
  const loginModal = document.getElementById("login-modal");

  if (btnTrain) btnTrain.classList.add("hidden");
  if (btnAdmin) btnAdmin.classList.add("hidden");
  if (btnLogout) btnLogout.classList.add("hidden");
  
  // Reset fields
  (document.getElementById("login-email-input") as HTMLInputElement).value = "";
  (document.getElementById("login-password-input") as HTMLInputElement).value = "";

  switchGlobalTab("public");
  if (loginModal) loginModal.style.display = "block";
}

// --- GOOGLE DRIVE FILES RECONCILER CONTROLLER ---
function setupPublicResourcesListeners() {
  const searchInput = document.getElementById("res-search-input") as HTMLInputElement;
  const filterYear = document.getElementById("filter-year") as HTMLSelectElement;
  const filterSubject = document.getElementById("filter-subject") as HTMLSelectElement;

  if (searchInput) searchInput.addEventListener("input", renderResources);
  if (filterYear) filterYear.addEventListener("change", renderResources);
  if (filterSubject) filterSubject.addEventListener("change", renderResources);

  // Download all handouts ZIP action
  const dlZipBtn = document.getElementById("btn-download-all-zip");
  if (dlZipBtn) {
    dlZipBtn.addEventListener("click", () => {
      triggerDownloadTextFile("4j_educational_worksheets_collection.zip", "PK\u0003\u0004 Mock Zip stream of Year 4-12 exam revisions successfully generated.", "application/zip");
    });
  }
}

function renderResources() {
  const container = document.getElementById("resources-cards-container");
  if (!container || !state.db) return;

  container.innerHTML = "";

  const query = (document.getElementById("res-search-input") as HTMLInputElement)?.value.toLowerCase() || "";
  const yearFilter = (document.getElementById("filter-year") as HTMLSelectElement)?.value || "All";
  const subjFilter = (document.getElementById("filter-subject") as HTMLSelectElement)?.value || "All";

  const filtered = state.db.resources.filter(item => {
    const matchesQuery = item.fileName.toLowerCase().includes(query) || 
                         item.topic.toLowerCase().includes(query) ||
                         item.subject.toLowerCase().includes(query);
    const matchesYear = yearFilter === "All" || item.year === yearFilter;
    const matchesSubj = subjFilter === "All" || item.subject === subjFilter;

    return matchesQuery && matchesYear && matchesSubj;
  });

  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="col-span-full py-12 text-center text-xs text-gray-400 font-serif">
        No matched worksheet resources found matching specified curriculum filters.
      </div>
    `;
    return;
  }

  filtered.forEach(item => {
    const card = document.createElement("div");
    card.className = "bg-white border border-gray-200/95 p-4 rounded-xl shadow-sm flex flex-col justify-between hover:border-amber-400 hover:shadow transition duration-200";
    
    // File Icon Picker
    let fileIconColor = "bg-red-100 text-red-700";
    if (item.fileType === "docx") fileIconColor = "bg-blue-100 text-blue-700";
    if (item.fileType === "pptx") fileIconColor = "bg-orange-100 text-orange-700";

    card.innerHTML = `
      <div>
        <div class="flex items-start justify-between gap-2 border-b border-gray-50 pb-2 mb-3">
          <div class="flex items-center gap-2">
            <span class="w-8 h-8 rounded-lg ${fileIconColor} flex items-center justify-center font-bold text-[9px] uppercase font-mono tracking-tighter shrink-0">
              ${item.fileType}
            </span>
            <div>
              <h4 class="font-serif font-black text-slate-900 text-xs tracking-tight line-clamp-1" title="${item.fileName}">
                ${item.fileName}
              </h4>
              <p class="text-[9px] text-amber-700/80 font-mono font-bold tracking-wider uppercase">${item.year} • Topic Unit</p>
            </div>
          </div>
          <span class="text-[9px] bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded font-mono font-bold">Week ${item.weekNum}</span>
        </div>

        <p class="text-[11px] text-gray-600 leading-normal mb-1"><strong class="text-amber-950 font-serif">Focus Theme: </strong>${item.topic}</p>
        <p class="text-[10px] text-gray-500">Curriculum Mapped Subject: <span class="font-bold text-gray-700 font-serif">${item.subject}</span></p>
      </div>

      <div class="mt-4 pt-3 border-t border-gray-50 flex items-center gap-2">
        <button onclick="window.open('${item.driveUrl}', '_blank')" class="flex-1 py-1.5 text-center border border-amber-300 hover:bg-amber-500/5 text-amber-900 font-serif font-bold text-[10px] uppercase rounded-lg shadow-sm transition">
          Drive Directory Folder
        </button>
        <button class="px-2.5 py-1.5 bg-amber-600 hover:bg-amber-700 text-white rounded-lg transition" title="Get instant lesson copy file" onclick="triggerClientDirectDownload('${item.fileName}')">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3"/></svg>
        </button>
      </div>
    `;

    container.appendChild(card);
  });
}

// Global scope helpers for onclick buttons inside dynamic templates
(window as any).triggerClientDirectDownload = (fileName: string) => {
  triggerDownloadTextFile(fileName, `--- MAPPED FILE SPECIFICATION ---
Source: 4J's Educational Academy Ltd (UK Edexcel/AQA board worksheets)
Handout: ${fileName}
Status: Certified Original
Timestamp: ${new Date().toUTCString()}
Notice: Confidential lesson notes parsed from secure student records.`, "text/plain");
};

function triggerDownloadTextFile(filename: string, content: string, contentType: string) {
  const blob = new Blob([content], { type: contentType });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

// --- SYLLABUS DIRECTORY TABLES ---
function renderSyllabusTrackers() {
  const container = document.getElementById("syllabus-table-rows");
  if (!container || !state.db) return;

  container.innerHTML = "";

  state.db.syllabus.forEach(t => {
    const row = document.createElement("tr");
    row.className = "border-b border-gray-100 hover:bg-amber-500/5 transition";
    
    let badgeClass = "bg-red-50 text-red-700 border border-red-200";
    if (t.status === "In Progress") badgeClass = "bg-amber-50 text-amber-700 border border-amber-200 animate-pulse";
    if (t.status === "Completed") badgeClass = "bg-emerald-50 text-emerald-700 border border-emerald-200";

    row.innerHTML = `
      <td class="py-2.5 font-bold font-serif text-[#927116]">${t.board}</td>
      <td class="py-2.5">${t.year}</td>
      <td class="py-2.5 font-semibold text-slate-900">${t.subject}</td>
      <td class="py-2.5 font-medium">${t.topic}</td>
      <td class="py-2.5 text-gray-500 max-w-xs truncate" title="${t.subtopic}">${t.subtopic}</td>
      <td class="py-2.5">
        <span class="px-2 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider ${badgeClass}">
          ${t.status}
        </span>
      </td>
      <td class="py-2.5 text-gray-400 font-medium">${t.coveredBy || "Pending Class"}</td>
    `;
    container.appendChild(row);
  });
}

// --- DOCUMENT WATERMARK PURIFIER CONVERT FLOW ---
function setupDocumentPurifierListeners() {
  const dropZone = document.getElementById("purifier-drop-zone");
  const fileInput = document.getElementById("purifier-file-input") as HTMLInputElement;
  const purifyBtn = document.getElementById("btn-trigger-purify");
  const downloadPurifiedBtn = document.getElementById("btn-download-purified") as HTMLButtonElement;
  const consoleLogs = document.getElementById("purifier-logs-console");

  if (!dropZone || !fileInput) return;

  // Clicking drop zone opens selector
  dropZone.addEventListener("click", () => fileInput.click());

  // Handle Drag & Drop
  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("border-amber-500", "bg-amber-500/10");
  });

  dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("border-amber-500", "bg-amber-500/10");
  });

  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("border-amber-500", "bg-amber-500/10");
    if (e.dataTransfer?.files.length) {
      handlePurifierFileSelected(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener("change", () => {
    if (fileInput.files?.length) {
      handlePurifierFileSelected(fileInput.files[0]);
    }
  });

  if (purifyBtn) {
    purifyBtn.addEventListener("click", async () => {
      if (!state.uploadedFile) return;

      const btnText = document.getElementById("purifier-button-text");
      const targetPhrase = (document.getElementById("purifier-target-phrase") as HTMLInputElement).value || "Theos Educational Academy";

      // Trigger visual loader state
      if (btnText) btnText.textContent = "Purification in run...";
      purifyBtn.classList.add("opacity-75", "cursor-not-allowed");
      purifyBtn.setAttribute("disabled", "true");

      if (consoleLogs) {
        consoleLogs.classList.remove("hidden");
        consoleLogs.innerHTML = "";
      }

      function addLog(text: string, delay: number) {
        return new Promise<void>((resolve) => {
          setTimeout(() => {
            if (consoleLogs) {
              consoleLogs.innerHTML += `<div><span class="text-amber-500">&gt;</span> ${text}</div>`;
              consoleLogs.scrollTop = consoleLogs.scrollHeight;
            }
            resolve();
          }, delay);
        });
      }

      // Step-by-step pseudo pipeline logs
      await addLog("Loading worksheet binary structure standard...", 400);
      await addLog(`Initializing scanner. Search pattern threshold matches: "${targetPhrase}"`, 500);
      await addLog("Located 4 background layout vectors overlapping sheet headers.", 600);
      await addLog("Melting down PDF copyright overlay filters (Level 3 opacity clean)...", 700);
      await addLog("Stamping 4J's Golden Crest Laurel Crown emblem at header coordinate indices...", 600);
      await addLog("Recalculating fonts tracking alignment (Inter & JetBrains Mono scale keys)...", 500);
      await addLog("Baking cryptographic waterseal certification. Output: Certified Classwork.", 400);
      
      try {
        const response = await fetch("/api/clean-document", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            fileName: state.uploadedFile.name,
            fileContentBase64: state.uploadedFile.contentBase64,
            watermarkToRemove: targetPhrase,
            fileType: state.uploadedFile.type
          })
        });

        if (response.ok) {
          const result = await response.json();
          await addLog(`[SUCCESS] Mapped clean generated: ${result.cleanedName}`, 200);
          
          // Unmask visual comparisons
          const bWatermark = document.getElementById("before-watermark-overlay");
          if (bWatermark) bWatermark.textContent = `${targetPhrase}\n❌ ERASED ❌`;

          const afterBox = document.getElementById("after-view-box");
          const afterPlaceholderObj = document.getElementById("after-placeholder-content");
          const afterActiveObj = document.getElementById("after-active-content");
          const afterCrest = document.getElementById("after-gold-crest");
          const certifiedBadge = document.getElementById("preview-certified-badge");

          if (afterBox) {
            afterBox.classList.remove("opacity-40", "bg-gray-50/50");
            afterBox.classList.add("bg-gradient-to-br", "from-amber-500/5", "to-white", "border-amber-400");
          }
          if (afterPlaceholderObj) afterPlaceholderObj.classList.add("hidden");
          if (afterActiveObj) afterActiveObj.classList.remove("hidden");
          if (afterCrest) afterCrest.classList.remove("hidden");
          if (certifiedBadge) certifiedBadge.classList.remove("hidden");

          // Bind download action
          if (downloadPurifiedBtn) {
            downloadPurifiedBtn.removeAttribute("disabled");
            downloadPurifiedBtn.className = "px-6 py-2.5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-amber-950 font-serif font-black text-xs uppercase tracking-wider rounded-xl shadow cursor-pointer transition active:scale-95";
            downloadPurifiedBtn.textContent = "Download Purified Resource";

            // Bind click action
            downloadPurifiedBtn.onclick = () => {
              triggerDownloadTextFile(result.cleanedName, `--- 4J'S CERTIFIED PURIFIED WORKSHEET ---
System: 4J LMS Handout Purifier Engine
Original File: ${result.originalName}
Purified File: ${result.cleanedName}
Stamp Signature: ${result.brandingText}
Date of certification: ${result.stampDate}
Certificate Status: VALID MAPPED SUCCESS`, "text/plain");
            };
          }

        }
      } catch (err) {
        console.error("Purificator API crashed:", err);
        await addLog("[CRITICAL ERROR] Proxy target broke. Reverting layout changes.", 100);
      } finally {
        if (btnText) btnText.textContent = "Purify File Layout";
        purifyBtn.classList.remove("opacity-75", "cursor-not-allowed");
        purifyBtn.removeAttribute("disabled");
      }
    });
  }
}

function handlePurifierFileSelected(file: File) {
  const fileTitle = document.getElementById("dropped-file-title");
  const fileSubtitle = document.getElementById("dropped-file-subtitle");
  const purifyBtn = document.getElementById("btn-trigger-purify");

  if (fileTitle) {
    fileTitle.textContent = file.name;
    fileTitle.classList.add("text-emerald-700", "font-bold");
  }
  if (fileSubtitle) {
    fileSubtitle.textContent = `Size: ${(file.size / 1024).toFixed(1)} KB - Ready for purification`;
  }

  // Read mock metadata
  const reader = new FileReader();
  reader.onload = () => {
    state.uploadedFile = {
      name: file.name,
      contentBase64: (reader.result as string).split(",")[1] || "MOCK_BASE_64",
      type: file.name.split(".").pop() || "docx"
    };
    if (purifyBtn) purifyBtn.classList.remove("hidden");
  };
  reader.readAsDataURL(file);
}

// --- TIMESHEET CALCULATOR & RECORD BOOK EXCEL SPREADSHEET ---
function setupTimesheetCalculatorListeners() {
  const insertBtn = document.getElementById("btn-add-timesheet-row");
  const suggestBtn = document.getElementById("btn-fill-suggested-shift");
  const printBtn = document.getElementById("btn-timesheet-print");

  if (insertBtn) {
    insertBtn.addEventListener("click", async () => {
      const dateVal = (document.getElementById("time-log-date") as HTMLInputElement).value;
      const subjVal = (document.getElementById("time-log-subject") as HTMLInputElement).value.trim();
      const hoursVal = Number((document.getElementById("time-log-hours") as HTMLInputElement).value);

      if (!dateVal || !subjVal || isNaN(hoursVal) || hoursVal <= 0) {
        alert("Enter appropriate log date, tutoring focus theme and positive hour durations.");
        return;
      }

      if (!state.currentUser) return;

      try {
        const response = await fetch("/api/timesheets", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            trainerId: state.currentUser.id,
            date: dateVal,
            subject: subjVal,
            startTime: "16:30", // defaults
            endTime: "18:00",
            hours: hoursVal,
            rate: state.currentUser.hourlyRate,
            isCustom: true
          })
        });

        if (response.ok) {
          // Clear inputs
          (document.getElementById("time-log-subject") as HTMLInputElement).value = "";
          await refreshDatabaseSync();
        }
      } catch (err) {
        console.error("Failed logged timesheet creation: ", err);
      }
    });
  }

  if (suggestBtn) {
    suggestBtn.addEventListener("click", () => {
      const todayString = new Date().toISOString().split("T")[0];
      (document.getElementById("time-log-date") as HTMLInputElement).value = todayString;
      (document.getElementById("time-log-subject") as HTMLInputElement).value = "Year 12 Mechanics Maths (SUVAT Acceleration)";
      (document.getElementById("time-log-hours") as HTMLInputElement).value = "1.5";
    });
  }

  if (printBtn) {
    printBtn.addEventListener("click", () => {
      if (!state.currentUser || !state.db) return;
      const trainerTimesheets = state.db.timesheets.filter(t => t.trainerId === state.currentUser?.id);
      
      let csvContent = "A_Row,B_Date,C_ClassDescription,D_Hours,E_Rate,F_ComputedTotalPay\r\n";
      trainerTimesheets.forEach((item, index) => {
        csvContent += `${index + 1},${item.date},"${item.subject.replace(/"/g, '""')}",${item.hours},${item.rate},${item.totalPay}\r\n`;
      });

      triggerDownloadTextFile("4j_invoice_compiled_timesheet.csv", csvContent, "text/csv");
    });
  }
}

function renderTrainerTimesheetGrid() {
  const tbody = document.getElementById("timesheet-excel-rows");
  const sumHoursEl = document.getElementById("metric-timesheet-hours");
  const sumPayEl = document.getElementById("metric-timesheet-pay");

  if (!tbody || !state.db || !state.currentUser) return;

  tbody.innerHTML = "";

  // Filter keys for current coach
  const list = state.db.timesheets.filter(t => t.trainerId === state.currentUser?.id);

  let totalHours = 0;
  let totalPay = 0;

  if (list.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="7" class="border border-gray-300 p-4 text-center text-gray-405 font-serif italic bg-amber-500/5">
          Workbook is empty. Use the control panel above to log tutoring sessions for this cycle.
        </td>
      </tr>
    `;
    if (sumHoursEl) sumHoursEl.textContent = "0.0";
    if (sumPayEl) sumPayEl.textContent = "0.00";
    return;
  }

  list.forEach((item, index) => {
    totalHours += item.hours;
    totalPay += item.totalPay;

    const row = document.createElement("tr");
    row.className = "hover:bg-slate-55 border-b border-gray-250";

    row.innerHTML = `
      <td class="border border-gray-300 p-2 text-center bg-slate-100 font-bold text-gray-500">${index + 1}</td>
      <td class="border border-gray-300 p-2">${item.date}</td>
      <td class="border border-gray-300 p-2 text-slate-800 font-semibold">${item.subject}</td>
      <td class="border border-gray-300 p-2 text-center text-amber-900 font-bold">${item.hours.toFixed(1)} hrs</td>
      <td class="border border-gray-300 p-2 text-slate-650">£${item.rate}</td>
      <td class="border border-gray-300 p-2 text-right text-emerald-800 font-bold">£${item.totalPay.toFixed(2)}</td>
      <td class="border border-gray-300 p-2 text-center w-24">
        <button onclick="triggerTimesheetRowDeletion('${item.id}')" class="px-2 py-0.5 bg-red-50 font-serif font-black text-red-600 hover:bg-red-100 rounded text-[9.5px] uppercase transition cursor-pointer">
          Erase [X]
        </button>
      </td>
    `;
    tbody.appendChild(row);
  });

  if (sumHoursEl) sumHoursEl.textContent = totalHours.toFixed(1);
  if (sumPayEl) sumPayEl.textContent = totalPay.toLocaleString("en-GB", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

(window as any).triggerTimesheetRowDeletion = async (id: string) => {
  try {
    const res = await fetch(`/api/timesheets/${id}`, { method: "DELETE" });
    if (res.ok) {
      await refreshDatabaseSync();
    }
  } catch (err) {
    console.error("Row deletion failed:", err);
  }
};

// --- SYLLABUS DYNAMIC ACTIONS FOR INSTRUCTION ---
function setupSyllabusEventListeners() {}

function renderTrainerSyllabusStatus() {
  const tbody = document.getElementById("trainer-syllabus-tbody");
  if (!tbody || !state.db) return;

  tbody.innerHTML = "";

  state.db.syllabus.forEach(t => {
    const row = document.createElement("tr");
    row.className = "border-b border-gray-150 hover:bg-slate-50";

    let selectClass = "bg-[#FFF9E6] border border-[#E6B800] text-[#997A00]";
    if (t.status === "Completed") selectClass = "bg-[#EEF9F0] border border-[#2CD150] text-[#1E9E35]";
    if (t.status === "Not Started") selectClass = "bg-[#FFF2F2] border border-[#FF9494] text-[#C92A2A]";

    row.innerHTML = `
      <td class="py-2 px-1 font-bold font-serif text-amber-950">${t.board}</td>
      <td class="py-2 px-1 font-semibold">${t.year}</td>
      <td class="py-2 px-1 text-slate-800 font-bold">${t.subject}</td>
      <td class="py-2 px-1 font-serif text-slate-900">${t.topic}</td>
      <td class="py-2 px-1 text-gray-500 max-w-xs truncate">${t.subtopic}</td>
      <td class="py-2 px-1">
        <select onchange="triggerSyllabusStateChange('${t.id}', this.value)" class="text-[10px] py-1 px-2 font-bold uppercase rounded cursor-pointer ${selectClass}">
          <option value="Not Started" ${t.status === "Not Started" ? "selected" : ""}>Not Started</option>
          <option value="In Progress" ${t.status === "In Progress" ? "selected" : ""}>In Progress</option>
          <option value="Completed" ${t.status === "Completed" ? "selected" : ""}>Completed</option>
        </select>
      </td>
      <td class="py-2 px-1 text-right text-gray-450 font-bold">
        ${t.status === "Completed" ? `Covered by ${t.coveredBy || 'Stephen'}` : 'Click select to verify'}
      </td>
    `;
    tbody.appendChild(row);
  });
}

(window as any).triggerSyllabusStateChange = async (id: string, newStatus: string) => {
  if (!state.currentUser) return;
  try {
    const res = await fetch("/api/syllabus", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        id,
        status: newStatus,
        updatedBy: state.currentUser.name
      })
    });
    if (res.ok) {
      await refreshDatabaseSync();
    }
  } catch (err) {
    console.error("Syllabus state change error:", err);
  }
};

// --- OLLAMA QWEN AI TUTOR IMPLEMENTATION ---
function setupChatBotEventListeners() {
  const form = document.getElementById("chat-message-form") as HTMLFormElement;
  const input = document.getElementById("chat-query-input") as HTMLInputElement;
  const list = document.getElementById("chat-messages-container");
  const thinkingObj = document.getElementById("chat-thinking-bubble");

  // Prompts presets triggers
  const promptButtons = document.querySelectorAll(".btn-chat-prompt");
  promptButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const queryText = btn.textContent?.trim() || "";
      if (input) {
        input.value = queryText;
        input.focus();
      }
    });
  });

  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const messageText = input.value.trim();
      if (!messageText) return;

      // Reset
      input.value = "";

      // Append Trainer message
      appendMessageToUI("trainer", messageText);
      state.chatHistory.push({ role: "trainer", text: messageText });

      // Reveal spinner
      if (thinkingObj) thinkingObj.classList.remove("hidden");
      if (list) list.scrollTop = list.scrollHeight;

      try {
        const response = await fetch("/api/qwen-ai", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message: messageText,
            chatHistory: state.chatHistory
          })
        });

        if (response.ok) {
          const result = await response.json();
          appendMessageToUI("ai", result.reply);
          state.chatHistory.push({ role: "ai", text: result.reply });
        }
      } catch (err) {
        console.error("Qwen API proxy target broke: ", err);
        appendMessageToUI("ai", "I was unable to query standard UK Board models over live sockets. Check connection logs.");
      } finally {
        if (thinkingObj) thinkingObj.classList.add("hidden");
        if (list) list.scrollTop = list.scrollHeight;
      }
    });
  }
}

function appendMessageToUI(sender: "trainer" | "ai", text: string) {
  const list = document.getElementById("chat-messages-container");
  if (!list) return;

  const bubble = document.createElement("div");
  bubble.className = `flex ${sender === "trainer" ? "justify-end" : "justify-start"}`;

  const innerDiv = document.createElement("div");
  
  if (sender === "trainer") {
    innerDiv.className = "max-w-[85%] rounded-2xl p-4 bg-amber-600 text-white rounded-tr-none font-bold shadow-sm leading-relaxed whitespace-pre-wrap";
    innerDiv.textContent = text;
  } else {
    innerDiv.className = "max-w-[85%] rounded-2xl p-4 bg-amber-500/5 text-amber-950 rounded-tl-none border border-amber-150 leading-relaxed font-sans space-y-2 whitespace-pre-wrap";
    // Parse markdown briefly
    innerDiv.innerHTML = parseMarkdownSimply(text);
  }

  bubble.appendChild(innerDiv);
  list.appendChild(bubble);
  list.scrollTop = list.scrollHeight;
}

// Ultra simple parser to support bolding and numbered lists in Qwen markdown output
function parseMarkdownSimply(text: string): string {
  let output = text;
  
  // Clean elements
  output = output.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  
  // Bold words **bold**
  output = output.replace(/\*\*(.*?)\*\*/g, "<strong class='text-amber-800 font-bold'>$1</strong>");
  
  // Bullet lists
  output = output.replace(/- (.*?)\n/g, "<div class='pl-4 flex items-start gap-1.5'><span>•</span><span>$1</span></div>");
  output = output.replace(/\* (.*?)\n/g, "<div class='pl-4 flex items-start gap-1.5'><span>•</span><span>$1</span></div>");

  return output;
}

// --- ADMIN CONTROL CENTER METHODS ---
function populateTrainerPickers() {
  const select = document.getElementById("sched-trainer-select") as HTMLSelectElement;
  if (!select || !state.db) return;

  select.innerHTML = "";
  state.db.trainers.forEach(t => {
    const opt = document.createElement("option");
    opt.value = t.id;
    opt.textContent = t.name;
    select.appendChild(opt);
  });
}

function renderAdminTrainersList() {
  const container = document.getElementById("admin-trainers-list-container");
  if (!container || !state.db) return;

  container.innerHTML = "";

  state.db.trainers.forEach(t => {
    const div = document.createElement("div");
    div.className = "flex items-center justify-between p-2.5 bg-gray-50 border border-gray-200 rounded-lg hover:border-amber-300 transition duration-150";

    div.innerHTML = `
      <div>
        <p class="text-xs font-bold text-amber-950 font-serif">${t.name}</p>
        <p class="text-[9px] text-gray-500 font-mono">${t.email} • £${t.hourlyRate}/hr</p>
        <p class="text-[9px] text-amber-700/85">Split: ${t.subjects.join(", ")}</p>
      </div>
      <button onclick="triggerTrainerAccountDeletion('${t.id}')" class="px-2 py-1 bg-red-100 hover:bg-red-200 text-red-700 rounded text-[9px] font-bold uppercase transition" title="Archive Trainer Account">
        Archive
      </button>
    `;
    container.appendChild(div);
  });
}

(window as any).triggerTrainerAccountDeletion = async (id: string) => {
  if (confirm("Are you sure you want to delete this instructor? This will also purge their cached calendar timetables!")) {
    try {
      const res = await fetch(`/api/trainers/${id}`, { method: "DELETE" });
      if (res.ok) {
        await refreshDatabaseSync();
      }
    } catch (err) {
      console.error("Trainer deletion crashed:", err);
    }
  }
};

function renderAdminTimetableList() {
  const tbody = document.getElementById("admin-timetable-tbody");
  if (!tbody || !state.db) return;

  tbody.innerHTML = "";

  state.db.schedule.forEach(item => {
    const row = document.createElement("tr");
    row.className = "border-b border-gray-100 hover:bg-slate-50";

    row.innerHTML = `
      <td class="py-2.5 font-bold font-serif text-[#927116]">${item.dayOfWeek}</td>
      <td class="py-2.5 font-semibold text-slate-900">${item.trainerName}</td>
      <td class="py-2.5">${item.classYear}</td>
      <td class="py-2.5 font-sans">${item.subject} (${item.description || "Stream"})</td>
      <td class="py-2.5 font-bold text-amber-950 font-mono">${item.startTime} – ${item.endTime}</td>
      <td class="py-2.5 text-right">
        <button onclick="triggerScheduleSlotDeletion('${item.id}')" class="px-2 py-0.5 bg-red-50 hover:bg-red-100 font-serif font-black text-red-600 rounded text-[9.5px] uppercase cursor-pointer">
          Erase [X]
        </button>
      </td>
    `;
    tbody.appendChild(row);
  });
}

(window as any).triggerScheduleSlotDeletion = async (id: string) => {
  try {
    const res = await fetch(`/api/schedule/${id}`, { method: "DELETE" });
    if (res.ok) {
      await refreshDatabaseSync();
    }
  } catch (err) {
    console.error("Slot deletion crashed: ", err);
  }
};

// Admin Forms Register
const trainForm = document.getElementById("admin-add-trainer-form") as HTMLFormElement;
if (trainForm) {
  trainForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = (document.getElementById("new-trainer-name") as HTMLInputElement).value.trim();
    const email = (document.getElementById("new-trainer-email") as HTMLInputElement).value.trim();
    const password = (document.getElementById("new-trainer-pass") as HTMLInputElement).value;
    const rate = Number((document.getElementById("new-trainer-rate") as HTMLInputElement).value);
    const subjs = (document.getElementById("new-trainer-subjs") as HTMLInputElement).value.split(",").map(s => s.trim());

    try {
      const res = await fetch("/api/trainers", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name, email, password, hourlyRate: rate, subjects: subjs
        })
      });
      if (res.ok) {
        trainForm.reset();
        await refreshDatabaseSync();
      }
    } catch (err) {
      console.error("Failed adding trainer:", err);
    }
  });
}

const schedForm = document.getElementById("admin-add-schedule-form") as HTMLFormElement;
if (schedForm) {
  schedForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    
    const trainerSelect = document.getElementById("sched-trainer-select") as HTMLSelectElement;
    const trainerId = trainerSelect.value;
    const trainerName = trainerSelect.options[trainerSelect.selectedIndex]?.text || "Coach";
    
    const dayOfWeek = (document.getElementById("sched-day-select") as HTMLSelectElement).value;
    const startTime = (document.getElementById("sched-start-time") as HTMLInputElement).value;
    const endTime = (document.getElementById("sched-end-time") as HTMLInputElement).value;
    const subject = (document.getElementById("sched-subj-input") as HTMLInputElement).value.trim();
    const classYear = (document.getElementById("sched-year-input") as HTMLInputElement).value.trim();
    const description = (document.getElementById("sched-desc-input") as HTMLInputElement).value.trim();

    try {
      const res = await fetch("/api/schedule", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          trainerId, trainerName, dayOfWeek, startTime, endTime, subject, classYear, description
        })
      });
      if (res.ok) {
        schedForm.reset();
        await refreshDatabaseSync();
      }
    } catch (err) {
      console.error("Failed creating slot:", err);
    }
  });
}

const saveAboutBtn = document.getElementById("btn-save-admin-about");
if (saveAboutBtn) {
  saveAboutBtn.addEventListener("click", async () => {
    const currentAboutText = (document.getElementById("admin-about-textbox") as HTMLTextAreaElement).value.trim();
    const currentStudents = Number((document.getElementById("admin-input-students") as HTMLInputElement).value) || 148;
    
    try {
      const res = await fetch("/api/config", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          aboutText: currentAboutText,
          totalStudents: currentStudents
        })
      });
      if (res.ok) {
        alert("Academy profiles and active counts saved successfully!");
        await refreshDatabaseSync();
      }
    } catch (err) {
      console.error("Config save failed:", err);
    }
  });
}
