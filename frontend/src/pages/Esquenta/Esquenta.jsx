import "./Esquenta.css";
import Navbar from "../../components/Navbar/Navbar";
import CardInfo from "../../components/CardInfo/CardInfo";
import { FaFireAlt, FaMobileAlt, FaCheck } from "react-icons/fa";
import { AiOutlineClose } from "react-icons/ai";
import { useState } from "react";

export default function Esquenta() {
    const [valor, setValor] = useState(40);

    // Calcula a porcentagem do preenchimento dinamicamente
    const preenchimento = {
        background: `linear-gradient(to right, #4CAF50 0%, #4CAF50 ${valor}%, #ddd ${valor}%, #ddd 100%)`
    };
    return (
        <div className="esquenta-container">
            <nav className="navbar">
                <Navbar />
            </nav>
            <div className="esquenta-content">
                <div className="esquenta-mini-cards">
                    <CardInfo icon={<FaMobileAlt />} text="27 Conectados" ></CardInfo>
                    <CardInfo icon={<FaFireAlt />} text="12 Esquentando" ></CardInfo>
                    <CardInfo icon={<FaCheck />} text="27 Concluídos" ></CardInfo >
                    <CardInfo icon={<AiOutlineClose />} text="13 Não concluídos" ></CardInfo>
                </div>
                <div className="esquenta-medium-card">
                    <div className="esquenta-medium-left-card">
                        <p className="esquenta-medium-card-title montserrat-medium">Progresso</p>
                        <div className="esquenta-medium-left-card-content">
                            <input onChange={(e) => setValor(e.target.value)} style={preenchimento} type="range" min="0" max="100" value={valor} className="esquenta-slider" />
                            <div className="esquenta-slider-info-container">
                                <span className="esquenta-slider-info">{valor}% Completo</span>
                                <span className="esquenta-slider-info">2 Horas restantes</span>
                            </div>
                        </div>
                    </div>
                    <div className="esquenta-medium-right-card">
                        <p className="esquenta-medium-card-title">Titulo</p>
                        <div className="esquenta-medium-card-content">
                            <p className="esquenta-status-text">A decidir ainda</p>
                        </div>
                    </div>
                </div>
                <div className="esquenta-bottom-card">
                    <p className="esquenta-bottom-card-title">Informações</p>
                </div>
            </div>
        </div>
    );
}