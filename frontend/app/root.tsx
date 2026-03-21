import {
  isRouteErrorResponse,
  Links,
  Meta,
  Outlet,
  Scripts,
  ScrollRestoration,
} from 'react-router';

import type { Route } from './+types/root';
import Navbar from '~/components/layout/Navbar';
import { DutchSessionProvider } from '~/context/dutchSession';
import './app.css';

export const links: Route.LinksFunction = () => [
  { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
  { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossOrigin: 'anonymous' },
  { rel: 'icon', href: '/favicon.ico' },
  { rel: 'apple-touch-icon', href: '/apple-touch-icon.png' },
  { rel: 'apple-touch-icon-precomposed', href: '/apple-touch-icon-precomposed.png' },
  {
    rel: 'stylesheet',
    href: 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap',
  },
];

export function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <Meta />
        <Links />
      </head>
      <body>
        <DutchSessionProvider>
          <Navbar />
          {children}
        </DutchSessionProvider>
        <ScrollRestoration />
        <Scripts />
      </body>
    </html>
  );
}

export default function App() {
  return <Outlet />;
}

export function ErrorBoundary({ error }: Route.ErrorBoundaryProps) {
  let message = 'Oops!';
  let details = 'An unexpected error occurred.';
  let stack: string | undefined;

  if (isRouteErrorResponse(error)) {
    message = error.status === 404 ? '404' : 'Error';
    details =
      error.status === 404
        ? 'The requested page could not be found.'
        : error.statusText || details;
  } else if (import.meta.env.DEV && error instanceof Error) {
    details = error.message;
    stack = error.stack;
  }

  return (
    <main className="page-container" style={{ textAlign: 'center', paddingTop: '140px' }}>
      <h1 style={{ color: 'var(--error)', marginBottom: '16px' }}>{message}</h1>
      <p style={{ opacity: 0.7, marginBottom: '24px' }}>{details}</p>
      {stack && (
        <pre style={{
          background: 'var(--card-bg)',
          border: '1px solid var(--glass-border)',
          borderRadius: '12px',
          padding: '20px',
          overflow: 'auto',
          textAlign: 'left',
          fontSize: '0.8rem',
          opacity: 0.7,
        }}>
          <code>{stack}</code>
        </pre>
      )}
    </main>
  );
}
