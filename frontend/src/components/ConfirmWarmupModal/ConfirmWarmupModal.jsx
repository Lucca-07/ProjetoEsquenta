import "./ConfirmWarmupModal.css";
import { useState } from "react";

const OPCOES_DURACAO = [
    { horas: 6, label: "6h" },
    { horas: 12, label: "12h" },
    { horas: 24, label: "24h" },
    { horas: 48, label: "2 dias" },
    { horas: 72, label: "3 dias" },
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

    if (!open) return null;

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
        onConfirm({
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
                    <b>{numeros.length}</b> números selecionados
                </div>

                <div className="warmup-section">
                    <p>Intervalo entre mensagens</p>

                    <input
                        type="number"
                        value={intervalo}
                        min={30}
                        onChange={(e) => setIntervalo(Number(e.target.value))}
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
                                    duracao === opcao.horas ? "active" : ""
                                }
                                onClick={() => setDuracao(opcao.horas)}
                            >
                                {opcao.label}
                            </button>
                        ))}
                    </div>
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
