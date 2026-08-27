/**
 * Doorlopende performance monitor voor het opsporen van UI-lag.
 *
 * Format-afspraak (voor overzicht):
 *  - Directe waarschuwingen (long task / trage GraphQL call / trage storage write)
 *    komen altijd als ÉÉN ingeklapte console.group met hetzelfde icoon-schema.
 *  - Het periodieke rapport (elke 2s) is ook ÉÉN group met precies twee tabellen:
 *    "Vitals" (altijd) en "Aandachtspunten" (alleen als er iets afwijkt).
 *  - Niets wordt los ge-console.log't buiten deze twee formats.
 */

type TabMetric = {
  name: string;
  duration: number;
  timestamp: string;
  heapUsedMB: number | null;
  inFlightRequests: number;
  slow: boolean;
};

type VueMeasure = { name: string; duration: number; startTime: number };
type Interaction = { type: string; target: string; time: number };
type GraphqlCall = { operation: string; duration: number; sizeKB: number; time: number };
type StorageWrite = { key: string; duration: number; sizeKB: number; time: number };

declare global {
  interface Window {
    tabMetrics: TabMetric[];
    getTabReport: () => void;
    clearTabMetrics: () => void;
    exportPerfReport: () => void;
    stopPerfMonitor: () => void;
    __activeRequests: number;
    __activeIntervals: number;
    __activeTimeouts: number;
    __activeListeners: number;
    __wsOpenCount: number;
    __wsMessagesSinceLastReport: number;
    __recentVueMeasures: VueMeasure[];
    __recentInteractions: Interaction[];
    __graphqlCalls: GraphqlCall[];
    __storageWrites: StorageWrite[];
    __eventLoopLagMs: number;
  }
}

const PERF_DEBUG_VERSION = "1.9";
const SLOW_THRESHOLD_MS = 100;
const REPORT_INTERVAL_MS = 2000;
const LONGTASK_MS = 50;
const GQL_SLOW_MS = 200;
const STORAGE_SLOW_MS = 10;

// ---------------------------------------------------------------------------
// Kleine helpers
// ---------------------------------------------------------------------------

function getHeapMB(): number | null {
  const mem = (performance as unknown as { memory?: { usedJSHeapSize: number } }).memory;
  return mem ? Math.round((mem.usedJSHeapSize / 1024 / 1024) * 10) / 10 : null;
}

function describeElement(el: Element | null): string {
  if (!el) return "onbekend";
  const tag = el.tagName.toLowerCase();
  const id = (el as HTMLElement).id ? `#${(el as HTMLElement).id}` : "";
  const cls = el.classList.length ? `.${el.classList[0]}` : "";
  const text = (el.textContent || "").trim().slice(0, 30);
  return `${tag}${id}${cls}${text ? ` "${text}"` : ""}`;
}

/** Eén vast format voor een directe waarschuwing — altijd ingeklapt, altijd dezelfde opbouw. */
function logAlert(icon: string, title: string, rows: [string, string][]) {
  console.group(`%c${icon} ${title}`, "color:#e11; font-weight:bold");
  for (const [label, value] of rows) {
    console.log(`%c${label}:%c ${value}`, "font-weight:bold", "font-weight:normal");
  }
  console.groupEnd();
}

// ---------------------------------------------------------------------------
// Installatie (eenmalig)
// ---------------------------------------------------------------------------

if (typeof window !== "undefined" && !(window as unknown as { __perfDebugInstalled?: boolean }).__perfDebugInstalled) {
  (window as unknown as { __perfDebugInstalled: boolean }).__perfDebugInstalled = true;

  window.tabMetrics = [];
  window.__activeRequests = 0;
  window.__activeIntervals = 0;
  window.__activeTimeouts = 0;
  window.__activeListeners = 0;
  window.__wsOpenCount = 0;
  window.__wsMessagesSinceLastReport = 0;
  window.__recentVueMeasures = [];
  window.__recentInteractions = [];
  window.__graphqlCalls = [];
  window.__storageWrites = [];
  window.__eventLoopLagMs = 0;

  // --- fetch: in-flight teller + GraphQL operation naam/duur/omvang (incl. body download+parse) ---
  const originalFetch = window.fetch;
  window.fetch = async (...args: Parameters<typeof fetch>) => {
    window.__activeRequests++;
    const start = performance.now();

    let operation = "onbekende call";
    try {
      const body = args[1]?.body;
      if (typeof body === "string") {
        const parsed = JSON.parse(body);
        operation =
          parsed.operationName ||
          (parsed.query ? parsed.query.match(/(?:query|mutation)\s+(\w+)/)?.[1] : null) ||
          "anonieme operation";
      }
    } catch {
      // geen GraphQL body, negeren
    }

    try {
      const response = await originalFetch(...args);
      window.__activeRequests--;

      response
        .clone()
        .text()
        .then((text) => {
          const duration = Math.round(performance.now() - start);
          const sizeKB = Math.round((text.length / 1024) * 10) / 10;
          window.__graphqlCalls.push({ operation, duration, sizeKB, time: performance.now() });
          if (window.__graphqlCalls.length > 100) window.__graphqlCalls.shift();

          if (duration > GQL_SLOW_MS || sizeKB > 100) {
            logAlert("🐌", `GraphQL call traag/groot: ${operation}`, [
              ["Duur (incl. download+parse)", `${duration}ms`],
              ["Payload", `${sizeKB}KB`],
            ]);
          }
        })
        .catch(() => undefined);

      return response;
    } catch (err) {
      window.__activeRequests--;
      throw err;
    }
  };

  // --- setInterval / setTimeout tellers (leak-indicator) ---
  const originalSetInterval = window.setInterval;
  const originalClearInterval = window.clearInterval;
  window.setInterval = ((...args: Parameters<typeof setInterval>) => {
    window.__activeIntervals++;
    return originalSetInterval(...args);
  }) as typeof setInterval;
  window.clearInterval = ((id?: Parameters<typeof clearInterval>[0]) => {
    if (id !== undefined) window.__activeIntervals = Math.max(0, window.__activeIntervals - 1);
    return originalClearInterval(id);
  }) as typeof clearInterval;

  const originalSetTimeout = window.setTimeout;
  const originalClearTimeout = window.clearTimeout;
  window.setTimeout = ((...args: Parameters<typeof setTimeout>) => {
    window.__activeTimeouts++;
    const id = originalSetTimeout(() => {
      window.__activeTimeouts = Math.max(0, window.__activeTimeouts - 1);
      (args[0] as () => void)();
    }, args[1] as number);
    return id;
  }) as typeof setTimeout;
  window.clearTimeout = ((id?: Parameters<typeof clearTimeout>[0]) => {
    if (id !== undefined) window.__activeTimeouts = Math.max(0, window.__activeTimeouts - 1);
    return originalClearTimeout(id);
  }) as typeof clearTimeout;

  // --- event listener teller (leak-indicator) ---
  const originalAddEventListener = EventTarget.prototype.addEventListener;
  const originalRemoveEventListener = EventTarget.prototype.removeEventListener;
  EventTarget.prototype.addEventListener = function (...args) {
    window.__activeListeners++;
    return originalAddEventListener.apply(this, args);
  };
  EventTarget.prototype.removeEventListener = function (...args) {
    window.__activeListeners = Math.max(0, window.__activeListeners - 1);
    return originalRemoveEventListener.apply(this, args);
  };

  // --- WebSocket activiteit (graphql-ws subscriptions) ---
  const OriginalWebSocket = window.WebSocket;
  window.WebSocket = new Proxy(OriginalWebSocket, {
    construct(target, args) {
      window.__wsOpenCount++;
      const ws = new target(...(args as ConstructorParameters<typeof WebSocket>));
      ws.addEventListener("message", () => window.__wsMessagesSinceLastReport++);
      ws.addEventListener("close", () => (window.__wsOpenCount = Math.max(0, window.__wsOpenCount - 1)));
      return ws;
    },
  }) as unknown as typeof WebSocket;

  // --- localStorage schrijftijd + omvang ---
  const originalSetItem = Storage.prototype.setItem;
  Storage.prototype.setItem = function (key: string, value: string) {
    const start = performance.now();
    const result = originalSetItem.call(this, key, value);
    const duration = Math.round((performance.now() - start) * 10) / 10;
    const sizeKB = Math.round((value.length / 1024) * 10) / 10;
    window.__storageWrites.push({ key, duration, sizeKB, time: performance.now() });
    if (window.__storageWrites.length > 100) window.__storageWrites.shift();

    if (duration > STORAGE_SLOW_MS || sizeKB > 200) {
      logAlert("💾", `localStorage write traag/groot: "${key}"`, [
        ["Duur", `${duration}ms`],
        ["Omvang", `${sizeKB}KB`],
      ]);
    }
    return result;
  };

  // --- event loop lag probe (main-thread drukte, ook zonder repaint) ---
  let lagCheckStart = performance.now();
  function checkEventLoopLag() {
    const now = performance.now();
    window.__eventLoopLagMs = Math.max(0, Math.round(now - lagCheckStart - 100));
    lagCheckStart = now;
    originalSetTimeout(checkEventLoopLag, 100);
  }
  originalSetTimeout(checkEventLoopLag, 100);

  // --- gebruikersinteracties bijhouden (voor "wat gebeurde er net voor de lag") ---
  ["pointerdown", "input", "change", "keydown"].forEach((type) => {
    document.addEventListener(
      type,
      (e: Event) => {
        window.__recentInteractions.push({ type, target: describeElement(e.target as Element), time: performance.now() });
        if (window.__recentInteractions.length > 20) window.__recentInteractions.shift();
      },
      true,
    );
  });

  // --- Vue per-component render/patch/mount timing (vereist app.config.performance = true) ---
  try {
    const measureObs = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        window.__recentVueMeasures.push({
          name: entry.name,
          duration: Math.round(entry.duration * 10) / 10,
          startTime: Math.round(entry.startTime),
        });
      }
      const cutoff = performance.now() - 5000;
      window.__recentVueMeasures = window.__recentVueMeasures.filter((m) => m.startTime > cutoff);
    });
    measureObs.observe({ entryTypes: ["measure"] });
  } catch {
    console.warn("[PERF] measure PerformanceObserver niet ondersteund");
  }

  // --- Long task observer: directe waarschuwing met component + laatste actie erbij ---
  const longTasks: { duration: number; start: number }[] = [];
  try {
    const obs = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        const duration = Math.round(entry.duration);
        const start = Math.round(entry.startTime);
        longTasks.push({ duration, start });

        const overlapping = window.__recentVueMeasures
          .filter((m) => m.startTime >= start - 20 && m.startTime <= start + duration + 20)
          .sort((a, b) => b.duration - a.duration)
          .slice(0, 3);

        const lastInteraction = [...window.__recentInteractions].reverse().find((i) => i.time <= start + duration);

        logAlert("🐢", `Long task: ${duration}ms`, [
          [
            "Laatste actie ervoor",
            lastInteraction
              ? `${lastInteraction.type} op ${lastInteraction.target} (${Math.round(start - lastInteraction.time)}ms eerder)`
              : "geen — waarschijnlijk achtergrondproces (polling/websocket)",
          ],
          [
            "Traagste component(en) tijdens blok",
            overlapping.length ? overlapping.map((m) => `${m.name} (${m.duration}ms)`).join(", ") : "geen — check GraphQL/storage in het 2s-rapport",
          ],
        ]);
      }
    });
    obs.observe({ entryTypes: ["longtask"] });
  } catch {
    console.warn("[PERF] longtask PerformanceObserver niet ondersteund in deze browser");
  }

  // --- Frame rate / frame time ---
  let frameCount = 0;
  let worstFrameMs = 0;
  let lastFrameTime = performance.now();
  let rafHandle = requestAnimationFrame(function frameLoop() {
    const now = performance.now();
    const frameMs = now - lastFrameTime;
    lastFrameTime = now;
    frameCount++;
    if (frameMs > worstFrameMs) worstFrameMs = frameMs;
    rafHandle = requestAnimationFrame(frameLoop);
  });

  // --- Tab-switch duur ---
  document.addEventListener(
    "pointerdown",
    (e: Event) => {
      const target = (e.target as HTMLElement)?.closest('[role="tab"]');
      if (!target) return;
      const tabName = target.textContent?.trim() || "unknown";
      const clickStart = performance.now();
      const inFlightAtClick = window.__activeRequests;
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          const duration = Math.round((performance.now() - clickStart) * 10) / 10;
          window.tabMetrics.push({
            name: tabName,
            duration,
            timestamp: new Date().toLocaleTimeString(),
            heapUsedMB: getHeapMB(),
            inFlightRequests: inFlightAtClick,
            slow: duration > SLOW_THRESHOLD_MS,
          });
        });
      });
    },
    true,
  );

  // ---------------------------------------------------------------------
  // Publieke commando's
  // ---------------------------------------------------------------------

  window.getTabReport = () => {
    console.group("%c📑 Tab-switch rapport", "color:#06c; font-weight:bold");
    if (!window.tabMetrics.length) {
      console.log("Nog geen tab-switches gemeten — klik eerst een paar tabs aan.");
    } else {
      console.table(
        window.tabMetrics.map((m) => ({
          Tab: m.name,
          "Duur (ms)": m.duration,
          Traag: m.slow ? "⚠️" : "",
          "Heap (MB)": m.heapUsedMB ?? "n/a",
          "Netwerk actief": m.inFlightRequests || "",
          Tijd: m.timestamp,
        })),
      );
    }
    console.groupEnd();
  };

  window.clearTabMetrics = () => {
    window.tabMetrics = [];
    console.log("Tab metrics gewist.");
  };

  window.exportPerfReport = () => {
    const heapMB = getHeapMB();
    const slowGql = [...window.__graphqlCalls].sort((a, b) => b.duration - a.duration).slice(0, 10);
    const slowComponents = [...window.__recentVueMeasures].sort((a, b) => b.duration - a.duration).slice(0, 10);
    const slowTabs = window.tabMetrics.filter((m) => m.slow);
    const slowWrites = [...window.__storageWrites].sort((a, b) => b.duration - a.duration).slice(0, 5);

    const lines = [
      `Perf report v${PERF_DEBUG_VERSION} — ${new Date().toLocaleString()}`,
      `User agent: ${navigator.userAgent}`,
      `JS Heap: ${heapMB ?? "n/a"}MB | DOM nodes: ${document.getElementsByTagName("*").length}`,
      `Actieve intervals: ${window.__activeIntervals} | timeouts: ${window.__activeTimeouts} | listeners: ${window.__activeListeners} | open sockets: ${window.__wsOpenCount}`,
      "",
      "--- Traagste GraphQL calls ---",
      ...(slowGql.length ? slowGql.map((c) => `${c.duration}ms, ${c.sizeKB}KB — ${c.operation}`) : ["(nog geen calls gemeten)"]),
      "",
      "--- Traagste componenten (laatste 5s) ---",
      ...(slowComponents.length ? slowComponents.map((m) => `${m.duration}ms — ${m.name}`) : ["(nog geen metingen)"]),
      "",
      "--- Traagste localStorage writes ---",
      ...(slowWrites.length ? slowWrites.map((w) => `${w.duration}ms, ${w.sizeKB}KB — ${w.key}`) : ["(nog geen writes gemeten)"]),
      "",
      "--- Trage tab-switches ---",
      ...(slowTabs.length ? slowTabs.map((m) => `${m.duration}ms — ${m.name} (netwerk actief: ${m.inFlightRequests})`) : ["(geen trage tab-switches)"]),
    ];

    const text = lines.join("\n");
    console.log(text);

    if (navigator.clipboard?.writeText) {
      navigator.clipboard
        .writeText(text)
        .then(() => console.log("%c✓ Gekopieerd naar klembord — plak dit in Slack/Teams.", "color:green; font-weight:bold"))
        .catch(() => console.log("Kon niet automatisch kopiëren — selecteer de tekst hierboven handmatig."));
    }
  };

  // ---------------------------------------------------------------------
  // Periodiek rapport — één group, twee tabellen, klaar
  // ---------------------------------------------------------------------

  const startHeap = getHeapMB();
  const startTime = performance.now();

  const reportTimer = originalSetInterval(() => {
    const heapMB = getHeapMB();
    const heapGrowth = startHeap !== null && heapMB !== null ? Math.round((heapMB - startHeap) * 10) / 10 : null;
    const fps = Math.round((frameCount / (REPORT_INTERVAL_MS / 1000)) * 10) / 10;
    const domNodes = document.getElementsByTagName("*").length;
    const uptimeSec = Math.round((performance.now() - startTime) / 1000);
    const worstLongTask = longTasks.length ? Math.max(...longTasks.map((t) => t.duration)) : 0;
    const totalBlockedMs = longTasks.reduce((sum, t) => sum + t.duration, 0);

    const cutoff = performance.now() - REPORT_INTERVAL_MS;
    const vueCutoff = performance.now() - 5000; // vue measures worden al op 5s bijgehouden
    const recentGql = window.__graphqlCalls.filter((c) => c.time > cutoff);
    const recentWrites = window.__storageWrites.filter((w) => w.time > cutoff);
    const recentComponents = window.__recentVueMeasures.filter((m) => m.startTime > vueCutoff - performance.timeOrigin);

    console.group(
      `%c⏱ Perf rapport ${new Date().toLocaleTimeString()}%c — uptime ${uptimeSec}s`,
      "color:#06c; font-weight:bold",
      "color:inherit; font-weight:normal",
    );

    // Tabel 1: vitals — altijd getoond, vast format
    console.table([
      { Meting: "FPS", Waarde: fps, Alarm: fps < 30 ? "⚠️ laag" : "" },
      { Meting: "Traagste frame", Waarde: `${worstFrameMs.toFixed(0)}ms`, Alarm: worstFrameMs > 100 ? "⚠️" : "" },
      { Meting: "Long tasks (>50ms)", Waarde: longTasks.length, Alarm: longTasks.length ? `⚠️ traagste ${worstLongTask}ms` : "" },
      { Meting: "Main thread geblokkeerd", Waarde: `${totalBlockedMs}/${REPORT_INTERVAL_MS}ms`, Alarm: totalBlockedMs > 200 ? "⚠️" : "" },
      { Meting: "Event loop lag", Waarde: `${window.__eventLoopLagMs}ms`, Alarm: window.__eventLoopLagMs > 30 ? "⚠️ druk" : "" },
      { Meting: "JS Heap", Waarde: heapMB !== null ? `${heapMB}MB` : "n/a", Alarm: heapGrowth !== null && heapGrowth > 5 ? `⚠️ +${heapGrowth}MB sinds start` : "" },
      { Meting: "DOM nodes", Waarde: domNodes },
      { Meting: "Netwerk / intervals / timeouts / listeners / sockets", Waarde: `${window.__activeRequests} / ${window.__activeIntervals} / ${window.__activeTimeouts} / ${window.__activeListeners} / ${window.__wsOpenCount}` },
    ]);

    // Tabel 2: alle componenten (laatste 5s), zoals in v1.6 — niet alleen de traagste 5
    const componentRows = recentComponents
      .filter((m) => m.duration > 4)
      .sort((a, b) => b.duration - a.duration)
      .map((m) => ({ Component: m.name, "Duur (ms)": m.duration, Alarm: m.duration > 100 ? "⚠️" : "" }));
    if (componentRows.length) {
      console.log(`%cTraagste componenten (laatste 5s, ${componentRows.length}x):`, "font-weight:bold");
      console.table(componentRows);
    }

    // Tabel 3: alle GraphQL calls in dit venster, niet alleen de trage
    if (recentGql.length) {
      console.log(`%cGraphQL calls (laatste 2s, ${recentGql.length}x):`, "font-weight:bold");
      console.table(
        recentGql
          .sort((a, b) => b.duration - a.duration)
          .map((c) => ({ Operation: c.operation, "Duur (ms)": c.duration, "Payload (KB)": c.sizeKB, Alarm: c.duration > GQL_SLOW_MS ? "⚠️ traag" : "" })),
      );
    }

    // Tabel 4: alle localStorage writes in dit venster
    if (recentWrites.length) {
      console.log(`%clocalStorage writes (laatste 2s, ${recentWrites.length}x):`, "font-weight:bold");
      console.table(
        recentWrites
          .sort((a, b) => b.duration - a.duration)
          .map((w) => ({ Key: w.key, "Duur (ms)": w.duration, "Omvang (KB)": w.sizeKB, Alarm: w.duration > STORAGE_SLOW_MS ? "⚠️ traag" : "" })),
      );
    }

    console.groupEnd();

    // Reset per-venster tellers
    frameCount = 0;
    worstFrameMs = 0;
    longTasks.length = 0;
    window.__wsMessagesSinceLastReport = 0;
  }, REPORT_INTERVAL_MS);

  window.stopPerfMonitor = () => {
    originalClearInterval(reportTimer);
    cancelAnimationFrame(rafHandle);
    console.log("Perf monitor gestopt.");
  };

  console.log(
    `%c✓ Perf monitor v${PERF_DEBUG_VERSION} actief%c — elke 2s één rapport (groep, klik om te openen). getTabReport() / exportPerfReport() / stopPerfMonitor() beschikbaar.`,
    "color: green; font-weight: bold",
    "color: inherit; font-weight: normal",
  );
}
