// bitcoach: Upbit 거래내역 자동 수집
// DevTools > Sources > Snippets에서 실행
(async () => {
  // --- UI ---
  const overlay = document.createElement("div");
  overlay.style.cssText =
    "position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.7);z-index:99999;display:flex;align-items:center;justify-content:center;font-family:sans-serif";
  const box = document.createElement("div");
  box.style.cssText =
    "background:#1a1a2e;color:#fff;padding:32px 40px;border-radius:16px;text-align:center;min-width:340px";
  box.innerHTML =
    '<h2 style="margin:0 0 8px;font-size:18px">bitcoach</h2>' +
    '<p id="bc-s" style="margin:0;font-size:14px;color:#aaa">인증 토큰 감지 중...</p>' +
    '<p id="bc-c" style="margin:8px 0 0;font-size:24px;font-weight:bold;color:#0ea5e9">0건</p>';
  overlay.appendChild(box);
  document.body.appendChild(overlay);
  const sEl = document.getElementById("bc-s");
  const cEl = document.getElementById("bc-c");

  function addClose() {
    box.innerHTML +=
      '<button id="bc-x" style="margin-top:16px;padding:8px 24px;border:none;border-radius:8px;background:#0ea5e9;color:#fff;font-size:14px;cursor:pointer">닫기</button>';
    document.getElementById("bc-x").onclick = () => overlay.remove();
  }

  // --- Step 1: Intercept fetch/XHR to capture Authorization header ---
  let capturedToken = null;
  const origFetch = window.fetch;
  const origXHROpen = XMLHttpRequest.prototype.open;
  const origXHRSetHeader = XMLHttpRequest.prototype.setRequestHeader;

  window.fetch = function (...args) {
    try {
      const opts = args[1] || {};
      const headers = opts.headers;
      if (headers) {
        const h =
          headers instanceof Headers ? headers : new Headers(headers);
        const auth = h.get("authorization");
        if (auth && auth.startsWith("Bearer ")) capturedToken = auth;
      }
    } catch {}
    return origFetch.apply(this, args);
  };

  XMLHttpRequest.prototype.setRequestHeader = function (name, value) {
    if (
      name.toLowerCase() === "authorization" &&
      value.startsWith("Bearer ")
    ) {
      capturedToken = value;
    }
    return origXHRSetHeader.apply(this, arguments);
  };

  // --- Step 2: Wait for the page to make an authenticated request ---
  // Trigger a mini navigation to force the page to re-fetch data
  const currentUrl = location.href;
  const historyState = history.state;

  // Try triggering page's data refetch by dispatching events
  window.dispatchEvent(new Event("focus"));
  window.dispatchEvent(new Event("visibilitychange"));

  // Wait up to 15 seconds for a token
  for (let i = 0; i < 30; i++) {
    if (capturedToken) break;
    await new Promise((r) => setTimeout(r, 500));
    sEl.textContent = `인증 토큰 감지 중... (${Math.floor(i / 2)}초)`;
  }

  // Restore original functions
  window.fetch = origFetch;
  XMLHttpRequest.prototype.setRequestHeader = origXHRSetHeader;

  if (!capturedToken) {
    sEl.textContent = "인증 토큰을 감지하지 못했습니다.";
    sEl.style.color = "#f87171";
    box.innerHTML +=
      '<p style="margin:12px 0 0;font-size:12px;color:#aaa;line-height:1.6">' +
      "페이지의 다른 탭(거래소 등)을 클릭했다가<br>" +
      "다시 투자내역으로 돌아온 후 <b>다시 실행</b>해주세요.</p>";
    addClose();
    return;
  }

  // --- Step 3: Fetch all trade events using captured token ---
  sEl.textContent = "거래내역 수집 시작...";

  const LIMIT = 100;
  const FROM = "2020-01-01T00:00:00.000+09:00";
  const TO = new Date().toISOString();
  const BASE = "https://ccx.upbit.com/api/v1/investments/events";

  let allEvents = [];
  let lastUuid = undefined;
  let page = 0;

  try {
    while (true) {
      const params = new URLSearchParams({
        limit: String(LIMIT),
        from: FROM,
        to: TO,
      });
      if (lastUuid) params.set("uuid", lastUuid);

      const resp = await origFetch(`${BASE}?${params}`, {
        credentials: "include",
        headers: {
          Authorization: capturedToken,
          Accept: "application/json",
        },
      });

      if (resp.status === 401) {
        // Token expired, try to get a new one
        sEl.textContent = "토큰 만료. 페이지를 새로고침 후 다시 실행해주세요.";
        sEl.style.color = "#f87171";
        addClose();
        return;
      }

      if (!resp.ok) {
        sEl.textContent = `API 오류: ${resp.status}`;
        sEl.style.color = "#f87171";
        addClose();
        return;
      }

      const events = await resp.json();
      if (!events.length) break;

      const trades = events.filter(
        (e) => e.event_type === "bid" || e.event_type === "ask"
      );
      allEvents.push(...trades);

      page++;
      sEl.textContent = `페이지 ${page} 수집 중...`;
      cEl.textContent = `${allEvents.length.toLocaleString()}건`;

      lastUuid = events[events.length - 1].uuid;
      if (events.length < LIMIT) break;
      await new Promise((r) => setTimeout(r, 130));
    }

    await navigator.clipboard.writeText(JSON.stringify(allEvents));
    sEl.textContent = "클립보드 복사 완료!";
    sEl.style.color = "#4ade80";
    cEl.textContent = `${allEvents.length.toLocaleString()}건`;
    box.innerHTML +=
      '<p style="margin:16px 0 0;font-size:13px;color:#aaa">bitcoach 설정에서 <b>Ctrl+V</b></p>';
    addClose();
  } catch (err) {
    sEl.textContent = `오류: ${err.message}`;
    sEl.style.color = "#f87171";
    addClose();
  }
})();
