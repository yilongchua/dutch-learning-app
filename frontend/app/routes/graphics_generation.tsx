import type { Route } from './+types/graphics_generation';
import ChatInterface from '~/components/graphics_generation/ChatInterface';

export function meta({}: Route.MetaArgs) {
  return [
    { title: 'Graphics Generation' },
    { name: 'description', content: 'Chat interface for creating AI images and videos.' },
  ];
}

export default function GraphicsPage() {
  return (
    <div className="page-container" style={{ padding: '0 20px', height: 'calc(100vh - 120px)', display: 'flex', flexDirection: 'column' }}>
      <div style={{ paddingTop: '80px', paddingBottom: '20px', textAlign: 'center', flexShrink: 0 }}>
        <h1 style={{ marginBottom: '8px', fontSize: '2rem' }}>
          Graphics{' '}
          <span style={{ background: 'linear-gradient(90deg, #a78bfa, #c084fc)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Generation
          </span>
        </h1>
      </div>
      <div style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column', background: 'var(--card-bg)', border: '1px solid var(--glass-border)', borderRadius: '24px', boxShadow: '0 10px 40px rgba(0,0,0,0.1)' }}>
        <ChatInterface />
      </div>
    </div>
  );
}
