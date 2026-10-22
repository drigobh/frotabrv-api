import type { ReactNode } from "react";

interface Props {
  eyebrow?: string;
  title: string;
  description?: string;
  actions?: ReactNode;
}

export function PageHeader({ eyebrow, title, description, actions }: Props) {
  return (
    <header className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
      <div>
        {eyebrow && (
          <p className="mb-1 font-mono text-[11px] uppercase tracking-[0.18em] text-sky-400/80">{eyebrow}</p>
        )}
        <h1 className="text-3xl font-semibold text-slate-50 md:text-4xl" data-testid="page-title">
          {title}
        </h1>
        {description && <p className="mt-1.5 max-w-2xl text-sm text-slate-400">{description}</p>}
      </div>
      {actions && <div className="flex flex-wrap items-center gap-2">{actions}</div>}
    </header>
  );
}
