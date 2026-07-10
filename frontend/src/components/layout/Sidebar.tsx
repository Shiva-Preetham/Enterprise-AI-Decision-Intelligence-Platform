import { NavLink, useLocation } from 'react-router-dom';
import { cn } from '../../lib/utils';
import {
  LayoutDashboard, Users, MessageSquare, GitBranch, ShieldCheck,
  Lightbulb, ClipboardList, Box, Activity, Database, Server,
  Bell, Settings, Network, Play, ChevronLeft, ChevronRight,
} from 'lucide-react';
import { useState } from 'react';

const NAV_GROUPS = [
  {
    label: 'Overview',
    items: [
      { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
      { to: '/customers', icon: Users, label: 'Customers' },
    ],
  },
  {
    label: 'Intelligence',
    items: [
      { to: '/copilot', icon: MessageSquare, label: 'AI Copilot' },
      { to: '/recommendations', icon: Lightbulb, label: 'Recommendations' },
      { to: '/workflows', icon: GitBranch, label: 'Workflows' },
      { to: '/approvals', icon: ShieldCheck, label: 'Approvals' },
      { to: '/audit', icon: ClipboardList, label: 'Audit Explorer' },
    ],
  },
  {
    label: 'Operations',
    items: [
      { to: '/models', icon: Box, label: 'Model Registry' },
      { to: '/drift', icon: Activity, label: 'Drift Monitor' },
      { to: '/features', icon: Database, label: 'Feature Store' },
      { to: '/mlops', icon: Server, label: 'MLOps' },
      { to: '/alerts', icon: Bell, label: 'Alerts' },
    ],
  },
  {
    label: 'System',
    items: [
      { to: '/admin', icon: Settings, label: 'Admin' },
      { to: '/architecture', icon: Network, label: 'Architecture' },
      { to: '/demo', icon: Play, label: 'Demo Mode' },
    ],
  },
];

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();

  return (
    <aside
      className={cn(
        'flex flex-col h-screen bg-sidebar border-r border-border transition-all duration-300 scrollbar-thin overflow-y-auto',
        collapsed ? 'w-16' : 'w-60'
      )}
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 h-14 border-b border-border shrink-0">
        <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
          <span className="text-primary-foreground font-bold text-sm">CI</span>
        </div>
        {!collapsed && (
          <span className="text-sm font-semibold text-foreground truncate">
            Customer Intelligence
          </span>
        )}
      </div>

      {/* Nav Groups */}
      <nav className="flex-1 py-4 px-2 space-y-6">
        {NAV_GROUPS.map((group) => (
          <div key={group.label}>
            {!collapsed && (
              <p className="px-3 mb-2 text-[11px] font-medium uppercase tracking-wider text-muted-foreground">
                {group.label}
              </p>
            )}
            <ul className="space-y-0.5">
              {group.items.map((item) => {
                const isActive =
                  item.to === '/'
                    ? location.pathname === '/'
                    : location.pathname.startsWith(item.to);
                return (
                  <li key={item.to}>
                    <NavLink
                      to={item.to}
                      className={cn(
                        'flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors',
                        isActive
                          ? 'bg-primary/10 text-primary font-medium'
                          : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                      )}
                      title={item.label}
                    >
                      <item.icon className="w-4 h-4 shrink-0" />
                      {!collapsed && <span className="truncate">{item.label}</span>}
                    </NavLink>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </nav>

      {/* Collapse toggle */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="flex items-center justify-center h-10 border-t border-border text-muted-foreground hover:text-foreground transition-colors shrink-0"
        aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      >
        {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
      </button>
    </aside>
  );
}
