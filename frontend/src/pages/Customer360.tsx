import { useParams } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { StatusBadge } from '../components/widgets/StatusBadge';
import { formatCurrency, formatPercent } from '../lib/utils';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { User, ShoppingCart, Star, MapPin, Clock, Brain, TrendingUp } from 'lucide-react';

const MOCK_PROFILE = {
  customer: { customer_unique_id: '', customer_city: 'São Paulo', customer_state: 'SP' },
  features: { total_lifetime_value: 542.30, average_order_value: 135.58, purchase_count: 4, days_since_last_purchase: 87, review_score_mean: 3.8, freight_value_sum: 62.10 },
  prediction: { probability: 0.72, label: 'Churn', risk_level: 'high' },
};
const SHAP_DATA = [
  { feature: 'days_since_last', value: 0.18 }, { feature: 'purchase_count', value: -0.12 },
  { feature: 'avg_order_value', value: 0.08 }, { feature: 'review_score', value: -0.15 },
  { feature: 'freight_sum', value: 0.05 }, { feature: 'lifetime_value', value: -0.04 },
];
const TIMELINE = [
  { date: '2024-01-15', type: 'Order', details: 'Order #1234 — $135.00' },
  { date: '2024-02-20', type: 'Review', details: 'Review — 4 stars' },
  { date: '2024-04-10', type: 'Order', details: 'Order #1567 — $189.00' },
  { date: '2024-06-05', type: 'Prediction', details: 'Churn risk flagged at 72%' },
  { date: '2024-06-06', type: 'Recommendation', details: 'Retention offer generated' },
];

export default function Customer360() {
  const { id } = useParams();
  const profile = { ...MOCK_PROFILE, customer: { ...MOCK_PROFILE.customer, customer_unique_id: id || 'unknown' } };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Customer 360</h1>
          <p className="text-sm text-muted-foreground mt-1 font-mono">{profile.customer.customer_unique_id}</p>
        </div>
        <Badge variant={profile.prediction?.risk_level === 'high' ? 'destructive' : 'success'}>
          {profile.prediction?.risk_level?.toUpperCase()} RISK
        </Badge>
      </div>

      {/* Profile + Prediction */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader><CardTitle className="flex items-center gap-2"><User className="w-4 h-4" />Profile</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center gap-2 text-sm"><MapPin className="w-3.5 h-3.5 text-muted-foreground" />{profile.customer.customer_city}, {profile.customer.customer_state}</div>
            <div className="flex items-center gap-2 text-sm"><ShoppingCart className="w-3.5 h-3.5 text-muted-foreground" />{profile.features.purchase_count} orders</div>
            <div className="flex items-center gap-2 text-sm"><Star className="w-3.5 h-3.5 text-muted-foreground" />{profile.features.review_score_mean} avg review</div>
            <div className="flex items-center gap-2 text-sm"><Clock className="w-3.5 h-3.5 text-muted-foreground" />{profile.features.days_since_last_purchase} days since last order</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle className="flex items-center gap-2"><TrendingUp className="w-4 h-4" />Feature Store</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-2.5 text-sm">
              {Object.entries(profile.features).filter(([k]) => k !== 'customer_unique_id').map(([k, v]) => (
                <div key={k} className="flex justify-between"><span className="text-muted-foreground">{k.replace(/_/g, ' ')}</span><span className="font-medium">{typeof v === 'number' ? (v > 10 ? formatCurrency(v) : v.toFixed(2)) : v}</span></div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle className="flex items-center gap-2"><Brain className="w-4 h-4" />Prediction</CardTitle></CardHeader>
          <CardContent className="flex flex-col items-center gap-4">
            <div className="relative w-28 h-28">
              <svg className="w-28 h-28 -rotate-90" viewBox="0 0 120 120">
                <circle cx="60" cy="60" r="50" fill="none" stroke="hsl(var(--muted))" strokeWidth="10" />
                <circle cx="60" cy="60" r="50" fill="none" stroke={profile.prediction.probability > 0.5 ? '#ef4444' : '#10b981'} strokeWidth="10"
                  strokeDasharray={`${profile.prediction.probability * 314} 314`} strokeLinecap="round" />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-2xl font-bold">{formatPercent(profile.prediction.probability)}</span>
              </div>
            </div>
            <StatusBadge status={profile.prediction.risk_level === 'high' ? 'critical' : 'ok'} />
          </CardContent>
        </Card>
      </div>

      {/* SHAP Waterfall */}
      <Card>
        <CardHeader><CardTitle>SHAP Explanation</CardTitle><CardDescription>Feature importance for this prediction</CardDescription></CardHeader>
        <CardContent>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={SHAP_DATA} layout="vertical" margin={{ left: 100 }}>
                <XAxis type="number" tick={{ fontSize: 12, fill: 'hsl(var(--muted-foreground))' }} />
                <YAxis type="category" dataKey="feature" tick={{ fontSize: 12, fill: 'hsl(var(--muted-foreground))' }} width={100} />
                <Tooltip contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: '8px', fontSize: '12px' }} />
                <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                  {SHAP_DATA.map((entry) => (<Cell key={entry.feature} fill={entry.value > 0 ? '#ef4444' : '#10b981'} />))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Timeline */}
      <Card>
        <CardHeader><CardTitle>Customer Timeline</CardTitle></CardHeader>
        <CardContent>
          <div className="relative">
            <div className="absolute left-4 top-0 bottom-0 w-px bg-border" />
            <div className="space-y-6">
              {TIMELINE.map((event, i) => (
                <div key={i} className="flex items-start gap-4 pl-8 relative">
                  <div className="absolute left-[11px] w-2.5 h-2.5 rounded-full bg-primary border-2 border-background" />
                  <div>
                    <p className="text-sm font-medium text-foreground">{event.type}</p>
                    <p className="text-xs text-muted-foreground">{event.details}</p>
                    <p className="text-xs text-muted-foreground mt-0.5">{event.date}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
