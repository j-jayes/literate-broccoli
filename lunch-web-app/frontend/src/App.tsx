import { BrowserRouter, Routes, Route } from "react-router-dom";
import AuthGate from "./components/AuthGate";
import AdminPanel from "./components/AdminPanel";
import PollPage from "./components/PollPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={
            <AuthGate>
              <AdminPanel />
            </AuthGate>
          }
        />
        <Route path="/session/:id" element={<PollPage />} />
      </Routes>
    </BrowserRouter>
  );
}
