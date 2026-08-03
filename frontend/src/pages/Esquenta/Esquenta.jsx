import "./Esquenta.css";
import Navbar from "../../components/Navbar/Navbar";
import CardInfo from "../../components/CardInfo/CardInfo";
import CardCodeqr from "../../components/CardCodeqr/CardCodeqr";
import CardCodigo from "../../components/CardCodigo/CardCodigo";
import ConfirmWarmupModal from "../../components/ConfirmWarmupModal/ConfirmWarmupModal";
import { FaFireAlt, FaMobileAlt, FaCheck, FaSearch } from "react-icons/fa";
import { AiOutlineClose } from "react-icons/ai";
import { useEffect, useMemo, useRef, useState } from "react";
import { numbersApi, sessionsApi, warmupApi } from "../../api/numbers";

const NODE_NAME = "kvm8-1"; // ajuste se quiser escolher o nó no próprio formulário

function statusClassName(status) {
    const classes = {
        "Em andamento": "warming",
        Esquentando: "warming",
        Concluído: "completed",
        "Sem ação": "idle",
        Pausado: "paused",
        Conectando: "connecting",
        Desconectado: "disconnected",
        Falhou: "failed",
    };

    return classes[status] || "idle";
}

function statusLabel(status) {
    return status === "Em andamento" ? "Esquentando" : status;
}

function remainingTimeValue(label) {
    if (!label || label === "Concluído") return 0;
    const days = Number(label.match(/(\d+)d/)?.[1] || 0);
    const hours = Number(label.match(/(\d+)h/)?.[1] || 0);
    const minutes = Number(label.match(/(\d+)min/)?.[1] || 0);
    return days * 86400 + hours * 3600 + minutes * 60;
}

export default function Esquenta() {
    const [numeros, setNumeros] = useState([]);
    const [summary, setSummary] = useState({
        connected: 0,
        warming: 0,
        completed: 0,
        not_completed: 0,
    });
    const [selecionados, setSelecionados] = useState([]);
    const [buscaNumero, setBuscaNumero] = useState("");
    const [ordenacao, setOrdenacao] = useState({
        key: "numero",
        direction: "asc",
    });
    const [loading, setLoading] = useState(true);
    const [parando, setParando] = useState(false);
    const [desconectando, setDesconectando] = useState(false);
    const [erro, setErro] = useState(null);

    const [showConfirmModal, setShowConfirmModal] = useState(false);

    const [hidden, setHidden] = useState(true);

    const [telefone, setTelefone] = useState("");
    const [conectando, setConectando] = useState(false);
    const [qrValue, setQrValue] = useState(null);
    const [pairingCode, setPairingCode] = useState(null);
    const [connectionMethod, setConnectionMethod] = useState("qr");
    const [conectarErro, setConectarErro] = useState(null);
    const pollRef = useRef(null);

    const progressoMedio = numeros.length
        ? Math.round(
              numeros.reduce((acc, n) => acc + n.progresso, 0) / numeros.length,
          )
        : 0;
    const preenchimento = {
        background: `linear-gradient(to right, #426143 0%, #4CAF50 ${progressoMedio}%, #ddd ${progressoMedio}%, #ddd 100%)`,
    };
    const tempoRestanteGeral =
        numeros.find((item) =>
            ["Em andamento", "Esquentando"].includes(item.status),
        )
            ?.tempo_restante || "Nenhum aquecimento em andamento";

    const numerosOrdenados = useMemo(() => {
        const termo = buscaNumero.trim().toLowerCase();
        const termoNumerico = termo.replace(/\D/g, "");
        const numerosFiltrados = numeros.filter((item) => {
            if (!termo) return true;
            const numero = String(item.numero || "").toLowerCase();
            const numeroNumerico = numero.replace(/\D/g, "");
            return (
                numero.includes(termo) ||
                (termoNumerico && numeroNumerico.includes(termoNumerico))
            );
        });

        const valueFor = (item) => {
            if (ordenacao.key === "progresso") return item.progresso;
            if (ordenacao.key === "tempo_restante") {
                return remainingTimeValue(item.tempo_restante);
            }
            return item[ordenacao.key] || "";
        };

        return numerosFiltrados.sort((first, second) => {
            const firstValue = valueFor(first);
            const secondValue = valueFor(second);
            const comparison =
                typeof firstValue === "number"
                    ? firstValue - secondValue
                    : String(firstValue).localeCompare(String(secondValue), "pt-BR", {
                          numeric: true,
                      });
            return ordenacao.direction === "asc" ? comparison : -comparison;
        });
    }, [numeros, ordenacao, buscaNumero]);

    const todosSelecionados =
        numerosOrdenados.length > 0 &&
        numerosOrdenados.every((item) => selecionados.includes(item.id));

    function ordenarPor(key) {
        setOrdenacao((current) => ({
            key,
            direction:
                current.key === key && current.direction === "asc"
                    ? "desc"
                    : "asc",
        }));
    }

    function indicadorOrdenacao(key) {
        if (ordenacao.key !== key) return "↕";
        return ordenacao.direction === "asc" ? "↑" : "↓";
    }

    function toggleTodos() {
        const idsVisiveis = numerosOrdenados.map((item) => item.id);
        setSelecionados((current) =>
            todosSelecionados
                ? current.filter((id) => !idsVisiveis.includes(id))
                : [...new Set([...current, ...idsVisiveis])],
        );
    }

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
        const initialLoad = setTimeout(carregarDados, 0);
        const interval = setInterval(carregarDados, 10000);
        return () => {
            clearTimeout(initialLoad);
            clearInterval(interval);
        };
    }, []);

    useEffect(() => {
        return () => clearInterval(pollRef.current);
    }, []);

    function toggleSelecionado(id) {
        setSelecionados((prev) =>
            prev.includes(id)
                ? prev.filter((item) => item !== id)
                : [...prev, id],
        );
    }

    async function iniciarEsquenta(config) {
        if (!selecionados.length) return;

        try {
            await warmupApi.startBulk({
                name: config.nome,
                number_ids: selecionados,

                interval_seconds: config.intervalo,

                duration_hours: config.duracao,
            });

            setSelecionados([]);

            setShowConfirmModal(false);

            carregarDados();
        } catch (err) {
            console.error(err);
        }
    }

    async function pararEsquenta() {
        if (!selecionados.length) return;

        setParando(true);
        setErro(null);

        try {
            await warmupApi.stopBulk(selecionados);
            setSelecionados([]);
            await carregarDados();
        } catch (err) {
            console.error(err);
            setErro(`Não foi possível parar o esquenta: ${err.message}`);
        } finally {
            setParando(false);
        }
    }

    async function desconectarNumeros() {
        if (!selecionados.length) return;

        const confirmado = window.confirm(
            "Desconectar e remover permanentemente os números selecionados? " +
                "O histórico de mensagens e aquecimento também será excluído.",
        );
        if (!confirmado) return;

        setDesconectando(true);
        setErro(null);

        try {
            await Promise.all(
                selecionados.map((numberId) =>
                    sessionsApi.stop(numberId),
                ),
            );
            setSelecionados([]);
            await carregarDados();
        } catch (err) {
            console.error(err);
            setErro(`Não foi possível desconectar: ${err.message}`);
        } finally {
            setDesconectando(false);
        }
    }

    async function iniciarConexao(metodo = "qr") {
        if (!telefone.trim()) {
            setConectarErro("Informe o número com DDI e DDD.");
            return;
        }
        setConectarErro(null);
        setConectando(true);
        setConnectionMethod(metodo);
        setQrValue(null);
        setPairingCode(null);
        try {
            const pending = await sessionsApi.create(
                telefone.replace(/\D/g, ""),
                NODE_NAME,
            );
            if (metodo === "code") {
                const response = await sessionsApi.requestCode(
                    pending.session_name,
                    pending.phone,
                    NODE_NAME,
                );
                setPairingCode(response.code);
            }
            pollRef.current = setInterval(async () => {
                try {
                    const status = await sessionsApi.getPendingStatus(
                        pending.session_name,
                        pending.phone,
                        NODE_NAME,
                    );
                    if (metodo === "qr" && status.qr) {
                        setQrValue(status.qr);
                    }
                    if (status.status === "WORKING") {
                        clearInterval(pollRef.current);
                        setHidden(true);
                        setTelefone("");
                        setQrValue(null);
                        setPairingCode(null);
                        setConectando(false);
                        carregarDados();
                    }
                } catch (requestError) {
                    setConectarErro(requestError.message);
                }
            }, 3000);
        } catch (requestError) {
            setConectarErro(requestError.message);
            setConectando(false);
        }
    }

    async function conectarNumero(e) {
        e.preventDefault();
        await iniciarConexao("qr");
        if (e.defaultPrevented) return;
        setConectarErro(null);
        setConectando(true);
        setQrValue(null);
        try {
            const numero = await sessionsApi.create(
                telefone.replace(/\D/g, ""),
                NODE_NAME,
            );
            pollRef.current = setInterval(async () => {
                try {
                    const status = await sessionsApi.getStatus(numero.id);

                    if (status.qr) {
                        setQrValue(status.qr);
                    }
                    if (status.status === "WORKING") {
                        clearInterval(pollRef.current);
                        setHidden(true);
                        setTelefone("");
                        setQrValue(null);
                        setConectando(false);
                        carregarDados();
                    }
                    if (
                        status.status === "STOPPED" ||
                        status.status === "FAILED"
                    ) {
                        clearInterval(pollRef.current);
                        setConectarErro(
                            "Não foi possível iniciar a sessão. Tente novamente.",
                        );
                        setConectando(false);
                    }
                } catch (err) {
                    console.error(err);
                    console.log(err.response);

                    setConectarErro(
                        err.response?.message ||
                            err.message ||
                            "Erro ao conectar",
                    );

                    if (err.response?.status === 409) {
                        // sessão já existe
                        // agora só consulta o status dela

                        setConectando(true);

                        pollRef.current = setInterval(async () => {
                            const status = await sessionsApi.getStatus(
                                telefone.replace(/\D/g, ""),
                            );

                            if (status.qr) setQrValue(status.qr);
                        }, 3000);

                        return;
                    }

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
        setPairingCode(null);
        setConectarErro(null);
    }
    return (
        <div className="esquenta-container">
            {!hidden && (
                <div className="esquenta-codes">
                    {!conectando && (
                        <CardCodigo codeHidden={false}>
                            <form
                                className="esquenta-connect-form"
                                onSubmit={conectarNumero}
                            >
                                <label
                                    className="montserrat-medium"
                                    htmlFor="telefone-connect"
                                >
                                    Número (com DDI + DDD)
                                </label>
                                <input
                                    id="telefone-connect"
                                    className="montserrat-medium-italic"
                                    type="text"
                                    placeholder="5511999999999"
                                    value={telefone}
                                    onChange={(e) =>
                                        setTelefone(e.target.value)
                                    }
                                    required
                                />
                                <button
                                    type="button"
                                    className="card-connect montserrat-medium"
                                    onClick={() => iniciarConexao("qr")}
                                >
                                    Gerar QR Code
                                </button>
                                <button
                                    type="button"
                                    className="card-connect secondary montserrat-medium"
                                    onClick={() => iniciarConexao("code")}
                                >
                                    Conectar com código
                                </button>
                                {conectarErro && (
                                    <p className="esquenta-connect-erro">
                                        {conectarErro}
                                    </p>
                                )}
                            </form>
                        </CardCodigo>
                    )}
                    {conectando && (
                        <CardCodeqr
                            codeHidden={false}
                            qr={qrValue}
                            pairingCode={pairingCode}
                            mode={connectionMethod}
                        >
                            {conectarErro && (
                                <p className="esquenta-connect-erro">
                                    {conectarErro}
                                </p>
                            )}
                            <div
                                className="card-voltar"
                                onClick={() => {
                                    clearInterval(pollRef.current);
                                    setConectando(false);
                                    setQrValue(null);
                                    setPairingCode(null);
                                }}
                            >
                                Voltar
                            </div>
                        </CardCodeqr>
                    )}
                    <div
                        className="esquenta-codeqr-overlay"
                        onClick={fecharModal}
                    />
                </div>
            )}
            <Navbar func={{ setHidden }} />
            <div className="esquenta-content">
                <div className="esquenta-card">
                    <header className="esquenta-page-header">
                        <div>
                            <span className="esquenta-page-eyebrow">
                                Painel de aquecimento
                            </span>
                            <h1>Visão geral</h1>
                            <p>
                                Acompanhe seus números e controle os ciclos de
                                aquecimento.
                            </p>
                        </div>
                        <div className="esquenta-live-status">
                            <span />
                            Sistema ativo
                        </div>
                    </header>
                    {erro && (
                        <p className="esquenta-connect-erro">
                            Não foi possível falar com o backend: {erro}
                        </p>
                    )}
                    <div className="esquenta-mini-cards">
                        <CardInfo
                            icon={<FaMobileAlt />}
                            text={`${summary.connected} Conectados`}
                        ></CardInfo>
                        <CardInfo
                            icon={<FaFireAlt />}
                            text={`${summary.warming} Esquentando`}
                        ></CardInfo>
                        <CardInfo
                            icon={<FaCheck />}
                            text={`${summary.completed} Concluídos`}
                        ></CardInfo>
                        <CardInfo
                            icon={<AiOutlineClose />}
                            text={`${summary.not_completed} Não concluídos`}
                        ></CardInfo>
                    </div>
                    <div className="esquenta-medium-card">
                        <div className="esquenta-medium-left-card">
                            <p className="esquenta-medium-card-title montserrat-medium">
                                Progresso
                            </p>
                            <div className="esquenta-medium-left-card-content">
                                <input
                                    readOnly
                                    style={preenchimento}
                                    type="range"
                                    min="0"
                                    max="100"
                                    value={progressoMedio}
                                    className="esquenta-slider"
                                />
                                <div className="esquenta-slider-info-container">
                                    <span className="esquenta-slider-info">
                                        {progressoMedio}% Completo (média)
                                    </span>
                                    <span className="esquenta-slider-info">
                                        Tempo restante: {tempoRestanteGeral}
                                    </span>
                                </div>
                            </div>
                        </div>
                        <div className="esquenta-medium-right-card">
                            <p className="esquenta-medium-card-title montserrat-medium">
                                Status geral
                            </p>
                            <div className="esquenta-medium-card-content">
                                <p className="esquenta-status-text">
                                    {summary.warming > 0
                                        ? `${summary.warming} número(s) em aquecimento`
                                        : "Nenhum aquecimento em andamento"}
                                </p>
                            </div>
                        </div>
                    </div>
                    <div className="esquenta-bottom-card">
                        <div className="esquenta-bottom-card-header">
                            <p className="esquenta-bottom-card-title montserrat-medium">
                                Números
                            </p>
                            <label className="esquenta-number-search">
                                <FaSearch aria-hidden="true" />
                                <input
                                    type="search"
                                    value={buscaNumero}
                                    onChange={(event) =>
                                        setBuscaNumero(event.target.value)
                                    }
                                    placeholder="Pesquisar número..."
                                    aria-label="Pesquisar números"
                                />
                                {buscaNumero && (
                                    <button
                                        type="button"
                                        onClick={() => setBuscaNumero("")}
                                        aria-label="Limpar pesquisa"
                                    >
                                        ×
                                    </button>
                                )}
                            </label>
                            <div className="esquenta-bottom-card-buttons">
                                <button
                                    type="button"
                                    className="esquenta-bottom-card-button desconectar montserrat-semibold"
                                    disabled={
                                        !selecionados.length ||
                                        desconectando
                                    }
                                    onClick={desconectarNumeros}
                                >
                                    {desconectando
                                        ? "Desconectando..."
                                        : "Desconectar"}
                                </button>
                                <button
                                    type="button"
                                    className="esquenta-bottom-card-button parar montserrat-semibold"
                                    disabled={
                                        !selecionados.length || parando
                                    }
                                    onClick={pararEsquenta}
                                >
                                    {parando
                                        ? "Parando..."
                                        : "Parar Esquenta"}
                                </button>

                                <button
                                    type="button"
                                    className="esquenta-bottom-card-button iniciar montserrat-semibold"
                                    disabled={!selecionados.length}
                                    onClick={() => {
                                        setShowConfirmModal(true);
                                    }}
                                >
                                    Iniciar Esquenta
                                </button>
                            </div>
                        </div>
                        <div className="esquenta-bottom-card-table-div">
                            <table className="esquenta-bottom-card-table">
                                <thead>
                                    <tr className="esquenta-bottom-card-table-header">
                                        <th className="esquenta-bottom-card-table-header-checkbox">
                                            <label className="esquenta-select-all">
                                                <input
                                                    type="checkbox"
                                                    className="esquenta-bottom-card-table-checkbox-input"
                                                    checked={todosSelecionados}
                                                    onChange={toggleTodos}
                                                    disabled={!numerosOrdenados.length}
                                                    aria-label="Selecionar todos os números"
                                                />
                                                <span>Selecionar</span>
                                            </label>
                                        </th>
                                        <th className="esquenta-bottom-card-table-header">
                                            <button
                                                type="button"
                                                className="esquenta-sort-button"
                                                onClick={() => ordenarPor("numero")}
                                            >
                                                Número
                                                <span>{indicadorOrdenacao("numero")}</span>
                                            </button>
                                        </th>
                                        <th className="esquenta-bottom-card-table-header">
                                            <button
                                                type="button"
                                                className="esquenta-sort-button"
                                                onClick={() => ordenarPor("progresso")}
                                            >
                                                Progresso
                                                <span>{indicadorOrdenacao("progresso")}</span>
                                            </button>
                                        </th>
                                        <th className="esquenta-bottom-card-table-header">
                                            <button
                                                type="button"
                                                className="esquenta-sort-button"
                                                onClick={() =>
                                                    ordenarPor("tempo_restante")
                                                }
                                            >
                                                Tempo restante
                                                <span>
                                                    {indicadorOrdenacao(
                                                        "tempo_restante",
                                                    )}
                                                </span>
                                            </button>
                                        </th>
                                        <th className="esquenta-bottom-card-table-header">
                                            <button
                                                type="button"
                                                className="esquenta-sort-button"
                                                onClick={() => ordenarPor("grupo")}
                                            >
                                                Grupo
                                                <span>{indicadorOrdenacao("grupo")}</span>
                                            </button>
                                        </th>
                                        <th className="esquenta-bottom-card-table-header">
                                            <button
                                                type="button"
                                                className="esquenta-sort-button"
                                                onClick={() => ordenarPor("status")}
                                            >
                                                Status
                                                <span>{indicadorOrdenacao("status")}</span>
                                            </button>
                                        </th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {loading && (
                                        <tr>
                                            <td
                                                colSpan={6}
                                                className="esquenta-bottom-card-table-cell"
                                            >
                                                Carregando...
                                            </td>
                                        </tr>
                                    )}
                                    {!loading && numeros.length === 0 && (
                                        <tr>
                                            <td
                                                colSpan={6}
                                                className="esquenta-bottom-card-table-cell"
                                            >
                                                Nenhum número cadastrado ainda.
                                                Clique em "Conectar" na barra
                                                lateral.
                                            </td>
                                        </tr>
                                    )}
                                    {!loading &&
                                        numeros.length > 0 &&
                                        numerosOrdenados.length === 0 && (
                                            <tr>
                                                <td
                                                    colSpan={6}
                                                    className="esquenta-bottom-card-table-cell esquenta-table-empty"
                                                >
                                                    Nenhum número encontrado
                                                    para “{buscaNumero}”.
                                                </td>
                                            </tr>
                                        )}
                                    {numerosOrdenados.map((item) => (
                                        <tr
                                            key={item.id}
                                            className={`esquenta-bottom-card-table-row status-row-${statusClassName(item.status)}`}
                                        >
                                            <td
                                                className="esquenta-bottom-card-table-cell esquenta-bottom-card-table-checkbox"
                                                style={{ width: "10%" }}
                                            >
                                                <input
                                                    type="checkbox"
                                                    className="esquenta-bottom-card-table-checkbox-input"
                                                    checked={selecionados.includes(
                                                        item.id,
                                                    )}
                                                    onChange={() =>
                                                        toggleSelecionado(
                                                            item.id,
                                                        )
                                                    }
                                                />
                                            </td>
                                            <td className="esquenta-bottom-card-table-cell">
                                                {item.numero}
                                            </td>
                                            <td className="esquenta-bottom-card-table-cell">
                                                {item.progresso}%
                                            </td>
                                            <td className="esquenta-bottom-card-table-cell">
                                                {item.tempo_restante}
                                            </td>
                                            <td className="esquenta-bottom-card-table-cell">
                                                <span className="esquenta-group-name">
                                                    {item.grupo}
                                                </span>
                                            </td>
                                            <td className="esquenta-bottom-card-table-cell">
                                                <span
                                                    className={`esquenta-status-badge status-${statusClassName(item.status)}`}
                                                >
                                                    <span
                                                        className="esquenta-status-dot"
                                                        aria-hidden="true"
                                                    />
                                                    {statusLabel(item.status)}
                                                </span>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
            <ConfirmWarmupModal
                open={showConfirmModal}
                onClose={() => setShowConfirmModal(false)}
                numeros={selecionados}
                onConfirm={iniciarEsquenta}
            />
        </div>
    );
}
