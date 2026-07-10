import { useState } from 'react';
import { Card, CardContent } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { StatusBadge } from '../components/widgets/StatusBadge';
import { ShieldCheck, Check, X } from 'lucide-react';

const PENDING = [
  { id: 'wf-002', customer: 'c_01023', type: 'Win-back Campaign', confidence: 0.78, reason: 'Customer has been inactive for 120 days. Historical win-back success rate: 45%.', cost: 25, impact: '$180 estimated CLV recovery' },
  { id: 'wf-006', customer: 'c_02150', type: 'Premium Upgrade', confidence: 0.91, reason: 'Top 5% by CLV. High engagement pattern detected.', cost: 0, impact: '$420 annual revenue increase' },
];

export default function ApprovalCenter() {
  const [approvals, setApprovals] = useState(PENDING);

  const handleApprove = (id: string) => setApprovals((prev) => prev.filter((a) => a.id !== id));
  const handleReject = (id: string) => setApprovals((prev) => prev.filter((a) => a.id !== id));

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Approval Center</h1>
          <p className="text-sm text-muted-foreground mt-1">{approvals.length} items pending review</p>
        </div>
        <ShieldCheck className="w-5 h-5 text-primary" />
      </div>
      {approvals.length === 0 ? (
        <Card><CardContent className="p-12 text-center"><p className="text-muted-foreground">No pending approvals</p></CardContent></Card>
      ) : (
        <div className="space-y-4">
          {approvals.map((item) => (
            <Card key={item.id} className="hover:border-primary/30 transition-colors">
              <CardContent className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <p className="text-base font-semibold">{item.type}</p>
                    <p className="text-xs text-muted-foreground mt-0.5">{item.customer} · Confidence: {(item.confidence * 100).toFixed(0)}%</p>
                  </div>
                  <StatusBadge status="PendingApproval" />
                </div>
                <div className="bg-muted/30 rounded-md p-4 text-sm space-y-2 mb-4">
                  <p><span className="text-muted-foreground">Business Reason:</span> {item.reason}</p>
                  <p><span className="text-muted-foreground">Expected Impact:</span> {item.impact}</p>
                  <p><span className="text-muted-foreground">Estimated Cost:</span> ${item.cost}</p>
                </div>
                <div className="flex gap-2 justify-end">
                  <Button variant="outline" size="sm" onClick={() => handleReject(item.id)}><X className="w-3.5 h-3.5 mr-1" />Reject</Button>
                  <Button size="sm" onClick={() => handleApprove(item.id)}><Check className="w-3.5 h-3.5 mr-1" />Approve</Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
