// Markdown renderer for assistant chat messages
// Uses react-markdown + remark-gfm for GitHub Flavored Markdown support

import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { Components } from 'react-markdown';

interface MarkdownMessageProps {
  content: string;
}

const components: Components = {
  h1: ({ children }) => (
    <h1 className="font-semibold text-base mb-1">{children}</h1>
  ),
  h2: ({ children }) => (
    <h2 className="font-semibold text-base mb-1">{children}</h2>
  ),
  h3: ({ children }) => (
    <h3 className="font-semibold text-sm mb-1">{children}</h3>
  ),
  strong: ({ children }) => (
    <strong className="font-semibold">{children}</strong>
  ),
  em: ({ children }) => <em className="italic">{children}</em>,
  code: ({ children, className }) => {
    const isBlock = className?.startsWith('language-');
    if (isBlock) {
      return (
        <code className="block font-mono text-xs text-gray-100">{children}</code>
      );
    }
    return (
      <code className="font-mono bg-gray-100 dark:bg-gray-800 rounded px-1 text-xs">
        {children}
      </code>
    );
  },
  pre: ({ children }) => (
    <pre className="bg-gray-900 text-gray-100 rounded-lg p-3 overflow-x-auto text-xs font-mono my-2">
      {children}
    </pre>
  ),
  ul: ({ children }) => (
    <ul className="list-disc pl-4 space-y-0.5 my-1">{children}</ul>
  ),
  ol: ({ children }) => (
    <ol className="list-decimal pl-4 space-y-0.5 my-1">{children}</ol>
  ),
  li: ({ children }) => <li className="text-sm">{children}</li>,
  p: ({ children }) => <p className="mb-1 last:mb-0 text-sm">{children}</p>,
  a: ({ href, children }) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="text-blue-600 underline hover:text-blue-800"
    >
      {children}
    </a>
  ),
  blockquote: ({ children }) => (
    <blockquote className="border-l-2 border-gray-400 pl-3 italic text-gray-700 my-1">
      {children}
    </blockquote>
  ),
  hr: () => <hr className="my-2 border-gray-300" />,
};

export default function MarkdownMessage({ content }: MarkdownMessageProps) {
  return (
    <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
      {content}
    </ReactMarkdown>
  );
}
