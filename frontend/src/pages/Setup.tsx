import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Key, Upload, AlertTriangle, Shield, CheckCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import { api } from "@/lib/api";
import type { AuthMethod } from "@/types";

export default function Setup() {
  const navigate = useNavigate();
  const [method, setMethod] = useState<AuthMethod>("api_key");
  const [accessKey, setAccessKey] = useState("");
  const [secretKey, setSecretKey] = useState("");
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);

  const handleConnect = async () => {
    if (!accessKey || !secretKey) return;
    setLoading(true);
    setError(null);
    setStatus("업비트 연결 확인 중...");

    try {
      // Step 1: Connect (sends keys to backend memory)
      const connectResult = await api.connect(accessKey, secretKey);
      if (!connectResult.success) {
        setError(connectResult.message);
        return;
      }

      setStatus(`연결 성공! ${connectResult.balance_count}개 잔고 확인. 거래내역 동기화 중...`);

      // Step 2: Sync trades
      const syncResult = await api.syncTrades();
      setStatus(`${syncResult.synced}건 동기화 완료!`);

      // Navigate after brief delay
      setTimeout(() => navigate("/dashboard"), 1000);
    } catch (e: any) {
      setError(e.message || "연결 실패");
    } finally {
      setLoading(false);
    }
  };

  const handleCsvUpload = async () => {
    if (!csvFile) return;
    setLoading(true);
    setError(null);
    setStatus("CSV 파싱 중...");

    try {
      const result = await api.uploadCsv(csvFile);
      setStatus(`${result.synced}건 저장 완료!`);
      setTimeout(() => navigate("/dashboard"), 1000);
    } catch (e: any) {
      setError(e.message || "업로드 실패");
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
        {(["api_key", "csv"] as const).map((m) => (
          <button
            key={m}
            onClick={() => { setMethod(m); setError(null); setStatus(null); }}
            className={cn(
              "flex items-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium transition-colors",
              method === m
                ? "bg-brand-600 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            )}
          >
            {m === "api_key" ? <Key className="h-4 w-4" /> : <Upload className="h-4 w-4" />}
            {m === "api_key" ? "API Key" : "CSV 업로드"}
          </button>
        ))}
      </div>

      {/* Error */}
      {error && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Status */}
      {status && !error && (
        <div className="mb-4 flex items-center gap-2 rounded-lg border border-green-200 bg-green-50 p-3 text-sm text-green-700">
          <CheckCircle className="h-4 w-4" />
          {status}
        </div>
      )}

      {/* API Key form */}
      {method === "api_key" && (
        <div className="space-y-4">
          <div className="rounded-lg border border-blue-200 bg-blue-50 p-4">
            <div className="flex gap-3">
              <Shield className="h-5 w-5 flex-shrink-0 text-blue-600" />
              <div className="text-sm text-blue-800">
                <p className="mb-1 font-semibold">보안 안내</p>
                <p>
                  API Key는 <strong>서버 메모리에만</strong> 보관되며,
                  디스크/DB에 저장되지 않습니다. 서버 재시작 시 자동 삭제됩니다.
                </p>
                <p className="mt-1">
                  업비트에서 <strong>출금 권한 OFF, 조회 전용</strong>으로
                  발급해주세요.
                </p>
              </div>
            </div>
          </div>

          <div className="rounded-lg border border-amber-200 bg-amber-50 p-4">
            <div className="flex gap-3">
              <AlertTriangle className="h-5 w-5 flex-shrink-0 text-amber-600" />
              <div className="text-sm text-amber-800">
                <p>
                  업비트 Exchange API는 <strong>고정 IP 등록이 필수</strong>입니다.
                  로컬에서 사용 시 공인 IP를 업비트 API 설정에 등록해주세요.
                </p>
              </div>
            </div>
          </div>

          <div>
            <label className="mb-1.5 block text-sm font-medium text-gray-700">
              Access Key
            </label>
            <input
              type="password"
              value={accessKey}
              onChange={(e) => setAccessKey(e.target.value)}
              placeholder="업비트 Access Key"
              className="w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
          </div>

          <div>
            <label className="mb-1.5 block text-sm font-medium text-gray-700">
              Secret Key
            </label>
            <input
              type="password"
              value={secretKey}
              onChange={(e) => setSecretKey(e.target.value)}
              placeholder="업비트 Secret Key"
              className="w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
          </div>

          <button
            onClick={handleConnect}
            disabled={!accessKey || !secretKey || loading}
            className="w-full rounded-lg bg-brand-600 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-brand-700 disabled:opacity-50"
          >
            {loading ? "연결 중..." : "연결 및 거래내역 가져오기"}
          </button>
        </div>
      )}

      {/* CSV upload */}
      {method === "csv" && (
        <div className="space-y-4">
          <p className="text-sm text-gray-500">
            업비트 앱 → 입출금 → 거래내역 → CSV 다운로드 후 업로드해주세요.
            API Key 없이도 사용 가능합니다.
          </p>

          <label className="flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-gray-300 bg-white p-8 transition-colors hover:border-brand-400">
            <Upload className="mb-3 h-8 w-8 text-gray-400" />
            <span className="text-sm font-medium text-gray-600">
              {csvFile ? csvFile.name : "CSV 파일을 선택하거나 드래그하세요"}
            </span>
            <input
              type="file"
              accept=".csv"
              className="hidden"
              onChange={(e) => setCsvFile(e.target.files?.[0] ?? null)}
            />
          </label>

          <button
            onClick={handleCsvUpload}
            disabled={!csvFile || loading}
            className="w-full rounded-lg bg-brand-600 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-brand-700 disabled:opacity-50"
          >
            {loading ? "업로드 중..." : "업로드 및 분석 시작"}
          </button>
        </div>
      )}
    </div>
  );
}
