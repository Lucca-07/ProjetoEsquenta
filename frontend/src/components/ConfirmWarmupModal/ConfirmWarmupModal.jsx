import "./ConfirmWarmupModal.css";
import { useState } from "react";

export default function ConfirmWarmupModal({
    open,
    onClose,
    onConfirm,
    numeros,
}) {
    const [intervalo, setIntervalo] = useState(90);
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
                        <button
                            type="button"
                            className={duracao === 6 ? "active" : ""}
                            onClick={() => setDuracao(6)}
                        >
                            6h
                        </button>

                        <button
                            type="button"
                            className={duracao === 12 ? "active" : ""}
                            onClick={() => setDuracao(12)}
                        >
                            12h
                        </button>

                        <button
                            type="button"
                            className={duracao === 24 ? "active" : ""}
                            onClick={() => setDuracao(24)}
                        >
                            24h
                        </button>

                        <button
                            type="button"
                            className={duracao === 48 ? "active" : ""}
                            onClick={() => setDuracao(48)}
                        >
                            48h
                        </button>
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
