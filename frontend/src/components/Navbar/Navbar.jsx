import "./Navbar.css";
import {
    FaChartBar,
    FaFireAlt,
    FaUserShield,
    FaWhatsapp,
} from "react-icons/fa";
import { FiLogOut } from "react-icons/fi";
import { useNavigate } from "react-router-dom";
import { clearSession, getStoredUser } from "../../api/auth";

export default function Navbar({ func }) {
    const navigate = useNavigate();
    const user = getStoredUser();
    const navbarLinks = [
        { label: "Esquenta", href: "/esquenta", icon: <FaFireAlt /> },
        { label: "Conectar", action: "connect", icon: <FaWhatsapp /> },
        ...(user?.role === "ADMIN"
            ? [
                  {
                      label: "Logs",
                      href: "/logs",
                      icon: <FaChartBar />,
                  },
                  {
                      label: "ADM",
                      href: "/admin",
                      icon: <FaUserShield />,
                  },
              ]
            : []),
    ];

    function handleLink(link) {
        if (link.action === "connect") {
            if (func?.setHidden) {
                func.setHidden(false);
            } else {
                navigate("/esquenta");
            }
            return;
        }
        navigate(link.href);
    }

    function logout() {
        clearSession();
        navigate("/", { replace: true });
    }

    const initial = user?.name?.trim()?.[0]?.toUpperCase() || "U";

    return (
        <nav className="navbar">
            <div className="navbar-brand">
                <div className="navbar-brand-card">
                    <img
                        src="../../../assets/simbolo_pl.svg"
                        alt="Símbolo do PL"
                    />
                    <p className="montserrat-medium">Painel Esquenta</p>
                </div>
            </div>
            <div className="navbar-links">
                {navbarLinks.map((link) => (
                    <a
                        key={link.label}
                        onClick={() => handleLink(link)}
                        className="navbar-link montserrat-regular"
                    >
                        {link.icon}
                        <span>{link.label}</span>
                    </a>
                ))}
            </div>
            <div className="navbar-footer">
                <div className="navbar-profile">
                    <div className="navbar-profile-image">
                        <p className="montserrat-medium">{initial}</p>
                    </div>
                    <div className="navbar-profile-info">
                        <p className="navbar-profile-name">{user?.name}</p>
                        <p className="navbar-profile-email">{user?.email}</p>
                    </div>
                </div>
                <div className="navbar-logout">
                    <a onClick={logout}>
                        <FiLogOut />
                        <span>Sair</span>
                    </a>
                </div>
            </div>
        </nav>
    );
}
