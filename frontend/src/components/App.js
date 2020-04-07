import React, { Component } from "react";
import { render } from "react-dom";

class App extends Component {
  render() {
    return(
      <p>Test Test Test 2</p>
    );
  }
}

export default App;

const container = document.getElementById("app");
render(<App />, container);
