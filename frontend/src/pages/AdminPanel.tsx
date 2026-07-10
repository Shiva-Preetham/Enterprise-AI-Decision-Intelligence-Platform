import { Card, CardContent, CardHeader, CardTitle } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Users, Shield, Flag } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const USERS_DATA = [
  { username: 'admin', role: 'admin', lastLogin: '2024-06-10 09:15' },
  { username: 'manager', role: 'manager', lastLogin: '2024-06-10 14:30' },
  { username: 'analyst', role: 'analyst', lastLogin: '2024-06-09 11:00' },
  { username: 'viewer', role: 'viewer', lastLogin: '2024-06-08 16:45' },
];

const FEATURE_FLAGS = [
  { name: 'ENABLE_DRIFT_DETECTION', value: true, description: 'Enable automated drift detection alerts' },
  { name: 'ENABLE_AUTO_ROLLBACK', value: false, description: 'Automatically rollback model on drift alert' },
  { name: 'ENABLE_AI_COPILOT', value: true, description: 'Enable LangGraph AI Copilot feature' },
  { name: 'ENABLE_HITL_APPROVAL', value: true, description: 'Require human approval for high-cost recommendations' },
];

export default function AdminPanel() {
  const { hasRole } = useAuth();
  const isAdmin = hasRole('admin');

  return (
    <div className="space-y-6 animate-fade-in">
      <div><h1 className="text-2xl font-bold">Admin Panel</h1><p className="text-sm text-muted-foreground mt-1">Platform configuration and user management</p></div>

      {!isAdmin && (
        <div className="flex items-center gap-3 bg-amber-500/10 border border-amber-500/20 rounded-lg p-4">
          <Shield className="w-5 h-5 text-amber-500" />
          <p className="text-sm text-amber-500">You need Admin privileges to modify settings. Currently viewing in read-only mode.</p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader><CardTitle className="flex items-center gap-2"><Users className="w-4 h-4" />User Management</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {USERS_DATA.map((u) => (
              <div key={u.username} className="flex items-center justify-between p-3 rounded-md bg-muted/30">
                <div><p className="text-sm font-medium">{u.username}</p><p className="text-xs text-muted-foreground">Last login: {u.lastLogin}</p></div>
                <Badge variant={u.role === 'admin' ? 'default' : 'outline'}>{u.role}</Badge>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle className="flex items-center gap-2"><Flag className="w-4 h-4" />Feature Flags</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {FEATURE_FLAGS.map((ff) => (
              <div key={ff.name} className="flex items-center justify-between p-3 rounded-md bg-muted/30">
                <div><p className="text-sm font-mono">{ff.name}</p><p className="text-xs text-muted-foreground">{ff.description}</p></div>
                <div className={`w-10 h-5 rounded-full flex items-center px-0.5 transition-colors cursor-pointer ${ff.value ? 'bg-primary justify-end' : 'bg-muted justify-start'}`}>
                  <div className="w-4 h-4 rounded-full bg-white shadow" />
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
