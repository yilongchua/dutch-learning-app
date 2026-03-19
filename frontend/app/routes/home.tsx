import { Link } from 'react-router';
import { Newspaper, GraduationCap, PenTool, Mic, Headphones, ArrowRight, Zap, Image } from 'lucide-react';
import type { Route } from './+types/home';

export function meta({}: Route.MetaArgs) {
  return [
    { title: 'YL App — Dutch Learning Hub' },
    { name: 'description', content: 'Your all-in-one Dutch B1 learning platform with news feed and practice exercises.' },
  ];
}

const quickLinks = [
  { title: 'News Feed', path: '/news', icon: <Newspaper size={18} />, color: '#60a5fa' },
  { title: 'Writing', path: '/dutch/writing', icon: <PenTool size={18} />, color: '#FF9F1C' },
  { title: 'Speaking', path: '/dutch/speaking', icon: <Mic size={18} />, color: '#2EC4B6' },
  { title: 'Listening', path: '/dutch/listening', icon: <Headphones size={18} />, color: '#E71D36' },
  { title: 'Graphics', path: '/graphics-generation', icon: <Image size={18} />, color: '#a78bfa' },
];

export default function Home() {
  return (
    <div className="page-container">
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '60vh', padding: '20px' }}>
        <h1 style={{ marginBottom: '16px' }}>
          <span style={{ background: 'linear-gradient(90deg, var(--primary), var(--secondary))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            GRANDPA SHIBBS!
          </span>
        </h1>
        <p style={{ fontSize: '1.1rem', opacity: 0.7, maxWidth: '520px', margin: '0 auto 40px', lineHeight: 1.6, textAlign: 'center' }}>
          Select Learning
        </p>

        {/* Vital Links */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', width: '100%', maxWidth: '400px' }}>
          {quickLinks.map((l) => (
            <Link
              key={l.path}
              to={l.path}
              className="glass"
              style={{
                display: 'flex', alignItems: 'center', gap: '14px',
                padding: '20px 24px', borderRadius: '16px', textDecoration: 'none',
                border: l.path === '/graphics-generation' ? '1px solid #a78bfa55' : '1px solid var(--glass-border)',
                color: l.color, fontWeight: 600, fontSize: '1.1rem',
                transition: 'all 0.25s',
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLAnchorElement).style.transform = 'translateY(-3px)';
                (e.currentTarget as HTMLAnchorElement).style.boxShadow = `0 10px 30px ${l.color}22`;
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLAnchorElement).style.transform = 'translateY(0)';
                (e.currentTarget as HTMLAnchorElement).style.boxShadow = 'none';
              }}
            >
              <div style={{ padding: '10px', borderRadius: '12px', background: `${l.color}15` }}>
                {l.icon}
              </div>
              <span style={{ flex: 1, color: 'var(--text-light)' }}>{l.title}</span>
              <ArrowRight size={18} style={{ opacity: 0.5 }} />
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
