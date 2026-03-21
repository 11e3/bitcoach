import { Link } from "react-router-dom";
import {
  BarChart3, ArrowRight, Shield, Zap, Brain, GitBranch,
  TrendingUp, Github,
} from "lucide-react";
const features = [
  {
    icon: Zap,
    title: "거래내역 분석",
    desc: "승률, 수익률, 보유기간, 종목별·시간대별 패턴을 6종 차트로 한눈에",
    color: "from-blue-500 to-cyan-400",
  },
  {
    icon: Brain,
    title: "AI 코칭 리포트",
    desc: "LangGraph 5단계 파이프라인이 반복되는 실수를 찾아 구체적 액션 제안",
    color: "from-violet-500 to-purple-400",
  },
  {
    icon: Shield,
    title: "API Key 보안",
    desc: "서버 메모리 only. 디스크 미저장. 서버 재시작 시 자동 삭제. 오픈소스 투명성.",
    color: "from-emerald-500 to-green-400",
  },
  {
    icon: GitBranch,
    title: "오픈소스",
    desc: "MIT 라이선스. 코드 100% 공개. 직접 확인하고, 직접 돌리세요.",
    color: "from-orange-500 to-amber-400",
  },
];

const pipelineSteps = [
  { label: "분류", model: "Haiku", desc: "FOMO, 손절, 스윙 등 거래 유형 자동 태깅" },
  { label: "통계", model: "Python", desc: "FIFO 매칭, 승률, PnL, 보유기간 계산" },
  { label: "패턴", model: "Haiku", desc: "반복 행동 패턴 탐지 (시간대, 종목 편중 등)" },
  { label: "코칭", model: "Sonnet", desc: "강점/약점/개선안 종합 리포트" },
  { label: "액션", model: "Sonnet", desc: "측정 가능한 실행 액션 아이템 추출" },
];

export default function Landing() {
  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      {/* Nav */}
      <nav className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
        <div className="flex items-center gap-2.5">
          <BarChart3 className="h-7 w-7 text-cyan-400" />
          <span className="text-lg font-bold tracking-tight">bitcoach</span>
        </div>
        <div className="flex items-center gap-4">
          <a
            href="https://github.com/11e3/bitcoach"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 text-sm text-gray-400 transition-colors hover:text-white"
          >
            <Github className="h-4 w-4" />
            GitHub
          </a>
          <Link
            to="/setup"
            className="rounded-lg bg-cyan-500 px-4 py-2 text-sm font-semibold text-gray-950 transition-colors hover:bg-cyan-400"
          >
            시작하기
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative overflow-hidden px-6 pb-20 pt-16">
        {/* Grid background */}
        <div
          className="pointer-events-none absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage: `linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px),
                              linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)`,
            backgroundSize: "60px 60px",
          }}
        />
        {/* Glow */}
        <div className="pointer-events-none absolute left-1/2 top-0 h-[500px] w-[800px] -translate-x-1/2 rounded-full bg-cyan-500/10 blur-[120px]" />

        <div className="relative mx-auto max-w-3xl text-center">
          <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-gray-800 bg-gray-900 px-4 py-1.5 text-xs text-gray-400">
            <span className="h-1.5 w-1.5 rounded-full bg-cyan-400" />
            오픈소스 · MIT License · React + FastAPI + LangGraph
          </div>

          <h1 className="mb-5 text-4xl font-extrabold leading-tight tracking-tight sm:text-5xl md:text-6xl">
            업비트 거래,{" "}
            <span className="bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
              AI가 코칭
            </span>
            해드립니다
          </h1>

          <p className="mx-auto mb-8 max-w-xl text-lg leading-relaxed text-gray-400">
            거래내역을 분석하고 반복 패턴을 찾아
            실행 가능한 개선점을 제안하는 AI 트레이딩 코치
          </p>

          <div className="flex items-center justify-center gap-4">
            <Link
              to="/setup"
              className="group inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-500 px-7 py-3.5 text-sm font-bold text-white shadow-lg shadow-cyan-500/20 transition-all hover:shadow-cyan-500/30"
            >
              무료로 시작하기
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </Link>
            <a
              href="https://github.com/11e3/bitcoach"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 rounded-xl border border-gray-700 bg-gray-900 px-7 py-3.5 text-sm font-semibold text-gray-300 transition-colors hover:border-gray-600 hover:text-white"
            >
              <Github className="h-4 w-4" />
              소스코드
            </a>
          </div>

          {/* Quick start */}
          <div className="mx-auto mt-12 max-w-md overflow-hidden rounded-xl border border-gray-800 bg-gray-900/80 text-left">
            <div className="flex items-center gap-2 border-b border-gray-800 px-4 py-2.5">
              <div className="h-2.5 w-2.5 rounded-full bg-red-500/60" />
              <div className="h-2.5 w-2.5 rounded-full bg-yellow-500/60" />
              <div className="h-2.5 w-2.5 rounded-full bg-green-500/60" />
              <span className="ml-2 text-[11px] text-gray-500">terminal</span>
            </div>
            <div className="px-4 py-3 font-mono text-[13px] leading-relaxed">
              <p className="text-gray-500">$ git clone https://github.com/11e3/bitcoach</p>
              <p className="text-gray-500">$ cd bitcoach</p>
              <p className="text-gray-500">$ cp .env.example .env</p>
              <p className="text-cyan-400">$ docker compose up --build</p>
              <p className="mt-1 text-green-400">✓ Frontend: localhost:5173</p>
              <p className="text-green-400">✓ Backend:  localhost:8000/docs</p>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="border-t border-gray-800/50 px-6 py-20">
        <div className="mx-auto max-w-6xl">
          <h2 className="mb-12 text-center text-2xl font-bold">핵심 기능</h2>
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {features.map(({ icon: Icon, title, desc, color }) => (
              <div
                key={title}
                className="group relative overflow-hidden rounded-2xl border border-gray-800 bg-gray-900/50 p-6 transition-colors hover:border-gray-700"
              >
                <div
                  className={`mb-4 inline-flex rounded-xl bg-gradient-to-br ${color} p-2.5`}
                >
                  <Icon className="h-5 w-5 text-white" />
                </div>
                <h3 className="mb-2 font-bold text-gray-100">{title}</h3>
                <p className="text-sm leading-relaxed text-gray-400">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pipeline */}
      <section className="border-t border-gray-800/50 px-6 py-20">
        <div className="mx-auto max-w-4xl">
          <h2 className="mb-3 text-center text-2xl font-bold">LangGraph 코칭 파이프라인</h2>
          <p className="mb-12 text-center text-sm text-gray-500">
            5단계 agentic workflow가 거래내역을 체계적으로 분석합니다
          </p>

          <div className="space-y-4">
            {pipelineSteps.map((step, i) => (
              <div key={step.label} className="flex items-center gap-4">
                {/* Step number */}
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gray-800 text-sm font-bold text-cyan-400">
                  {i + 1}
                </div>

                {/* Content */}
                <div className="flex flex-1 items-center justify-between rounded-xl border border-gray-800 bg-gray-900/50 px-5 py-3.5">
                  <div>
                    <span className="font-semibold text-gray-100">{step.label}</span>
                    <span className="ml-2 text-xs text-gray-500">{step.desc}</span>
                  </div>
                  <span
                    className={`shrink-0 rounded-full px-3 py-1 text-xs font-bold ${
                      step.model === "Haiku"
                        ? "bg-blue-500/10 text-blue-400"
                        : step.model === "Python"
                          ? "bg-amber-500/10 text-amber-400"
                          : "bg-green-500/10 text-green-400"
                    }`}
                  >
                    {step.model}
                  </span>
                </div>

                {/* Connector line */}
                {i < pipelineSteps.length - 1 && (
                  <div className="absolute left-[26px] h-4 w-px bg-gray-800" style={{ display: "none" }} />
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Data input methods */}
      <section className="border-t border-gray-800/50 px-6 py-20">
        <div className="mx-auto max-w-4xl">
          <h2 className="mb-12 text-center text-2xl font-bold">두 가지 방법으로 시작</h2>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div className="rounded-2xl border border-gray-800 bg-gray-900/50 p-8">
              <div className="mb-4 inline-flex rounded-xl bg-cyan-500/10 p-3">
                <TrendingUp className="h-6 w-6 text-cyan-400" />
              </div>
              <h3 className="mb-2 text-lg font-bold">거래내역 자동 수집</h3>
              <p className="mb-4 text-sm leading-relaxed text-gray-400">
                업비트 웹에서 스크립트 한 줄 실행하면 전체 거래내역을 자동 수집합니다.
                API Key 불필요. 부분체결까지 정확하게.
              </p>
              <ul className="space-y-1.5 text-xs text-gray-500">
                <li className="flex items-center gap-2">
                  <span className="h-1 w-1 rounded-full bg-gray-600" />
                  API Key 불필요
                </li>
                <li className="flex items-center gap-2">
                  <span className="h-1 w-1 rounded-full bg-gray-600" />
                  전체 거래 내역 수집
                </li>
                <li className="flex items-center gap-2">
                  <span className="h-1 w-1 rounded-full bg-gray-600" />
                  부분체결 포함
                </li>
              </ul>
            </div>
            <div className="rounded-2xl border border-gray-800 bg-gray-900/50 p-8">
              <div className="mb-4 inline-flex rounded-xl bg-blue-500/10 p-3">
                <TrendingUp className="h-6 w-6 text-blue-400" />
              </div>
              <h3 className="mb-2 text-lg font-bold">API Key 연동</h3>
              <p className="mb-4 text-sm leading-relaxed text-gray-400">
                조회 전용 API Key로 거래내역을 자동 동기화합니다.
                고정 IP 등록이 필요하며 일부 데이터가 제한될 수 있습니다.
              </p>
              <ul className="space-y-1.5 text-xs text-gray-500">
                <li className="flex items-center gap-2">
                  <span className="h-1 w-1 rounded-full bg-gray-600" />
                  자동 동기화
                </li>
                <li className="flex items-center gap-2">
                  <span className="h-1 w-1 rounded-full bg-gray-600" />
                  고정 IP 등록 필요
                </li>
                <li className="flex items-center gap-2">
                  <span className="h-1 w-1 rounded-full bg-gray-600" />
                  서버 메모리 only
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="border-t border-gray-800/50 px-6 py-20">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="mb-4 text-3xl font-extrabold">
            거래 습관,{" "}
            <span className="bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
              바꿔보세요
            </span>
          </h2>
          <p className="mb-8 text-gray-400">
            Docker 한 줄이면 로컬에서 바로 돌아갑니다
          </p>
          <Link
            to="/setup"
            className="group inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-500 px-8 py-4 text-sm font-bold text-white shadow-lg shadow-cyan-500/20"
          >
            시작하기
            <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-800/50 px-6 py-8 text-center text-xs text-gray-600">
        MIT License ·{" "}
        <a
          href="https://github.com/11e3"
          className="text-gray-500 hover:text-gray-300"
          target="_blank"
          rel="noopener noreferrer"
        >
          11e3
        </a>{" "}
        · React + FastAPI + LangGraph + Claude API
      </footer>
    </div>
  );
}
