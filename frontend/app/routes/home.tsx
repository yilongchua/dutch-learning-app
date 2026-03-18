import { Link } from 'react-router';
import { Newspaper, GraduationCap, PenTool, Mic, Headphones, ArrowRight, Zap } from 'lucide-react';
import type { Route } from './+types/home';

export function meta({}: Route.MetaArgs) {
  return [
    { title: 'YL App — Dutch Learning Hub' },
    { name: 'description', content: 'Your all-in-one Dutch B1 learning platform with news feed and practice exercises.' },
  ];
}

const apps = [
  {
    id: 'thenews',
    title: 'The News',
    tagline: 'Dutch B1 News Feed',
    description: 'AI-generated Dutch news articles with bilingual breakdowns, grammar spotlights, and image carousels — tailored for B1 learners.',
    icon: <Newspaper size={28} />,
    path: '/news',
    color: '#60a5fa',
    accent: 'rgba(96,165,250,0.12)',
    border: 'rgba(96,165,250,0.3)',
    sub: ['Bilingual captions', 'Grammar spotlight', 'Image carousel'],
  },
  {
    id: 'dutch',
    title: 'Dutch B1 System',
    tagline: 'Practice Exercises',
    description: 'AI-powered writing, speaking, and listening exercises at B1 level. Get instant feedback, model answers, and track your daily streak.',
    icon: <GraduationCap size={28} />,
    path: '/dutch',
    color: '#FF9F1C',
    accent: 'rgba(255,159,28,0.12)',
    border: 'rgba(255,159,28,0.3)',
    sub: ['Writing practice', 'Speaking with ASR', 'Listening comprehension'],
  },
];

const quickLinks = [
  { title: 'News Feed', path: '/news', icon: <Newspaper size={16} />, color: '#60a5fa' },
  { title: 'Dashboard', path: '/dutch', icon: <GraduationCap size={16} />, color: '#FF9F1C' },
  { title: 'Writing', path: '/dutch/writing', icon: <PenTool size={16} />, color: '#FF9F1C' },
  { title: 'Speaking', path: '/dutch/speaking', icon: <Mic size={16} />, color: '#2EC4B6' },
  { title: 'Listening', path: '/dutch/listening', icon: <Headphones size={16} />, color: '#E71D36' },
];

export default function Home() {
  return (
    <div className="page-container">
      {/* Hero */}
      <div style={{ textAlign: 'center', paddingBottom: '60px', paddingTop: '20px' }}>
        <div style={{
          display: 'inline-flex', alignItems: 'center', gap: '8px',
          padding: '6px 16px', borderRadius: '999px',
          background: 'rgba(255,159,28,0.1)', border: '1px solid rgba(255,159,28,0.25)',
          marginBottom: '24px', fontSize: '0.82rem', fontWeight: 600, color: 'var(--primary)',
        }}>
          <Zap size={13} /> Your Dutch Learning Hub
        </div>

        <h1 style={{ marginBottom: '16px' }}>
          All Your Apps,{' '}
          <span style={{ background: 'linear-gradient(90deg, var(--primary), var(--secondary))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            One Place
          </span>
        </h1>
        <p style={{ fontSize: '1.1rem', opacity: 0.6, maxWidth: '520px', margin: '0 auto 40px', lineHeight: 1.6 }}>
          Practice Dutch at B1 level with AI-powered exercises and stay up to date with bilingual news.
        </p>

        {/* Quick Links */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', justifyContent: 'center' }}>
          {quickLinks.map((l) => (
            <Link
              key={l.path}
              to={l.path}
              style={{
                display: 'flex', alignItems: 'center', gap: '7px',
                padding: '8px 16px', borderRadius: '999px', textDecoration: 'none',
                background: 'var(--card-bg)', border: '1px solid var(--glass-border)',
                color: l.color, fontWeight: 600, fontSize: '0.85rem',
                transition: 'all 0.2s',
              }}
            >
              {l.icon} {l.title}
            </Link>
          ))}
        </div>
      </div>

      {/* App Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '24px', marginBottom: '60px' }}>
        {apps.map((app) => (
          <Link key={app.id} to={app.path} style={{ textDecoration: 'none', color: 'inherit' }}>
            <div
              className="glass"
              style={{
                padding: '32px',
                border: `1px solid ${app.border}`,
                background: app.accent,
                transition: 'transform 0.25s, box-shadow 0.25s',
                cursor: 'pointer',
                height: '100%',
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLDivElement).style.transform = 'translateY(-6px)';
                (e.currentTarget as HTMLDivElement).style.boxShadow = `0 20px 60px ${app.border}`;
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLDivElement).style.transform = 'translateY(0)';
                (e.currentTarget as HTMLDivElement).style.boxShadow = 'none';
              }}
            >
              <div style={{
                width: 56, height: 56, borderRadius: 16, marginBottom: 20,
                background: `${app.color}22`, border: `1px solid ${app.border}`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                color: app.color,
              }}>
                {app.icon}
              </div>

              <p style={{ fontSize: '0.78rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: app.color, marginBottom: '6px' }}>
                {app.tagline}
              </p>
              <h2 style={{ marginBottom: '12px', fontSize: '1.5rem' }}>{app.title}</h2>
              <p style={{ opacity: 0.65, lineHeight: 1.6, fontSize: '0.95rem', marginBottom: '24px' }}>{app.description}</p>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '28px' }}>
                {app.sub.map((s) => (
                  <div key={s} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem', opacity: 0.8 }}>
                    <div style={{ width: 6, height: 6, borderRadius: '50%', background: app.color, flexShrink: 0 }} />
                    {s}
                  </div>
                ))}
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: app.color, fontWeight: 700, fontSize: '0.9rem' }}>
                Open App <ArrowRight size={16} />
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
