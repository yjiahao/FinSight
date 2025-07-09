import React from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import LoginPage from "./components/LoginPage";
import RegisterPage from "./components/RegisterPage"; // Add this import
import ChatPage from "./components/ChatPage";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />{" "}
        {/* Add this route */}
        <Route
          path="/chat"
          element={
            !!localStorage.getItem("access_token") ? (
              <ChatPage />
            ) : (
              <Navigate to="/login" />
            )
          }
        />
        <Route
          path="/"
          element={
            <Navigate
              to={!!localStorage.getItem("access_token") ? "/chat" : "/login"}
            />
          }
        />
      </Routes>
    </Router>
  );
}

export default App;
