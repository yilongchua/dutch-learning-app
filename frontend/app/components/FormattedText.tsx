import React from 'react';

interface FormattedTextProps {
  text: string;
}

export function FormattedText({ text }: FormattedTextProps) {
  if (!text) return null;

  // Regex to match anything inside <tag>...</tag>
  // e.g. <t1>omdat</t1>, <v1>ben</v1>, etc.
  const regex = /<([a-z0-9]+)>(.*?)<\/\1>/g;
  const parts: React.ReactNode[] = [];
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = regex.exec(text)) !== null) {
    // Add text before the match
    if (match.index > lastIndex) {
      parts.push(<React.Fragment key={`text-${lastIndex}`}>{text.substring(lastIndex, match.index)}</React.Fragment>);
    }

    const tag = match[1];
    const content = match[2];

    let style: React.CSSProperties = {
      fontWeight: 600,
      padding: '2px 6px',
      borderRadius: '6px',
      margin: '0 2px',
      display: 'inline-block',
      lineHeight: 1.2,
    };

    let title = '';

    if (tag.startsWith('t')) {
      // Trigger / Conjunction
      style = { ...style, color: '#f59e0b', background: 'rgba(245,158,11,0.15)', border: '1px solid rgba(245,158,11,0.2)' };
      title = 'Trigger / Conjunction';
    } else if (tag.startsWith('v')) {
      // Verb
      style = { ...style, color: '#3b82f6', background: 'rgba(59,130,246,0.15)', border: '1px solid rgba(59,130,246,0.2)' };
      title = 'Verb';
    } else if (tag.startsWith('s')) {
      // Subject
      style = { ...style, color: '#10b981', background: 'rgba(16,185,129,0.15)', border: '1px solid rgba(16,185,129,0.2)' };
      title = 'Subject';
    } else {
      // Default / Unknown tags
      style = { ...style, color: '#a855f7', background: 'rgba(168,85,247,0.15)', border: '1px solid rgba(168,85,247,0.2)' };
      title = tag;
    }

    parts.push(
      <span key={`tag-${match.index}`} style={style} title={title}>
        {content}
      </span>
    );

    lastIndex = regex.lastIndex;
  }

  // Add remaining text
  if (lastIndex < text.length) {
    parts.push(<React.Fragment key={`text-${lastIndex}`}>{text.substring(lastIndex)}</React.Fragment>);
  }

  return <>{parts}</>;
}
