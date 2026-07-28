import "./Esquenta.css";
import Navbar from "../../components/Navbar/Navbar";
import CardInfo from "../../components/CardInfo/CardInfo";
import CardCodeqr from "../../components/CardCodeqr/CardCodeqr";
import CardCodigo from "../../components/CardCodigo/CardCodigo";
import { FaFireAlt, FaMobileAlt, FaCheck } from "react-icons/fa";
import { AiOutlineClose } from "react-icons/ai";
import { useEffect, useRef, useState } from "react";
import { numbersApi, sessionsApi, warmupApi } from "../../api/numbers";

const NODE_NAME = "kvm8-1"; // ajuste se quiser escolher o nó no próprio formulário

export default function Esquenta() {
    const [numeros, setNumeros] = useState([]);
    const [summary, setSummary] = useState({ connected: 0, warming: 0, completed: 0, not_completed: 0 });
    const [selecionados, setSelecionados] = useState([]);
    const [loading, setLoading] = useState(true);
    const [erro, setErro] = useState(null);

    const [hidden, setHidden] = useState(true);

    const [telefone, setTelefone] = useState("");
    const [conectando, setConectando] = useState(false);
    const [qrValue, setQrValue] = useState(null);
    const [conectarErro, setConectarErro] = useState(null);
    const pollRef = useRef(null);

    const progressoMedio = numeros.length
        ? Math.round(numeros.reduce((acc, n) => acc + n.progresso, 0) / numeros.length)
        : 0;
    const preenchimento = {
        background: `linear-gradient(to right, #426143 0%, #4CAF50 ${progressoMedio}%, #ddd ${progressoMedio}%, #ddd 100%)`,
    };

    async function carregarDados() {
        try {
            const [lista, resumo] = await Promise.all([
                numbersApi.listDashboard(),
                numbersApi.getSummary(),
            ]);
            setNumeros(lista);
            setSummary(resumo);
            setErro(null);
        } catch (e) {
            setErro(e.message);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        carregarDados();
        const interval = setInterval(carregarDados, 10000);
        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        return () => clearInterval(pollRef.current);
    }, []);

    function toggleSelecionado(id) {
        setSelecionados((prev) =>
            prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
        );
    }

    async function iniciarEsquenta() {
        if (!selecionados.length) return;
        await warmupApi.startBulk(selecionados);
        setSelecionados([]);
        carregarDados();
    }

    async function pararEsquenta() {
        if (!selecionados.length) return;
        await warmupApi.pauseBulk(selecionados);
        setSelecionados([]);
        carregarDados();
    }

    async function conectarNumero(e) {
        e.preventDefault();
        setConectarErro(null);
        setConectando(true);
        setQrValue(null);
        try {
            const numero = await sessionsApi.create(telefone.replace(/\D/g, ""), NODE_NAME);
            pollRef.current = setInterval(async () => {
                try {
                    const status = await sessionsApi.getStatus(numero.id);
                    if (status.qr) setQrValue(status.qr);
                    if (status.status === "WORKING") {
                        clearInterval(pollRef.current);
                        setHidden(true);
                        setTelefone("");
                        setQrValue(null);
                        setConectando(false);
                        carregarDados();
                    }
                } catch (err) {
                    clearInterval(pollRef.current);
                    setConectarErro(err.message);
                    setConectando(false);
                }
            }, 3000);
        } catch (err) {
            setConectarErro(err.message);
            setConectando(false);
        }
    }

    function fecharModal() {
        clearInterval(pollRef.current);
        setHidden(true);
        setConectando(false);
        setQrValue(null);
        setConectarErro(null);
    }

    return (
        <div className="esquenta-container">
            {!hidden && (
                <div className="esquenta-codes">
                    {!conectando && (
                        <CardCodigo codeHidden={false}>
                            <form className="esquenta-connect-form" onSubmit={conectarNumero}>
                                <label className="montserrat-medium" htmlFor="telefone-connect">
                                    Número (com DDI + DDD)
                                </label>
                                <input
                                    id="telefone-connect"
                                    className="montserrat-medium-italic"
                                    type="text"
                                    placeholder="5511999999999"
                                    value={telefone}
                                    onChange={(e) => setTelefone(e.target.value)}
                                    required
                                />
                                <button type="submit" className="card-connect montserrat-medium">
                                    Gerar QR Code
                                </button>
                            </form>
                        </CardCodigo>
                    )}
                    {conectando && (
                        <CardCodeqr codeHidden={false} qr={qrValue}>
                            {conectarErro && <p className="esquenta-connect-erro">{conectarErro}</p>}
                            <div
                                className="card-voltar"
                                onClick={() => {
                                    clearInterval(pollRef.current);
                                    setConectando(false);
                                    setQrValue(null);
                                }}
                            >
                                Voltar
                            </div>
                        </CardCodeqr>
                    )}
                    <div className="esquenta-codeqr-overlay" onClick={fecharModal} />
                </div>
            )}
            <nav className="navbar">
                <Navbar func={{ setHidden }} />
            </nav>
            <div className="esquenta-content">
                <div className="esquenta-card">
                    {erro && <p className="esquenta-connect-erro">Não foi possível falar com o backend: {erro}</p>}
                    <div className="esquenta-mini-cards">
                        <CardInfo icon={<FaMobileAlt />} text={`${summary.connected} Conectados`}></CardInfo>
                        <CardInfo icon={<FaFireAlt />} text={`${summary.warming} Esquentando`}></CardInfo>
                        <CardInfo icon={<FaCheck />} text={`${summary.completed} Concluídos`}></CardInfo>
                        <CardInfo icon={<AiOutlineClose />} text={`${summary.not_completed} Não concluídos`}></CardInfo>
                    </div>
                    <div className="esquenta-medium-card">
                        <div className="esquenta-medium-left-card">
                            <p className="esquenta-medium-card-title montserrat-medium">Progresso</p>
                            <div className="esquenta-medium-left-card-content">
                                <input readOnly style={preenchimento} type="range" min="0" max="100" value={progressoMedio} className="esquenta-slider" />
                                <div className="esquenta-slider-info-container">
                                    <span className="esquenta-slider-info">{progressoMedio}% Completo (média)</span>
                                    <span className="esquenta-slider-info">{numeros.length} número(s)</span>
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
                                <button
                                    className="esquenta-bottom-card-button parar montserrat-semibold"
                                    disabled={!selecionados.length}
                                    onClick={pararEsquenta}
                                >
                                    Parar Esquenta
                                </button>
                                <button
                                    className="esquenta-bottom-card-button iniciar montserrat-semibold"
                                    disabled={!selecionados.length}
                                    onClick={iniciarEsquenta}
                                >
                                    Iniciar Esquenta
                                </button>
                            </div>
                        </div>
                        <div className="esquenta-bottom-card-table-div">
                            <table className="esquenta-bottom-card-table">
                                <thead>
                                    <tr className="esquenta-bottom-card-table-header">
                                        <th className="esquenta-bottom-card-table-header-checkbox">Selecionar</th>
                                        <th className="esquenta-bottom-card-table-header">Número</th>
                                        <th className="esquenta-bottom-card-table-header">Progresso</th>
                                        <th className="esquenta-bottom-card-table-header">Tempo restante</th>
                                        <th className="esquenta-bottom-card-table-header">Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {loading && (
                                        <tr>
                                            <td colSpan={5} className="esquenta-bottom-card-table-cell">Carregando...</td>
                                        </tr>
                                    )}
                                    {!loading && numeros.length === 0 && (
                                        <tr>
                                            <td colSpan={5} className="esquenta-bottom-card-table-cell">
                                                Nenhum número cadastrado ainda. Clique em "Conectar" na barra lateral.
                                            </td>
                                        </tr>
                                    )}
                                    {numeros.map((item) => (
                                        <tr key={item.id} className="esquenta-bottom-card-table-row">
                                            <td className="esquenta-bottom-card-table-cell esquenta-bottom-card-table-checkbox" style={{ width: "10%" }}>
                                                <input
                                                    type="checkbox"
                                                    className="esquenta-bottom-card-table-checkbox-input"
                                                    checked={selecionados.includes(item.id)}
                                                    onChange={() => toggleSelecionado(item.id)}
                                                />
                                            </td>
                                            <td className="esquenta-bottom-card-table-cell">{item.numero}</td>
                                            <td className="esquenta-bottom-card-table-cell">{item.progresso}%</td>
                                            <td className="esquenta-bottom-card-table-cell">{item.tempo_restante}</td>
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
