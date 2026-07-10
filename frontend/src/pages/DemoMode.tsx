import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { StatusBadge } from '../components/widgets/StatusBadge';
import { Play, RotateCcw, ChevronRight } from 'lucide-react';

const DEMO_STEPS = [
  { id: 1, title: 'Customer Begins Churning', description: 'Customer c_01000 has not purchased in 87 days. Feature store flags elevated risk.', status: 'prediction' },
  { id: 2, title: 'ML Prediction', description: 'XGBoost v3 predicts churn probability: 72%. Risk level: HIGH.', status: 'analysis' },
  { id: 3, title: 'SHAP Explanation', description: 'Top driver: days_since_last_purchase (+0.18). Mitigator: purchase_count (-0.12).', status: 'analysis' },
  { id: 4, title: 'AI Copilot Analysis', description: 'LangGraph agent recommends retention offer based on CLV ($542) and churn pattern.', status: 'recommendation' },
  { id: 5, title: 'Policy Engine Evaluation', description: 'Policy ALLOW: CLV > $200, churn_prob > 0.5, no prior offers in 30 days.', status: 'policy' },
  { id: 6, title: 'Recommendation Generated', description: 'Type: Retention Offer. Confidence: 92%. Estimated Cost: $50. Expected Impact: $542 CLV.', status: 'recommendation' },
  { id: 7, title: 'Human Approval Required', description: 'Routed to manager for approval. Cost exceeds $25 threshold.', status: 'approval' },
  { id: 8, title: 'Manager Approves', description: 'Approved by manager_1. Comment: "High-value customer, proceed."', status: 'approved' },
  { id: 9, title: 'Execution', description: 'NotificationExecutor sends personalized email with 15% discount code.', status: 'execution' },
  { id: 10, title: 'Outcome Recorded', description: 'Customer redeems offer within 48 hours. Churn risk drops to 12%. Audit trail complete.', status: 'success' },
];

const STEP_COLORS: Record<string, string> = {
  prediction: 'bg-blue-500', analysis: 'bg-purple-500', recommendation: 'bg-amber-500',
  policy: 'bg-cyan-500', approval: 'bg-amber-500', approved: 'bg-emerald-500',
  execution: 'bg-indigo-500', success: 'bg-emerald-600',
};

export default function DemoMode() {
  const [currentStep, setCurrentStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);

  const advance = useCallback(() => {
    setCurrentStep((prev) => {
      if (prev >= DEMO_STEPS.length - 1) { setIsPlaying(false); return prev; }
      return prev + 1;
    });
  }, []);

  useEffect(() => {
    if (!isPlaying) return;
    const timer = setInterval(advance, 2500);
    return () => clearInterval(timer);
  }, [isPlaying, advance]);

  const reset = () => { setCurrentStep(0); setIsPlaying(false); };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold">Demo Mode</h1><p className="text-sm text-muted-foreground mt-1">Guided workflow replay for presentations</p></div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={reset}><RotateCcw className="w-3.5 h-3.5 mr-1" />Reset</Button>
          <Button size="sm" onClick={() => setIsPlaying(!isPlaying)}>{isPlaying ? 'Pause' : <><Play className="w-3.5 h-3.5 mr-1" />Play</>}</Button>
        </div>
      </div>

      {/* Progress */}
      <div className="flex gap-1">
        {DEMO_STEPS.map((_, i) => (
          <div key={i} className={`h-1.5 flex-1 rounded-full transition-colors ${i <= currentStep ? 'bg-primary' : 'bg-muted'}`} />
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Timeline */}
        <Card>
          <CardHeader><CardTitle>Workflow Timeline</CardTitle></CardHeader>
          <CardContent>
            <div className="relative">
              <div className="absolute left-4 top-0 bottom-0 w-px bg-border" />
              <div className="space-y-4">
                {DEMO_STEPS.map((step, i) => (
                  <div key={step.id} className={`flex items-start gap-4 pl-10 relative transition-opacity ${i > currentStep ? 'opacity-30' : 'opacity-100'}`}>
                    <div className={`absolute left-[10px] w-3 h-3 rounded-full border-2 border-background transition-colors ${
                      i <= currentStep ? STEP_COLORS[step.status] || 'bg-primary' : 'bg-muted'
                    } ${i === currentStep ? 'ring-2 ring-primary ring-offset-2 ring-offset-background' : ''}`} />
                    <div>
                      <p className="text-sm font-medium">{step.title}</p>
                      {i <= currentStep && <p className="text-xs text-muted-foreground mt-0.5">{step.description}</p>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Current Step Detail */}
        <Card className="border-primary/30">
          <CardContent className="p-8 flex flex-col items-center justify-center min-h-[300px] text-center">
            <div className={`w-12 h-12 rounded-full flex items-center justify-center text-white mb-4 ${STEP_COLORS[DEMO_STEPS[currentStep].status] || 'bg-primary'}`}>
              <span className="text-lg font-bold">{currentStep + 1}</span>
            </div>
            <h2 className="text-xl font-bold mb-2">{DEMO_STEPS[currentStep].title}</h2>
            <p className="text-sm text-muted-foreground max-w-md">{DEMO_STEPS[currentStep].description}</p>
            {currentStep < DEMO_STEPS.length - 1 && !isPlaying && (
              <Button variant="outline" size="sm" className="mt-6" onClick={advance}>Next <ChevronRight className="w-3.5 h-3.5 ml-1" /></Button>
            )}
            {currentStep === DEMO_STEPS.length - 1 && (
              <div className="mt-6"><StatusBadge status="Completed" /></div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
