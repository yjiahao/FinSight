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
    <div className="text-muted d-flex justify-content-start align-items-center pe-3 pt-3 mt-2">
      {/* <img
        src="https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-chat/ava1-bg.webp"
        alt="avatar 3"
        style={{ width: "40px", height: "40px" }}
      /> */}
      <i
        className={"bi bi-person-circle"}
        style={{
          fontSize: "1.7rem",
          paddingRight: "0.5rem",
          color: "cornflowerblue",
        }}
      ></i>
      <input
        type="text"
        className="form-control form-control-lg"
        id="messageInput"
        placeholder="Type message"
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyPress={handleKeyPress}
      />
      <a className="ms-1 text-muted" href="#!">
        <i className="fas fa-paperclip"></i>
      </a>
      <a className="ms-3 text-muted" href="#!">
        <i className="fas fa-smile"></i>
      </a>
      <a className="ms-3" href="#!" onClick={handleSendMessage}>
        <i className="fas fa-paper-plane"></i>
      </a>
    </div>
  );
}

export default ChatBar;
