import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { AlertTriangle, Shield, CheckCircle, Loader2, ClipboardPaste, Key, Copy } from "lucide-react";
import { cn } from "@/lib/utils";
import { api } from "@/lib/api";

const SCRIPT_URL = "https://cdn.jsdelivr.net/gh/11e3/bitcoach@master/frontend/public/upbit-export.js";

type Method = "script" | "api_key";

export default function Setup() {
  const navigate = useNavigate();
  const [method, setMethod] = useState<Method>("script");
  const [pasteText, setPasteText] = useState("");
  const [accessKey, setAccessKey] = useState("");
  const [secretKey, setSecretKey] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [scriptCopied, setScriptCopied] = useState(false);
  const [scriptText, setScriptText] = useState<string | null>(null);

  const handleCopyScript = async () => {
    try {
      let text = scriptText;
      if (!text) {
        const resp = await fetch(`${SCRIPT_URL}?t=${Date.now()}`);
        text = await resp.text();
        setScriptText(text);
      }
      await navigator.clipboard.writeText(text);
      setScriptCopied(true);
      setTimeout(() => setScriptCopied(false), 2000);
    } catch {
      setError("스크립트 복사 실패. 페이지를 새로고침 후 다시 시도해주세요.");
    }
  };

  const handlePaste = async () => {
    if (!pasteText.trim()) return;
    setLoading(true);
    setError(null);
    setStatus("거래내역 파싱 중...");

    try {
      const result = await api.pasteTrades(pasteText);
      setStatus(`${result.synced}건 저장 완료! (총 ${result.total_parsed}건 파싱)`);
      setTimeout(() => navigate("/dashboard"), 1500);
    } catch (e: any) {
      setError(e.message || "파싱 실패");
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async () => {
    if (!accessKey || !secretKey) return;
    setLoading(true);
    setError(null);
    setStatus("업비트 연결 확인 중...");

    try {
      const connectResult = await api.connect(accessKey, secretKey);
      if (!connectResult.success) {
        setError(connectResult.message);
        return;
      }
      setStatus("연결 성공! 거래내역 동기화 중... (1~2분 소요)");
      const syncResult = await api.syncTrades();
      setStatus(
        `${syncResult.synced}건 동기화 완료!` +
        (syncResult.market_orders_enriched
          ? ` (시장가 ${syncResult.market_orders_enriched}건 체결가 수집)`
          : "")
      );
      setTimeout(() => navigate("/dashboard"), 1500);
    } catch (e: any) {
      setError(e.message || "연결 실패");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-lg">
      <h1 className="mb-2 text-2xl font-bold text-gray-900">설정</h1>
      <p className="mb-8 text-sm text-gray-500">
        거래내역을 가져올 방법을 선택하세요
      </p>

      {/* Method tabs */}
      <div className="mb-6 flex gap-2">
        <button
          onClick={() => { setMethod("script"); setError(null); setStatus(null); }}
          className={cn(
            "flex items-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium transition-colors",
            method === "script"
              ? "bg-brand-600 text-white"
              : "bg-gray-100 text-gray-600 hover:bg-gray-200"
          )}
        >
          <ClipboardPaste className="h-4 w-4" />
          거래내역 가져오기
        </button>
        <button
          onClick={() => { setMethod("api_key"); setError(null); setStatus(null); }}
          className={cn(
            "flex items-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium transition-colors",
            method === "api_key"
              ? "bg-brand-600 text-white"
              : "bg-gray-100 text-gray-600 hover:bg-gray-200"
          )}
        >
          <Key className="h-4 w-4" />
          API Key
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Status */}
      {status && !error && (
        <div className="mb-4 flex items-start gap-2 rounded-lg border border-green-200 bg-green-50 p-3 text-sm text-green-700">
          {loading ? (
            <Loader2 className="mt-0.5 h-4 w-4 flex-shrink-0 animate-spin" />
          ) : (
            <CheckCircle className="mt-0.5 h-4 w-4 flex-shrink-0" />
          )}
          <span className="whitespace-pre-line">{status}</span>
        </div>
      )}

      {/* Script method */}
      {method === "script" && (
        <div className="space-y-4">
          <div className="rounded-lg border border-blue-200 bg-blue-50 p-4">
            <p className="mb-3 text-sm font-semibold text-blue-800">
              업비트 거래내역 자동 수집
            </p>
            <ol className="space-y-2.5 text-xs text-blue-800">
              <li className="flex gap-2">
                <span className="font-bold text-blue-600">①</span>
                <span>아래 <b>"수집 스크립트 복사"</b> 버튼 클릭</span>
              </li>
              <li className="flex gap-2">
                <span className="font-bold text-blue-600">②</span>
                <span>
                  <a href="https://upbit.com/investments/history" target="_blank" rel="noopener noreferrer" className="underline">
                    업비트 투자내역
                  </a>
                  {" "}페이지 열기 (로그인 필수)
                </span>
              </li>
              <li className="flex gap-2">
                <span className="font-bold text-blue-600">③</span>
                <span><b>F12</b> → <b>Sources</b> 탭 → 좌측 <b>Snippets</b> → <b>New snippet</b></span>
              </li>
              <li className="flex gap-2">
                <span className="font-bold text-blue-600">④</span>
                <span>편집 영역에 <b>Ctrl+V</b> (스크립트 붙여넣기)</span>
              </li>
              <li className="flex gap-2">
                <span className="font-bold text-blue-600">⑤</span>
                <span>
                  <b>Ctrl+Enter</b> 또는 우클릭 → <b>Run</b> (수집 팝업이 뜨고 자동 완료)
                </span>
              </li>
              <li className="flex gap-2">
                <span className="font-bold text-blue-600">⑥</span>
                <span>아래 입력창에 <b>Ctrl+V</b> (클립보드에 자동 복사됨)</span>
              </li>
            </ol>
          </div>

          <button
            onClick={handleCopyScript}
            className="flex w-full items-center justify-center gap-2 rounded-lg border border-gray-300 bg-white py-2.5 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
          >
            <Copy className="h-4 w-4" />
            {scriptCopied ? "복사됨!" : "수집 스크립트 복사"}
          </button>

          <textarea
            value={pasteText}
            onChange={(e) => setPasteText(e.target.value)}
            placeholder="수집 완료 후 여기에 Ctrl+V"
            rows={6}
            className="w-full rounded-lg border border-gray-300 px-3 py-2.5 font-mono text-xs focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
          />

          <button
            onClick={handlePaste}
            disabled={!pasteText.trim() || loading}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-brand-600 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-brand-700 disabled:opacity-50"
          >
            {loading && <Loader2 className="h-4 w-4 animate-spin" />}
            {loading ? "저장 중..." : "거래내역 저장 및 분석 시작"}
          </button>
        </div>
      )}

      {/* API Key method */}
      {method === "api_key" && (
        <div className="space-y-4">
          <div className="rounded-lg border border-amber-200 bg-amber-50 p-4">
            <div className="flex gap-3">
              <AlertTriangle className="h-5 w-5 flex-shrink-0 text-amber-600" />
              <div className="text-sm text-amber-800">
                <p className="mb-1 font-semibold">API Key 제한사항</p>
                <p>고정 IP 등록 필수. 업비트 API 한계로 일부 거래만 조회될 수 있습니다. 전체 내역이 필요하면 "거래내역 가져오기" 탭을 이용하세요.</p>
              </div>
            </div>
          </div>

          <div className="rounded-lg border border-blue-200 bg-blue-50 p-4">
            <div className="flex gap-3">
              <Shield className="h-5 w-5 flex-shrink-0 text-blue-600" />
              <div className="text-sm text-blue-800">
                <p>API Key는 서버 메모리에만 보관. 출금 권한 OFF, 조회 전용으로 발급하세요.</p>
              </div>
            </div>
          </div>

          <div>
            <label className="mb-1.5 block text-sm font-medium text-gray-700">Access Key</label>
            <input
              type="password" value={accessKey}
              onChange={(e) => setAccessKey(e.target.value)}
              placeholder="업비트 Access Key"
              className="w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
          </div>
          <div>
            <label className="mb-1.5 block text-sm font-medium text-gray-700">Secret Key</label>
            <input
              type="password" value={secretKey}
              onChange={(e) => setSecretKey(e.target.value)}
              placeholder="업비트 Secret Key"
              className="w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
          </div>

          <button
            onClick={handleConnect}
            disabled={!accessKey || !secretKey || loading}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-brand-600 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-brand-700 disabled:opacity-50"
          >
            {loading && <Loader2 className="h-4 w-4 animate-spin" />}
            {loading ? "동기화 중..." : "연결 및 거래내역 가져오기"}
          </button>
        </div>
      )}
    </div>
  );
}
