// --- Trade Types ---

export interface Trade {
  id: number;
  uuid: string;
  market: string;
  side: "buy" | "sell";
  price: number;
  volume: number;
  funds: number;
  fee: number;
  traded_at: string;
  trade_type: string | null;
}

export interface TradeStats {
  total_trades: number;
  total_buy: number;
  total_sell: number;
  unique_markets: number;
  total_volume_krw: number;
  period_start: string | null;
  period_end: string | null;
}

// --- Coaching Types ---

export interface ActionItem {
  action: string;
  priority: "high" | "medium" | "low";
  metric: string;
  timeframe: string;
}

export interface CoachingReport {
  id: number;
  summary: string;
  strengths: string;
  weaknesses: string;
  suggestions: string;
  action_items: ActionItem[];
  trade_count: number;
  period_start: string | null;
  period_end: string | null;
  created_at: string;
}

// --- Auth Types ---

export type AuthMethod = "api_key" | "csv";

export interface UpbitCredentials {
  access_key: string;
  secret_key: string;
}

// --- Analysis Types ---

export interface CoinPerformance {
  market: string;
  trade_count: number;
  buy_count: number;
  sell_count: number;
  total_buy_funds: number;
  total_sell_funds: number;
  total_fees: number;
  realized_pnl: number;
  pnl_pct: number;
  avg_hold_period_hours: number | null;
}

export interface FullAnalysis {
  overall: {
    total_trades: number;
    total_buy: number;
    total_sell: number;
    unique_markets: number;
    total_buy_funds: number;
    total_sell_funds: number;
    total_fees: number;
    realized_pnl: number;
    win_rate: number;
    period_start: string | null;
    period_end: string | null;
    active_days: number;
    avg_trades_per_day: number;
  };
  by_coin: CoinPerformance[];
  by_hour: { hour: number; trade_count: number; buy_count: number; sell_count: number; avg_funds: number }[];
  by_weekday: { weekday: number; weekday_name: string; trade_count: number; buy_count: number; sell_count: number }[];
  holding_periods: { bucket: string; count: number; pct: number }[];
  top_winners: CoinPerformance[];
  top_losers: CoinPerformance[];
}
