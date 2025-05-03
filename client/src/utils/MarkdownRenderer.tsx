import ReactMarkdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';

/**
 * MarkdownRenderer
 * Renders markdown content using react-markdown with raw HTML support.
 *
 * @param content - The markdown string to render
 * @param className - Optional className to apply to a wrapping div (for styling/wrapping)
 *
 * Used in: coach-state-visualizer/utils/renderUtils.tsx (for prompt rendering)
 */
interface MarkdownRendererProps {
  content: string; // Markdown string to render
  className?: string; // Optional className for styling/wrapping
}

const MarkdownRenderer = ({ content, className }: MarkdownRendererProps) => {
  // Wrap ReactMarkdown in a div to apply className, since ReactMarkdown does not support className prop in v8+
  return (
    <div className={className}>
      <ReactMarkdown rehypePlugins={[rehypeRaw]}>{content}</ReactMarkdown>
    </div>
  );
};

export default MarkdownRenderer;
