import Esquenta from "./pages/Esquenta/Esquenta";
import Login from "./pages/Login/Login";

import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/esquenta" element={<Esquenta />} />
      </Routes>
    </Router>
  );
}