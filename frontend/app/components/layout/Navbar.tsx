import { NavLink, useLocation } from 'react-router';
import {
  GraduationCap,
  Newspaper,
  PenTool,
  Mic,
  Headphones,
  ChevronDown,
  Image,
  CalendarClock,
  Images,
} from 'lucide-react';
import { useState } from 'react';

interface NavSection {
  label: string;
  icon: React.ReactNode;
  color: string;
  accent: string;
  items: { title: string; path: string; icon: React.ReactNode }[];
}

const sections: NavSection[] = [
  {
    label: 'The News',
    icon: <Newspaper size={16} />,
    color: '#60a5fa',
    accent: 'rgba(96,165,250,0.15)',
    items: [
      { title: 'News Feed', path: '/news', icon: <Newspaper size={15} /> },
    ],
  },
  {
    label: 'Dutch B1',
    icon: <GraduationCap size={16} />,
    color: 'var(--primary)',
    accent: 'rgba(255,159,28,0.15)',
    items: [
      { title: 'Writing', path: '/dutch/writing', icon: <PenTool size={15} /> },
      { title: 'Speaking', path: '/dutch/speaking', icon: <Mic size={15} /> },
      { title: 'Listening', path: '/dutch/listening', icon: <Headphones size={15} /> },
    ],
  },
  {
    label: 'Graphics',
    icon: <Image size={16} />,
    color: '#a78bfa',
    accent: 'rgba(167,139,250,0.15)',
    items: [
      { title: 'Create', path: '/graphics-generation', icon: <Image size={15} /> },
    ],
  },
  {
    label: 'Tasks',
    icon: <CalendarClock size={16} />,
    color: '#4ade80',
    accent: 'rgba(74,222,128,0.15)',
    items: [
      { title: 'Scheduler', path: '/scheduler', icon: <CalendarClock size={15} /> },
    ],
  },
  {
    label: 'Gallery',
    icon: <Images size={16} />,
    color: '#f472b6',
    accent: 'rgba(244,114,182,0.15)',
    items: [
      { title: 'Media Library', path: '/gallery', icon: <Images size={15} /> },
    ],
  },
];

export default function Navbar() {
  const location = useLocation();
  const [openSection, setOpenSection] = useState<string | null>(null);

  return (
    <nav
      className="glass-strong"
      style={{
        position: 'fixed',
        top: '16px',
        left: '50%',
        transform: 'translateX(-50%)',
        zIndex: 1000,
        width: 'calc(100% - 48px)',
        maxWidth: '1100px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '10px 20px',
        boxShadow: '0 8px 40px rgba(0,0,0,0.4)',
      }}
    >
      {/* Nav Sections */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
        {sections.map((section) => {
          const isActive = section.items.some((item) => location.pathname.startsWith(item.path));
          const isOpen = openSection === section.label;
          const isSingleItem = section.items.length === 1;

          if (isSingleItem) {
            const item = section.items[0];
            return (
              <NavLink
                key={section.label}
                to={item.path}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '7px 13px',
                  borderRadius: '10px',
                  textDecoration: 'none',
                  background: isActive ? section.accent : 'transparent',
                  color: isActive ? section.color : 'var(--text-muted)',
                  cursor: 'pointer',
                  fontWeight: 600,
                  fontSize: '0.87rem',
                  fontFamily: 'inherit',
                  transition: 'all 0.2s',
                }}
              >
                {section.icon}
                <span className="nav-label">{section.label}</span>
              </NavLink>
            );
          }

          return (
            <div
              key={section.label}
              style={{ position: 'relative' }}
              onMouseEnter={() => setOpenSection(section.label)}
              onMouseLeave={() => setOpenSection(null)}
            >
              <button
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '7px 13px',
                  borderRadius: '10px',
                  border: 'none',
                  background: isActive ? section.accent : 'transparent',
                  color: isActive ? section.color : 'var(--text-muted)',
                  cursor: 'pointer',
                  fontWeight: 600,
                  fontSize: '0.87rem',
                  fontFamily: 'inherit',
                  transition: 'all 0.2s',
                }}
              >
                {section.icon}
                <span className="nav-label">{section.label}</span>
                <ChevronDown size={12} style={{ transition: 'transform 0.2s', transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)' }} />
              </button>

              {isOpen && (
                <div
                  style={{
                    position: 'absolute',
                    top: '100%',
                    left: '50%',
                    transform: 'translateX(-50%)',
                    paddingTop: '8px',
                    zIndex: 1000,
                  }}
                >
                  <div
                    style={{
                      background: 'rgba(1,22,39,0.95)',
                      backdropFilter: 'blur(20px)',
                      border: '1px solid var(--glass-border)',
                      borderRadius: '14px',
                      padding: '8px',
                      minWidth: '160px',
                      boxShadow: '0 20px 60px rgba(0,0,0,0.5)',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '4px',
                      animation: 'fadeIn 0.15s ease',
                    }}
                  >
                    {section.items.map((item) => (
                      <NavLink
                        key={item.path}
                        to={item.path}
                        style={({ isActive }) => ({
                          display: 'flex',
                          alignItems: 'center',
                          gap: '8px',
                          padding: '9px 12px',
                          borderRadius: '9px',
                          textDecoration: 'none',
                          color: isActive ? section.color : 'var(--text-light)',
                          background: isActive ? section.accent : 'transparent',
                          fontWeight: isActive ? 700 : 500,
                          fontSize: '0.88rem',
                          transition: 'all 0.15s',
                        })}
                        end
                      >
                        {item.icon}
                        {item.title}
                      </NavLink>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      <style>{`
        @media (max-width: 600px) { .nav-label { display: none; } }
      `}</style>
    </nav>
  );
}
