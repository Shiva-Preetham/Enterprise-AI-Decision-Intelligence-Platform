import { Card, CardContent } from '../components/common/Card';
import { ClipboardList } from 'lucide-react';

const AUDIT_EVENTS = [
  { id: '1', customer: 'c_01000', event_type: 'policy_evaluated', details: '{"action":"RETENTION_OFFER","decision":"ALLOW"}', workflow: 'wf-001', date: '2024-06-01 10:15:32' },
  { id: '2', customer: 'c_01000', event_type: 'reasoning_generated', details: '{"confidence":0.92}', workflow: 'wf-001', date: '2024-06-01 10:15:34' },
  { id: '3', customer: 'c_01000', event_type: 'recommendation_created', details: '{"type":"Retention Offer"}', workflow: 'wf-001', date: '2024-06-01 10:15:35' },
  { id: '4', customer: 'c_01000', event_type: 'approval_granted', details: '{"approver":"manager_1"}', workflow: 'wf-001', date: '2024-06-01 14:30:00' },
  { id: '5', customer: 'c_01000', event_type: 'execution_completed', details: '{"executor":"NotificationExecutor","status":"Success"}', workflow: 'wf-001', date: '2024-06-01 14:30:05' },
  { id: '6', customer: 'c_01023', event_type: 'policy_evaluated', details: '{"action":"WIN_BACK","decision":"ALLOW"}', workflow: 'wf-002', date: '2024-06-05 09:00:12' },
];

const EVENT_COLORS: Record<string, string> = {
  policy_evaluated: 'bg-blue-500', reasoning_generated: 'bg-purple-500', recommendation_created: 'bg-amber-500',
  approval_granted: 'bg-emerald-500', execution_completed: 'bg-emerald-600', policy_violation: 'bg-red-500',
  feedback_received: 'bg-cyan-500',
};

export default function AuditExplorer() {
  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold">Audit Explorer</h1><p className="text-sm text-muted-foreground mt-1">Complete decision audit trail</p></div>
        <ClipboardList className="w-5 h-5 text-primary" />
      </div>
      <Card>
        <CardContent className="p-6">
          <div className="relative">
            <div className="absolute left-4 top-0 bottom-0 w-px bg-border" />
            <div className="space-y-6">
              {AUDIT_EVENTS.map((event) => (
                <div key={event.id} className="flex items-start gap-4 pl-10 relative">
                  <div className={`absolute left-[10px] w-3 h-3 rounded-full ${EVENT_COLORS[event.event_type] || 'bg-muted'} border-2 border-background`} />
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium">{event.event_type.replace(/_/g, ' ')}</p>
                      <span className="text-xs text-muted-foreground">{event.date}</span>
                    </div>
                    <p className="text-xs text-muted-foreground mt-0.5">{event.customer} · {event.workflow}</p>
                    <pre className="text-xs text-muted-foreground mt-1 bg-muted/30 rounded px-2 py-1 overflow-x-auto font-mono">{event.details}</pre>
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
