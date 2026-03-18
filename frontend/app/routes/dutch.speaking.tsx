import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { getExercise, evaluateSpeaking, generateTheme } from '~/services/dutchApi';
import { Mic, Square, CheckCircle, AlertCircle, RefreshCcw } from 'lucide-react';
import { WavRecorder } from '~/utils/audioUtils';
import type { Route } from './+types/dutch.speaking';

export function meta({}: Route.MetaArgs) {
  return [
    { title: 'Speaking Practice — Dutch B1' },
    { name: 'description', content: 'AI-powered Dutch B1 speaking exercises with speech recognition and evaluation.' },
  ];
}

interface Keyword { dutch: string; english: string; }
interface Exercise { theme: string; prompt: string; keywords?: Keyword[]; }
interface SpeakingResult {
  transcription: string;
  score: number;
  feedback: string;
  model_answer: string;
  improvement_tips: string;
}

export default function SpeakingPage() {
  const [exercise, setExercise] = useState<Exercise | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [result, setResult] = useState<SpeakingResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const recorder = useRef<WavRecorder | null>(null);

  const fetchNewExercise = async (ignoreCache = false) => {
    setLoading(true);
    try {
      let theme = localStorage.getItem('current_theme') || 'Dagelijkse routine';
      const cacheKey = 'speaking_exercise_cache';
      const cached = localStorage.getItem(cacheKey);
      if (!ignoreCache && cached) {
        const p = JSON.parse(cached);
        if (p.theme === theme) { setExercise(p); setLoading(false); return; }
      }
      if (ignoreCache) {
        const r = await generateTheme(theme);
        theme = r.data.theme;
        localStorage.setItem('current_theme', theme);
        localStorage.removeItem('writing_exercise_cache');
        localStorage.removeItem('listening_exercise_cache');
      }
      const res = await getExercise('speaking', theme);
      setExercise(res.data);
      localStorage.setItem(cacheKey, JSON.stringify(res.data));
      setResult(null); setAudioBlob(null); setError(null);
    } catch {
      setError('Unable to connect to the Dutch B1 server.');
    } finally { setLoading(false); }
  };

  useEffect(() => { fetchNewExercise(false); }, []);

  const startRecording = async () => {
    try {
      if (!recorder.current) recorder.current = new WavRecorder();
      await recorder.current.start();
      setIsRecording(true);
      setAudioBlob(null);
      setResult(null);
    } catch {
      alert('Microphone access required. Please grant permission.');
    }
  };

  const stopRecording = () => {
    if (recorder.current) {
      const blob = recorder.current.stop();
      setAudioBlob(blob);
      setIsRecording(false);
    }
  };

  const handleSubmit = async () => {
    if (!audioBlob || !exercise) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('audio', audioBlob, 'speaking.wav');
    formData.append('user_id', 'local_user');
    formData.append('theme', exercise.theme);
    formData.append('prompt', exercise.prompt);
    formData.append('date', new Date().toISOString().split('T')[0]);
    formData.append('keywords', JSON.stringify(exercise.keywords || []));
    try {
      const res = await evaluateSpeaking(formData);
      setResult(res.data);
    } catch { /* silent */ }
    finally { setLoading(false); }
  };

  if (!exercise && loading) return (
    <div className="page-container" style={{ textAlign: 'center', paddingTop: '120px' }}>
      <RefreshCcw className="spinning" size={36} color="var(--secondary)" />
      <h2 style={{ marginTop: '20px' }}>Generating Your Scenario...</h2>
    </div>
  );

  if (error) return (
    <div className="page-container" style={{ textAlign: 'center', paddingTop: '120px' }}>
      <AlertCircle size={48} color="var(--error)" />
      <h2 style={{ marginTop: '20px' }}>Connection Issue</h2>
      <p style={{ color: 'var(--text-muted)', margin: '12px auto 24px', maxWidth: 480 }}>{error}</p>
      <button className="btn btn-primary" onClick={() => fetchNewExercise(true)}>Try Again</button>
    </div>
  );

  if (!exercise) return null;

  return (
    <div className="page-container">
      <header style={{ marginBottom: '32px', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h1>Speaking Practice</h1>
          <p style={{ color: 'var(--text-muted)', marginTop: '4px' }}>Theme: <strong style={{ color: 'var(--secondary)' }}>{exercise.theme}</strong></p>
        </div>
        <button className="btn btn-secondary" onClick={() => fetchNewExercise(true)} disabled={loading}>
          <RefreshCcw size={16} /> New Exercise
        </button>
      </header>

      <div style={{ maxWidth: 680, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '24px' }}>
        {/* Scenario */}
        <section className="glass card" style={{ textAlign: 'center' }}>
          <div style={{ width: 64, height: 64, borderRadius: '50%', background: 'rgba(46,196,182,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px' }}>
            <Mic size={28} color="var(--secondary)" />
          </div>
          <h3 style={{ color: 'var(--secondary)', marginBottom: '10px' }}>Role Play Scenario</h3>
          <p style={{ fontSize: '1.1rem', fontWeight: 600, lineHeight: 1.6 }}>{exercise.prompt}</p>

          {exercise.keywords && exercise.keywords.length > 0 && (
            <div style={{ marginTop: '20px' }}>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '12px' }}>Key Points to Cover:</p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', justifyContent: 'center' }}>
                {exercise.keywords.map((kw, i) => (
                  <div key={i} style={{ background: 'rgba(255,255,255,0.04)', padding: '8px 14px', borderRadius: '12px', border: '1px solid var(--glass-border)' }}>
                    <div style={{ fontWeight: 700, color: 'var(--secondary)', fontSize: '0.9rem' }}>{kw.dutch}</div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>{kw.english}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div style={{ marginTop: '28px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px' }}>
            {!isRecording ? (
              <motion.button
                whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.96 }}
                className="btn"
                style={{ background: 'var(--secondary)', color: 'var(--bg-dark)', fontWeight: 700, padding: '14px 32px', boxShadow: '0 8px 24px rgba(46,196,182,0.3)' }}
                onClick={startRecording}
                disabled={loading}
              >
                <Mic size={18} /> Start Recording
              </motion.button>
            ) : (
              <motion.button
                whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.96 }}
                className="btn"
                style={{ background: 'var(--error)', color: '#fff', fontWeight: 700, padding: '14px 32px', animation: 'pulse-glow 1.5s ease infinite' }}
                onClick={stopRecording}
              >
                <Square size={18} /> Stop Recording
              </motion.button>
            )}

            {audioBlob && !isRecording && (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px', width: '100%' }}>
                <audio controls src={URL.createObjectURL(audioBlob)} style={{ width: '100%' }} />
                <button className="btn btn-primary" onClick={handleSubmit} disabled={loading} style={{ width: '200px' }}>
                  {loading ? 'Analyzing...' : 'Submit Speaking'}
                </button>
              </div>
            )}
          </div>
        </section>

        {/* Results */}
        {result && (
          <motion.div initial={{ opacity: 0, scale: 0.97 }} animate={{ opacity: 1, scale: 1 }}>
            <div className="glass card" style={{ border: '2px solid var(--secondary)', marginBottom: '20px' }}>
              <div style={{ textAlign: 'center', marginBottom: '20px' }}>
                <h2 style={{ fontSize: '3rem', color: 'var(--secondary)' }}>{Math.round(result.score)}%</h2>
                <p style={{ color: 'var(--text-muted)' }}>Fluency & Accuracy</p>
              </div>
              <div style={{ background: 'rgba(255,255,255,0.03)', padding: '16px', borderRadius: '12px', marginBottom: '16px' }}>
                <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '6px' }}>TRANSCRIPTION</p>
                <p style={{ fontStyle: 'italic', fontSize: '0.95rem' }}>"{result.transcription}"</p>
              </div>
              <h4 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                <CheckCircle size={16} color="var(--secondary)" /> AI Feedback
              </h4>
              <p style={{ lineHeight: 1.6, fontSize: '0.93rem', whiteSpace: 'pre-wrap' }}>{result.feedback}</p>
            </div>

            <div className="glass card" style={{ borderLeft: '4px solid var(--primary)' }}>
              <h4 style={{ color: 'var(--primary)', marginBottom: '12px' }}>Teacher's Model Answer</h4>
              <p style={{ fontStyle: 'italic', background: 'rgba(255,159,28,0.05)', padding: '14px', borderRadius: '10px', marginBottom: '16px', lineHeight: 1.6 }}>{result.model_answer}</p>
              <h4 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '8px' }}>Improvement Tips:</h4>
              <p style={{ fontSize: '0.9rem', lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>{result.improvement_tips}</p>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
