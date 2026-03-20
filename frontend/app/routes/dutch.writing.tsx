import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { getExercise, improveWriting, generateTheme, getHistory } from '~/services/dutchApi';
import { Send, CheckCircle, AlertCircle, Wand2, RefreshCcw } from 'lucide-react';
import type { Route } from './+types/dutch.writing';

export function meta({}: Route.MetaArgs) {
  return [
    { title: 'Writing Practice — Dutch B1' },
    { name: 'description', content: 'AI-powered Dutch B1 writing exercises with instant feedback and model answers.' },
  ];
}

interface Keyword {
  dutch: string;
  english: string;
}

interface Exercise {
  id?: number;
  theme: string;
  prompt: string;
  keywords?: Keyword[];
  question?: string; 
}

interface EvalResult {
  score: number;
  feedback: string;
  improved_text: string;
  model_answer: string;
  explanation: string;
}

interface HistoryItem {
  id: number;
  prompt: string;
  user_text: string;
  score: number;
  improved_text: string;
  date: string;
}

export default function WritingPage() {
  const [exercise, setExercise] = useState<Exercise | null>(null);
  const [text, setText] = useState('');
  const [result, setResult] = useState<EvalResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<any[]>([]);

  const fetchHistoryFromBackend = async () => {
    try {
      const res = await getHistory(10);
      setHistory(res.data);
    } catch (e) {
      console.error('History fetch failed:', e);
    }
  };

  const fetchNewExercise = async (ignoreCache = false) => {
    setLoading(true);
    try {
      let theme = localStorage.getItem('current_theme') || 'Dagelijkse routine';
      const cacheKey = 'writing_exercise_cache';
      const cached = localStorage.getItem(cacheKey);

      if (!ignoreCache && cached) {
        const parsed = JSON.parse(cached);
        if (parsed.theme === theme) {
          setExercise(parsed);
          setLoading(false);
          return;
        }
      }

      if (ignoreCache) {
        const r = await generateTheme(theme);
        theme = r.data.theme;
        localStorage.setItem('current_theme', theme);
      }

      const res = await getExercise('writing', theme);
      const data = res.data;
      // Map backend 'question' to frontend 'prompt'
      const mapped = { ...data, prompt: data.question || data.prompt };
      setExercise(mapped);
      localStorage.setItem(cacheKey, JSON.stringify(mapped));
      setResult(null);
      setText('');
      setError(null);
      fetchHistoryFromBackend();
    } catch {
      setError('Unable to connect to the Dutch B1 server.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNewExercise(false);
    fetchHistoryFromBackend();
  }, []);

  const handleEvaluate = async () => {
    if (!text.trim() || loading || !exercise) return;
    setLoading(true);
    try {
      const res = await improveWriting({
        id: exercise.id,
        text,
        theme: exercise.theme,
        prompt: exercise.prompt || exercise.question,
        exercise_type: 'writing'
      });
      const r = res.data;
      setResult(r);
      fetchHistoryFromBackend();
    } catch { /* error shown via UI */ }
    finally { setLoading(false); }
  };

  if (!exercise && loading) return (
    <div className="page-container" style={{ textAlign: 'center', paddingTop: '120px' }}>
      <RefreshCcw className="spinning" size={36} color="var(--primary)" />
      <h2 style={{ marginTop: '20px' }}>Generating Your Assignment...</h2>
      <p style={{ color: 'var(--text-muted)' }}>Our AI is crafting a unique Dutch B1 scenario for you.</p>
    </div>
  );

  if (error) return (
    <div className="page-container" style={{ textAlign: 'center', paddingTop: '120px' }}>
      <AlertCircle size={48} color="var(--error)" />
      <h2 style={{ marginTop: '20px' }}>Connection Issue</h2>
      <p style={{ color: 'var(--text-muted)', maxWidth: '480px', margin: '12px auto 24px', lineHeight: 1.6 }}>{error}</p>
      <button className="btn btn-primary" onClick={() => fetchNewExercise(true)}>Try Again</button>
    </div>
  );

  if (!exercise) return null;

  return (
    <div className="page-container">
      <header style={{ marginBottom: '32px', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h1>Writing Practice</h1>
        </div>
        <button className="btn btn-secondary" onClick={() => fetchNewExercise(true)} disabled={loading}>
          <RefreshCcw size={16} /> New Exercise
        </button>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px' }}>
        {/* Left: prompt + input */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <section className="glass card">
            <h3 style={{ color: 'var(--primary)', marginBottom: '12px' }}>Assignment</h3>
            <p style={{ lineHeight: 1.7, fontSize: '1.05rem' }}>{exercise.prompt}</p>
            {exercise.keywords && exercise.keywords.length > 0 && (
              <div style={{ marginTop: '16px', display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {exercise.keywords.map((kw, i) => (
                  <span key={i} title={kw.english} style={{ padding: '4px 12px', background: 'rgba(255,159,28,0.1)', borderRadius: 999, fontSize: '0.82rem', color: 'var(--primary)', border: '1px solid rgba(255,159,28,0.2)', cursor: 'help' }}>
                    {kw.dutch} <small style={{ opacity: 0.6, marginLeft: '4px' }}>({kw.english})</small>
                  </span>
                ))}
              </div>
            )}
          </section>

          <textarea
            className="glass"
            style={{ width: '100%', minHeight: '280px', padding: '20px', fontSize: '1rem', color: 'var(--text-light)', resize: 'vertical', outline: 'none', background: 'var(--card-bg)', fontFamily: 'inherit', lineHeight: 1.7 }}
            placeholder="Schrijf hier je tekst..."
            value={text}
            onChange={(e) => setText(e.target.value)}
          />

          <div style={{ display: 'flex', gap: '12px' }}>
            <button className="btn btn-primary" onClick={handleEvaluate} disabled={loading || !text.trim()} style={{ flex: 2, padding: '14px' }}>
              {loading ? 'Analyzing...' : <><Wand2 size={18} /> Get AI Evaluation</>}
            </button>
          </div>
        </div>

        {/* Right: results */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {result ? (
            <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}>
              <div className="glass card" style={{ border: '2px solid var(--primary)', marginBottom: '20px' }}>
                <div style={{ textAlign: 'center', marginBottom: '20px' }}>
                  <h2 style={{ fontSize: '3rem', color: 'var(--primary)' }}>{result.score}%</h2>
                  <p style={{ color: 'var(--text-muted)' }}>AI Predicted Score</p>
                </div>
                <h4 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
                  <CheckCircle size={16} color="var(--secondary)" /> Feedback
                </h4>
                <p style={{ fontSize: '0.93rem', lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>{result.feedback}</p>
              </div>

              <div className="glass card" style={{ borderLeft: '4px solid var(--secondary)' }}>
                <h4 style={{ color: 'var(--secondary)', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Wand2 size={16} /> Improved & Model Answers
                </h4>
                <div style={{ marginBottom: '16px' }}>
                  <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '6px' }}>Improved Version:</p>
                  <p style={{ background: 'rgba(255,255,255,0.04)', padding: '12px', borderRadius: '10px', fontStyle: 'italic', fontSize: '0.95rem' }}>"{result.improved_text}"</p>
                </div>
                <div style={{ marginBottom: '12px' }}>
                  <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '6px' }}>Teacher's Model:</p>
                  <p style={{ background: 'rgba(46,196,182,0.06)', padding: '12px', borderRadius: '10px', fontSize: '0.95rem' }}>{result.model_answer}</p>
                </div>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', borderTop: '1px solid var(--glass-border)', paddingTop: '10px' }}>
                  <strong style={{ color: 'var(--text-light)' }}>Tip:</strong> {result.explanation}
                </p>
              </div>
            </motion.div>
          ) : (
            <div className="glass card" style={{ opacity: 0.45, textAlign: 'center', padding: '60px 20px' }}>
              <Send size={36} style={{ marginBottom: '16px', color: 'var(--text-muted)' }} />
              <p style={{ color: 'var(--text-muted)' }}>Type your Dutch text and click Evaluate to see AI feedback.</p>
            </div>
          )}

          {history.length > 0 && (
            <div>
              <h3 style={{ marginBottom: '14px', opacity: 0.8 }}>Recent History</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {history.slice(0, 10).map((item) => (
                  <div key={item.id} className="glass card" style={{ padding: '14px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                      <span style={{ color: 'var(--primary)', fontWeight: 700 }}>{item.score}%</span>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        {item.created_at ? new Date(item.created_at).toLocaleDateString() : (item.date || '')}
                      </span>
                    </div>
                    <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', fontStyle: 'italic', overflow: 'hidden', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' }}>
                      {item.user_answer || item.user_text}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      <style>{`
        @media (max-width: 860px) {
          .page-container > div[style*="grid"] { grid-template-columns: 1fr !important; }
        }
      `}</style>
    </div>
  );
}
