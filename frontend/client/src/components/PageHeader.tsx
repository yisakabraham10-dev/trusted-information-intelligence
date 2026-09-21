import { ArrowUpRight, ChevronLeft } from "lucide-react";
import { Link } from "wouter";
import type { ReactNode } from "react";

export function PageHeader({ eyebrow, title, description, actions, backHref, backLabel }: { eyebrow?: string; title: string; description?: string; actions?: ReactNode; backHref?: string; backLabel?: string }) {
  return (
    <div className="mb-8 flex flex-col gap-5 border-b border-[#dce6e8] pb-7 lg:flex-row lg:items-end lg:justify-between">
      <div>
        {backHref && <Link href={backHref} className="mb-4 inline-flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-[0.14em] text-[#78909a] transition hover:text-[#2b6871]"><ChevronLeft size={14} /> {backLabel ?? "Back"}</Link>}
        {eyebrow && <div className="mb-2 text-[10px] font-bold uppercase tracking-[0.24em] text-[#7c9a9e]">{eyebrow}</div>}
        <h1 className="font-display text-3xl font-semibold tracking-[-0.035em] text-[#173a50] md:text-[38px]">{title}</h1>
        {description && <p className="mt-2 max-w-2xl text-[13px] leading-6 text-[#71858d]">{description}</p>}
      </div>
      {actions && <div className="flex shrink-0 items-center gap-2">{actions}</div>}
    </div>
  );
}

export function TextButton({ children, onClick }: { children: ReactNode; onClick?: () => void }) {
  return <button onClick={onClick} className="inline-flex items-center gap-1.5 rounded-lg px-2.5 py-2 text-[11px] font-semibold text-[#3c7079] transition hover:bg-[#eaf2f2] hover:text-[#215864]">{children}<ArrowUpRight size={13} /></button>;
}

export function EmptyState({ title, description }: { title: string; description: string }) {
  return <div className="rounded-2xl border border-dashed border-[#d4e0e3] bg-white px-6 py-16 text-center"><div className="mx-auto max-w-sm"><h3 className="font-display text-xl font-semibold text-[#264b5b]">{title}</h3><p className="mt-2 text-sm leading-6 text-[#7b8f97]">{description}</p></div></div>;
}
