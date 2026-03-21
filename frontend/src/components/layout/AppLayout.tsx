import { Outlet, NavLink } from "react-router-dom";
import { cn } from "@/lib/utils";
import { BarChart3, BotMessageSquare, LayoutDashboard, Settings } from "lucide-react";

const navItems = [
  { to: "/dashboard", label: "대시보드", icon: LayoutDashboard },
  { to: "/coaching", label: "AI 코칭", icon: BotMessageSquare },
  { to: "/setup", label: "설정", icon: Settings },
];

export function AppLayout() {
  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      <aside className="w-60 border-r border-gray-200 bg-white px-3 py-6">
        <NavLink to="/" className="mb-8 flex items-center gap-2 px-3">
          <BarChart3 className="h-7 w-7 text-brand-600" />
          <span className="text-lg font-bold text-gray-900">bitcoach</span>
        </NavLink>

        <nav className="flex flex-col gap-1">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-brand-50 text-brand-700"
                    : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
                )
              }
            >
              <Icon className="h-5 w-5" />
              {label}
            </NavLink>
          ))}
        </nav>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        <div className="mx-auto max-w-6xl px-6 py-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
