/**
 * SkillMap Dashboard Charts (Chart.js)
 * ------------------------------------
 * Renders interactive Weekly Learning Activity and Skills Mastery charts
 * from live SQLite datasets embedded via structured JSON script elements.
 * Supports clean re-initialization on zero-refresh EN/FA language switching.
 *
 * AI Assistance Note:
 * Chart.js configuration, gradient fills, and color-tier styling were authored
 * with AI assistance and verified against live SQLite dashboard data.
 */

(function () {
  "use strict";

  let weeklyChartInstance = null;
  let skillsChartInstance = null;

  function readJsonDataset(elementId) {
    const el = document.getElementById(elementId);
    if (!el) return null;
    try {
      return JSON.parse(el.textContent || "{}");
    } catch (_err) {
      return null;
    }
  }

  function createVerticalGradient(ctx, chartArea, stops) {
    const gradient = ctx.createLinearGradient(0, chartArea.bottom, 0, chartArea.top);
    stops.forEach(([offset, color]) => gradient.addColorStop(offset, color));
    return gradient;
  }

  function createHorizontalGradient(ctx, chartArea, stops) {
    const gradient = ctx.createLinearGradient(chartArea.left, 0, chartArea.right, 0);
    stops.forEach(([offset, color]) => gradient.addColorStop(offset, color));
    return gradient;
  }

  function destroyCharts() {
    if (weeklyChartInstance) {
      weeklyChartInstance.destroy();
      weeklyChartInstance = null;
    }
    if (skillsChartInstance) {
      skillsChartInstance.destroy();
      skillsChartInstance = null;
    }
  }

  function initDashboardCharts() {
    if (typeof window.Chart === "undefined") {
      return;
    }

    destroyCharts();

    const i18n = readJsonDataset("skillmap-i18n-data") || {};
    const activeLang = i18n.lang || document.documentElement.lang || "en";
    const isRtl = (i18n.dir || document.documentElement.dir) === "rtl";

    window.Chart.defaults.font.family =
      activeLang === "fa"
        ? '"Vazirmatn", "DM Sans", -apple-system, BlinkMacSystemFont, sans-serif'
        : '"DM Sans", -apple-system, BlinkMacSystemFont, sans-serif';
    window.Chart.defaults.color = "#475569";

    const studyHoursLabel = i18n.chartStudyHours || "Study Hours";
    const hrsSuffix = i18n.chartHrsSuffix || "hrs logged";
    const masteryLabel = i18n.chartMasteryLabel || "Mastery %";
    const masterySuffix = i18n.chartMasterySuffix || "% mastery";
    const hoursUnit = i18n.hoursUnit || "h";

    const weeklyCanvas = document.getElementById("weeklyActivityChart");
    const weeklyData = readJsonDataset("weekly-activity-data");
    if (weeklyCanvas && weeklyData && Array.isArray(weeklyData.labels)) {
      weeklyChartInstance = new window.Chart(weeklyCanvas, {
        type: "bar",
        data: {
          labels: weeklyData.labels,
          datasets: [
            {
              label: studyHoursLabel,
              data: weeklyData.hours,
              backgroundColor: (context) => {
                const { ctx, chartArea } = context.chart;
                if (!chartArea) return "#6D28D9";
                return createVerticalGradient(ctx, chartArea, [
                  [0, "#6D28D9"],
                  [0.55, "#3B82F6"],
                  [1, "#06B6D4"],
                ]);
              },
              hoverBackgroundColor: (context) => {
                const { ctx, chartArea } = context.chart;
                if (!chartArea) return "#5B21B6";
                return createVerticalGradient(ctx, chartArea, [
                  [0, "#5B21B6"],
                  [0.5, "#EC4899"],
                  [1, "#FB7185"],
                ]);
              },
              borderRadius: 8,
              borderSkipped: false,
              maxBarThickness: 38,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              rtl: isRtl,
              backgroundColor: "#171A3B",
              titleColor: "#F8FAFC",
              bodyColor: "#E0E7FF",
              borderColor: "rgba(167, 139, 250, 0.35)",
              borderWidth: 1,
              cornerRadius: 8,
              padding: 12,
              callbacks: {
                label: (ctx) => `${ctx.parsed.y} ${hrsSuffix}`,
              },
            },
          },
          scales: {
            x: {
              grid: { display: false },
              border: { color: "#E2E8F0" },
              ticks: { color: "#475569", font: { weight: "500" } },
            },
            y: {
              position: isRtl ? "right" : "left",
              beginAtZero: true,
              suggestedMax: 4,
              ticks: {
                color: "#64748B",
                callback: (val) => (activeLang === "fa" ? `${val} ${hoursUnit}` : `${val}${hoursUnit}`),
              },
              grid: { color: "rgba(139, 92, 246, 0.08)" },
              border: { display: false },
            },
          },
        },
      });
    }

    const skillsCanvas = document.getElementById("skillsProgressChart");
    const skillsData = readJsonDataset("skills-progress-data");
    if (skillsCanvas && skillsData && Array.isArray(skillsData.labels) && skillsData.labels.length > 0) {
      const tierPalettes = [
        { min: 80, stops: [[0, "#0D9488"], [1, "#06B6D4"]], fallback: "#0D9488" },
        { min: 55, stops: [[0, "#4F46E5"], [1, "#3B82F6"]], fallback: "#4F46E5" },
        { min: 30, stops: [[0, "#7C3AED"], [1, "#C084FC"]], fallback: "#7C3AED" },
        { min: 0, stops: [[0, "#EC4899"], [1, "#FB7185"]], fallback: "#EC4899" },
      ];

      skillsChartInstance = new window.Chart(skillsCanvas, {
        type: "bar",
        data: {
          labels: skillsData.labels,
          datasets: [
            {
              label: masteryLabel,
              data: skillsData.values,
              backgroundColor: (context) => {
                const val = Number(context.raw ?? 0);
                const tier = tierPalettes.find((t) => val >= t.min) || tierPalettes[tierPalettes.length - 1];
                const { ctx, chartArea } = context.chart;
                if (!chartArea) return tier.fallback;
                return createHorizontalGradient(ctx, chartArea, tier.stops);
              },
              borderRadius: 7,
              borderSkipped: false,
              maxBarThickness: 22,
            },
          ],
        },
        options: {
          indexAxis: "y",
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              rtl: isRtl,
              backgroundColor: "#171A3B",
              titleColor: "#F8FAFC",
              bodyColor: "#E0E7FF",
              borderColor: "rgba(167, 139, 250, 0.35)",
              borderWidth: 1,
              cornerRadius: 8,
              padding: 12,
              callbacks: {
                label: (ctx) => `${ctx.parsed.x}${masterySuffix}`,
              },
            },
          },
          scales: {
            x: {
              beginAtZero: true,
              max: 100,
              ticks: {
                color: "#64748B",
                callback: (val) => `${val}%`,
              },
              grid: { color: "rgba(59, 130, 246, 0.08)" },
              border: { display: false },
            },
            y: {
              position: isRtl ? "right" : "left",
              grid: { display: false },
              border: { color: "#E2E8F0" },
              ticks: { color: "#334155", font: { weight: "500" } },
            },
          },
        },
      });
    }
  }

  window.SkillMapCharts = {
    init: initDashboardCharts,
  };

  document.addEventListener("DOMContentLoaded", initDashboardCharts);
})();
