import { Card, CardContent } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Database } from 'lucide-react';

const FEATURES = [
  { name: 'total_lifetime_value', type: 'float', nullRate: 0.0, mean: 287.5, std: 412.3, min: 0, max: 13664 },
  { name: 'average_order_value', type: 'float', nullRate: 0.0, mean: 154.2, std: 189.7, min: 0, max: 6735 },
  { name: 'purchase_count', type: 'int', nullRate: 0.0, mean: 1.3, std: 0.7, min: 1, max: 17 },
  { name: 'days_since_last_purchase', type: 'int', nullRate: 0.0, mean: 178.4, std: 115.2, min: 0, max: 730 },
  { name: 'review_score_mean', type: 'float', nullRate: 0.32, mean: 4.09, std: 0.98, min: 1, max: 5 },
  { name: 'freight_value_sum', type: 'float', nullRate: 0.0, mean: 19.8, std: 22.1, min: 0, max: 409 },
];

export default function FeatureStoreExplorer() {
  return (
    <div className="space-y-6 animate-fade-in">
      <div><h1 className="text-2xl font-bold">Feature Store Explorer</h1><p className="text-sm text-muted-foreground mt-1">Inspect engineered customer features</p></div>
      <Card>
        <CardContent className="p-0">
          <table className="w-full text-sm">
            <thead><tr className="border-b border-border">
              <th className="text-left p-4 font-medium text-muted-foreground">Feature</th>
              <th className="text-left p-4 font-medium text-muted-foreground">Type</th>
              <th className="text-left p-4 font-medium text-muted-foreground">Null %</th>
              <th className="text-left p-4 font-medium text-muted-foreground">Mean</th>
              <th className="text-left p-4 font-medium text-muted-foreground">Std</th>
              <th className="text-left p-4 font-medium text-muted-foreground">Min</th>
              <th className="text-left p-4 font-medium text-muted-foreground">Max</th>
            </tr></thead>
            <tbody>
              {FEATURES.map((f) => (
                <tr key={f.name} className="border-b border-border/50 hover:bg-muted/30 transition-colors">
                  <td className="p-4 font-mono text-xs flex items-center gap-2"><Database className="w-3.5 h-3.5 text-muted-foreground" />{f.name}</td>
                  <td className="p-4"><Badge variant="outline">{f.type}</Badge></td>
                  <td className="p-4"><Badge variant={f.nullRate > 0.1 ? 'warning' : 'success'}>{(f.nullRate * 100).toFixed(1)}%</Badge></td>
                  <td className="p-4">{f.mean.toFixed(2)}</td>
                  <td className="p-4">{f.std.toFixed(2)}</td>
                  <td className="p-4">{f.min}</td>
                  <td className="p-4">{f.max.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}
