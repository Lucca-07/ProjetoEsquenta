import { useEffect, useState } from "react";
import {
    FaCheckCircle,
    FaClock,
    FaExclamationCircle,
    FaFilter,
    FaPaperPlane,
    FaTrash,
} from "react-icons/fa";
import { logsApi } from "../../api/numbers";
import Navbar from "../../components/Navbar/Navbar";
import "./LogsPage.css";

const EMPTY_DASHBOARD = {
    total_messages: 0,
    sent_messages: 0,
    failed_messages: 0,
    pending_messages: 0,
    by_number: [],
    by_group: [],
    failed_numbers: [],
    warmups: [],
};

function formatDate(value) {
    if (!value) return "—";
    return new Date(value).toLocaleString("pt-BR", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    });
}

function groupStatus(status) {
    const labels = {
        ACTIVE: "Esquentando",
        COMPLETED: "Concluído",
        STOPPED: "Parado",
    };
    return labels[status] || status;
}

export default function Logs() {
    const [dashboard, setDashboard] = useState(EMPTY_DASHBOARD);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [period, setPeriod] = useState("30");
    const [phone, setPhone] = useState("");
    const [status, setStatus] = useState("");
    const [deletingId, setDeletingId] = useState(null);

    async function deleteWarmup(warmup) {
        const confirmed = window.confirm(
            `Excluir o grupo “${warmup.name}” do histórico? Essa ação não pode ser desfeita.`,
        );
        if (!confirmed) return;

        setDeletingId(warmup.id);
        setError("");
        try {
            await logsApi.deleteWarmup(warmup.id);
            setDashboard((current) => ({
                ...current,
                warmups: current.warmups.filter(
                    (item) => item.id !== warmup.id,
                ),
            }));
        } catch (requestError) {
            setError(requestError.message);
        } finally {
            setDeletingId(null);
        }
    }

    useEffect(() => {
        let active = true;

        async function load() {
            try {
                const data = await logsApi.dashboard({
                    days: period,
                    phone: phone.trim(),
                    status,
                });
                if (active) {
                    setDashboard({
                        ...EMPTY_DASHBOARD,
                        ...data,
                        by_number: data.by_number || [],
                        by_group: data.by_group || [],
                        failed_numbers: data.failed_numbers || [],
                        warmups: data.warmups || [],
                    });
                    setError("");
                }
            } catch (requestError) {
                if (active) setError(requestError.message);
            } finally {
                if (active) setLoading(false);
            }
        }

        load();
        const interval = setInterval(load, 15000);
        return () => {
            active = false;
            clearInterval(interval);
        };
    }, [period, phone, status]);

    const cards = [
        {
            label: "Mensagens registradas",
            value: dashboard.total_messages,
            icon: <FaPaperPlane />,
            tone: "blue",
        },
        {
            label: "Enviadas com sucesso",
            value: dashboard.sent_messages,
            icon: <FaCheckCircle />,
            tone: "green",
        },
        {
            label: "Pendentes",
            value: dashboard.pending_messages,
            icon: <FaClock />,
            tone: "gold",
        },
        {
            label: "Falhas",
            value: dashboard.failed_messages,
            icon: <FaExclamationCircle />,
            tone: "orange",
        },
    ];

    return (
        <div className="logs-layout">
            <Navbar />
            <main className="logs-content">
                <div className="logs-container">
                    <header className="logs-header">
                        <div>
                            <span>Monitoramento</span>
                            <h1>Histórico e logs</h1>
                            <p>
                                Acompanhe os envios e o desempenho dos grupos de
                                aquecimento.
                            </p>
                        </div>
                        <div className="logs-live">
                            <span />
                            Atualização automática
                        </div>
                    </header>

                    {error && <p className="logs-error">{error}</p>}

                    <section className="logs-filters">
                        <div className="logs-filter-title">
                            <FaFilter />
                            <span>Filtros</span>
                        </div>
                        <label>
                            Período
                            <select
                                value={period}
                                onChange={(event) =>
                                    setPeriod(event.target.value)
                                }
                            >
                                <option value="7">Últimos 7 dias</option>
                                <option value="30">Últimos 30 dias</option>
                                <option value="90">Últimos 90 dias</option>
                                <option value="">Todo o histórico</option>
                            </select>
                        </label>
                        <label className="logs-filter-phone">
                            Número
                            <input
                                type="search"
                                value={phone}
                                onChange={(event) =>
                                    setPhone(event.target.value)
                                }
                                placeholder="Buscar por número"
                            />
                        </label>
                        <label>
                            Status do esquenta
                            <select
                                value={status}
                                onChange={(event) =>
                                    setStatus(event.target.value)
                                }
                            >
                                <option value="">Todos</option>
                                <option value="ACTIVE">Esquentando</option>
                                <option value="COMPLETED">Concluído</option>
                                <option value="STOPPED">Parado</option>
                            </select>
                        </label>
                        <button
                            type="button"
                            onClick={() => {
                                setPeriod("30");
                                setPhone("");
                                setStatus("");
                            }}
                        >
                            Limpar filtros
                        </button>
                    </section>

                    <section className="logs-summary">
                        {cards.map((card) => (
                            <article
                                className={`logs-summary-card ${card.tone}`}
                                key={card.label}
                            >
                                <div>{card.icon}</div>
                                <span>{card.label}</span>
                                <strong>{loading ? "—" : card.value}</strong>
                            </article>
                        ))}
                    </section>

                    <section className="logs-grid">
                        <article className="logs-panel">
                            <header>
                                <h2>Mensagens por número</h2>
                                <span>{dashboard.by_number.length} números</span>
                            </header>
                            <div className="logs-table-wrap">
                                <table>
                                    <thead>
                                        <tr>
                                            <th>Número</th>
                                            <th>Enviadas</th>
                                            <th>Recebidas</th>
                                            <th>Falhas</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {dashboard.by_number.map((number) => (
                                            <tr key={number.id}>
                                                <td>{number.phone}</td>
                                                <td>{number.sent}</td>
                                                <td>{number.received}</td>
                                                <td>{number.failed}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                                {!loading &&
                                    dashboard.by_number.length === 0 && (
                                        <p className="logs-empty">
                                            Nenhum número com histórico.
                                        </p>
                                    )}
                            </div>
                        </article>

                        <article className="logs-panel failures">
                            <header>
                                <h2>Números com falha</h2>
                                <span>
                                    {dashboard.failed_numbers.length} afetados
                                </span>
                            </header>
                            <div className="logs-failure-list">
                                {dashboard.failed_numbers.map((number) => (
                                    <div
                                        className="logs-failure-item"
                                        key={number.id}
                                    >
                                        <div>
                                            <strong>{number.phone}</strong>
                                            <span>
                                                {number.last_error ||
                                                    "Falha de sessão"}
                                            </span>
                                        </div>
                                        <b>{number.failures} falha(s)</b>
                                    </div>
                                ))}
                                {!loading &&
                                    dashboard.failed_numbers.length === 0 && (
                                        <p className="logs-empty success">
                                            Nenhuma falha registrada.
                                        </p>
                                    )}
                            </div>
                        </article>
                    </section>

                    <section className="logs-panel logs-history">
                        <header>
                            <h2>Mensagens por grupo</h2>
                            <span>{dashboard.by_group.length} grupos</span>
                        </header>
                        <div className="logs-table-wrap">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Grupo</th>
                                        <th>Números</th>
                                        <th>Total</th>
                                        <th>Enviadas</th>
                                        <th>Pendentes</th>
                                        <th>Falhas</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {dashboard.by_group.map((group) => (
                                        <tr key={group.id}>
                                            <td>
                                                <strong>{group.name}</strong>
                                            </td>
                                            <td>{group.member_count}</td>
                                            <td>{group.total}</td>
                                            <td>{group.sent}</td>
                                            <td>{group.pending}</td>
                                            <td>{group.failed}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                            {!loading && dashboard.by_group.length === 0 && (
                                <p className="logs-empty">
                                    Nenhum grupo com histórico.
                                </p>
                            )}
                        </div>
                    </section>

                    <section className="logs-panel logs-history">
                        <header>
                            <h2>Histórico de esquentas</h2>
                            <span>{dashboard.warmups.length} execuções</span>
                        </header>
                        <div className="logs-table-wrap">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Grupo</th>
                                        <th>Status</th>
                                        <th>Números</th>
                                        <th>Início</th>
                                        <th>Término previsto</th>
                                        <th>Enviadas</th>
                                        <th>Falhas</th>
                                        <th>Ações</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {dashboard.warmups.map((warmup) => (
                                        <tr key={warmup.id}>
                                            <td>
                                                <strong>{warmup.name}</strong>
                                            </td>
                                            <td>
                                                <span
                                                    className={`logs-status ${warmup.status.toLowerCase()}`}
                                                >
                                                    {groupStatus(warmup.status)}
                                                </span>
                                            </td>
                                            <td title={warmup.members.join(", ")}>
                                                {warmup.member_count}
                                            </td>
                                            <td>
                                                {formatDate(warmup.started_at)}
                                            </td>
                                            <td>
                                                {formatDate(warmup.finish_at)}
                                            </td>
                                            <td>{warmup.messages_sent}</td>
                                            <td>{warmup.messages_failed}</td>
                                            <td>
                                                <button
                                                    type="button"
                                                    className="logs-delete-button"
                                                    onClick={() =>
                                                        deleteWarmup(warmup)
                                                    }
                                                    disabled={
                                                        deletingId === warmup.id
                                                    }
                                                    title="Excluir grupo"
                                                    aria-label={`Excluir grupo ${warmup.name}`}
                                                >
                                                    <FaTrash />
                                                    {deletingId === warmup.id
                                                        ? "Excluindo..."
                                                        : "Excluir"}
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                            {!loading && dashboard.warmups.length === 0 && (
                                <p className="logs-empty">
                                    Nenhum esquenta registrado.
                                </p>
                            )}
                        </div>
                    </section>
                </div>
            </main>
        </div>
    );
}
