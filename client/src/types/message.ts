/**
 * A single message in the conversation history.
 */
export interface Message {
  role: string;
  content: string;
  timestamp: string;
}
