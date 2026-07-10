import { Card, CardContent, CardHeader, CardTitle } from '../components/common/Card';
import { StatusBadge } from '../components/widgets/StatusBadge';
import { Button } from '../components/common/Button';
import { Box, RotateCcw } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { useModels, useRollbackModel } from '../hooks/useApi';

export default function ModelRegistry() {
  const { data: models = [], isLoading, refetch } = useModels();
  const { mutate: rollbackModel, isPending: isRollingBack } = useRollbackModel();

  if (isLoading) {
    return <div className="p-8 animate-pulse text-muted-foreground">Loading models...</div>;
  }

  // Parse metrics JSON from models
  const comparisonData = models.map((m: any) => {
    let accuracy = 0, f1 = 0, auc = 0;
    try {
      const metrics = JSON.parse(m.metrics || '{}');
      accuracy = (metrics.accuracy || 0) * 100;
      f1 = (metrics.f1_score || 0) * 100;
      auc = (metrics.roc_auc || 0) * 100;
    } catch (e) {
      console.error("Failed to parse metrics", e);
    }
    return {
      version: `v${m.version}`,
      accuracy,
      f1,
      auc,
      algorithm: 'AutoML', // Backend doesn't expose algorithm directly yet
      features: 10,
    };
  });

  const handleRollback = (version: number) => {
    rollbackModel(version, {
      onSuccess: () => refetch(),
    });
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div><h1 className="text-2xl font-bold">Model Registry</h1><p className="text-sm text-muted-foreground mt-1">Version control for ML models</p></div>

      <Card>
        <CardHeader><CardTitle>Model Comparison</CardTitle></CardHeader>
        <CardContent>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={comparisonData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="version" tick={{ fontSize: 12, fill: 'hsl(var(--muted-foreground))' }} />
                <YAxis tick={{ fontSize: 12, fill: 'hsl(var(--muted-foreground))' }} domain={[70, 100]} />
                <Tooltip contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: '8px', fontSize: '12px' }} />
                <Bar dataKey="accuracy" name="Accuracy" fill="hsl(var(--chart-1))" radius={[4, 4, 0, 0]} />
                <Bar dataKey="f1" name="F1" fill="hsl(var(--chart-2))" radius={[4, 4, 0, 0]} />
                <Bar dataKey="auc" name="AUC" fill="hsl(var(--chart-4))" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <div className="space-y-3">
        {models.map((m: any, idx: number) => {
          const comp = comparisonData[idx];
          return (
            <Card key={m.version} className={m.deployment_status === 'production' ? 'border-primary/30' : ''}>
              <CardContent className="p-5 flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="p-2 rounded-md bg-primary/10"><Box className="w-4 h-4 text-primary" /></div>
                  <div>
                    <p className="text-sm font-semibold">Model v{m.version} <span className="text-xs font-normal text-muted-foreground">({comp.algorithm})</span></p>
                    <p className="text-xs text-muted-foreground">{new Date(m.training_timestamp).toLocaleDateString()} · {comp.features} features · Acc: {comp.accuracy.toFixed(1)}%</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <StatusBadge status={m.deployment_status} />
                  {m.deployment_status !== 'production' && (
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={() => handleRollback(m.version)}
                      disabled={isRollingBack}
                    >
                      <RotateCcw className="w-3.5 h-3.5 mr-1" />
                      Rollback
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
