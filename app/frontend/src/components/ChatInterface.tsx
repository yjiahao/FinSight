import React, { useState, useEffect, useRef } from "react";
import { Fragment } from "react";
import ChatMessage from "./ChatMessage";
import ChatBar from "./ChatBar";
import ChatHeader from "./ChatHeader";

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
    {
      id: "1",
      text: "Hello! How can I help you today?",
      isOutgoing: false,
      timestamp: "12:00 PM",
      date: "15/06/2025",
    },
    {
      id: "2",
      text: "I need help with my investment portfolio",
      isOutgoing: true,
      timestamp: "12:01 PM",
      date: "15/06/2025",
    },
  ]);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

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
    }
  };

  return (
    <div>
      <ChatHeader></ChatHeader>
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
        {messages.map((message) => (
          <ChatMessage
            key={message.id}
            text={message.text}
            isOutgoing={message.isOutgoing}
            timestamp={message.timestamp}
            date={message.date}
          />
        ))}
        {/* Auto-scroll target */}
        <div ref={messagesEndRef} />
      </div>

      {/* ChatBar Component */}
      <ChatBar messages={messages} onSendMessage={handleSendMessage} />
    </div>
  );
}

export default ChatInterface;
