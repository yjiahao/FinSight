import robotIcon from "bootstrap-icons/icons/android2.svg";
import personIcon from "bootstrap-icons/icons/person-circle.svg";
import React from "react";
import ReactMarkdown from "react-markdown";

interface ChatMessageProps {
  text: string;
  isOutgoing: boolean;
  timestamp: string;
  date: string;
}

function ChatMessage({ text, isOutgoing, timestamp, date }: ChatMessageProps) {
  return (
    <div
      className={`d-flex flex-row ${
        isOutgoing ? "justify-content-end" : "justify-content-start"
      }`}
    >
      <div>
        <p
          className={`small p-2 ms-3 mb-1 rounded-3 ${
            isOutgoing ? "text-white" : "text-dark"
          }`}
          style={{
            backgroundColor: isOutgoing ? "#495057" : "#f8f9fa",
            border: isOutgoing ? "none" : "1px solid #dee2e6",
            boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
          }}
        >
          <ReactMarkdown>{text}</ReactMarkdown>
        </p>
        <p className="small ms-3 mb-3 rounded-3 text-muted float-end">
          {`${timestamp} | ${date}`}
        </p>
      </div>
    </div>
  );
}

export default ChatMessage;
