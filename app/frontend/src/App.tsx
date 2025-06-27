import React, { useState } from "react";

import Message from "./Message";
import Alert from "./components/Alert";
import ListGroup from "./components/ListGroup";
import ChatInterface from "./components/ChatInterface";
import Button from "./components/Button";
import LineChart from "./components/LineChart";
import Selector from "./components/Selector";

import Split from "react-split";

function App() {
  const [alertVisible, setAlertVisibility] = useState(false);
  // let items = ["New York", "San Francisco", "Tokyo", "London", "Paris"];

  // const handleSelectItem = (item: string) => {
  //   console.log(item);
  // };

  // return (
  //   <div>
  //     <ListGroup
  //       items={items}
  //       heading={"Cities"}
  //       onSelectItem={handleSelectItem}
  //     ></ListGroup>
  //   </div>
  // );

  // return (
  //   <div>
  //     <Alert>
  //       <h1>
  //         Hello <span>world</span>
  //       </h1>
  //     </Alert>
  //   </div>
  // );

  // return <Button onClick={() => console.log("Clicked")}>Click Me</Button>;
  // return (
  //   <div>
  //     {alertVisible && (
  //       <Alert onClick={() => setAlertVisibility(false)}>
  //         <strong>Holy guacamole!</strong> You should check in on some of those
  //         fields below.
  //       </Alert>
  //     )}
  //     <Button onClick={() => setAlertVisibility(true)}>Click Me</Button>
  //   </div>
  // );
  return (
    <div className="container-fluid p-0">
      <div className="row g-0 min-vh-100">
        {/* Chart and Selector - Full width on mobile, 70% on large screens */}
        <div className="col-12 col-lg-8 order-1 order-lg-1">
          <div
            className="d-flex flex-column h-100"
            style={{ background: "#f5f5f5" }}
          >
            {/* Chart */}
            <div className="flex-grow-1 p-3">
              <div style={{ height: "100%" }}>
                <LineChart />
              </div>
            </div>

            {/* Selector */}
            <div className="p-3">
              <Selector
                startDate="2010-01-01"
                endDate="2025-01-01"
                stock="AAPL"
              />
            </div>
          </div>
        </div>

        {/* Chat Interface - Full width on mobile (goes below), 30% on large screens */}
        <div className="col-12 col-lg-4 order-2 order-lg-2">
          <div
            className="h-100 p-3"
            style={{
              background: "#ffffff",
              borderLeft: "2px solid #ccc",
              minHeight: "50vh", // Ensure minimum height on mobile
            }}
          >
            <ChatInterface />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
