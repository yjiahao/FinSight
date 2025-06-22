import React, { useState } from "react";

import Message from "./Message";
import Alert from "./components/Alert";
import ListGroup from "./components/ListGroup";
import ChatInterface from "./components/ChatInterface";
import Button from "./components/Button";
import LineChart from "./components/StockGraphs";
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
    <div style={{ display: "flex", height: "100vh", width: "100vw" }}>
      {/* Left column: 70% */}
      <div
        style={{
          flex: 7,
          overflow: "auto",
          padding: "1rem",
          background: "#f5f5f5",
        }}
      >
        <LineChart />
        <div
          style={{
            flex: 1,
            overflow: "hidden",
            display: "flex",
            flexDirection: "column",
          }}
        >
          <Selector
            startDate="2010-01-01"
            endDate="2025-01-01"
            stock="AAPL"
          ></Selector>
        </div>
      </div>

      {/* Gutter */}
      <div
        style={{
          width: "2px",
          backgroundColor: "#ccc",
        }}
      />

      {/* Right column: 30% */}
      <div
        style={{
          flex: 3,
          overflow: "auto",
          padding: "1rem",
          background: "#ffffff",
        }}
      >
        <ChatInterface />
      </div>
    </div>
  );
}

export default App;
