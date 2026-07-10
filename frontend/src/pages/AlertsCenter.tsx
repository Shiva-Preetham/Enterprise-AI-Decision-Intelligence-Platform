import { Card, CardContent } from '../components/common/Card';
import { StatusBadge } from '../components/widgets/StatusBadge';
import { Badge } from '../components/common/Badge';
import { Bell, AlertTriangle, Server, Zap, Activity } from 'lucide-react';
import { useAlerts } from '../hooks/useApi';

const ICON_MAP: Record<string, typeof Bell> = { drift: Activity, error_rate: AlertTriangle, cache: Zap, latency: Server };

export default function AlertsCenter() {
  const { data: alerts = [], isLoading } = useAlerts();

  if (isLoading) {
    return <div className="p-8 animate-pulse text-muted-foreground">Loading alerts...</div>;
  }

  const activeCount = alerts.filter((a: any) => a.status === 'new').length;

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold">Alerts Center</h1><p className="text-sm text-muted-foreground mt-1">{activeCount} active alerts</p></div>
        <Bell className="w-5 h-5 text-primary" />
      </div>
      <div className="space-y-3">
        {alerts.map((alert: any) => {
          const Icon = ICON_MAP[alert.alert_type] || Bell;
          return (
            <Card key={alert.alert_id} className={alert.status === 'new' ? 'border-amber-500/30' : ''}>
              <CardContent className="p-4 flex items-center gap-4">
                <div className={`p-2 rounded-md ${alert.severity === 'critical' ? 'bg-red-500/10' : 'bg-amber-500/10'}`}>
                  <Icon className={`w-4 h-4 ${alert.severity === 'critical' ? 'text-red-500' : 'text-amber-500'}`} />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium">{alert.details}</p>
                  <p className="text-xs text-muted-foreground mt-0.5">{new Date(alert.timestamp).toLocaleString()}</p>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={alert.severity === 'critical' ? 'destructive' : 'warning'}>{alert.severity}</Badge>
                  <StatusBadge status={alert.status} />
                </div>
              </CardContent>
            </Card>
          );
        })}
        {alerts.length === 0 && (
          <div className="p-8 text-center text-muted-foreground">
            No alerts found.
          </div>
        )}
      </div>
    </div>
  );
}
