import "./ConfirmWarmupModal.css";
import { useState } from "react";

const OPCOES_DURACAO = [
    { horas: 6, label: "6h" },
    { horas: 12, label: "12h" },
    { horas: 24, label: "24h" },
    { horas: 48, label: "2 dias" },
    { horas: 120, label: "5 dias" },
    { horas: 168, label: "1 semana" },
    { horas: 336, label: "2 semanas" },
];

export default function ConfirmWarmupModal({
    open,
    onClose,
    onConfirm,
    numeros,
}) {
    const [intervalo, setIntervalo] = useState(240);
    const [duracao, setDuracao] = useState(24);
    const [nome, setNome] = useState("");
    const [duracaoPersonalizada, setDuracaoPersonalizada] = useState("24");
    const [unidadePersonalizada, setUnidadePersonalizada] =
        useState("horas");
    const [personalizado, setPersonalizado] = useState(false);

    if (!open) return null;

    function atualizarDuracaoPersonalizada(value, unit) {
        const amount = Number(value) || 1;
        setDuracao(unit === "dias" ? amount * 24 : amount);
    }

    function calcularFim() {
        const data = new Date();
        data.setHours(data.getHours() + duracao);
        return data.toLocaleString("pt-BR", {
            day: "2-digit",
            month: "2-digit",
            hour: "2-digit",
            minute: "2-digit",
        });
    }

    function confirmar() {
        const dataInicio = new Date().toLocaleDateString("pt-BR", {
            day: "2-digit",
            month: "2-digit",
        });
        onConfirm({
            nome: nome.trim() || dataInicio,
            intervalo,
            duracao,
        });
        onClose();
    }

    return (
        <div className="warmup-overlay">
            <div className="warmup-modal">
                <h2>Confirmar aquecimento</h2>

                <div className="warmup-selected">
                    <b>{numeros.length}</b> números no mesmo grupo
                </div>

                <div className="warmup-section">
                    <p>Nome do esquenta</p>
                    <input
                        className="warmup-name-input"
                        type="text"
                        value={nome}
                        maxLength={80}
                        placeholder="Opcional — ex.: Grupo principal"
                        onChange={(event) => setNome(event.target.value)}
                    />
                </div>

                <div className="warmup-section">
                    <p>Intervalo entre mensagens</p>
                    <input
                        type="number"
                        value={intervalo}
                        min={10}
                        onChange={(event) =>
                            setIntervalo(Number(event.target.value))
                        }
                    />
                    <span>segundos</span>
                </div>

                <div className="warmup-section">
                    <p>Duração</p>
                    <div className="warmup-buttons">
                        {OPCOES_DURACAO.map((opcao) => (
                            <button
                                key={opcao.horas}
                                type="button"
                                className={
                                    !personalizado &&
                                    duracao === opcao.horas
                                        ? "active"
                                        : ""
                                }
                                onClick={() => {
                                    setDuracao(opcao.horas);
                                    setPersonalizado(false);
                                }}
                            >
                                {opcao.label}
                            </button>
                        ))}
                        <button
                            type="button"
                            className={personalizado ? "active" : ""}
                            onClick={() => {
                                setPersonalizado(true);
                                atualizarDuracaoPersonalizada(
                                    duracaoPersonalizada,
                                    unidadePersonalizada,
                                );
                            }}
                        >
                            Personalizado
                        </button>
                    </div>

                    {personalizado && (
                        <div className="warmup-custom-duration">
                            <input
                                type="number"
                                min={1}
                                max={
                                    unidadePersonalizada === "dias"
                                        ? 30
                                        : 720
                                }
                                value={duracaoPersonalizada}
                                placeholder="Quantidade"
                                onChange={(event) => {
                                    setDuracaoPersonalizada(
                                        event.target.value,
                                    );
                                    atualizarDuracaoPersonalizada(
                                        event.target.value,
                                        unidadePersonalizada,
                                    );
                                }}
                            />
                            <select
                                value={unidadePersonalizada}
                                onChange={(event) => {
                                    setUnidadePersonalizada(
                                        event.target.value,
                                    );
                                    atualizarDuracaoPersonalizada(
                                        duracaoPersonalizada,
                                        event.target.value,
                                    );
                                }}
                            >
                                <option value="horas">Horas</option>
                                <option value="dias">Dias</option>
                            </select>
                            <span>
                                máximo de{" "}
                                {unidadePersonalizada === "dias"
                                    ? "30 dias"
                                    : "720 horas"}
                            </span>
                        </div>
                    )}
                </div>

                <div className="warmup-summary">
                    <h4>Resumo</h4>
                    <div>
                        <span>Início</span>
                        <b>Imediato</b>
                    </div>
                    <div>
                        <span>Término</span>
                        <b>{calcularFim()}</b>
                    </div>
                </div>

                <div className="warmup-footer">
                    <button className="cancel" onClick={onClose}>
                        Cancelar
                    </button>
                    <button className="confirm" onClick={confirmar}>
                        Confirmar aquecimento
                    </button>
                </div>
            </div>
        </div>
    );
}
