import { useState } from 'react';
import { Card, CardContent } from '../components/common/Card';
import { Network } from 'lucide-react';

const NODES = [
  { id: 'etl', label: 'ETL Pipeline', description: 'Olist CSV ingestion → PostgreSQL tables', color: '#3b82f6' },
  { id: 'feature', label: 'Feature Store', description: 'RFM + CLV + behavioral features → customer_feature_store', color: '#8b5cf6' },
  { id: 'ml', label: 'ML Pipeline', description: 'XGBoost + LightGBM + RandomForest → model selection + SHAP', color: '#10b981' },
  { id: 'api', label: 'FastAPI Backend', description: 'REST API with Repository Pattern + DI + async SQLAlchemy', color: '#f59e0b' },
  { id: 'cache', label: 'Redis + RabbitMQ', description: 'Caching layer + Celery message broker', color: '#ef4444' },
  { id: 'decision', label: 'Decision Engine', description: 'Policy Engine → Reasoning Engine → Recommendation → Workflow', color: '#ec4899' },
  { id: 'agent', label: 'LangGraph Agent', description: 'AI Copilot with tool calling + RAG + guardrails', color: '#06b6d4' },
  { id: 'mlops', label: 'MLOps Layer', description: 'Model Registry + Drift Detection + Prometheus + Alerting', color: '#84cc16' },
  { id: 'frontend', label: 'Enterprise UI', description: 'React + TypeScript + TailwindCSS + Recharts', color: '#f97316' },
];

export default function ArchitectureExplorer() {
  const [selected, setSelected] = useState<string | null>(null);
  const selectedNode = NODES.find((n) => n.id === selected);

  return (
    <div className="space-y-6 animate-fade-in">
      <div><h1 className="text-2xl font-bold">Architecture Explorer</h1><p className="text-sm text-muted-foreground mt-1">Interactive platform architecture</p></div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card>
            <CardContent className="p-8">
              <div className="flex flex-col items-center gap-3">
                {NODES.map((node, i) => (
                  <div key={node.id}>
                    <button onClick={() => setSelected(node.id)}
                      className={`w-64 p-4 rounded-lg border-2 text-center transition-all hover:scale-105 ${
                        selected === node.id ? 'border-primary shadow-lg shadow-primary/20' : 'border-border hover:border-primary/50'
                      }`} style={{ borderLeftColor: node.color, borderLeftWidth: '4px' }}>
                      <p className="text-sm font-semibold">{node.label}</p>
                    </button>
                    {i < NODES.length - 1 && (
                      <div className="flex justify-center"><div className="w-px h-4 bg-border" /><div className="w-2 h-2 border-b-2 border-r-2 border-border transform rotate-45 -mt-1" /></div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        <div>
          <Card className="sticky top-6">
            <CardContent className="p-6">
              {selectedNode ? (
                <div className="animate-fade-in">
                  <div className="w-3 h-3 rounded-full mb-3" style={{ backgroundColor: selectedNode.color }} />
                  <h3 className="text-lg font-semibold">{selectedNode.label}</h3>
                  <p className="text-sm text-muted-foreground mt-2">{selectedNode.description}</p>
                </div>
              ) : (
                <div className="text-center py-8">
                  <Network className="w-8 h-8 text-muted-foreground mx-auto mb-3" />
                  <p className="text-sm text-muted-foreground">Click a component to view details</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
