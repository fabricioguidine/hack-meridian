import { Buffer } from "buffer";
// @stellar/stellar-sdk expects a global Buffer in the browser.
(globalThis as unknown as { Buffer: typeof Buffer }).Buffer =
  (globalThis as unknown as { Buffer?: typeof Buffer }).Buffer ?? Buffer;

import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";

import App from "./App";
import "../stellar_ds_autogen/stellar.css";
import "./theme.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
);
