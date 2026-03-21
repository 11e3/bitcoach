import { useQuery } from "@tanstack/react-query";
import {
  TrendingUp, TrendingDown, BarChart3, Coins,
  Trophy,
} from "lucide-react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from "recharts";
import { api } from "@/lib/api";
import { formatKRW } from "@/lib/utils";
import { cn } from "@/lib/utils";

// --- Stat Card ---

function StatCard({
  label, value, sub, icon: Icon, color = "text-brand-600", bg = "bg-brand-50",
}: {
  label: string; value: string | number; sub?: string;
  icon: React.ElementType; color?: string; bg?: string;
}) {
  return (
    <div className="rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
      <div className="mb-3 flex items-center justify-between">
        <span className="text-sm font-medium text-gray-500">{label}</span>
        <div className={cn("rounded-lg p-2", bg)}>
          <Icon className={cn("h-4 w-4", color)} />
        </div>
      </div>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
      {sub && <p className="mt-1 text-xs text-gray-400">{sub}</p>}
    </div>
  );
}

// --- Chart Card wrapper ---

function ChartCard({ title, children, className }: {
  title: string; children: React.ReactNode; className?: string;
}) {
  return (
    <div className={cn("rounded-xl border border-gray-100 bg-white p-6 shadow-sm", className)}>
      <h3 className="mb-4 text-sm font-semibold text-gray-700">{title}</h3>
      {children}
    </div>
  );
}

// --- Colors ---

const COLORS = {
  profit: "#16a34a",
  loss: "#dc2626",
  brand: "#0c87f2",
  brandLight: "#7cc4ff",
  gray: "#9ca3af",
  buy: "#3b82f6",
  sell: "#f97316",
};

const PIE_COLORS = ["#0c87f2", "#16a34a", "#f97316", "#8b5cf6", "#ec4899", "#14b8a6", "#eab308", "#64748b"];

// --- Custom Tooltip ---

function KRWTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border border-gray-200 bg-white px-3 py-2 text-xs shadow-md">
      <p className="font-medium text-gray-700">{label}</p>
      {payload.map((entry: any, i: number) => (
        <p key={i} style={{ color: entry.color }}>
          {entry.name}: {typeof entry.value === "number" && Math.abs(entry.value) > 1000
            ? formatKRW(entry.value) : entry.value}
        </p>
      ))}
    </div>
  );
}

// --- Main Dashboard ---

export default function Dashboard() {
  const { data: analysis, isLoading } = useQuery({
    queryKey: ["full-analysis"],
    queryFn: () => api.getFullAnalysis() as Promise<any>,
  });

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-brand-600 border-t-transparent" />
      </div>
    );
  }

  const stats = analysis?.overall;

  if (!stats || stats.total_trades === 0) {
    return (
      <div className="flex h-64 flex-col items-center justify-center text-center">
        <BarChart3 className="mb-4 h-12 w-12 text-gray-300" />
        <p className="mb-2 text-lg font-semibold text-gray-600">거래내역이 없습니다</p>
        <p className="text-sm text-gray-400">
          설정에서 API Key 또는 CSV로 거래내역을 가져와주세요
        </p>
      </div>
    );
  }

  // Prepare chart data
  const coinData = (analysis.by_coin || [])
    .filter((c: any) => c.trade_count >= 2)
    .slice(0, 10)
    .map((c: any) => ({
      name: c.market.replace("KRW-", ""),
      PnL: Math.round(c.realized_pnl),
      거래수: c.trade_count,
    }));

  const hourData = (analysis.by_hour || []).map((h: any) => ({
    시간: `${h.hour}시`,
    매수: h.buy_count,
    매도: h.sell_count,
  }));

  const weekdayData = (analysis.by_weekday || []).map((d: any) => ({
    요일: d.weekday_name,
    거래수: d.trade_count,
    매수: d.buy_count,
    매도: d.sell_count,
  }));

  const holdingData = (analysis.holding_periods || []).filter((h: any) => h.count > 0);

  const topWinners = analysis.top_winners || [];
  const topLosers = analysis.top_losers || [];

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">대시보드</h1>
        {stats.period_start && (
          <span className="text-xs text-gray-400">
            {new Date(stats.period_start).toLocaleDateString("ko-KR")} ~{" "}
            {new Date(stats.period_end).toLocaleDateString("ko-KR")}
          </span>
        )}
      </div>

      {/* Stats row */}
      <div className="mb-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard
          label="총 거래" value={stats.total_trades.toLocaleString()}
          sub={`${stats.active_days}일 / 일평균 ${stats.avg_trades_per_day}건`}
          icon={BarChart3} />
        <StatCard
          label="실현 손익" value={formatKRW(stats.realized_pnl)}
          sub={`수수료 ${formatKRW(stats.total_fees)}`}
          icon={stats.realized_pnl >= 0 ? TrendingUp : TrendingDown}
          color={stats.realized_pnl >= 0 ? "text-profit" : "text-loss"}
          bg={stats.realized_pnl >= 0 ? "bg-green-50" : "bg-red-50"} />
        <StatCard
          label="승률" value={`${stats.win_rate}%`}
          sub={`${stats.unique_markets}개 종목 거래`}
          icon={Trophy} color="text-amber-600" bg="bg-amber-50" />
        <StatCard
          label="매수 / 매도" value={`${stats.total_buy} / ${stats.total_sell}`}
          sub={`매수 ${formatKRW(stats.total_buy_funds)}`}
          icon={Coins} />
      </div>

      {/* Charts row 1 */}
      <div className="mb-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Coin PnL */}
        <ChartCard title="종목별 손익 (Top 10)">
          {coinData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={coinData} layout="vertical" margin={{ left: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis type="number" tickFormatter={(v) => `${(v / 10000).toFixed(0)}만`}
                  tick={{ fontSize: 11 }} />
                <YAxis type="category" dataKey="name" width={60}
                  tick={{ fontSize: 12, fontWeight: 500 }} />
                <Tooltip content={<KRWTooltip />} />
                <Bar dataKey="PnL" radius={[0, 4, 4, 0]}>
                  {coinData.map((entry: any, i: number) => (
                    <Cell key={i} fill={entry.PnL >= 0 ? COLORS.profit : COLORS.loss} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="py-12 text-center text-sm text-gray-400">데이터 부족</p>
          )}
        </ChartCard>

        {/* Hourly distribution */}
        <ChartCard title="시간대별 거래 분포">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={hourData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="시간" tick={{ fontSize: 10 }} interval={2} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Bar dataKey="매수" fill={COLORS.buy} radius={[2, 2, 0, 0]} stackId="a" />
              <Bar dataKey="매도" fill={COLORS.sell} radius={[2, 2, 0, 0]} stackId="a" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {/* Charts row 2 */}
      <div className="mb-6 grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Weekday */}
        <ChartCard title="요일별 거래">
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={weekdayData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="요일" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="매수" fill={COLORS.buy} radius={[2, 2, 0, 0]} stackId="a" />
              <Bar dataKey="매도" fill={COLORS.sell} radius={[2, 2, 0, 0]} stackId="a" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Holding period pie */}
        <ChartCard title="보유기간 분포">
          {holdingData.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={holdingData} dataKey="count" nameKey="bucket"
                  cx="50%" cy="50%" innerRadius={50} outerRadius={85}
                  paddingAngle={2} label={({ bucket, pct }) => `${bucket} ${pct}%`}
                  labelLine={false}
                  style={{ fontSize: 10 }}>
                  {holdingData.map((_: any, i: number) => (
                    <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="py-12 text-center text-sm text-gray-400">매매 페어 부족</p>
          )}
        </ChartCard>

        {/* Top winners & losers */}
        <ChartCard title="Best / Worst 종목">
          <div className="space-y-3">
            {topWinners.slice(0, 3).map((c: any, i: number) => (
              <div key={`w-${i}`} className="flex items-center justify-between rounded-lg bg-green-50 px-3 py-2">
                <span className="text-sm font-medium text-gray-700">
                  {c.market.replace("KRW-", "")}
                </span>
                <span className="text-sm font-bold text-profit">
                  +{formatKRW(c.realized_pnl)}
                </span>
              </div>
            ))}
            {topLosers.slice(0, 3).map((c: any, i: number) => (
              <div key={`l-${i}`} className="flex items-center justify-between rounded-lg bg-red-50 px-3 py-2">
                <span className="text-sm font-medium text-gray-700">
                  {c.market.replace("KRW-", "")}
                </span>
                <span className="text-sm font-bold text-loss">
                  {formatKRW(c.realized_pnl)}
                </span>
              </div>
            ))}
            {topWinners.length === 0 && topLosers.length === 0 && (
              <p className="py-8 text-center text-sm text-gray-400">매도 완료 종목 없음</p>
            )}
          </div>
        </ChartCard>
      </div>
    </div>
  );
}
