/**
 * Doorlopende performance monitor voor het opsporen van UI-lag.
 *
 * Format-afspraak (voor overzicht):
 *  - Directe waarschuwingen (long task / trage GraphQL call / trage storage write)
 *    komen altijd als ÉÉN uitgeklapte console.group met hetzelfde icoon-schema.
 *  - Het periodieke rapport (elke 2s) is ook ÉÉN group met meerdere tabellen:
 *    Vitals, Event listeners per type, Traagste componenten, GraphQL calls,
 *    localStorage writes.
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
    __listenersByType: Record<string, number>;
    __wsOpenCount: number;
    __wsMessagesSinceLastReport: number;
    __recentVueMeasures: VueMeasure[];
    __recentInteractions: Interaction[];
    __graphqlCalls: GraphqlCall[];
    __storageWrites: StorageWrite[];
    __eventLoopLagMs: number;
    __sessionStats: SessionStats;
  }
}

type SessionStats = {
  sessionStartTime: number;
  longTaskCount: number;
  longTaskWorstMs: number;
  blockedMsTotal: number;
  fpsWorst: number;
  heapMaxMB: number | null;
  listenersMaxCount: number;
  gqlCallCount: number;
  gqlWorst: { operation: string; duration: number } | null;
  componentWorst: { name: string; duration: number } | null;
  storageWorst: { key: string; duration: number } | null;
};

const PERF_DEBUG_VERSION = "2.4";
const SLOW_THRESHOLD_MS = 100;
const REPORT_INTERVAL_MS = 2000;
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

/** Eén vast format voor een directe waarschuwing — altijd dezelfde opbouw. */
function logAlert(icon: string, title: string, rows: [string, string][]) {
  console.log(" ");
  console.log("%c----- WAARSCHUWING START -----", "color:#e11");
  console.group(`%c${icon} ${title}`, "color:#e11; font-weight:bold");
  for (const [label, value] of rows) {
    console.log(`%c${label}:%c ${value}`, "font-weight:bold", "font-weight:normal");
  }
  console.groupEnd();
  console.log("%c------ WAARSCHUWING EIND ------", "color:#e11");
  console.log(" ");
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
  window.__listenersByType = {};
  window.__wsOpenCount = 0;
  window.__wsMessagesSinceLastReport = 0;
  window.__recentVueMeasures = [];
  window.__recentInteractions = [];
  window.__graphqlCalls = [];
  window.__storageWrites = [];
  window.__eventLoopLagMs = 0;
  window.__sessionStats = {
    sessionStartTime: performance.now(),
    longTaskCount: 0,
    longTaskWorstMs: 0,
    blockedMsTotal: 0,
    fpsWorst: 60,
    heapMaxMB: null,
    listenersMaxCount: 0,
    gqlCallCount: 0,
    gqlWorst: null,
    componentWorst: null,
    storageWorst: null,
  };

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

          window.__sessionStats.gqlCallCount++;
          if (!window.__sessionStats.gqlWorst || duration > window.__sessionStats.gqlWorst.duration) {
            window.__sessionStats.gqlWorst = { operation, duration };
          }

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

  // --- event listener teller, uitgesplitst per event-type (leak-indicator + pointer naar bron) ---
  const originalAddEventListener = EventTarget.prototype.addEventListener;
  const originalRemoveEventListener = EventTarget.prototype.removeEventListener;
  EventTarget.prototype.addEventListener = function (type: string, ...rest) {
    window.__activeListeners++;
    window.__listenersByType[type] = (window.__listenersByType[type] ?? 0) + 1;
    if (window.__activeListeners > window.__sessionStats.listenersMaxCount) {
      window.__sessionStats.listenersMaxCount = window.__activeListeners;
    }
    return originalAddEventListener.call(this, type, ...(rest as [EventListenerOrEventListenerObject, (boolean | AddEventListenerOptions)?]));
  };
  EventTarget.prototype.removeEventListener = function (type: string, ...rest) {
    window.__activeListeners = Math.max(0, window.__activeListeners - 1);
    window.__listenersByType[type] = Math.max(0, (window.__listenersByType[type] ?? 0) - 1);
    return originalRemoveEventListener.call(this, type, ...(rest as [EventListenerOrEventListenerObject, (boolean | EventListenerOptions)?]));
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

    if (!window.__sessionStats.storageWorst || duration > window.__sessionStats.storageWorst.duration) {
      window.__sessionStats.storageWorst = { key, duration };
    }

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
      for (const entry of list.getEntries()) {
        if (!window.__sessionStats.componentWorst || entry.duration > window.__sessionStats.componentWorst.duration) {
          window.__sessionStats.componentWorst = { name: entry.name, duration: Math.round(entry.duration * 10) / 10 };
        }
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

        window.__sessionStats.longTaskCount++;
        window.__sessionStats.blockedMsTotal += duration;
        if (duration > window.__sessionStats.longTaskWorstMs) window.__sessionStats.longTaskWorstMs = duration;

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
              : "geen — waarschijnlijk achtergrondproces (polling/websocket/GC)",
          ],
          [
            "Traagste component(en) tijdens blok",
            overlapping.length ? overlapping.map((m) => `${m.name} (${m.duration}ms)`).join(", ") : "geen — check GraphQL/storage/listeners in het 2s-rapport",
          ],
          ["Listeners op dit moment", `${window.__activeListeners} totaal`],
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
    const topListenerTypes = Object.entries(window.__listenersByType)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10);

    const lines = [
      "=============== PERF REPORT START ===============",
      "",
      `Perf report v${PERF_DEBUG_VERSION} — ${new Date().toLocaleString()}`,
      `User agent: ${navigator.userAgent}`,
      `JS Heap: ${heapMB ?? "n/a"}MB | DOM nodes: ${document.getElementsByTagName("*").length}`,
      `Actieve intervals: ${window.__activeIntervals} | timeouts: ${window.__activeTimeouts} | listeners: ${window.__activeListeners} | open sockets: ${window.__wsOpenCount}`,
      "",
      `--- Sessie-totalen (sinds start, ${Math.round((performance.now() - window.__sessionStats.sessionStartTime) / 1000)}s geleden) ---`,
      `Ergste FPS ooit: ${window.__sessionStats.fpsWorst}`,
      `Ergste long task ooit: ${window.__sessionStats.longTaskWorstMs}ms (totaal ${window.__sessionStats.longTaskCount}x, ${window.__sessionStats.blockedMsTotal}ms geblokkeerd)`,
      `Hoogste JS Heap ooit: ${window.__sessionStats.heapMaxMB ?? "n/a"}MB`,
      `Hoogste aantal listeners ooit: ${window.__sessionStats.listenersMaxCount}`,
      `Traagste GraphQL call ooit: ${window.__sessionStats.gqlWorst ? `${window.__sessionStats.gqlWorst.duration}ms — ${window.__sessionStats.gqlWorst.operation}` : "n/a"} (totaal ${window.__sessionStats.gqlCallCount} calls)`,
      `Traagste component ooit: ${window.__sessionStats.componentWorst ? `${window.__sessionStats.componentWorst.duration}ms — ${window.__sessionStats.componentWorst.name}` : "n/a"}`,
      `Traagste localStorage write ooit: ${window.__sessionStats.storageWorst ? `${window.__sessionStats.storageWorst.duration}ms — ${window.__sessionStats.storageWorst.key}` : "n/a"}`,
      "",
      "--- Listeners per type (top 10) ---",
      ...(topListenerTypes.length ? topListenerTypes.map(([type, count]) => `${count}x — ${type}`) : ["(geen data)"]),
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
      "",
      "================ PERF REPORT END ================",
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
  // Periodiek rapport
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

    // Sessie-brede aggregaten bijwerken (los van dit 2s-venster)
    if (fps < window.__sessionStats.fpsWorst) window.__sessionStats.fpsWorst = fps;
    if (heapMB !== null && (window.__sessionStats.heapMaxMB === null || heapMB > window.__sessionStats.heapMaxMB)) {
      window.__sessionStats.heapMaxMB = heapMB;
    }

    const cutoff = performance.now() - REPORT_INTERVAL_MS;
    const vueCutoff = performance.now() - 5000;
    const recentGql = window.__graphqlCalls.filter((c) => c.time > cutoff);
    const recentWrites = window.__storageWrites.filter((w) => w.time > cutoff);
    const recentComponents = window.__recentVueMeasures.filter((m) => m.startTime > vueCutoff - performance.timeOrigin);

    console.log(" ");
    console.log("%c=========== RAPPORT START ===========", "color:#06c");
    console.group(
      `%c⏱ Perf rapport ${new Date().toLocaleTimeString()}%c — uptime ${uptimeSec}s`,
      "color:#06c; font-weight:bold",
      "color:inherit; font-weight:normal",
    );

    // Tabel 0: sessie-totalen SINDS START — altijd getoond, vangt pieken die je gemist hebt
    const sessionUptimeSec = Math.round((performance.now() - window.__sessionStats.sessionStartTime) / 1000);
    console.log(`%cSessie-totalen (sinds start, ${sessionUptimeSec}s geleden):`, "font-weight:bold");
    console.table([
      { Meting: "Ergste FPS ooit", Waarde: window.__sessionStats.fpsWorst, Alarm: window.__sessionStats.fpsWorst < 20 ? "⚠️" : "" },
      { Meting: "Ergste long task ooit", Waarde: `${window.__sessionStats.longTaskWorstMs}ms`, Alarm: window.__sessionStats.longTaskWorstMs > 500 ? "⚠️" : "" },
      { Meting: "Long tasks totaal", Waarde: window.__sessionStats.longTaskCount },
      { Meting: "Main thread geblokkeerd totaal", Waarde: `${window.__sessionStats.blockedMsTotal}ms` },
      { Meting: "Hoogste JS Heap ooit", Waarde: window.__sessionStats.heapMaxMB !== null ? `${window.__sessionStats.heapMaxMB}MB` : "n/a" },
      { Meting: "Hoogste aantal listeners ooit", Waarde: window.__sessionStats.listenersMaxCount, Alarm: window.__sessionStats.listenersMaxCount > 500 ? "⚠️" : "" },
      { Meting: "Trage GraphQL call, ergste", Waarde: window.__sessionStats.gqlWorst ? `${window.__sessionStats.gqlWorst.duration}ms — ${window.__sessionStats.gqlWorst.operation}` : "n/a", Alarm: window.__sessionStats.gqlWorst && window.__sessionStats.gqlWorst.duration > GQL_SLOW_MS ? "⚠️" : "" },
      { Meting: "GraphQL calls totaal", Waarde: window.__sessionStats.gqlCallCount },
      { Meting: "Traagste component ooit", Waarde: window.__sessionStats.componentWorst ? `${window.__sessionStats.componentWorst.duration}ms — ${window.__sessionStats.componentWorst.name}` : "n/a" },
      { Meting: "Traagste localStorage write ooit", Waarde: window.__sessionStats.storageWorst ? `${window.__sessionStats.storageWorst.duration}ms — ${window.__sessionStats.storageWorst.key}` : "n/a" },
    ]);

    // Tabel 1: vitals (dit venster van 2s) — altijd getoond, vast format
    console.log("%cDit venster (laatste 2s):", "font-weight:bold");
    console.table([
      { Meting: "FPS", Waarde: fps, Alarm: fps < 30 ? "⚠️ laag" : "" },
      { Meting: "Traagste frame", Waarde: `${worstFrameMs.toFixed(0)}ms`, Alarm: worstFrameMs > 100 ? "⚠️" : "" },
      { Meting: "Long tasks (>50ms)", Waarde: longTasks.length, Alarm: longTasks.length ? `⚠️ traagste ${worstLongTask}ms` : "" },
      { Meting: "Main thread geblokkeerd", Waarde: `${totalBlockedMs}/${REPORT_INTERVAL_MS}ms`, Alarm: totalBlockedMs > 200 ? "⚠️" : "" },
      { Meting: "Event loop lag", Waarde: `${window.__eventLoopLagMs}ms`, Alarm: window.__eventLoopLagMs > 30 ? "⚠️ druk" : "" },
      { Meting: "JS Heap", Waarde: heapMB !== null ? `${heapMB}MB` : "n/a", Alarm: heapGrowth !== null && heapGrowth > 5 ? `⚠️ +${heapGrowth}MB sinds start` : "" },
      { Meting: "DOM nodes", Waarde: domNodes },
      { Meting: "Netwerk / intervals / timeouts / listeners / sockets", Waarde: `${window.__activeRequests} / ${window.__activeIntervals} / ${window.__activeTimeouts} / ${window.__activeListeners} / ${window.__wsOpenCount}`, Alarm: window.__activeListeners > 500 ? "⚠️ veel listeners" : "" },
    ]);

    // Tabel 2: listeners per type — alleen tonen als het aantal hoog is of oploopt, top 8
    const listenerRows = Object.entries(window.__listenersByType)
      .filter(([, count]) => count > 5)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 8)
      .map(([type, count]) => ({ Type: type, Aantal: count }));
    if (listenerRows.length) {
      console.log(`%cEvent listeners per type (top ${listenerRows.length}, totaal ${window.__activeListeners}):`, "font-weight:bold");
      console.table(listenerRows);
    }

    // Tabel 3: alle componenten (laatste 5s)
    const componentRows = recentComponents
      .filter((m) => m.duration > 4)
      .sort((a, b) => b.duration - a.duration)
      .map((m) => ({ Component: m.name, "Duur (ms)": m.duration, Alarm: m.duration > 100 ? "⚠️" : "" }));
    if (componentRows.length) {
      console.log(`%cTraagste componenten (laatste 5s, ${componentRows.length}x):`, "font-weight:bold");
      console.table(componentRows);
    }

    // Tabel 4: alle GraphQL calls in dit venster
    if (recentGql.length) {
      console.log(`%cGraphQL calls (laatste 2s, ${recentGql.length}x):`, "font-weight:bold");
      console.table(
        recentGql
          .sort((a, b) => b.duration - a.duration)
          .map((c) => ({ Operation: c.operation, "Duur (ms)": c.duration, "Payload (KB)": c.sizeKB, Alarm: c.duration > GQL_SLOW_MS ? "⚠️ traag" : "" })),
      );
    }

    // Tabel 5: alle localStorage writes in dit venster
    if (recentWrites.length) {
      console.log(`%clocalStorage writes (laatste 2s, ${recentWrites.length}x):`, "font-weight:bold");
      console.table(
        recentWrites
          .sort((a, b) => b.duration - a.duration)
          .map((w) => ({ Key: w.key, "Duur (ms)": w.duration, "Omvang (KB)": w.sizeKB, Alarm: w.duration > STORAGE_SLOW_MS ? "⚠️ traag" : "" })),
      );
    }

    console.groupEnd();
    console.log("%c============ RAPPORT EIND ============", "color:#06c");
    console.log(" ");

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
    `%c✓ Perf monitor v${PERF_DEBUG_VERSION} actief%c — elke 2s een rapport. getTabReport() / exportPerfReport() / stopPerfMonitor() beschikbaar.`,
    "color: green; font-weight: bold",
    "color: inherit; font-weight: normal",
  );
}
