/**
 * SkillMap Frontend Interactive Controller
 * ----------------------------------------
 * Handles responsive sidebar navigation, custom confirmation modals,
 * AJAX task/resource persistence with CSRF headers, dependent career-skill
 * selects, edit modal population, and zero-refresh EN/FA language switching.
 *
 * AI Assistance Note:
 * Client-side DOM handlers, language morphing, and fetch() persistence helpers
 * were drafted and refined with AI assistance and verified by the author.
 */

(function () {
  "use strict";

  function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    const metaVal = meta ? (meta.getAttribute("content") || "").trim() : "";
    if (metaVal) return metaVal;
    const input = document.querySelector('input[name="csrf_token"]');
    return input ? (input.value || "").trim() : "";
  }

  function syncCsrfTokens(token) {
    if (!token) return;
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (meta) {
      meta.setAttribute("content", token);
    }
    document.querySelectorAll('input[name="csrf_token"]').forEach((input) => {
      input.value = token;
    });
  }

  function getI18n() {
    const el = document.getElementById("skillmap-i18n-data");
    if (!el) return {};
    try {
      return JSON.parse(el.textContent || "{}");
    } catch (_err) {
      return {};
    }
  }

  function formatTemplate(template, vars) {
    let out = String(template || "");
    Object.keys(vars || {}).forEach((key) => {
      out = out.replaceAll(`{${key}}`, String(vars[key]));
    });
    return out;
  }

  /* ------------------------------------------------------------
     1. Mobile Sidebar Drawer (Delegated for DOM morph safety)
  ------------------------------------------------------------ */
  function setSidebarOpen(open) {
    const sidebar = document.getElementById("app-sidebar");
    const backdrop = document.getElementById("sidebar-backdrop");
    const openMenuBtn = document.getElementById("mobile-menu-btn");
    if (!sidebar || !backdrop) return;
    sidebar.classList.toggle("open", open);
    backdrop.classList.toggle("open", open);
    if (openMenuBtn) {
      openMenuBtn.setAttribute("aria-expanded", String(open));
    }
  }

  document.addEventListener("click", (event) => {
    if (event.target.closest("#mobile-menu-btn")) {
      setSidebarOpen(true);
      return;
    }
    if (event.target.closest("#sidebar-close-btn") || event.target.closest("#sidebar-backdrop")) {
      setSidebarOpen(false);
    }
  });

  /* ------------------------------------------------------------
     2. Dismissible Flash Alerts
  ------------------------------------------------------------ */
  document.addEventListener("click", (event) => {
    const dismissBtn = event.target.closest("[data-dismiss-alert]");
    if (!dismissBtn) return;
    const alertEl = dismissBtn.closest(".alert");
    if (alertEl) {
      alertEl.remove();
    }
  });

  /* ------------------------------------------------------------
     3. Custom Confirmation Modal (No window.confirm)
  ------------------------------------------------------------ */
  let pendingConfirmForm = null;

  function closeConfirmModal() {
    const confirmModal = document.getElementById("confirm-modal");
    if (!confirmModal) return;
    confirmModal.classList.remove("open");
    pendingConfirmForm = null;
  }

  document.addEventListener("submit", (event) => {
    const form = event.target;
    if (!form.matches("[data-confirm]")) return;
    if (form.dataset.confirmed === "true") return;

    event.preventDefault();
    pendingConfirmForm = form;
    const confirmModal = document.getElementById("confirm-modal");
    const confirmMessage = document.getElementById("confirm-modal-message");
    const confirmProceedBtn = document.getElementById("confirm-modal-proceed");
    const i18n = getI18n();
    if (confirmMessage) {
      confirmMessage.textContent = form.dataset.confirm || i18n.confirmDefault || "Are you sure you want to delete this item?";
    }
    if (confirmModal) {
      confirmModal.classList.add("open");
      if (confirmProceedBtn) confirmProceedBtn.focus();
    }
  });

  document.addEventListener("click", (event) => {
    if (event.target.closest("#confirm-modal-proceed")) {
      if (pendingConfirmForm) {
        pendingConfirmForm.dataset.confirmed = "true";
        pendingConfirmForm.submit();
      }
      closeConfirmModal();
      return;
    }
    if (event.target.closest("[data-close-confirm]")) {
      closeConfirmModal();
    }
  });

  /* ------------------------------------------------------------
     4. Generic Modals (Project Edit / Note Edit)
  ------------------------------------------------------------ */
  document.addEventListener("click", (event) => {
    const openBtn = event.target.closest("[data-open-modal]");
    if (openBtn) {
      const targetId = openBtn.getAttribute("data-open-modal");
      const modal = document.getElementById(targetId);
      if (modal) {
        modal.classList.add("open");
      }
      return;
    }

    const closeBtn = event.target.closest("[data-close-modal]");
    if (closeBtn) {
      const modal = closeBtn.closest(".modal-overlay");
      if (modal) modal.classList.remove("open");
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      setSidebarOpen(false);
      closeConfirmModal();
      document.querySelectorAll(".modal-overlay.open").forEach((m) => m.classList.remove("open"));
    }
  });

  /* ------------------------------------------------------------
     5. Dependent Career -> Skill Dropdown Filtering
  ------------------------------------------------------------ */
  function initDependentSelects() {
    document.querySelectorAll("[data-career-select]").forEach((careerSelect) => {
      const targetId = careerSelect.getAttribute("data-career-select");
      const skillSelect = document.getElementById(targetId);
      if (!skillSelect) return;

      const allOptions = Array.from(skillSelect.querySelectorAll("option[data-career-id]"));

      function syncSkills() {
        const selectedCareer = careerSelect.value;
        allOptions.forEach((opt) => {
          const matches = !selectedCareer || opt.getAttribute("data-career-id") === selectedCareer;
          opt.hidden = !matches;
          opt.disabled = !matches;
        });
        const currentOpt = skillSelect.selectedOptions[0];
        if (currentOpt && currentOpt.hidden) {
          skillSelect.value = "";
        }
      }

      careerSelect.addEventListener("change", syncSkills);
      syncSkills();
    });
  }

  initDependentSelects();

  /* ------------------------------------------------------------
     6. AJAX Task Completion Toggle (Roadmap)
  ------------------------------------------------------------ */
  document.addEventListener("click", async (event) => {
    const btn = event.target.closest("[data-ajax-task-toggle]");
    if (!btn) return;
    event.preventDefault();

    const taskId = btn.getAttribute("data-ajax-task-toggle");
    const taskItem = btn.closest(".task-item");
    btn.disabled = true;

    try {
      const csrfToken = getCsrfToken();
      const response = await fetch(`/api/tasks/${taskId}/toggle`, {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({ csrf_token: csrfToken }),
      });
      if (!response.ok) throw new Error("Failed to toggle task");
      const data = await response.json();
      const i18n = getI18n();

      btn.classList.toggle("checked", data.is_completed);
      btn.setAttribute("aria-pressed", String(data.is_completed));
      if (taskItem) {
        taskItem.classList.toggle("completed", data.is_completed);
      }

      const progressBar = document.getElementById("roadmap-progress-bar");
      const progressText = document.getElementById("roadmap-progress-text");
      const completedCountEl = document.getElementById("roadmap-completed-count");
      const hoursCountEl = document.getElementById("roadmap-hours-count");
      if (progressBar) {
        progressBar.style.width = `${data.career_percent}%`;
      }
      if (progressText) {
        progressText.textContent = `${data.career_percent}%`;
      }
      if (completedCountEl) {
        completedCountEl.textContent = formatTemplate(i18n.tasksRatio || "{done} / {total} tasks", {
          done: data.career_completed,
          total: data.career_total,
        });
      }
      if (hoursCountEl && typeof data.completed_hours === "number") {
        hoursCountEl.textContent = formatTemplate(i18n.hoursRatio || "{done} / {total} hrs", {
          done: data.completed_hours,
          total: data.total_hours,
        });
      }

      if (data.skill_id !== null && data.skill_mastery !== null) {
        const skillCard = document.querySelector(`[data-skill-card="${data.skill_id}"]`);
        if (skillCard) {
          const pctLabel = skillCard.querySelector("[data-skill-pct]");
          const bar = skillCard.querySelector("[data-skill-bar]");
          const hoursLabel = skillCard.querySelector("[data-skill-hours]");
          const masteryInput = skillCard.querySelector('input[name="mastery_percent"]');
          const hoursInput = skillCard.querySelector('input[name="hours_logged"]');
          if (pctLabel) pctLabel.textContent = `${data.skill_mastery}%`;
          if (bar) bar.style.width = `${data.skill_mastery}%`;
          if (hoursLabel && typeof data.skill_hours === "number") {
            hoursLabel.textContent = formatTemplate(i18n.hoursLoggedShort || "{hours}h logged", {
              hours: data.skill_hours,
            });
          }
          if (masteryInput) masteryInput.value = String(data.skill_mastery);
          if (hoursInput && typeof data.skill_hours === "number") {
            hoursInput.value = String(data.skill_hours);
          }
        }
      }
    } catch (_err) {
      const fallbackForm = btn.closest("form");
      if (fallbackForm) fallbackForm.submit();
    } finally {
      btn.disabled = false;
    }
  });

  /* ------------------------------------------------------------
     7. AJAX Resource Completion Toggle
  ------------------------------------------------------------ */
  document.addEventListener("click", async (event) => {
    const btn = event.target.closest("[data-ajax-resource-toggle]");
    if (!btn) return;
    event.preventDefault();

    const resourceId = btn.getAttribute("data-ajax-resource-toggle");
    btn.disabled = true;

    try {
      const csrfToken = getCsrfToken();
      const response = await fetch(`/api/resources/${resourceId}/toggle`, {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({ csrf_token: csrfToken }),
      });
      if (!response.ok) throw new Error("Failed to toggle resource");
      const data = await response.json();
      const i18n = getI18n();

      const row = btn.closest("tr");
      const statusLabel = row ? row.querySelector("[data-resource-status]") : null;
      if (data.is_completed) {
        btn.textContent = i18n.resourceReopen || "Reopen";
        if (statusLabel) {
          statusLabel.textContent = i18n.resourceCompleted || "Completed";
          statusLabel.className = "status-label success";
        }
      } else {
        btn.textContent = i18n.resourceMarkComplete || "Mark Complete";
        if (statusLabel) {
          statusLabel.textContent = i18n.resourceUnread || "Unread";
          statusLabel.className = "status-label muted";
        }
      }
    } catch (_err) {
      const fallbackForm = btn.closest("form");
      if (fallbackForm) fallbackForm.submit();
    } finally {
      btn.disabled = false;
    }
  });

  /* ------------------------------------------------------------
     8. Populate Edit Modals (Projects, Notes, Tasks, Resources)
  ------------------------------------------------------------ */
  document.addEventListener("click", (event) => {
    const editProjBtn = event.target.closest("[data-edit-project]");
    if (editProjBtn) {
      const modal = document.getElementById("edit-project-modal");
      const form = document.getElementById("edit-project-form");
      if (!modal || !form) return;

      form.action = `/projects/${editProjBtn.dataset.id}/update`;
      document.getElementById("edit-proj-name").value = editProjBtn.dataset.name || "";
      document.getElementById("edit-proj-stack").value = editProjBtn.dataset.stack || "";
      document.getElementById("edit-proj-status").value = editProjBtn.dataset.status || "Planned";
      document.getElementById("edit-proj-pct").value = editProjBtn.dataset.pct || "0";
      document.getElementById("edit-proj-github").value = editProjBtn.dataset.github || "";
      document.getElementById("edit-proj-desc").value = editProjBtn.dataset.desc || "";
      const careerEl = document.getElementById("edit-proj-career");
      if (careerEl) careerEl.value = editProjBtn.dataset.careerId || "";
      modal.classList.add("open");
    }

    const editNoteBtn = event.target.closest("[data-edit-note]");
    if (editNoteBtn) {
      const modal = document.getElementById("edit-note-modal");
      const form = document.getElementById("edit-note-form");
      if (!modal || !form) return;

      form.action = `/notes/${editNoteBtn.dataset.id}/edit`;
      document.getElementById("edit-note-title").value = editNoteBtn.dataset.title || "";
      document.getElementById("edit-note-content").value = editNoteBtn.dataset.content || "";
      modal.classList.add("open");
    }

    const editTaskBtn = event.target.closest("[data-edit-task]");
    if (editTaskBtn) {
      const modal = document.getElementById("edit-task-modal");
      const form = document.getElementById("edit-task-form");
      if (!modal || !form) return;

      form.action = `/roadmap/tasks/${editTaskBtn.dataset.id}/edit`;
      document.getElementById("edit-task-title").value = editTaskBtn.dataset.title || "";
      document.getElementById("edit-task-level").value = editTaskBtn.dataset.level || "Beginner";
      document.getElementById("edit-task-skill").value = editTaskBtn.dataset.skillId || "";
      document.getElementById("edit-task-hours").value = editTaskBtn.dataset.hours || "2.0";
      document.getElementById("edit-task-due").value = editTaskBtn.dataset.due || "";
      document.getElementById("edit-task-desc").value = editTaskBtn.dataset.desc || "";
      modal.classList.add("open");
    }

    const editResBtn = event.target.closest("[data-edit-resource]");
    if (editResBtn) {
      const modal = document.getElementById("edit-resource-modal");
      const form = document.getElementById("edit-resource-form");
      if (!modal || !form) return;

      form.action = `/resources/${editResBtn.dataset.id}/edit`;
      document.getElementById("edit-res-title").value = editResBtn.dataset.title || "";
      document.getElementById("edit-res-url").value = editResBtn.dataset.url || "";
      document.getElementById("edit-res-cat").value = editResBtn.dataset.category || "Article";
      document.getElementById("edit-res-diff").value = editResBtn.dataset.difficulty || "Beginner";
      document.getElementById("edit-res-career").value = editResBtn.dataset.careerId || "";
      document.getElementById("edit-res-desc").value = editResBtn.dataset.desc || "";
      modal.classList.add("open");
    }
  });

  /* ------------------------------------------------------------
     8b. Password Visibility Toggle
  ------------------------------------------------------------ */
  document.addEventListener("click", (event) => {
    const toggleBtn = event.target.closest("[data-password-toggle]");
    if (!toggleBtn) return;

    const targetId = toggleBtn.getAttribute("data-password-toggle");
    const input = targetId ? document.getElementById(targetId) : null;
    if (!input) return;

    const i18n = getI18n();
    const showLabel = i18n.showPassword || "Show password";
    const hideLabel = i18n.hidePassword || "Hide password";

    const willShow = input.type === "password";
    input.type = willShow ? "text" : "password";
    toggleBtn.classList.toggle("is-visible", willShow);
    toggleBtn.setAttribute("aria-pressed", String(willShow));
    toggleBtn.setAttribute("aria-label", willShow ? hideLabel : showLabel);
    toggleBtn.setAttribute("title", willShow ? hideLabel : showLabel);
  });

  /* ------------------------------------------------------------
     9. Bilingual EN / FA Zero-Refresh Language Switcher
  ------------------------------------------------------------ */
  function markUserEdited(target) {
    if (!target || !target.matches("input, textarea, select")) return;
    if (target.type === "hidden") return;
    target.dataset.userEdited = "true";
  }

  document.addEventListener("input", (event) => markUserEdited(event.target));
  document.addEventListener("change", (event) => markUserEdited(event.target));

  function captureInteractiveState() {
    const scrollY = window.scrollY;
    const openModalIds = Array.from(document.querySelectorAll(".modal-overlay.open"))
      .map((el) => el.id)
      .filter(Boolean);

    const editedFields = [];
    document.querySelectorAll('input[data-user-edited="true"], textarea[data-user-edited="true"], select[data-user-edited="true"]').forEach((el) => {
      if (el.type === "radio" || el.type === "checkbox") {
        editedFields.push({
          id: el.id || "",
          name: el.name || "",
          type: el.type,
          value: el.value,
          checked: el.checked,
        });
      } else {
        const form = el.closest("form");
        editedFields.push({
          id: el.id || "",
          name: el.name || "",
          formAction: form ? form.getAttribute("action") || "" : "",
          type: el.type || "text",
          value: el.value,
        });
      }
    });

    const editFormActions = {};
    ["edit-project-form", "edit-note-form", "edit-task-form", "edit-resource-form"].forEach((formId) => {
      const f = document.getElementById(formId);
      if (f) editFormActions[formId] = f.getAttribute("action") || "";
    });

    return { scrollY, openModalIds, editedFields, editFormActions };
  }

  function restoreInteractiveState(snapshot) {
    if (!snapshot) return;

    Object.keys(snapshot.editFormActions || {}).forEach((formId) => {
      const f = document.getElementById(formId);
      if (f && snapshot.editFormActions[formId]) {
        f.setAttribute("action", snapshot.editFormActions[formId]);
      }
    });

    (snapshot.editedFields || []).forEach((item) => {
      let target = item.id ? document.getElementById(item.id) : null;
      if (!target && item.name) {
        if (item.type === "radio" || item.type === "checkbox") {
          target = document.querySelector(
            `input[name="${CSS.escape(item.name)}"][value="${CSS.escape(item.value)}"]`
          );
        } else if (item.formAction) {
          target = document.querySelector(
            `form[action="${CSS.escape(item.formAction)}"] [name="${CSS.escape(item.name)}"]`
          );
        } else {
          target = document.querySelector(`[name="${CSS.escape(item.name)}"]`);
        }
      }
      if (!target) return;
      if (item.type === "radio" || item.type === "checkbox") {
        target.checked = Boolean(item.checked);
      } else {
        target.value = item.value;
      }
      target.dataset.userEdited = "true";
    });

    (snapshot.openModalIds || []).forEach((modalId) => {
      const modal = document.getElementById(modalId);
      if (modal) modal.classList.add("open");
    });

    window.scrollTo(0, snapshot.scrollY || 0);
  }

  async function applyLanguage(nextLang, options) {
    const opts = options || {};
    if (nextLang !== "en" && nextLang !== "fa") return;
    if (document.documentElement.dataset.langSwitching === "true") return;
    document.documentElement.dataset.langSwitching = "true";

    const switcherBtns = document.querySelectorAll("[data-lang-switch]");
    switcherBtns.forEach((b) => {
      b.disabled = true;
    });

    const snapshot = captureInteractiveState();
    let apiStatus = 0;

    try {
      const csrfToken = getCsrfToken();
      const apiRes = await fetch("/api/language", {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({ lang: nextLang, csrf_token: csrfToken }),
      });
      apiStatus = apiRes.status;
      if (!apiRes.ok) {
        throw new Error(`Language update failed (${apiRes.status})`);
      }

      try {
        window.localStorage.setItem("skillmap_lang", nextLang);
      } catch (_storageErr) {
        // Ignore storage restrictions
      }

      let fetchUrl = window.location.href;
      if (document.querySelector('[data-quiz-submitted="true"]')) {
        const parsed = new URL(window.location.href);
        parsed.searchParams.set("view", "result");
        fetchUrl = parsed.toString();
      }

      const pageRes = await fetch(fetchUrl, {
        method: "GET",
        credentials: "same-origin",
        headers: { "X-Requested-With": "SkillMap-i18n" },
      });
      if (!pageRes.ok) throw new Error("Failed to fetch localized view");

      const html = await pageRes.text();
      const doc = new window.DOMParser().parseFromString(html, "text/html");

      const newAppShell = doc.querySelector(".app-shell");
      const curAppShell = document.querySelector(".app-shell");
      const newPublicHeader = doc.querySelector(".public-header");
      const curPublicHeader = document.querySelector(".public-header");
      const newMain = doc.querySelector("main.public-container");
      const curMain = document.querySelector("main.public-container");

      // If auth state changed across tabs/session expiration, follow the full navigation cleanly
      if ((newAppShell && !curAppShell) || (!newAppShell && curAppShell)) {
        window.location.href = pageRes.url || fetchUrl;
        return;
      }

      document.documentElement.lang = doc.documentElement.lang || nextLang;
      document.documentElement.dir = doc.documentElement.dir || (nextLang === "fa" ? "rtl" : "ltr");
      document.title = doc.title;

      const newMetaDesc = doc.querySelector('meta[name="description"]');
      const curMetaDesc = document.querySelector('meta[name="description"]');
      if (newMetaDesc && curMetaDesc) {
        curMetaDesc.setAttribute("content", newMetaDesc.getAttribute("content") || "");
      }

      const newI18n = doc.getElementById("skillmap-i18n-data");
      const curI18n = document.getElementById("skillmap-i18n-data");
      if (newI18n && curI18n) {
        curI18n.textContent = newI18n.textContent;
      }

      if (newAppShell && curAppShell) {
        curAppShell.replaceWith(newAppShell);
      } else {
        if (newPublicHeader && curPublicHeader) {
          curPublicHeader.replaceWith(newPublicHeader);
        }
        if (newMain && curMain) {
          curMain.replaceWith(newMain);
        }
      }

      const newConfirm = doc.getElementById("confirm-modal");
      const curConfirm = document.getElementById("confirm-modal");
      if (newConfirm && curConfirm) {
        curConfirm.replaceWith(newConfirm);
      }

      const newCsrf = doc.querySelector('meta[name="csrf-token"]');
      if (newCsrf) {
        syncCsrfTokens((newCsrf.getAttribute("content") || "").trim());
      }

      initDependentSelects();
      restoreInteractiveState(snapshot);

      if (window.SkillMapCharts && typeof window.SkillMapCharts.init === "function") {
        window.SkillMapCharts.init();
      }
    } catch (_err) {
      if (apiStatus === 400) {
        // Stale CSRF token (e.g. cross-tab login/logout): refresh once on explicit user action
        if (!opts.isAutoRestore) {
          window.location.reload();
        }
        return;
      }
      if (!opts.isAutoRestore) {
        const activeBtn = document.querySelector(`[data-lang-switch="${nextLang}"]`);
        const form = activeBtn ? activeBtn.closest("form") : null;
        if (form) {
          syncCsrfTokens(getCsrfToken());
          form.submit();
        }
      }
    } finally {
      document.documentElement.dataset.langSwitching = "false";
      document.querySelectorAll("[data-lang-switch]").forEach((b) => {
        b.disabled = false;
      });
    }
  }

  document.addEventListener("click", (event) => {
    const btn = event.target.closest("[data-lang-switch]");
    if (!btn) return;
    event.preventDefault();
    const targetLang = btn.getAttribute("data-lang-switch");
    if (!targetLang || targetLang === document.documentElement.lang) return;
    applyLanguage(targetLang);
  });

  document.addEventListener("submit", (event) => {
    const form = event.target.closest(".lang-switcher form");
    if (!form) return;
    event.preventDefault();
    const btn = form.querySelector("[data-lang-switch]");
    const targetLang = btn ? btn.getAttribute("data-lang-switch") : "";
    if (!targetLang || targetLang === document.documentElement.lang) return;
    applyLanguage(targetLang);
  });

  // Never serve stale CSRF tokens from browser back-forward cache
  window.addEventListener("pageshow", (event) => {
    if (event.persisted) {
      window.location.reload();
    }
  });

  // Restore saved localStorage preference seamlessly if cookies were cleared between sessions
  document.addEventListener("DOMContentLoaded", () => {
    try {
      const hasCookie = document.cookie.split(";").some((c) => c.trim().startsWith("skillmap_lang="));
      const storedLang = window.localStorage.getItem("skillmap_lang");
      if (!hasCookie && (storedLang === "en" || storedLang === "fa") && storedLang !== document.documentElement.lang) {
        applyLanguage(storedLang, { isAutoRestore: true });
      } else {
        window.localStorage.setItem("skillmap_lang", document.documentElement.lang || "en");
      }
    } catch (_err) {
      // Ignore storage errors
    }
  });
})();
