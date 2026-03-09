import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { FluentProvider, teamsLightTheme } from "@fluentui/react-components";
import App from "./App";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <FluentProvider theme={teamsLightTheme}>
      <App />
    </FluentProvider>
  </StrictMode>
);
