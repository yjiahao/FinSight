import React, { useState } from "react";
import Message from "./Message";
import Alert from "./components/Alert";
import ListGroup from "./components/ListGroup";
import ChatInterface from "./components/ChatInterface";
import Button from "./components/Button";

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

  return <ChatInterface></ChatInterface>;
}

export default App;
