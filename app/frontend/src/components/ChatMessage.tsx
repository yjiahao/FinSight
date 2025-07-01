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
      <i
        className={`bi ${isOutgoing ? "bi-person-circle" : "bi-android2"}`}
        style={{
          fontSize: "1.7rem",
          color: isOutgoing ? "cornflowerblue" : "#6c757d",
        }}
      ></i>
      <div>
        <p
          // TODO: is there anything we can do to make it look nicer? Like the colour of the chat boxes from the bot and from the user?
          className={`small p-2 ms-3 mb-1 rounded-3 ${
            isOutgoing
              ? "bg-gradient text-white"
              : "bg-secondary bg-gradient text-white"
          }`}
          style={{
            backgroundColor: "cornflowerblue",
          }}
        >
          {/* <pre style={{ whiteSpace: "pre-wrap" }}>{text}</pre> */}
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
