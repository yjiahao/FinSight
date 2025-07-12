import { useState } from "react";

interface Message {
  id: string;
  text: string;
  isOutgoing: boolean;
  timestamp: string;
  date: string;
}

interface ChatBarProps {
  messages: Message[];
  onSendMessage: (text: string) => void;
}

function ChatBar({ messages, onSendMessage }: ChatBarProps) {
  // TODO: integrate the voice recording feature here, need some way for frontend to receive the transcribed user's message from the backend (maybe yield the transcribed message)
  const [inputValue, setInputValue] = useState("");

  const handleSendMessage = () => {
    if (inputValue.trim()) {
      onSendMessage(inputValue);
      setInputValue("");
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleSendMessage();
    }
  };

  return (
    <div className="text-muted d-flex justify-content-start align-items-center pt-3 mt-2">
      <input
        type="text"
        className="form-control form-control-lg"
        placeholder="Type message"
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyDown={handleKeyPress}
      />
    </div>
  );
}

export default ChatBar;
