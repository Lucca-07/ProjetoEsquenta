import "./Navbar.css"
import { FaFireAlt, FaWhatsapp } from "react-icons/fa";
import { FiLogOut } from "react-icons/fi";
import { useNavigate } from "react-router-dom";

export default function Navbar() {
    const navbarLinks = [
        { label: "Esquenta", href: "/esquenta", icon: <FaFireAlt /> },
        { label: "Conectar", href: "get/conectar", icon: <FaWhatsapp /> },
    ]
    const navigate = useNavigate();

    return (
        <nav className="navbar">
            <div className="navbar-brand">
                <div className="navbar-brand-card">
                    <img src="../../../assets/simbolo_pl.svg" alt="Simbolo do PL" width="80px" />
                    <p className="montserrat-medium">Major Vitor Santos</p>
                </div>
            </div>
            <div className="navbar-links">
                {navbarLinks.map((link, index) => (
                    <a key={index} onClick={() => { link.href[0] == "/" ? navigate(link.href) : null }} className="navbar-link montserrat-regular-italic">
                        {link.icon}
                        <span>{link.label}</span>
                    </a>
                ))}
            </div>
            <div className="navbar-footer">
                <div className="navbar-profile">
                    <div className="navbar-profile-image">
                        <p className="montserrat-medium">M</p>
                    </div>
                    <div className="navbar-profile-info">
                        <p className="montserrat-regular navbar-profile-name">Major Vitor Santos</p>
                        <p className="montserrat-light navbar-profile-email">majorvitorsantos595@gmail.com</p>
                    </div>
                </div>
                <div className="navbar-logout">
                    <a className="montserrat-regular" onClick={() => { navigate("/") }}>
                        <FiLogOut />
                        <span>Sair</span>
                    </a>
                </div>
            </div>
        </nav>
    )
}