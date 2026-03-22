// bitcoach: Upbit 거래내역 수집 v6
// 방식: API 응답을 백그라운드로 가로채고, 사용자가 직접 스크롤
// DevTools > Sources > Snippets에서 실행
(async () => {
  const allEvents = [];
  const seenUuids = new Set();

  // --- Intercept fetch ---
  const origFetch = window.fetch;
  window.fetch = function (...args) {
    const url = typeof args[0] === "string" ? args[0] : args[0]?.url || "";
    const result = origFetch.apply(this, args);
    if (url.includes("investments/events")) {
      result.then(async (resp) => {
        try {
          const data = await resp.clone().json();
          if (Array.isArray(data)) {
            for (const e of data) {
              if ((e.event_type === "bid" || e.event_type === "ask") && !seenUuids.has(e.uuid)) {
                seenUuids.add(e.uuid);
                allEvents.push(e);
              }
            }
            cEl.textContent = `${allEvents.length.toLocaleString()}건`;
          }
        } catch {}
      });
    }
    return result;
  };

  // --- Intercept XMLHttpRequest ---
  const origOpen = XMLHttpRequest.prototype.open;
  const origSend = XMLHttpRequest.prototype.send;
  const xhrUrls = new WeakMap();
  XMLHttpRequest.prototype.open = function (m, url, ...r) {
    xhrUrls.set(this, url);
    return origOpen.call(this, m, url, ...r);
  };
  XMLHttpRequest.prototype.send = function (...args) {
    if ((xhrUrls.get(this) || "").includes("investments/events")) {
      this.addEventListener("load", function () {
        try {
          const data = JSON.parse(this.responseText);
          if (Array.isArray(data)) {
            for (const e of data) {
              if ((e.event_type === "bid" || e.event_type === "ask") && !seenUuids.has(e.uuid)) {
                seenUuids.add(e.uuid);
                allEvents.push(e);
              }
            }
            cEl.textContent = `${allEvents.length.toLocaleString()}건`;
          }
        } catch {}
      });
    }
    return origSend.apply(this, args);
  };

  // --- UI: floating bar at top (doesn't block scrolling) ---
  const bar = document.createElement("div");
  bar.style.cssText =
    "position:fixed;top:0;left:0;right:0;z-index:99999;background:#1a1a2e;color:#fff;padding:12px 20px;display:flex;align-items:center;justify-content:space-between;font-family:sans-serif;font-size:14px;box-shadow:0 2px 12px rgba(0,0,0,.5)";
  bar.innerHTML =
    '<div><b>bitcoach</b> · <span id="bc-s">거래내역을 맨 아래까지 스크롤하세요</span></div>' +
    '<div style="display:flex;align-items:center;gap:12px">' +
    '<span id="bc-c" style="font-size:20px;font-weight:bold;color:#0ea5e9">0건</span>' +
    '<button id="bc-done" style="padding:6px 16px;border:none;border-radius:6px;background:#0ea5e9;color:#fff;font-size:13px;cursor:pointer;font-weight:bold">수집 완료</button>' +
    "</div>";
  document.body.appendChild(bar);
  // Push page content down so bar doesn't cover it
  document.body.style.marginTop = "52px";

  const sEl = document.getElementById("bc-s");
  const cEl = document.getElementById("bc-c");

  // --- Wait for user to finish scrolling, then copy ---
  document.getElementById("bc-done").onclick = async () => {
    // Restore
    window.fetch = origFetch;
    XMLHttpRequest.prototype.open = origOpen;
    XMLHttpRequest.prototype.send = origSend;
    document.body.style.marginTop = "";

    if (allEvents.length === 0) {
      sEl.textContent = "수집된 거래가 없습니다. 스크롤 후 다시 시도하세요.";
      sEl.style.color = "#f87171";
      return;
    }

    try {
      await navigator.clipboard.writeText(JSON.stringify(allEvents));
      sEl.textContent = `${allEvents.length.toLocaleString()}건 클립보드 복사 완료! bitcoach 설정에서 Ctrl+V`;
      sEl.style.color = "#4ade80";
      document.getElementById("bc-done").textContent = "닫기";
      document.getElementById("bc-done").onclick = () => {
        bar.remove();
      };
    } catch {
      sEl.textContent = "클립보드 복사 실패";
      sEl.style.color = "#f87171";
    }
  };
})();
