import { useState, useRef } from "react";

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
  onSendAudio?: (blob: Blob, filename: string) => void;
}

function ChatBar({ messages, onSendMessage, onSendAudio }: ChatBarProps) {
  // TODO: integrate the voice recording feature here, need some way for frontend to receive the transcribed user's message from the backend (maybe yield the transcribed message)
  // const [inputValue, setInputValue] = useState("");

  const [inputValue, setInputValue] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

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

  const startRecording = async () => {
    if (!navigator.mediaDevices) {
      alert("Audio recording is not supported in this browser.");
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      audioChunksRef.current = [];
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = sendAudio;
      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error("Error accessing microphone:", err);
      alert("Could not start audio recording.");
    }
  };

  const stopRecording = () => {
    // Stop all tracks to release the microphone
    const tracks = mediaRecorderRef.current?.stream?.getTracks();
    tracks?.forEach((track) => track.stop());

    mediaRecorderRef.current?.stop();
    setIsRecording(false);
  };

  const sendAudio = () => {
    if (!onSendAudio || audioChunksRef.current.length === 0) return;

    const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" });
    onSendAudio(audioBlob, "audio.wav");
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
      {onSendAudio && (
        <button
          className={`btn ${isRecording ? "btn-danger" : "btn-primary"} ms-2`}
          onClick={isRecording ? stopRecording : startRecording}
          title={isRecording ? "Stop Recording" : "Record Audio"}
          type="button"
        >
          <i
            className={`bi ${isRecording ? "bi-stop-circle" : "bi-mic-fill"}`}
          ></i>
        </button>
      )}
    </div>
  );
}

export default ChatBar;
