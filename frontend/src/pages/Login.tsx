import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/common/Button';
import { Sparkles, AlertCircle } from 'lucide-react';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(username, password);
      navigate('/');
    } catch {
      setError('Invalid credentials. Try admin/admin, manager/manager, analyst/analyst, or viewer/viewer.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-sm space-y-8 animate-fade-in">
        {/* Logo */}
        <div className="text-center">
          <div className="w-14 h-14 rounded-2xl bg-primary mx-auto flex items-center justify-center mb-4">
            <Sparkles className="w-7 h-7 text-primary-foreground" />
          </div>
          <h1 className="text-xl font-bold text-foreground">Customer Intelligence</h1>
          <p className="text-sm text-muted-foreground mt-1">Enterprise AI Decision Platform</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-foreground mb-1.5">Username</label>
            <input value={username} onChange={(e) => setUsername(e.target.value)}
              className="w-full bg-muted/50 border border-border rounded-md px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-ring"
              placeholder="Enter username" autoFocus />
          </div>
          <div>
            <label className="block text-sm font-medium text-foreground mb-1.5">Password</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-muted/50 border border-border rounded-md px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-ring"
              placeholder="Enter password" />
          </div>

          {error && (
            <div className="flex items-center gap-2 text-xs text-red-500 bg-red-500/10 rounded-md p-3">
              <AlertCircle className="w-4 h-4 shrink-0" />{error}
            </div>
          )}

          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </Button>
        </form>

        <div className="text-center">
          <p className="text-xs text-muted-foreground">Demo credentials: <code className="bg-muted/50 px-1 py-0.5 rounded">admin / admin</code></p>
        </div>
      </div>
    </div>
  );
}
