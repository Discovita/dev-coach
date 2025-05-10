import { DOMImplementation, XMLSerializer, DOMParser } from "xmldom";
import { CoachState } from "@/types/coachState";
import { Message } from "@/types/message";

const sanitizeContent = (content: string): string => {
  const parser = new DOMParser();
  const doc = parser.parseFromString("<root></root>", "text/xml");
  const textNode = doc.createTextNode(content);
  return textNode.nodeValue || "";
};

// Helper function to format XML with proper indentation
const formatXml = (xml: string): string => {
  let formatted = "";
  let indent = "";
  const tab = "  "; // 2 spaces for indentation

  xml.split(/>\s*</).forEach((node) => {
    if (node.match(/^\/\w/)) {
      // Closing tag
      indent = indent.substring(tab.length);
    }

    formatted += indent + "<" + node + ">\n";

    if (node.match(/^<?\w[^>]*[^/]$/) && !node.startsWith("!--")) {
      // Opening tag and not self-closing
      indent += tab;
    }
  });

  // Replace XML declaration with properly formatted one
  return (
    '<?xml version="1.0" encoding="UTF-8"?>\n' +
    formatted.substring(formatted.indexOf("\n") + 1)
  );
};

export const convertToXml = (
  messages: Message[],
  userId: string,
  coachState: CoachState
): string => {
  const doc = new DOMImplementation().createDocument(
    null,
    "conversation",
    null
  );
  const root = doc.documentElement;

  // Create metadata
  const metadata = doc.createElement("metadata");
  root.appendChild(metadata);

  const userIdElement = doc.createElement("userId");
  userIdElement.textContent = userId;
  metadata.appendChild(userIdElement);

  const timestamp = doc.createElement("timestamp");
  timestamp.textContent = new Date().toISOString();
  metadata.appendChild(timestamp);

  const messageCount = doc.createElement("messageCount");
  messageCount.textContent = messages.length.toString();
  metadata.appendChild(messageCount);

  // Create messages
  const messagesElement = doc.createElement("messages");
  root.appendChild(messagesElement);

  messages.forEach((msg) => {
    const messageElement = doc.createElement("message");

    const roleElement = doc.createElement("role");
    roleElement.textContent = msg.role;
    messageElement.appendChild(roleElement);

    const contentElement = doc.createElement("content");
    const sanitizedContent = sanitizeContent(msg.content);
    contentElement.appendChild(doc.createCDATASection(sanitizedContent));
    messageElement.appendChild(contentElement);

    messagesElement.appendChild(messageElement);
  });

  // Add coach state
  const coachStateElement = doc.createElement("coach_state");
  root.appendChild(coachStateElement);

  // Add each property of the coach state
  Object.entries(coachState).forEach(([key, value]) => {
    const stateElement = doc.createElement(key);

    if (value === null) {
      stateElement.textContent = "null";
    } else if (typeof value === "object") {
      // Convert objects to JSON strings and wrap in CDATA to preserve formatting
      const jsonString = JSON.stringify(value, null, 2);
      stateElement.appendChild(doc.createCDATASection(jsonString));
    } else {
      stateElement.textContent = String(value);
    }

    coachStateElement.appendChild(stateElement);
  });

  // Get the XML string and format it with proper indentation
  const xmlString = new XMLSerializer().serializeToString(doc);
  return formatXml(xmlString);
};

export const downloadXml = (xmlContent: string) => {
  const blob = new Blob([xmlContent], { type: "application/xml" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `conversation-${new Date().toISOString()}.xml`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};
