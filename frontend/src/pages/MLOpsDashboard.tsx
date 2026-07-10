import { KPICard } from '../components/charts/KPICard';
import { Card, CardContent, CardHeader, CardTitle } from '../components/common/Card';
import { StatusBadge } from '../components/widgets/StatusBadge';
import { Server, Cpu, Zap, HardDrive, Clock, Activity } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

import { useHealth, useModels } from '../hooks/useApi';

const LATENCY = [
  { time: '00:00', p50: 12, p99: 45 }, { time: '04:00', p50: 10, p99: 38 },
  { time: '08:00', p50: 18, p99: 72 }, { time: '12:00', p50: 22, p99: 95 },
  { time: '16:00', p50: 25, p99: 110 }, { time: '20:00', p50: 15, p99: 52 },
];

export default function MLOpsDashboard() {
  const { data: healthData, isLoading: isLoadingHealth } = useHealth();
  const { data: modelsData, isLoading: isLoadingModels } = useModels();

  if (isLoadingHealth || isLoadingModels) {
    return <div className="p-8 animate-pulse text-muted-foreground">Loading MLOps data...</div>;
  }

  const health: any = healthData || {};
  const models = modelsData || [];

  const subsystems = [
    { name: 'API Server', status: health.api_status || 'unknown', latency: '-' },
    { name: 'PostgreSQL', status: health.database_status || 'unknown', latency: '-' },
    { name: 'ML Pipeline', status: health.ml_model_loaded ? 'ok' : 'error', latency: '-' },
    { name: 'Cache', status: 'ok', latency: '-' }
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <div><h1 className="text-2xl font-bold">MLOps Dashboard</h1><p className="text-sm text-muted-foreground mt-1">System observability and metrics</p></div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard title="API Latency (p50)" value="18ms" icon={Clock} change={-3} trend="down" />
        <KPICard title="Inference Time" value="42ms" icon={Cpu} change={1.2} trend="up" />
        <KPICard title="Uptime (s)" value={health.uptime_seconds ? String(health.uptime_seconds) : '-'} icon={Zap} trend="neutral" />
        <KPICard title="Environment" value={health.environment || '-'} icon={Activity} trend="neutral" />
      </div>

      <Card>
        <CardHeader><CardTitle>API Latency (24h)</CardTitle></CardHeader>
        <CardContent>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={LATENCY}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="time" tick={{ fontSize: 12, fill: 'hsl(var(--muted-foreground))' }} />
                <YAxis tick={{ fontSize: 12, fill: 'hsl(var(--muted-foreground))' }} unit="ms" />
                <Tooltip contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: '8px', fontSize: '12px' }} />
                <Line type="monotone" dataKey="p50" stroke="hsl(var(--chart-1))" strokeWidth={2} name="P50" />
                <Line type="monotone" dataKey="p99" stroke="hsl(var(--chart-5))" strokeWidth={2} name="P99" strokeDasharray="5 5" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader><CardTitle>Subsystem Health</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {subsystems.map((s) => (
              <div key={s.name} className="flex items-center justify-between p-3 rounded-md bg-muted/30">
                <div className="flex items-center gap-2"><Server className="w-3.5 h-3.5 text-muted-foreground" /><span className="text-sm">{s.name}</span></div>
                <div className="flex items-center gap-3"><span className="text-xs text-muted-foreground">{s.latency}</span><StatusBadge status={s.status === 'ok' ? 'ok' : 'critical'} /></div>
              </div>
            ))}
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Active Models</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {models.map((m: any) => (
              <div key={m.version} className="flex items-center justify-between p-3 rounded-md bg-muted/30">
                <div className="flex items-center gap-2"><HardDrive className="w-3.5 h-3.5 text-muted-foreground" /><span className="text-sm">Model v{m.version}</span></div>
                <div className="flex items-center gap-3"><span className="text-xs text-muted-foreground">{new Date(m.training_timestamp).toLocaleDateString()}</span><StatusBadge status={m.deployment_status} /></div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
