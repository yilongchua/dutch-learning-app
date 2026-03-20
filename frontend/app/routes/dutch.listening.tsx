import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import dutchApi, { getExercise, generateTheme } from '~/services/dutchApi';
import { useDutchSession } from '~/context/dutchSession';
import { Play, Pause, CheckCircle, AlertCircle, RefreshCcw } from 'lucide-react';
import type { Route } from './+types/dutch.listening';

export function meta({}: Route.MetaArgs) {
  return [
    { title: 'Listening Practice — Dutch B1' },
    { name: 'description', content: 'Dutch B1 listening comprehension exercises with AI-generated audio.' },
  ];
}

interface Exercise {
  id?: number;
  theme: string;
  question: string;
  audio_text?: string;
  text: string;
  options: string[];
  correct_answer: string;
  english_translation: string;
}

export default function ListeningPage() {
  const { state, hydrated, setCurrentTheme, setListeningState, resetListeningState } = useDutchSession();
  const exercise = state.listening.exercise as Exercise | null;
  const selected = state.listening.selected;
  const showResult = state.listening.showResult;
  const playbackSpeed = state.listening.playbackSpeed;

  const [audioUrl, setAudioUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [audioLoading, setAudioLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const fetchNewExercise = async (ignoreCache = false) => {
    setLoading(true);
    try {
      let theme = state.currentTheme || 'Dagelijkse routine';
      if (ignoreCache) {
        const r = await generateTheme(theme);
        theme = r.data.theme;
      }

      const res = await getExercise('listening', theme);
      const mapped = {
        ...res.data,
        audio_text: res.data.audio_text || '',
        text: res.data.audio_text || res.data.text || '',
        english_translation: res.data.audio_translation || res.data.english_translation || '',
      };
      setCurrentTheme(mapped.theme || theme);
      setListeningState({
        exercise: mapped,
        selected: null,
        showResult: false,
      });
      setAudioUrl('');
      setCurrentTime(0);
      setDuration(0);
      setError(null);
    } catch {
      setError('Unable to connect to the Dutch B1 server.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!hydrated) return;
    if (!exercise) {
      fetchNewExercise(false);
    }
  }, [hydrated]);

  const handlePlayAudio = async () => {
    if (audioUrl) {
      audioRef.current?.[isPlaying ? 'pause' : 'play']();
      return;
    }
    if (!exercise) return;
    setAudioLoading(true);
    try {
      const res = await dutchApi.get('/tts', { params: { text: exercise.text }, responseType: 'blob' });
      const url = URL.createObjectURL(new Blob([res.data], { type: 'audio/wav' }));
      setAudioUrl(url);
    } catch {
      // keep existing silent flow
    } finally {
      setAudioLoading(false);
    }
  };

  useEffect(() => {
    if (audioUrl && audioRef.current) audioRef.current.play();
  }, [audioUrl]);

  const changeSpeed = () => {
    const speeds = [1, 1.25, 1.5, 0.75];
    const next = speeds[(speeds.indexOf(playbackSpeed) + 1) % speeds.length];
    setListeningState({ playbackSpeed: next });
    if (audioRef.current) audioRef.current.playbackRate = next;
  };

  const handleNewExercise = async () => {
    resetListeningState();
    await fetchNewExercise(true);
  };

  const fmt = (t: number) => {
    if (isNaN(t)) return '0:00';
    return `${Math.floor(t / 60)}:${String(Math.floor(t % 60)).padStart(2, '0')}`;
  };

  if ((!exercise && loading) || !hydrated) return (
    <div className="page-container" style={{ textAlign: 'center', paddingTop: '120px' }}>
      <RefreshCcw className="spinning" size={36} color="var(--primary)" />
      <h2 style={{ marginTop: '20px' }}>Generating Listening Assignment...</h2>
    </div>
  );

  if (error) return (
    <div className="page-container" style={{ textAlign: 'center', paddingTop: '120px' }}>
      <AlertCircle size={48} color="var(--error)" />
      <h2 style={{ marginTop: '20px' }}>Connection Issue</h2>
      <p style={{ color: 'var(--text-muted)', margin: '12px auto 24px', maxWidth: 480 }}>{error}</p>
      <button className="btn btn-primary" onClick={handleNewExercise}>Try Again</button>
    </div>
  );

  if (!exercise) return null;

  const isCorrect = selected === exercise.correct_answer;

  return (
    <div className="page-container">
      <header style={{ marginBottom: '32px', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h1>Listening Practice</h1>
        </div>
        <button className="btn btn-secondary" onClick={handleNewExercise} disabled={loading}>
          <RefreshCcw size={16} /> New Exercise
        </button>
      </header>

      <div style={{ maxWidth: 680, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '24px' }}>
        <section className="glass card">
          <audio
            ref={audioRef}
            src={audioUrl}
            onTimeUpdate={() => setCurrentTime(audioRef.current?.currentTime || 0)}
            onLoadedMetadata={() => setDuration(audioRef.current?.duration || 0)}
            onPlay={() => setIsPlaying(true)}
            onPause={() => setIsPlaying(false)}
            onEnded={() => setIsPlaying(false)}
          />

          <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={handlePlayAudio}
              disabled={audioLoading}
              style={{
                width: 52,
                height: 52,
                borderRadius: '50%',
                background: 'var(--primary)',
                border: 'none',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                color: 'var(--bg-dark)',
                flexShrink: 0,
                boxShadow: '0 6px 20px var(--primary-glow)',
              }}
            >
              {audioLoading ? <RefreshCcw className="spinning" size={22} /> : isPlaying ? <Pause size={22} fill="currentColor" /> : <Play size={22} fill="currentColor" style={{ marginLeft: 2 }} />}
            </motion.button>

            <div style={{ flex: 1 }}>
              <input
                type="range"
                min="0"
                max={duration || 0}
                step="0.1"
                value={currentTime}
                onChange={(e) => {
                  const t = Number(e.target.value);
                  setCurrentTime(t);
                  if (audioRef.current) audioRef.current.currentTime = t;
                }}
                style={{ width: '100%', accentColor: 'var(--primary)', cursor: 'pointer' }}
              />
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                <span>{fmt(currentTime)}</span><span>{fmt(duration)}</span>
              </div>
            </div>

            <button
              onClick={changeSpeed}
              style={{
                padding: '7px 12px',
                borderRadius: '9px',
                background: 'var(--card-bg)',
                border: '1px solid var(--glass-border)',
                color: 'var(--text-light)',
                fontWeight: 700,
                cursor: 'pointer',
                fontSize: '0.88rem',
                fontFamily: 'inherit',
                minWidth: 56,
              }}
            >
              {playbackSpeed}x
            </button>
          </div>

          <p style={{ textAlign: 'center', color: 'var(--text-muted)', marginTop: '14px', fontSize: '0.85rem' }}>
            {audioLoading ? 'Generating audio...' : isPlaying ? '▶ Playing' : '▶ Click to play audio'}
          </p>

          <details style={{ marginTop: '16px' }}>
            <summary style={{ cursor: 'pointer', color: 'var(--text-muted)', fontWeight: 600 }}>
              Show Reference Transcript
            </summary>
            <div
              style={{
                marginTop: '10px',
                padding: '14px',
                borderRadius: '10px',
                background: 'rgba(255,255,255,0.03)',
                border: '1px solid var(--glass-border)',
              }}
            >
              <p style={{ margin: 0, lineHeight: 1.6 }}>
                {exercise.audio_text || exercise.text || 'Transcript is not available yet.'}
              </p>
            </div>
          </details>
        </section>

        <section className="glass card">
          <h3 style={{ marginBottom: '20px' }}>{exercise.question}</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {exercise.options.map((opt) => (
              <button
                key={opt}
                onClick={() => !showResult && setListeningState({ selected: opt })}
                style={{
                  padding: '14px 18px',
                  borderRadius: '12px',
                  textAlign: 'left',
                  cursor: showResult ? 'default' : 'pointer',
                  border: selected === opt ? '2px solid var(--primary)' : '1px solid var(--glass-border)',
                  background: selected === opt ? 'rgba(255,159,28,0.08)' : 'transparent',
                  color: 'var(--text-light)',
                  fontSize: '0.95rem',
                  fontFamily: 'inherit',
                  transition: 'all 0.2s',
                }}
              >
                {opt}
              </button>
            ))}
          </div>

          <div style={{ marginTop: '28px' }}>
            {!showResult ? (
              <button className="btn btn-primary" disabled={!selected} onClick={() => setListeningState({ showResult: true })}>
                Check Answer
              </button>
            ) : (
              <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px', color: isCorrect ? 'var(--secondary)' : 'var(--error)' }}>
                  {isCorrect ? <CheckCircle size={22} /> : <AlertCircle size={22} />}
                  <span style={{ fontWeight: 700, fontSize: '1.15rem' }}>{isCorrect ? 'Correct!' : `Actually: ${exercise.correct_answer}`}</span>
                </div>
                <div style={{ background: 'rgba(255,255,255,0.03)', padding: '20px', borderRadius: '12px', borderLeft: '4px solid var(--primary)' }}>
                  <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '8px', textTransform: 'uppercase' }}>Transcript</p>
                  <p style={{ fontWeight: 600, marginBottom: '14px', lineHeight: 1.6 }}>{exercise.text}</p>
                  <p style={{ fontStyle: 'italic', color: 'var(--text-muted)', fontSize: '0.9rem' }}>{exercise.english_translation}</p>
                </div>
              </motion.div>
            )}
          </div>
        </section>
      </div>
    </div>
  );
}
