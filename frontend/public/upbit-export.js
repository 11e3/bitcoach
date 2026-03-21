// bitcoach: Upbit 거래내역 자동 수집
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
    '<p id="bc-s" style="margin:0;font-size:14px;color:#aaa">인증 정보 검색 중...</p>' +
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

  // --- Find credentials in browser storage ---
  function searchStorage() {
    const stores = [localStorage, sessionStorage];
    let accessKey = null, secretKey = null, deviceId = null;

    for (const store of stores) {
      for (let i = 0; i < store.length; i++) {
        const key = store.key(i);
        const val = store.getItem(key);
        if (!val) continue;

        // Try parsing JSON values
        try {
          const parsed = typeof val === "string" && val.startsWith("{") ? JSON.parse(val) : null;
          if (parsed) {
            // Search nested objects for access_key, secret_key
            const searchObj = (obj, depth) => {
              if (depth > 3 || !obj || typeof obj !== "object") return;
              for (const [k, v] of Object.entries(obj)) {
                if (typeof v === "string" && v.length > 20 && v.length < 100) {
                  const kl = k.toLowerCase();
                  if (kl.includes("access") && kl.includes("key")) accessKey = v;
                  if (kl.includes("secret") && kl.includes("key")) secretKey = v;
                  if (kl.includes("device") && kl.includes("id")) deviceId = v;
                }
                if (typeof v === "object") searchObj(v, depth + 1);
                if (typeof v === "string" && v.startsWith("{")) {
                  try { searchObj(JSON.parse(v), depth + 1); } catch {}
                }
              }
            };
            searchObj(parsed, 0);
          }
        } catch {}

        // Also check key names directly
        const kl = key.toLowerCase();
        if (kl.includes("access") && val.length > 20 && val.length < 100) accessKey = val;
        if (kl.includes("secret") && val.length > 20 && val.length < 100) secretKey = val;
        if (kl.includes("device") && val.length > 20 && val.length < 100) deviceId = val;
      }
    }

    // Also search cookies
    document.cookie.split(";").forEach((c) => {
      const [name, ...rest] = c.split("=");
      const val = rest.join("=").trim();
      const n = name.trim().toLowerCase();
      if (n.includes("device") && val.length > 10) deviceId = val;
    });

    return { accessKey, secretKey, deviceId };
  }

  // --- JWT signing with Web Crypto API ---
  async function makeJWT(accessKey, secretKey, deviceId) {
    const header = { alg: "HS256", typ: "JWT" };
    const payload = {
      access_key: accessKey,
      nonce: Date.now(),
      device_id: deviceId || undefined,
    };

    const enc = new TextEncoder();
    const b64url = (s) =>
      btoa(s).replace(/=/g, "").replace(/\+/g, "-").replace(/\//g, "_");

    const hB64 = b64url(JSON.stringify(header));
    const pB64 = b64url(JSON.stringify(payload));
    const sigInput = `${hB64}.${pB64}`;

    const key = await crypto.subtle.importKey(
      "raw",
      enc.encode(secretKey),
      { name: "HMAC", hash: "SHA-256" },
      false,
      ["sign"]
    );
    const sig = await crypto.subtle.sign("HMAC", key, enc.encode(sigInput));
    const sB64 = b64url(String.fromCharCode(...new Uint8Array(sig)));

    return `${hB64}.${pB64}.${sB64}`;
  }

  // --- Main ---
  try {
    const creds = searchStorage();

    if (!creds.accessKey || !creds.secretKey) {
      sEl.textContent = "인증 정보를 찾을 수 없습니다.";
      sEl.style.color = "#f87171";
      box.innerHTML +=
        '<p style="margin:12px 0 0;font-size:12px;color:#aaa;text-align:left;line-height:1.6">' +
        "업비트 웹에 로그인된 상태에서 실행해주세요.<br>" +
        '그래도 안 되면 Console에서 <b style="color:#fff">allow pasting</b> 입력 후<br>' +
        "스크립트를 직접 붙여넣기 해주세요.</p>";
      addClose();
      return;
    }

    sEl.textContent = "거래내역 수집 시작...";

    const LIMIT = 100;
    const FROM = "2020-01-01T00:00:00.000+09:00";
    const TO = new Date().toISOString();
    const BASE = "https://ccx.upbit.com/api/v1/investments/events";

    let allEvents = [];
    let lastUuid = undefined;
    let page = 0;

    while (true) {
      const params = new URLSearchParams({
        limit: String(LIMIT),
        from: FROM,
        to: TO,
      });
      if (lastUuid) params.set("uuid", lastUuid);

      const token = await makeJWT(
        creds.accessKey,
        creds.secretKey,
        creds.deviceId
      );

      const resp = await fetch(`${BASE}?${params}`, {
        credentials: "include",
        headers: {
          Authorization: `Bearer ${token}`,
          Accept: "application/json",
        },
      });

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
