import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles } from 'lucide-react';
import { Button } from '../components/common/Button';
import { Card } from '../components/common/Card';
import ReactMarkdown from 'react-markdown';
import { useAgentChat } from '../hooks/useApi';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  toolsUsed?: string[];
  timestamp: Date;
}

const SUGGESTED_PROMPTS = [
  'Why is customer c_01000 likely to churn?',
  'What retention strategy do you recommend for high-value customers?',
  'Summarize today\'s model drift status.',
  'Show me the top 10 customers by revenue at risk.',
  'Explain the current churn rate trend.',
];

const MOCK_RESPONSES: Record<string, string> = {}; // No longer used

export default function AICopilot() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const { mutateAsync: chatWithAgent } = useAgentChat();

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;
    const userMsg: Message = { id: Date.now().toString(), role: 'user', content: input, timestamp: new Date() };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await chatWithAgent({ question: userMsg.content });
      
      const content = `${response.answer}
      
${response.reasoning ? `**Reasoning:** ${response.reasoning}` : ''}
${response.follow_up_questions?.length ? `\n\n**Suggested Follow-ups:**\n${response.follow_up_questions.map(q => `- ${q}`).join('\n')}` : ''}
`;

      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(), 
        role: 'assistant',
        content: content.trim(),
        toolsUsed: response.tools_used,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (error) {
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error communicating with the agent.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] animate-fade-in">
      <div className="mb-4">
        <h1 className="text-2xl font-bold text-foreground">Enterprise AI Copilot</h1>
        <p className="text-sm text-muted-foreground mt-1">Ask business questions in natural language</p>
      </div>

      {/* Chat Messages */}
      <Card className="flex-1 flex flex-col overflow-hidden">
        <div ref={scrollRef} className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full gap-6">
              <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center">
                <Sparkles className="w-8 h-8 text-primary" />
              </div>
              <div className="text-center">
                <h2 className="text-lg font-semibold text-foreground">How can I help?</h2>
                <p className="text-sm text-muted-foreground mt-1">Ask me about customers, churn predictions, or business strategies.</p>
              </div>
              <div className="flex flex-wrap gap-2 justify-center max-w-lg">
                {SUGGESTED_PROMPTS.map((prompt) => (
                  <button key={prompt} onClick={() => setInput(prompt)}
                    className="px-3 py-1.5 text-xs rounded-full border border-border text-muted-foreground hover:text-foreground hover:bg-accent transition-colors">
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg) => (
            <div key={msg.id} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : ''}`}>
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                  <Bot className="w-4 h-4 text-primary" />
                </div>
              )}
              <div className={`max-w-[70%] rounded-lg px-4 py-3 text-sm ${msg.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted/50'}`}>
                {msg.role === 'assistant' ? (
                  <div className="prose prose-sm dark:prose-invert max-w-none">
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  </div>
                ) : msg.content}
                {msg.toolsUsed && msg.toolsUsed.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2 pt-2 border-t border-border/50">
                    {msg.toolsUsed.map((tool) => (
                      <span key={tool} className="px-1.5 py-0.5 text-[10px] rounded bg-primary/10 text-primary font-mono">{tool}</span>
                    ))}
                  </div>
                )}
              </div>
              {msg.role === 'user' && (
                <div className="w-8 h-8 rounded-lg bg-secondary flex items-center justify-center shrink-0">
                  <User className="w-4 h-4" />
                </div>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                <Bot className="w-4 h-4 text-primary" />
              </div>
              <div className="bg-muted/50 rounded-lg px-4 py-3">
                <div className="flex gap-1"><span className="w-2 h-2 bg-muted-foreground rounded-full animate-pulse" /><span className="w-2 h-2 bg-muted-foreground rounded-full animate-pulse [animation-delay:0.2s]" /><span className="w-2 h-2 bg-muted-foreground rounded-full animate-pulse [animation-delay:0.4s]" /></div>
              </div>
            </div>
          )}
        </div>

        {/* Input */}
        <div className="border-t border-border p-4">
          <div className="flex gap-2">
            <input value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask a question..." className="flex-1 bg-muted/50 rounded-md px-4 py-2.5 text-sm outline-none text-foreground placeholder:text-muted-foreground focus:ring-2 focus:ring-ring" />
            <Button onClick={handleSend} disabled={!input.trim() || isLoading} size="icon"><Send className="w-4 h-4" /></Button>
          </div>
        </div>
      </Card>
    </div>
  );
}
