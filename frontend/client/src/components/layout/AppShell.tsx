import {
  Activity,
  BookOpen,
  Building2,
  ClipboardCheck,
  FileText,
  GitCompareArrows,
  LayoutDashboard,
  Settings,
  ShieldCheck,
} from "lucide-react";
import { Link, useLocation } from "wouter";
import type { ReactNode } from "react";

const navigation = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/changes", label: "Changes", icon: GitCompareArrows },
  { href: "/documents", label: "Documents", icon: FileText },
  { href: "/business-profile", label: "Business", icon: Building2 },
];

const secondaryNavigation = [
  { href: "/sources", label: "Sources", icon: BookOpen },
  { href: "/review", label: "Review", icon: ClipboardCheck },
];

export default function AppShell({ children }: { children: ReactNode }) {
  const [location] = useLocation();

  const isActive = (href: string) =>
    href === "/" ? location === "/" : location.startsWith(href);

  return (
    <div className="min-h-screen bg-[#f4f7f7] text-[#183346]">
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-[238px] border-r border-[#294d5d] bg-[#173a50] lg:block">
        <div className="flex h-full flex-col px-5 py-7">
          <Link href="/" className="block px-2">
            <div className="font-display text-[15px] font-bold tracking-[0.08em] text-white">
              TRUSTED INFORMATION
            </div>
            <div className="mt-1 text-[9px] uppercase tracking-[0.2em] text-[#91b2bc]">
              Regulatory intelligence
            </div>
          </Link>

          <div className="mt-10">
            <div className="px-2 pb-2 text-[9px] font-semibold uppercase tracking-[0.18em] text-[#7095a2]">
              Workspace
            </div>

            <nav className="space-y-0.5">
              {navigation.map(({ href, label, icon: Icon }) => {
                const active = isActive(href);

                return (
                  <Link
                    key={href}
                    href={href}
                    className={`flex items-center gap-3 border-l-2 px-2.5 py-2.5 text-[12px] font-medium transition ${
                      active
                        ? "border-[#a5cbc8] bg-[#214b5d] text-white"
                        : "border-transparent text-[#abc0c7] hover:bg-[#1d4557] hover:text-white"
                    }`}
                  >
                    <Icon
                      size={15}
                      strokeWidth={active ? 2 : 1.7}
                      className={active ? "text-[#b9d6d2]" : "text-[#7fa2ad]"}
                    />
                    {label}
                  </Link>
                );
              })}
            </nav>
          </div>

          <div className="mt-8">
            <div className="px-2 pb-2 text-[9px] font-semibold uppercase tracking-[0.18em] text-[#7095a2]">
              Evidence
            </div>

            <nav className="space-y-0.5">
              {secondaryNavigation.map(({ href, label, icon: Icon }) => {
                const active = isActive(href);

                return (
                  <Link
                    key={href}
                    href={href}
                    className={`flex items-center gap-3 border-l-2 px-2.5 py-2.5 text-[12px] font-medium transition ${
                      active
                        ? "border-[#a5cbc8] bg-[#214b5d] text-white"
                        : "border-transparent text-[#abc0c7] hover:bg-[#1d4557] hover:text-white"
                    }`}
                  >
                    <Icon
                      size={15}
                      strokeWidth={active ? 2 : 1.7}
                      className={active ? "text-[#b9d6d2]" : "text-[#7fa2ad]"}
                    />
                    {label}
                  </Link>
                );
              })}
            </nav>
          </div>

          <div className="mt-auto">
            <div className="border-t border-[#31586a] pt-5">
              <div className="space-y-0.5">
                <Link
                  href="/system-status"
                  className={`flex items-center gap-3 border-l-2 px-2.5 py-2.5 text-[11px] font-medium transition ${
                    isActive("/system-status")
                      ? "border-[#a5cbc8] bg-[#214b5d] text-white"
                      : "border-transparent text-[#9eb8c0] hover:bg-[#1d4557] hover:text-white"
                  }`}
                >
                  <Activity size={15} strokeWidth={1.7} />
                  System status
                </Link>

                <Link
                  href="/settings"
                  className={`flex items-center gap-3 border-l-2 px-2.5 py-2.5 text-[11px] font-medium transition ${
                    isActive("/settings")
                      ? "border-[#a5cbc8] bg-[#214b5d] text-white"
                      : "border-transparent text-[#9eb8c0] hover:bg-[#1d4557] hover:text-white"
                  }`}
                >
                  <Settings size={15} strokeWidth={1.7} />
                  Settings
                </Link>
              </div>

              <div className="mt-5 flex items-center gap-2 px-2">
                <ShieldCheck size={14} className="text-[#8fbab7]" />
                <span className="text-[9px] uppercase tracking-[0.16em] text-[#8fb0b8]">
                  Evidence first
                </span>
              </div>
            </div>
          </div>
        </div>
      </aside>

      <div className="lg:pl-[238px]">
        <main className="mx-auto min-h-screen max-w-[1500px] px-5 py-7 md:px-8 lg:px-10 lg:py-9">
          <div className="page-enter">{children}</div>
        </main>
      </div>
    </div>
  );
}
