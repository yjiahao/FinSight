import React, { useState, useEffect, useRef } from "react";
import { Fragment } from "react";
import ChatMessage from "./ChatMessage";
import ChatBar from "./ChatBar";
import ChatHeader from "./ChatHeader";

import { CHAT_URL } from "../constants";

import "../App.css";

interface Message {
  id: string;
  text: string;
  isOutgoing: boolean;
  timestamp: string;
  date: string;
}

function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    // {
    //   id: "1",
    //   text: "Hello! How can I help you today?",
    //   isOutgoing: false,
    //   timestamp: "12:00 PM",
    //   date: "15/06/2025",
    // },
    // {
    //   id: "2",
    //   text: "I need help with my investment portfolio",
    //   isOutgoing: true,
    //   timestamp: "12:01 PM",
    //   date: "15/06/2025",
    // },
  ]);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // stream response from server
  const streamResponse = async (message: string) => {
    const controller = new AbortController();

    const response = await fetch(CHAT_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content: message }),
      signal: controller.signal,
    });

    if (!response.body) return;

    // Step 1: Add placeholder response message (empty for now)
    const botMessageId = Date.now().toString();

    setMessages((prev) => [
      ...prev,
      {
        id: botMessageId,
        text: "",
        isOutgoing: false,
        timestamp: new Date().toLocaleTimeString("en-US", {
          hour: "2-digit",
          minute: "2-digit",
        }),
        date: new Date().toLocaleDateString("en-GB"),
      },
    ]);

    // Step 2: Stream and incrementally update that message
    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        if (line.trim()) {
          try {
            const json = JSON.parse(line);
            const newContent = json.response;

            // Step 3: Update the message with matching ID
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === botMessageId
                  ? { ...msg, text: msg.text + newContent }
                  : msg
              )
            );
          } catch (err) {
            console.error("Failed to parse:", line);
          }
        }
      }
    }
  };

  // Handle new messages from ChatBar
  const handleSendMessage = (text: string) => {
    if (text.trim()) {
      const newMessage: Message = {
        id: Date.now().toString(),
        text: text,
        isOutgoing: true,
        timestamp: new Date().toLocaleTimeString("en-US", {
          hour: "2-digit",
          minute: "2-digit",
        }),
        date: new Date().toLocaleDateString("en-GB"),
      };

      setMessages((prev) => prev.concat(newMessage));

      streamResponse(text);
    }
  };

  return (
    <div>
      {/* <ChatHeader></ChatHeader> */}
      {/* Messages Container */}
      <div
        className="pt-3 pe-3"
        style={{
          position: "relative",
          height: "80vh",
          overflowY: "auto",
          overflowX: "hidden",
        }}
      >
        {/* Messages render in the scrollable container */}
        {/* function to render messages. if no messages, then render animation to encourage user to type something */}
        {(() => {
          if (messages.length === 0) {
            return (
              <div className="d-flex flex-column justify-content-center align-items-center h-100 text-center">
                <div className="mb-4">
                  <i
                    className="bi bi-chat-dots"
                    style={{ fontSize: "3rem", color: "#6c757d" }}
                  ></i>
                </div>
                <h5 className="text-muted mb-2">No messages yet</h5>
                <p className="text-muted small">
                  <span className="typing-effect">
                    Ask me about stocks, market trends, or investment
                    strategies!
                  </span>
                </p>
              </div>
            );
          } else {
            return messages.map((message) => (
              <ChatMessage
                key={message.id}
                text={message.text}
                isOutgoing={message.isOutgoing}
                timestamp={message.timestamp}
                date={message.date}
              />
            ));
          }
        })()}
        {/* Auto-scroll target */}
        <div ref={messagesEndRef} />
      </div>

      {/* ChatBar Component */}
      <ChatBar messages={messages} onSendMessage={handleSendMessage} />
    </div>
  );
}

export default ChatInterface;
