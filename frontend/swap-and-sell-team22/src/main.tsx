import React from "react";
import ReactDOM from "react-dom/client";
import LogInOrSignUp from "./LogInOrSignUp.tsx";
import "./index.css";
import { BrowserRouter } from "react-router-dom";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <LogInOrSignUp />
    </BrowserRouter>
  </React.StrictMode>
);