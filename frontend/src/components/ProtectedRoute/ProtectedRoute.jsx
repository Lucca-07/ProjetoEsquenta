import { Navigate } from "react-router-dom";
import { getStoredUser } from "../../api/auth";

export default function ProtectedRoute({ children, adminOnly = false }) {
    const token = localStorage.getItem("auth_token");
    const user = getStoredUser();

    if (!token || !user) {
        return <Navigate to="/" replace />;
    }

    if (adminOnly && user.role !== "ADMIN") {
        return <Navigate to="/esquenta" replace />;
    }

    return children;
}
