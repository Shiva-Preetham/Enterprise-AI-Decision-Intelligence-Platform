import { Users, DollarSign, AlertTriangle, Lightbulb, ShieldCheck, Activity, Bell, Brain } from 'lucide-react';
import { KPICard } from '../components/charts/KPICard';
import { Card, CardContent, CardHeader, CardTitle } from '../components/common/Card';
import { StatusBadge } from '../components/widgets/StatusBadge';
import { formatCurrency, formatPercent, formatNumber } from '../lib/utils';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, CartesianGrid } from 'recharts';

// Mock data for when backend is unavailable
const MOCK_METRICS = { total_customers: 96096, high_risk_customers: 14414, average_clv: 287.50, average_review_score: 4.09, churn_rate: 0.15, model_version: 'v3' };
const TREND_DATA = [
  { month: 'Jan', churn: 0.18, revenue: 2400000 }, { month: 'Feb', churn: 0.17, revenue: 2100000 },
  { month: 'Mar', churn: 0.16, revenue: 2500000 }, { month: 'Apr', churn: 0.15, revenue: 2800000 },
  { month: 'May', churn: 0.14, revenue: 2700000 }, { month: 'Jun', churn: 0.15, revenue: 3000000 },
];
const SEGMENT_DATA = [
  { name: 'Champions', value: 25, color: '#3b82f6' }, { name: 'Loyal', value: 20, color: '#10b981' },
  { name: 'At Risk', value: 18, color: '#f59e0b' }, { name: 'Hibernating', value: 22, color: '#6366f1' },
  { name: 'Lost', value: 15, color: '#ef4444' },
];
const RECENT_DECISIONS = [
  { id: '1', customer: 'c_8901', type: 'Retention Offer', status: 'Completed', confidence: 0.92 },
  { id: '2', customer: 'c_3456', type: 'Win-back Campaign', status: 'PendingApproval', confidence: 0.78 },
  { id: '3', customer: 'c_7890', type: 'Loyalty Reward', status: 'Executing', confidence: 0.85 },
  { id: '4', customer: 'c_1234', type: 'Premium Upgrade', status: 'Approved', confidence: 0.91 },
];

export default function Dashboard() {
  const metrics = MOCK_METRICS;

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Executive Dashboard</h1>
        <p className="text-sm text-muted-foreground mt-1">Enterprise Customer Intelligence Overview</p>
      </div>

      {/* KPI Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard title="Total Customers" value={formatNumber(metrics.total_customers)} icon={Users} change={3.2} trend="up" />
        <KPICard title="Revenue at Risk" value={formatCurrency(metrics.high_risk_customers * metrics.average_clv)} icon={DollarSign} change={-5.1} trend="down" />
        <KPICard title="Churn Rate" value={formatPercent(metrics.churn_rate)} icon={AlertTriangle} change={-1.2} trend="down" />
        <KPICard title="Active Recommendations" value="47" icon={Lightbulb} change={12.5} trend="up" />
      </div>

      {/* Secondary KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard title="Pending Approvals" value="8" icon={ShieldCheck} trend="neutral" />
        <KPICard title="Model Health" value="Healthy" icon={Activity} trend="up" change={0} />
        <KPICard title="Drift Alerts" value="0" icon={Bell} trend="neutral" />
        <KPICard title="AI Copilot Sessions" value="156" icon={Brain} change={22} trend="up" />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Churn Trend */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Churn Rate Trend</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={TREND_DATA}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis dataKey="month" tick={{ fontSize: 12, fill: 'hsl(var(--muted-foreground))' }} />
                  <YAxis tick={{ fontSize: 12, fill: 'hsl(var(--muted-foreground))' }} tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} />
                  <Tooltip contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: '8px', fontSize: '12px' }} />
                  <Line type="monotone" dataKey="churn" stroke="hsl(var(--chart-1))" strokeWidth={2} dot={{ r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Segment Pie */}
        <Card>
          <CardHeader>
            <CardTitle>Customer Segments</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={SEGMENT_DATA} cx="50%" cy="50%" innerRadius={50} outerRadius={80} paddingAngle={4} dataKey="value">
                    {SEGMENT_DATA.map((entry) => (<Cell key={entry.name} fill={entry.color} />))}
                  </Pie>
                  <Tooltip contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: '8px', fontSize: '12px' }} />
                </PieChart>
              </ResponsiveContainer>
              <div className="flex flex-wrap gap-3 mt-2 justify-center">
                {SEGMENT_DATA.map((s) => (
                  <div key={s.name} className="flex items-center gap-1.5 text-xs text-muted-foreground">
                    <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: s.color }} />
                    {s.name}
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Revenue Bar + Recent Decisions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Monthly Revenue</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={TREND_DATA}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis dataKey="month" tick={{ fontSize: 12, fill: 'hsl(var(--muted-foreground))' }} />
                  <YAxis tick={{ fontSize: 12, fill: 'hsl(var(--muted-foreground))' }} tickFormatter={(v) => `$${(v / 1000000).toFixed(1)}M`} />
                  <Tooltip contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: '8px', fontSize: '12px' }} />
                  <Bar dataKey="revenue" fill="hsl(var(--chart-1))" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Decisions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {RECENT_DECISIONS.map((d) => (
                <div key={d.id} className="flex items-center justify-between p-3 rounded-md bg-muted/30 hover:bg-muted/50 transition-colors">
                  <div>
                    <p className="text-sm font-medium text-foreground">{d.type}</p>
                    <p className="text-xs text-muted-foreground">{d.customer}</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-muted-foreground">{formatPercent(d.confidence)}</span>
                    <StatusBadge status={d.status} />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
