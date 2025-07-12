import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { Fragment } from "react";
import ChatMessage from "./ChatMessage";
import ChatBar from "./ChatBar";
import ChatHeader from "./ChatHeader";

import { CHAT_POST_URL } from "../constants";
import { CHAT_HISTORY_URL } from "../constants";

import "../App.css";

interface Message {
  id: string;
  text: string;
  isOutgoing: boolean;
  timestamp: string;
  date: string;
}

function ChatInterface() {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Load chat history when component mounts
  useEffect(() => {
    loadChatHistory();
  }, []);

  const loadChatHistory = async () => {
    const token = localStorage.getItem("access_token");

    if (!token) {
      navigate("/login");
      return;
    }

    try {
      const response = await fetch(`${CHAT_POST_URL}/history`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        const data = await response.json();

        // Convert backend format to frontend Message format
        const formattedMessages: Message[] = data.messages.map(
          (msg: any, index: number) => ({
            id: `history-${index}`,
            text: msg.content,
            isOutgoing: msg.role === "user",
            timestamp: new Date().toLocaleTimeString("en-US", {
              hour: "2-digit",
              minute: "2-digit",
            }),
            date: new Date().toLocaleDateString("en-GB"),
          })
        );

        setMessages(formattedMessages);
      } else if (response.status === 401) {
        // Token expired, redirect to login
        localStorage.removeItem("access_token");
        navigate("/login");
      } else {
        console.error("Failed to load chat history");
      }
    } catch (error) {
      console.error("Error loading chat history:", error);
    } finally {
      setIsLoadingHistory(false);
    }
  };

  // Clear chat history
  const clearChatHistory = async () => {
    const token = localStorage.getItem("access_token");
    if (!token) return;

    try {
      const response = await fetch(`${CHAT_HISTORY_URL}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        setMessages([]);
      }
    } catch (error) {
      console.error("Failed to clear chat history:", error);
    }
  };

  // stream response from server
  const streamResponse = async (message: string) => {
    const controller = new AbortController();
    const token = localStorage.getItem("access_token");

    // If no token, redirect to login
    if (!token) {
      navigate("/login");
      return;
    }

    try {
      const response = await fetch(CHAT_POST_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`, // Add JWT token here
        },
        body: JSON.stringify({ content: message }),
        signal: controller.signal,
      });

      // Handle 401 Unauthorized (token expired/invalid)
      if (response.status === 401) {
        localStorage.removeItem("access_token");
        navigate("/login");
        return;
      }

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

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
    } catch (error) {
      console.error("Error in streamResponse:", error);
      // Handle error - maybe show error message to user
      const errorMessage: Message = {
        id: Date.now().toString(),
        text: "Sorry, there was an error processing your request.",
        isOutgoing: false,
        timestamp: new Date().toLocaleTimeString("en-US", {
          hour: "2-digit",
          minute: "2-digit",
        }),
        date: new Date().toLocaleDateString("en-GB"),
      };
      setMessages((prev) => [...prev, errorMessage]);
    }
  };

  // stream audio response from server
  const streamAudioResponse = async (audioBlob: Blob, filename: string) => {
    const controller = new AbortController();
    const token = localStorage.getItem("access_token");

    if (!token) {
      navigate("/login");
      return;
    }

    try {
      // Create FormData to send the audio file
      const formData = new FormData();
      formData.append("audio_file", audioBlob, filename);

      const response = await fetch(`${CHAT_POST_URL}/audio`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
        signal: controller.signal,
      });

      if (response.status === 401) {
        localStorage.removeItem("access_token");
        navigate("/login");
        return;
      }

      if (!response.ok)
        throw new Error(`HTTP error! status: ${response.status}`);
      if (!response.body) return;

      // Setup streaming
      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";

      // Track state
      let transcriptionProcessed = false;
      let botMessageId = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.trim()) continue;

          try {
            console.log("Received line:", line);
            const json = JSON.parse(line);

            // STEP 1: Handle the user's transcribed message
            if (json.role === "user" && !transcriptionProcessed) {
              transcriptionProcessed = true;
              botMessageId = Date.now().toString();

              // Add BOTH the user's message and the bot's placeholder in ONE update
              setMessages((prev) => [
                ...prev,
                {
                  id: Date.now().toString() + "-user",
                  text: json.response,
                  isOutgoing: true,
                  timestamp: new Date().toLocaleTimeString("en-US", {
                    hour: "2-digit",
                    minute: "2-digit",
                  }),
                  date: new Date().toLocaleDateString("en-GB"),
                },
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
            }
            // STEP 2: Handle the bot's response tokens
            else if (json.role === "assistant") {
              const newContent = json.response;

              // Update the bot message with each new token
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.id === botMessageId
                    ? { ...msg, text: msg.text + newContent }
                    : msg
                )
              );
            }
          } catch (err) {
            console.error("Failed to parse:", line);
          }
        }
      }
    } catch (error) {
      console.error("Error in streamAudioResponse:", error);
      // Show error message
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          text: "Sorry, there was an error processing your audio.",
          isOutgoing: false,
          timestamp: new Date().toLocaleTimeString("en-US", {
            hour: "2-digit",
            minute: "2-digit",
          }),
          date: new Date().toLocaleDateString("en-GB"),
        },
      ]);
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

  // handle sending audio messages
  const handleSendAudio = (audioBlob: Blob, filename: string) => {
    streamAudioResponse(audioBlob, filename);
  };

  // Show loading state while fetching history
  if (isLoadingHistory) {
    return (
      <div className="d-flex justify-content-center align-items-center h-100">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading chat history...</span>
        </div>
        <span className="ms-2 text-muted">Loading your conversation...</span>
      </div>
    );
  }

  return (
    <div className="d-flex flex-column h-100">
      {/* Optional: Chat Header with clear button */}
      <div className="d-flex justify-content-between align-items-center p-3 border-bottom">
        <h6 className="mb-0 text-muted">FinSight Bot</h6>
        <button
          onClick={clearChatHistory}
          className="btn btn-outline-danger btn-sm"
          title="Clear chat history"
        >
          <i className="bi bi-trash"></i> Clear
        </button>
      </div>

      {/* Messages Container */}
      <div
        className="flex-grow-1 pt-3 pe-3"
        style={{
          position: "relative",
          overflowY: "auto",
          overflowX: "hidden",
          minHeight: 0,
        }}
      >
        {/* Messages render in the scrollable container */}
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
                <h5 className="text-muted mb-2">Start a new conversation</h5>
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
      <div className="border-top">
        <ChatBar
          messages={messages}
          onSendMessage={handleSendMessage}
          onSendAudio={handleSendAudio}
        />
      </div>
    </div>
  );
}

export default ChatInterface;
