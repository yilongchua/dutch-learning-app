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
    <div className="page-container graphics-page-container">
      <div className="graphics-page-header">
        <h1 style={{ marginBottom: '8px', fontSize: '2rem' }}>
          Graphics{' '}
          <span style={{ background: 'linear-gradient(90deg, #a78bfa, #c084fc)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Generation
          </span>
        </h1>
      </div>
      <div className="graphics-page-shell">
        <ChatInterface />
      </div>
    </div>
  );
}
