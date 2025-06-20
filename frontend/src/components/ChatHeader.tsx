function ChatHeader() {
  return (
    <div
      className="container justify-content-center"
      style={{
        textAlign: "center",
        padding: "1rem 0",
        fontWeight: "600",
        fontSize: "1.8rem",
        color: "#333",
        boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
        backgroundColor: "#f9faff",
        userSelect: "none",
      }}
    >
      <h3
        style={{
          margin: 0,
          fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
        }}
      >
        Investment Analysis Bot
      </h3>
    </div>
  );
}

export default ChatHeader;
