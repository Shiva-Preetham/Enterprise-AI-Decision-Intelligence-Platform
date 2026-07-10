import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/common/Card';
import { StatusBadge } from '../components/widgets/StatusBadge';
import { AlertTriangle } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from 'recharts';

import { useDrift } from '../hooks/useApi';

const PSI_THRESHOLD = 0.2;

export default function DriftDashboard() {
  const { data: driftData, isLoading } = useDrift();

  if (isLoading) {
    return <div className="p-8 animate-pulse text-muted-foreground">Loading drift data...</div>;
  }

  // Use the most recent drift report
  const latestReport = driftData?.[0];
  const hasAlert = latestReport?.is_alert || false;
  
  let psiData: any[] = [];
  try {
    if (latestReport?.feature_stats) {
      const stats = JSON.parse(latestReport.feature_stats);
      psiData = Object.entries(stats).map(([feature, data]: [string, any]) => ({
        feature,
        psi: data.psi
      }));
    }
  } catch (e) {
    console.error("Failed to parse drift stats", e);
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Drift Monitor</h1>
          <p className="text-sm text-muted-foreground mt-1">Feature distribution stability</p>
          {latestReport && (
            <p className="text-xs text-muted-foreground mt-1">
              Last check: {new Date(latestReport.timestamp).toLocaleString()}
            </p>
          )}
        </div>
        <StatusBadge status={hasAlert ? 'warning' : 'ok'} />
      </div>

      {hasAlert && (
        <div className="flex items-center gap-3 bg-amber-500/10 border border-amber-500/20 rounded-lg p-4">
          <AlertTriangle className="w-5 h-5 text-amber-500 shrink-0" />
          <div><p className="text-sm font-medium text-amber-500">Drift Alert Active</p><p className="text-xs text-muted-foreground">One or more features exceed the PSI threshold of {PSI_THRESHOLD}</p></div>
        </div>
      )}

      <Card>
        <CardHeader><CardTitle>PSI by Feature</CardTitle><CardDescription>Population Stability Index — red bars exceed threshold ({PSI_THRESHOLD})</CardDescription></CardHeader>
        <CardContent>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={psiData} layout="vertical" margin={{ left: 120 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis type="number" tick={{ fontSize: 12, fill: 'hsl(var(--muted-foreground))' }} domain={[0, 0.3]} />
                <YAxis type="category" dataKey="feature" tick={{ fontSize: 12, fill: 'hsl(var(--muted-foreground))' }} width={120} />
                <Tooltip contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: '8px', fontSize: '12px' }} />
                <Bar dataKey="psi" radius={[0, 4, 4, 0]}>
                  {psiData.map((entry: any) => (<Cell key={entry.feature} fill={entry.psi > PSI_THRESHOLD ? '#ef4444' : 'hsl(var(--chart-1))'} />))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {psiData.map((f: any) => (
          <Card key={f.feature} className={f.psi > PSI_THRESHOLD ? 'border-red-500/30' : ''}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium">{f.feature.replace(/_/g, ' ')}</p>
                <StatusBadge status={f.psi > PSI_THRESHOLD ? 'critical' : 'ok'} />
              </div>
              <p className="text-2xl font-bold mt-2">{f.psi.toFixed(3)}</p>
              <div className="w-full bg-muted rounded-full h-1.5 mt-2">
                <div className={`h-1.5 rounded-full ${f.psi > PSI_THRESHOLD ? 'bg-red-500' : 'bg-primary'}`} style={{ width: `${Math.min(f.psi / 0.3 * 100, 100)}%` }} />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
