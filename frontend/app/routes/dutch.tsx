import { useEffect, useState } from 'react';
import { Link } from 'react-router';
import { motion } from 'framer-motion';
import { TrendingUp, Award, PenTool, Mic, Headphones, ArrowRight } from 'lucide-react';
import { getDashboardData } from '~/services/dutchApi';
import type { Route } from './+types/dutch';

export function meta({}: Route.MetaArgs) {
  return [
    { title: 'Dutch B1 Dashboard' },
    { name: 'description', content: 'Track your Dutch B1 learning progress — streaks, scores and daily exercises.' },
  ];
}

interface DashboardData {
  history: { id: number; exercise_type: string; score: number; date_completed: string; feedback: string }[];
  streak: number;
  level: string;
}

const exercises = [
  { title: 'Writing', desc: 'Practice B1 sentence structure with daily prompts.', path: '/dutch/writing', icon: <PenTool size={22} />, color: '#FF9F1C' },
  { title: 'Speaking', desc: 'Improve fluency with local speech recognition.', path: '/dutch/speaking', icon: <Mic size={22} />, color: '#2EC4B6' },
  { title: 'Listening', desc: 'Test comprehension with Dutch B1 audio clips.', path: '/dutch/listening', icon: <Headphones size={22} />, color: '#E71D36' },
];

const USER_ID = 'local_user';

export default function DutchDashboard() {
  const [data, setData] = useState<DashboardData>({ history: [], streak: 0, level: 'B1' });

  useEffect(() => {
    getDashboardData(USER_ID)
      .then((res) => setData(res.data))
      .catch(() => {/* backend may not be running */});
  }, []);

  const writingHistory: any[] = (() => {
    try { return JSON.parse(localStorage.getItem('writing_history') || '[]'); } catch { return []; }
  })();

  return (
    <div className="page-container">
      <header style={{ marginBottom: '40px' }}>
        <h1 style={{ background: 'linear-gradient(90deg, var(--primary), var(--secondary))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', marginBottom: '8px' }}>
          Dutch B1 Progress
        </h1>
        <p style={{ color: 'var(--text-muted)' }}>Your personalised learning dashboard</p>
      </header>

      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginBottom: '40px' }}>
        {[
          { icon: <TrendingUp color="var(--primary)" size={24} />, label: 'Streak', value: `${data.streak} Days`, sub: 'Keep it up!' },
          { icon: <Award color="var(--secondary)" size={24} />, label: 'Level', value: data.level, sub: 'Target: B1 Exam' },
        ].map((s) => (
          <motion.div key={s.label} whileHover={{ y: -4 }} className="glass card">
            <div style={{ display: 'flex', gap: '14px', alignItems: 'center' }}>
              <div style={{ padding: '10px', background: 'rgba(255,255,255,0.04)', borderRadius: '12px', flexShrink: 0 }}>{s.icon}</div>
              <div>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '4px' }}>{s.label}</p>
                <p style={{ fontSize: '1.6rem', fontWeight: 800 }}>{s.value}</p>
                <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>{s.sub}</p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Exercise Cards */}
      <section style={{ marginBottom: '40px' }}>
        <h2 style={{ marginBottom: '20px' }}>Daily Exercises</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
          {exercises.map((ex) => (
            <Link key={ex.path} to={ex.path} style={{ textDecoration: 'none', color: 'inherit' }}>
              <motion.div
                whileHover={{ scale: 1.02 }}
                className="glass card"
                style={{ borderLeft: `5px solid ${ex.color}`, cursor: 'pointer' }}
              >
                <div style={{ color: ex.color, marginBottom: '12px' }}>{ex.icon}</div>
                <h3 style={{ marginBottom: '8px' }}>{ex.title}</h3>
                <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', marginBottom: '20px', lineHeight: 1.5 }}>{ex.desc}</p>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: ex.color, fontWeight: 700, fontSize: '0.88rem' }}>
                  Start Practice <ArrowRight size={16} />
                </div>
              </motion.div>
            </Link>
          ))}
        </div>
      </section>

      {/* Writing History */}
      {writingHistory.length > 0 && (
        <section>
          <h2 style={{ marginBottom: '20px' }}>Writing History</h2>
          <div className="glass" style={{ overflow: 'hidden' }}>
            {writingHistory.map((item: any, i: number) => (
              <div
                key={item.id}
                style={{
                  padding: '20px 24px',
                  borderBottom: i < writingHistory.length - 1 ? '1px solid var(--glass-border)' : 'none',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <span style={{ fontWeight: 800, color: 'var(--primary)' }}>Score: {item.score}%</span>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{item.date}</span>
                </div>
                <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', fontStyle: 'italic', marginBottom: '6px' }}>
                  <strong style={{ color: 'var(--text-light)' }}>Prompt:</strong> {item.prompt}
                </p>
                {item.improved_text && (
                  <p style={{ fontSize: '0.82rem', color: 'var(--secondary)', marginTop: '6px' }}>
                    <strong>AI:</strong> {item.improved_text}
                  </p>
                )}
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
