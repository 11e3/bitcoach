import { Link } from "react-router-dom";
import {
  BarChart3, ArrowRight, Shield, Zap, Brain, TrendingUp,
  Github, AlertTriangle, FileText,
} from "lucide-react";

const features = [
  {
    icon: Zap,
    title: "거래 분석 대시보드",
    desc: "승률, 수익률, 보유기간, 종목별·시간대별 패턴을 한눈에 파악",
    color: "text-blue-600 bg-blue-50",
  },
  {
    icon: Brain,
    title: "AI 코칭 리포트",
    desc: "반복되는 실수를 찾고 구체적인 개선 액션을 제안",
    color: "text-violet-600 bg-violet-50",
  },
  {
    icon: Shield,
    title: "개인정보 보호",
    desc: "거래내역은 분석에만 사용. API Key 불필요. 회원가입 불필요.",
    color: "text-emerald-600 bg-emerald-50",
  },
  {
    icon: TrendingUp,
    title: "완전 무료",
    desc: "오픈소스 프로젝트. 숨겨진 비용 없이 무제한 사용.",
    color: "text-orange-600 bg-orange-50",
  },
];

const sampleReport = {
  summary:
    "총 165건 거래에서 승률 52.3%, 실현 수익 +485만원. XRP 단타 중심으로 수익을 내고 있지만, 손실 거래의 평균 손실폭이 수익 거래의 2.1배로 리스크 관리가 필요합니다.",
  strengths: [
    "XRP 단타에서 일관된 수익 패턴 — 평균 보유 3.2시간, 승률 58%",
    "손절 타이밍이 빠름 — 평균 손절까지 47분",
  ],
  weaknesses: [
    "수익 거래를 너무 빨리 청산 — 평균 +1.2%에서 익절, 추가 상승 여지 놓침",
    "9시~10시 집중 거래 — 이 시간대 승률 41%로 전체 평균보다 낮음",
  ],
  actions: [
    "익절 기준을 +1.2% → +2.0%로 상향 (다음 20건 거래에서 테스트)",
    "9시~10시 거래 자제 또는 포지션 사이즈 50% 축소",
  ],
};

export default function Landing() {
  return (
    <div className="min-h-screen bg-white text-gray-900">
      {/* Nav */}
      <nav className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
        <div className="flex items-center gap-2.5">
          <BarChart3 className="h-7 w-7 text-brand-600" />
          <span className="text-lg font-bold tracking-tight">bitcoach</span>
        </div>
        <div className="flex items-center gap-4">
          <a
            href="https://github.com/11e3/bitcoach"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 text-sm text-gray-400 transition-colors hover:text-gray-700"
          >
            <Github className="h-4 w-4" />
            GitHub
          </a>
          <Link
            to="/setup"
            className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-brand-700"
          >
            시작하기
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative overflow-hidden px-6 pb-20 pt-16">
        <div className="pointer-events-none absolute left-1/2 top-0 h-[500px] w-[800px] -translate-x-1/2 rounded-full bg-brand-100/50 blur-[120px]" />

        <div className="relative mx-auto max-w-3xl text-center">
          <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-gray-200 bg-gray-50 px-4 py-1.5 text-xs text-gray-500">
            <span className="h-1.5 w-1.5 rounded-full bg-brand-500" />
            무료 · 회원가입 불필요 · API Key 불필요
          </div>

          <h1 className="mb-5 text-4xl font-extrabold leading-tight tracking-tight sm:text-5xl md:text-6xl">
            업비트 거래,{" "}
            <span className="bg-gradient-to-r from-brand-600 to-blue-600 bg-clip-text text-transparent">
              AI가 코칭
            </span>
            해드립니다
          </h1>

          <p className="mx-auto mb-8 max-w-xl text-lg leading-relaxed text-gray-500">
            거래내역 붙여넣기만 하면 끝.<br />
            승률, 패턴, 반복 실수를 분석하고 실행 가능한 개선점을 제안합니다.
          </p>

          <Link
            to="/setup"
            className="group inline-flex items-center gap-2 rounded-xl bg-brand-600 px-8 py-4 text-sm font-bold text-white shadow-lg shadow-brand-500/20 transition-all hover:bg-brand-700 hover:shadow-brand-500/30"
          >
            무료로 시작하기
            <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
          </Link>
        </div>
      </section>

      {/* 3 Steps */}
      <section className="border-t border-gray-100 px-6 py-20">
        <div className="mx-auto max-w-4xl">
          <h2 className="mb-12 text-center text-2xl font-bold">30초면 끝</h2>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
            <div className="rounded-2xl border border-gray-200 bg-white p-8 text-center shadow-sm">
              <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-full bg-brand-50 text-xl font-bold text-brand-600">
                1
              </div>
              <h3 className="mb-2 font-bold">거래내역 복사</h3>
              <p className="text-sm text-gray-500">
                업비트 웹에서 거래내역을 드래그 → Ctrl+C
              </p>
            </div>
            <div className="rounded-2xl border border-gray-200 bg-white p-8 text-center shadow-sm">
              <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-full bg-blue-50 text-xl font-bold text-blue-600">
                2
              </div>
              <h3 className="mb-2 font-bold">여기에 붙여넣기</h3>
              <p className="text-sm text-gray-500">
                Ctrl+V 한 번이면 자동 파싱. 입출금 자동 제외.
              </p>
            </div>
            <div className="rounded-2xl border border-gray-200 bg-white p-8 text-center shadow-sm">
              <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-full bg-violet-50 text-xl font-bold text-violet-600">
                3
              </div>
              <h3 className="mb-2 font-bold">AI 코칭 받기</h3>
              <p className="text-sm text-gray-500">
                대시보드 + AI 리포트로 내 거래 습관 파악
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="border-t border-gray-100 bg-gray-50 px-6 py-20">
        <div className="mx-auto max-w-6xl">
          <h2 className="mb-12 text-center text-2xl font-bold">핵심 기능</h2>
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {features.map(({ icon: Icon, title, desc, color }) => (
              <div
                key={title}
                className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm transition-shadow hover:shadow-md"
              >
                <div className={`mb-4 inline-flex rounded-xl p-2.5 ${color}`}>
                  <Icon className="h-5 w-5" />
                </div>
                <h3 className="mb-2 font-bold text-gray-900">{title}</h3>
                <p className="text-sm leading-relaxed text-gray-500">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Sample Coaching Report */}
      <section className="border-t border-gray-100 px-6 py-20">
        <div className="mx-auto max-w-3xl">
          <h2 className="mb-3 text-center text-2xl font-bold">
            이런 코칭을 받을 수 있어요
          </h2>
          <p className="mb-10 text-center text-sm text-gray-400">
            실제 거래 패턴을 기반으로 AI가 분석한 리포트 예시
          </p>

          <div className="space-y-4">
            <div className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">
              <div className="flex items-center gap-2 bg-brand-50 px-5 py-3">
                <FileText className="h-4 w-4 text-brand-600" />
                <span className="text-sm font-semibold text-brand-600">요약</span>
              </div>
              <p className="px-5 py-4 text-sm leading-relaxed text-gray-600">
                {sampleReport.summary}
              </p>
            </div>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">
                <div className="flex items-center gap-2 bg-green-50 px-5 py-3">
                  <TrendingUp className="h-4 w-4 text-green-600" />
                  <span className="text-sm font-semibold text-green-600">강점</span>
                </div>
                <ul className="space-y-2 px-5 py-4">
                  {sampleReport.strengths.map((s, i) => (
                    <li key={i} className="text-sm leading-relaxed text-gray-600">
                      <span className="mr-1 text-green-500">+</span> {s}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">
                <div className="flex items-center gap-2 bg-red-50 px-5 py-3">
                  <AlertTriangle className="h-4 w-4 text-red-600" />
                  <span className="text-sm font-semibold text-red-600">약점</span>
                </div>
                <ul className="space-y-2 px-5 py-4">
                  {sampleReport.weaknesses.map((w, i) => (
                    <li key={i} className="text-sm leading-relaxed text-gray-600">
                      <span className="mr-1 text-red-500">!</span> {w}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">
              <div className="flex items-center gap-2 bg-amber-50 px-5 py-3">
                <BarChart3 className="h-4 w-4 text-amber-600" />
                <span className="text-sm font-semibold text-amber-600">액션 아이템</span>
              </div>
              <ul className="space-y-2 px-5 py-4">
                {sampleReport.actions.map((a, i) => (
                  <li key={i} className="text-sm leading-relaxed text-gray-700">
                    <span className="mr-1 font-bold text-amber-500">{i + 1}.</span> {a}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="border-t border-gray-100 bg-gray-50 px-6 py-20">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="mb-4 text-3xl font-extrabold">
            거래 습관,{" "}
            <span className="bg-gradient-to-r from-brand-600 to-blue-600 bg-clip-text text-transparent">
              바꿔보세요
            </span>
          </h2>
          <p className="mb-8 text-gray-500">
            회원가입도 API Key도 필요 없습니다. 거래내역 붙여넣기만 하세요.
          </p>
          <Link
            to="/setup"
            className="group inline-flex items-center gap-2 rounded-xl bg-brand-600 px-8 py-4 text-sm font-bold text-white shadow-lg shadow-brand-500/20 hover:bg-brand-700"
          >
            무료로 시작하기
            <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
          </Link>
        </div>
      </section>

      {/* Footer + Disclaimer */}
      <footer className="border-t border-gray-100 px-6 py-8">
        <p className="mx-auto max-w-2xl text-center text-[11px] leading-relaxed text-gray-400">
          본 서비스는 투자 자문이 아닙니다. AI가 제공하는 분석과 코칭은 참고 자료일 뿐이며,
          투자 결정에 대한 책임은 전적으로 이용자에게 있습니다.
          과거 거래 분석 결과가 미래 수익을 보장하지 않습니다.
        </p>
        <p className="mt-4 text-center text-xs text-gray-300">
          MIT License ·{" "}
          <a
            href="https://github.com/11e3/bitcoach"
            className="text-gray-400 hover:text-gray-600"
            target="_blank"
            rel="noopener noreferrer"
          >
            GitHub
          </a>{" "}
          · 오픈소스 프로젝트
        </p>
      </footer>
    </div>
  );
}
