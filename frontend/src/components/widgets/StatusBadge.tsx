import { cn } from '../../lib/utils';

interface StatusBadgeProps {
  status: string;
  className?: string;
}

const STATUS_MAP: Record<string, { color: string; label: string }> = {
  Created: { color: 'bg-blue-500/10 text-blue-500', label: 'Created' },
  PendingApproval: { color: 'bg-amber-500/10 text-amber-500', label: 'Pending' },
  Approved: { color: 'bg-emerald-500/10 text-emerald-500', label: 'Approved' },
  Executing: { color: 'bg-purple-500/10 text-purple-500', label: 'Executing' },
  Completed: { color: 'bg-emerald-500/10 text-emerald-500', label: 'Completed' },
  Failed: { color: 'bg-red-500/10 text-red-500', label: 'Failed' },
  Cancelled: { color: 'bg-zinc-500/10 text-zinc-500', label: 'Cancelled' },
  production: { color: 'bg-emerald-500/10 text-emerald-500', label: 'Production' },
  staging: { color: 'bg-amber-500/10 text-amber-500', label: 'Staging' },
  archived: { color: 'bg-zinc-500/10 text-zinc-500', label: 'Archived' },
  new: { color: 'bg-red-500/10 text-red-500', label: 'New' },
  resolved: { color: 'bg-emerald-500/10 text-emerald-500', label: 'Resolved' },
  warning: { color: 'bg-amber-500/10 text-amber-500', label: 'Warning' },
  critical: { color: 'bg-red-500/10 text-red-500', label: 'Critical' },
  healthy: { color: 'bg-emerald-500/10 text-emerald-500', label: 'Healthy' },
  degraded: { color: 'bg-amber-500/10 text-amber-500', label: 'Degraded' },
  ok: { color: 'bg-emerald-500/10 text-emerald-500', label: 'OK' },
  error: { color: 'bg-red-500/10 text-red-500', label: 'Error' },
};

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const mapped = STATUS_MAP[status] || { color: 'bg-zinc-500/10 text-zinc-500', label: status };
  return (
    <span className={cn('inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium', mapped.color, className)}>
      <span className={cn('w-1.5 h-1.5 rounded-full', mapped.color.replace('/10', ''))} />
      {mapped.label}
    </span>
  );
}
