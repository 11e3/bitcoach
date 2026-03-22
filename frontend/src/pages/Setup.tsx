import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { CheckCircle, Loader2 } from "lucide-react";
import { api } from "@/lib/api";

export default function Setup() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [pasteText, setPasteText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);

  const handlePaste = async () => {
    if (!pasteText.trim()) return;
    setLoading(true);
    setError(null);
    setStatus("거래내역 파싱 중...");

    try {
      const result = await api.pasteTrades(pasteText);
      setStatus(`${result.synced}건 저장 완료! (총 ${result.total_parsed}건 파싱)`);
      // Invalidate dashboard queries so they refetch with new data
      await queryClient.invalidateQueries();
      setTimeout(() => navigate("/dashboard"), 1500);
    } catch (e: any) {
      setError(e.message || "파싱 실패");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-lg">
      <h1 className="mb-2 text-2xl font-bold text-gray-900">설정</h1>
      <p className="mb-8 text-sm text-gray-500">
        업비트 거래내역을 복사-붙여넣기로 가져옵니다
      </p>

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

      <div className="space-y-4">
        <div className="rounded-lg border border-blue-200 bg-blue-50 p-4">
          <p className="mb-3 text-sm font-semibold text-blue-800">
            업비트 거래내역 복사-붙여넣기
          </p>
          <ol className="space-y-2 text-xs text-blue-800">
            <li className="flex gap-2">
              <span className="font-bold text-blue-600">①</span>
              <span>
                <a href="https://upbit.com/investments/history" target="_blank" rel="noopener noreferrer" className="underline font-semibold">
                  업비트 투자내역
                </a>
                {" "}페이지 열기 (로그인 필수)
              </span>
            </li>
            <li className="flex gap-2">
              <span className="font-bold text-blue-600">②</span>
              <span>거래내역을 <b>드래그</b>하여 선택 → <b>Ctrl+C</b> 복사</span>
            </li>
            <li className="flex gap-2">
              <span className="font-bold text-blue-600">③</span>
              <span>아래 입력창에 <b>Ctrl+V</b> 붙여넣기</span>
            </li>
          </ol>
          <p className="mt-2.5 text-xs text-blue-600">
            메뉴, 헤더 등이 함께 복사되어도 자동으로 거래내역만 추출합니다.
            입출금 기록도 자동 제외됩니다.
          </p>
        </div>

        <textarea
          value={pasteText}
          onChange={(e) => setPasteText(e.target.value)}
          placeholder="업비트에서 복사한 거래내역을 여기에 붙여넣기 (Ctrl+V)"
          rows={8}
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
    </div>
  );
}
