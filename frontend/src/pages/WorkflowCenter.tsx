import { Card, CardContent, CardHeader, CardTitle } from '../components/common/Card';
import { StatusBadge } from '../components/widgets/StatusBadge';
import { GitBranch } from 'lucide-react';

const WORKFLOW_STEPS = ['Created', 'PendingApproval', 'Approved', 'Executing', 'Completed'];
const MOCK_WORKFLOWS = [
  { id: 'wf-001', customer: 'c_01000', type: 'Retention Offer', status: 'Completed', created: '2024-06-01' },
  { id: 'wf-002', customer: 'c_01023', type: 'Win-back Campaign', status: 'PendingApproval', created: '2024-06-05' },
  { id: 'wf-003', customer: 'c_01045', type: 'Loyalty Reward', status: 'Executing', created: '2024-06-07' },
  { id: 'wf-004', customer: 'c_01067', type: 'Premium Upgrade', status: 'Approved', created: '2024-06-08' },
  { id: 'wf-005', customer: 'c_01089', type: 'Retention Offer', status: 'Failed', created: '2024-06-09' },
];

function WorkflowStepper({ currentStatus }: { currentStatus: string }) {
  const currentIdx = WORKFLOW_STEPS.indexOf(currentStatus);
  return (
    <div className="flex items-center gap-1">
      {WORKFLOW_STEPS.map((step, i) => (
        <div key={step} className="flex items-center">
          <div className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-medium ${
            i <= currentIdx ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'
          }`}>{i + 1}</div>
          {i < WORKFLOW_STEPS.length - 1 && <div className={`w-8 h-0.5 ${i < currentIdx ? 'bg-primary' : 'bg-muted'}`} />}
        </div>
      ))}
    </div>
  );
}

export default function WorkflowCenter() {
  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Workflow Center</h1>
        <p className="text-sm text-muted-foreground mt-1">Track decision workflow lifecycles</p>
      </div>
      <div className="space-y-4">
        {MOCK_WORKFLOWS.map((wf) => (
          <Card key={wf.id} className="hover:border-primary/30 transition-colors">
            <CardContent className="p-5">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <GitBranch className="w-4 h-4 text-muted-foreground" />
                  <div>
                    <p className="text-sm font-medium">{wf.type}</p>
                    <p className="text-xs text-muted-foreground">{wf.customer} · {wf.id}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-muted-foreground">{wf.created}</span>
                  <StatusBadge status={wf.status} />
                </div>
              </div>
              {wf.status !== 'Failed' && <WorkflowStepper currentStatus={wf.status} />}
              {wf.status === 'Failed' && <div className="text-xs text-red-500 bg-red-500/10 rounded px-3 py-1.5">Execution failed — executor timeout</div>}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
