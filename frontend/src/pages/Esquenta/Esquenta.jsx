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
        background: `linear-gradient(to right, #3e613f 0%, #4CAF50 ${valor}%, #ddd ${valor}%, #ddd 100%)`
    };
    const MOCK_NUMEROS = [
        { id: 1, numero: "11 9932821313", responsavel: "João", progresso: 50, tempoRestante: "2 horas", status: "Em andamento" },
        { id: 2, numero: "11 9932821313", responsavel: "Maria", progresso: 100, tempoRestante: "0 horas", status: "Concluído" },
        { id: 3, numero: "11 9932821313", responsavel: "Pedro", progresso: 75, tempoRestante: "1 hora", status: "Em andamento" },
        { id: 4, numero: "11 9932821313", responsavel: "Ana", progresso: 25, tempoRestante: "3 horas", status: "Em andamento" },
        { id: 5, numero: "11 9932821313", responsavel: "Ana", progresso: 25, tempoRestante: "3 horas", status: "Em andamento" },
        { id: 6, numero: "11 9932821313", responsavel: "Ana", progresso: 25, tempoRestante: "3 horas", status: "Em andamento" },
        { id: 7, numero: "11 9932821313", responsavel: "Ana", progresso: 25, tempoRestante: "3 horas", status: "Em andamento" },
        { id: 8, numero: "11 9932821313", responsavel: "Ana", progresso: 25, tempoRestante: "3 horas", status: "Em andamento" },
        { id: 9, numero: "11 9932821313", responsavel: "Ana", progresso: 25, tempoRestante: "3 horas", status: "Em andamento" },
    ]
    return (
        <div className="esquenta-container">
            <nav className="navbar">
                <Navbar />
            </nav>
            <div className="esquenta-content">
                <div className="esquenta-card">
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
                            <p className="esquenta-medium-card-title montserrat-medium">Título</p>
                            <div className="esquenta-medium-card-content">
                                <p className="esquenta-status-text">A decidir ainda</p>
                            </div>
                        </div>
                    </div>
                    <div className="esquenta-bottom-card">
                        <div className="esquenta-bottom-card-header">
                            <p className="esquenta-bottom-card-title montserrat-medium">Números</p>
                            <div className="esquenta-bottom-card-buttons">
                                <button className="esquenta-bottom-card-button parar montserrat-semibold" disabled>Parar Esquenta</button>
                                <button className="esquenta-bottom-card-button iniciar montserrat-semibold">Iniciar Esquenta</button>
                            </div>
                        </div>
                        <div className="esquenta-bottom-card-table-div">
                            <table className="esquenta-bottom-card-table">
                                <thead>
                                    <tr className="esquenta-bottom-card-table-header">
                                        <th className="esquenta-bottom-card-table-header-checkbox">Selecionar</th>
                                        <th className="esquenta-bottom-card-table-header">Número</th>
                                        <th className="esquenta-bottom-card-table-header">Responsável</th>
                                        <th className="esquenta-bottom-card-table-header">Progresso</th>
                                        <th className="esquenta-bottom-card-table-header">Tempo restante</th>
                                        <th className="esquenta-bottom-card-table-header">Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {MOCK_NUMEROS.map((item) => (
                                        <tr key={item.id} className="esquenta-bottom-card-table-row">
                                            <td className="esquenta-bottom-card-table-cell esquenta-bottom-card-table-checkbox" style={{ width: "10%" }}>
                                                <input type="checkbox" className="esquenta-bottom-card-table-checkbox-input" id={`checkbox-${item.id}`} />
                                            </td>
                                            <td className="esquenta-bottom-card-table-cell">{item.numero}</td>
                                            <td className="esquenta-bottom-card-table-cell">{item.responsavel}</td>
                                            <td className="esquenta-bottom-card-table-cell">{item.progresso}%</td>
                                            <td className="esquenta-bottom-card-table-cell">{item.tempoRestante}</td>
                                            <td className="esquenta-bottom-card-table-cell">{item.status}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}