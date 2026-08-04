import Esquenta from "./pages/Esquenta/Esquenta";
import Login from "./pages/Login/Login";
import Admin from "./pages/Admin/Admin";
import LogsPage from "./pages/LogsPage/LogsPage";
import ProtectedRoute from "./components/ProtectedRoute/ProtectedRoute";

import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route
          path="/esquenta"
          element={
            <ProtectedRoute>
              <Esquenta />
            </ProtectedRoute>
          }
        />
        <Route
          path="/logs"
          element={
            <ProtectedRoute adminOnly>
              <LogsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin"
          element={
            <ProtectedRoute adminOnly>
              <Admin />
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  );
}
