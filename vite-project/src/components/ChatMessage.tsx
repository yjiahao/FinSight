interface ChatMessageProps {
  text: string;
  isOutgoing: boolean;
  timestamp: string;
  date: string;
  avatarURL?: string;
}

function ChatMessage({
  text,
  isOutgoing,
  timestamp,
  date,
  avatarURL,
}: ChatMessageProps) {
  return (
    <div
      className={`d-flex flex-row ${
        isOutgoing ? "justify-content-end" : "justify-content-start"
      }`}
    >
      {
        <img
          src={avatarURL}
          alt="avatar"
          style={{ width: "45px", height: "45px" }}
        ></img>
      }
      <div>
        <p
          className={`small p-2 ms-3 mb-1 rounded-3 ${
            isOutgoing
              ? "bg-primary bg-gradient text-white"
              : "bg-secondary bg-gradient text-white"
          }`}
        >
          {text}
        </p>
        <p className="small ms-3 mb-3 rounded-3 text-muted float-end">
          {`${timestamp} | ${date}`}
        </p>
      </div>
    </div>
  );
}

export default ChatMessage;
