import ReactMarkdown from "react-markdown";
import rehypeRaw from "rehype-raw";
import rehypeSanitize from "rehype-sanitize";

/**
 * MarkdownRenderer
 * Renders markdown content using react-markdown with raw HTML support.
 * HTML is sanitized via rehype-sanitize to prevent XSS from untrusted content.
 *
 * @param content - The markdown string to render
 * @param className - Optional className to apply to a wrapping div (for styling/wrapping)
 *
 * Used in: coach-state-visualizer/utils/renderUtils.tsx (for prompt rendering)
 */
interface MarkdownRendererProps {
	content: string;
	className?: string;
}

const MarkdownRenderer = ({ content, className }: MarkdownRendererProps) => {
	return (
		<div className={className}>
			<ReactMarkdown rehypePlugins={[rehypeRaw, rehypeSanitize]}>
				{content}
			</ReactMarkdown>
		</div>
	);
};

export default MarkdownRenderer;
