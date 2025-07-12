import React, { useState } from "react";

import ChatInterface from "./ChatInterface";
import LineChart from "./LineChart";
import Selector from "./Selector";
import NavBar from "./Navbar";

function ChatPage() {
  const [alertVisible, setAlertVisibility] = useState(false);

  return (
    <div className="container-fluid p-0" style={{ height: "100vh" }}>
      <NavBar />

      {/* Main content - subtract navbar height */}
      <div className="row g-0" style={{ height: "calc(100vh - 80px)" }}>
        {/* Chart and Selector - Full width on mobile, 70% on large screens */}
        <div className="col-12 col-lg-8 order-1 order-lg-1">
          <div
            className="d-flex flex-column h-100"
            style={{ background: "#f5f5f5" }}
          >
            {/* Chart - 80% of remaining space */}
            <div className="p-3" style={{ height: "80%" }}>
              <div style={{ height: "100%", width: "100%" }}>
                <LineChart />
              </div>
            </div>

            {/* Selector - 20% of remaining space */}
            <div className="p-0 mt-3" style={{ height: "20%" }}>
              <Selector
                startDate="2010-01-01"
                endDate="2025-01-01"
                stock="AAPL"
              />
            </div>
          </div>
        </div>

        {/* Chat Interface column */}
        <div
          className="col-12 col-lg-4 order-2 order-lg-2 d-flex flex-column"
          style={{
            height: "calc(100vh - 80px)" /* Subtract navbar height */,
            maxHeight: "calc(100vh - 80px)",
            overflow: "hidden" /* Important! */,
          }}
        >
          <div
            className="h-100 p-3 d-flex flex-column"
            style={{
              background: "#ffffff",
              borderLeft: "2px solid #ccc",
            }}
          >
            <ChatInterface />
          </div>
        </div>
      </div>
    </div>
  );
}

export default ChatPage;
