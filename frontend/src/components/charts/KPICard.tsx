import { cn } from '../../lib/utils';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

interface KPICardProps {
  title: string;
  value: string | number;
  change?: number;
  icon: LucideIcon;
  trend?: 'up' | 'down' | 'neutral';
  className?: string;
}

export function KPICard({ title, value, change, icon: Icon, trend = 'neutral', className }: KPICardProps) {
  return (
    <div className={cn('rounded-lg border border-border bg-card p-6 animate-fade-in', className)}>
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-muted-foreground">{title}</p>
        <div className="p-2 rounded-md bg-primary/10">
          <Icon className="w-4 h-4 text-primary" />
        </div>
      </div>
      <div className="mt-3">
        <p className="text-2xl font-bold text-foreground">{value}</p>
        {change !== undefined && (
          <div className="flex items-center gap-1 mt-1">
            {trend === 'up' && <TrendingUp className="w-3 h-3 text-emerald-500" />}
            {trend === 'down' && <TrendingDown className="w-3 h-3 text-red-500" />}
            {trend === 'neutral' && <Minus className="w-3 h-3 text-muted-foreground" />}
            <span
              className={cn(
                'text-xs font-medium',
                trend === 'up' && 'text-emerald-500',
                trend === 'down' && 'text-red-500',
                trend === 'neutral' && 'text-muted-foreground'
              )}
            >
              {change > 0 ? '+' : ''}{change}%
            </span>
            <span className="text-xs text-muted-foreground">vs last period</span>
          </div>
        )}
      </div>
    </div>
  );
}
