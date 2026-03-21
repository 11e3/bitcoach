import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  BotMessageSquare, Plus, FileText, ChevronRight, Target,
  TrendingUp, AlertTriangle, Lightbulb, CheckCircle2, Loader2,
} from "lucide-react";
import { api } from "@/lib/api";
import { formatDateTime, cn } from "@/lib/utils";

// --- Report Detail View ---

function ReportDetail({ report, onBack }: { report: any; onBack: () => void }) {
  const sections = [
    { icon: FileText, label: "요약", content: report.summary, color: "text-brand-600", bg: "bg-brand-50" },
    { icon: TrendingUp, label: "강점", content: report.strengths, color: "text-green-600", bg: "bg-green-50" },
    { icon: AlertTriangle, label: "약점", content: report.weaknesses, color: "text-red-600", bg: "bg-red-50" },
    { icon: Lightbulb, label: "개선 제안", content: report.suggestions, color: "text-amber-600", bg: "bg-amber-50" },
  ];

  const priorityColors: Record<string, string> = {
    high: "border-red-200 bg-red-50 text-red-700",
    medium: "border-amber-200 bg-amber-50 text-amber-700",
    low: "border-green-200 bg-green-50 text-green-700",
  };

  return (
    <div>
      <button
        onClick={onBack}
        className="mb-4 text-sm text-gray-500 hover:text-gray-700"
      >
        ← 목록으로
      </button>

      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-900">코칭 리포트</h2>
          <p className="text-xs text-gray-400">
            {formatDateTime(report.created_at)} · {report.trade_count}건 분석
          </p>
        </div>
      </div>

      {/* Sections */}
      <div className="mb-8 space-y-4">
        {sections.map(({ icon: Icon, label, content, color, bg }) => (
          <div key={label} className="rounded-xl border border-gray-100 bg-white shadow-sm">
            <div className={cn("flex items-center gap-2 rounded-t-xl px-5 py-3", bg)}>
              <Icon className={cn("h-4 w-4", color)} />
              <span className={cn("text-sm font-semibold", color)}>{label}</span>
            </div>
            <div className="px-5 py-4">
              <p className="whitespace-pre-wrap text-sm leading-relaxed text-gray-700">
                {content || "데이터 없음"}
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Action Items */}
      {report.action_items?.length > 0 && (
        <div>
          <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold text-gray-700">
            <Target className="h-4 w-4 text-brand-600" />
            액션 아이템
          </h3>
          <div className="space-y-3">
            {report.action_items.map((item: any, i: number) => (
              <div
                key={i}
                className={cn(
                  "rounded-lg border p-4",
                  priorityColors[item.priority] || "border-gray-200 bg-gray-50"
                )}
              >
                <div className="mb-1 flex items-start justify-between">
                  <p className="text-sm font-medium">{item.action}</p>
                  <span className="ml-2 shrink-0 rounded-full px-2 py-0.5 text-[10px] font-bold uppercase">
                    {item.priority}
                  </span>
                </div>
                <div className="mt-2 flex gap-4 text-xs opacity-75">
                  <span>📏 {item.metric}</span>
                  <span>⏰ {item.timeframe}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// --- Main Coaching Page ---

export default function Coaching() {
  const [generating, setGenerating] = useState(false);
  const [genStatus, setGenStatus] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<number | null>(null);

  const { data: reports, isLoading, refetch } = useQuery({
    queryKey: ["coaching-reports"],
    queryFn: () => api.getReports() as Promise<any[]>,
  });

  const selectedReport = reports?.find((r: any) => r.id === selectedId);

  const handleGenerate = async () => {
    setGenerating(true);
    setGenStatus("거래 분류 중 (Haiku)...");

    try {
      const result = await api.generateReport() as any;
      setGenStatus(null);
      await refetch();
      setSelectedId(result.report_id);
    } catch (e: any) {
      setGenStatus(`오류: ${e.message}`);
    } finally {
      setGenerating(false);
    }
  };

  // Detail view
  if (selectedReport) {
    return <ReportDetail report={selectedReport} onBack={() => setSelectedId(null)} />;
  }

  // List view
  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">AI 코칭</h1>
        <button
          onClick={handleGenerate}
          disabled={generating}
          className="inline-flex items-center gap-2 rounded-lg bg-brand-600 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-brand-700 disabled:opacity-50"
        >
          {generating ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Plus className="h-4 w-4" />
          )}
          {generating ? "분석 중..." : "새 리포트 생성"}
        </button>
      </div>

      {/* Generation status */}
      {genStatus && (
        <div className="mb-4 rounded-lg border border-brand-200 bg-brand-50 p-3 text-sm text-brand-700">
          {genStatus}
        </div>
      )}

      {/* Pipeline explanation */}
      <div className="mb-6 flex items-center gap-2 overflow-x-auto rounded-lg border border-gray-100 bg-gray-50 px-4 py-3">
        {["분류 (Haiku)", "통계 (Python)", "패턴 (Haiku)", "코칭 (Sonnet)", "액션 (Sonnet)"].map(
          (step, i) => (
            <span key={step} className="flex shrink-0 items-center gap-1.5 text-xs text-gray-500">
              {i > 0 && <ChevronRight className="h-3 w-3 text-gray-300" />}
              <span className={cn(
                "rounded-full px-2.5 py-1 font-medium",
                i < 2 ? "bg-blue-100 text-blue-700" :
                i < 3 ? "bg-purple-100 text-purple-700" :
                "bg-green-100 text-green-700"
              )}>
                {step}
              </span>
            </span>
          )
        )}
      </div>

      {isLoading ? (
        <div className="flex h-48 items-center justify-center text-gray-400">
          <Loader2 className="mr-2 h-5 w-5 animate-spin" /> 로딩 중...
        </div>
      ) : !reports || reports.length === 0 ? (
        <div className="flex h-48 flex-col items-center justify-center text-center">
          <BotMessageSquare className="mb-4 h-12 w-12 text-gray-300" />
          <p className="mb-2 text-lg font-semibold text-gray-600">
            아직 코칭 리포트가 없습니다
          </p>
          <p className="text-sm text-gray-400">
            "새 리포트 생성"을 눌러 LangGraph AI 분석을 시작하세요
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {reports.map((report: any) => (
            <button
              key={report.id}
              onClick={() => setSelectedId(report.id)}
              className="w-full cursor-pointer rounded-xl border border-gray-100 bg-white p-5 text-left shadow-sm transition-shadow hover:shadow-md"
            >
              <div className="flex items-start gap-3">
                <CheckCircle2 className="mt-0.5 h-5 w-5 flex-shrink-0 text-green-500" />
                <div className="flex-1">
                  <p className="font-semibold text-gray-900">
                    {report.summary.slice(0, 120)}
                    {report.summary.length > 120 ? "..." : ""}
                  </p>
                  <div className="mt-2 flex gap-4 text-xs text-gray-400">
                    <span>{formatDateTime(report.created_at)}</span>
                    <span>{report.trade_count}건 분석</span>
                    <span>{report.action_items?.length || 0}개 액션</span>
                  </div>
                </div>
                <ChevronRight className="h-5 w-5 text-gray-300" />
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
