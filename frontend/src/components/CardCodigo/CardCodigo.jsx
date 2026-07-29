import "./CardCodigo.css";

export default function CardCodigo({ children, codeHidden }) {
    return (
        <div
            className="card-codigo-container montserrat-medium"
            hidden={codeHidden}
            role="dialog"
            aria-modal="true"
            aria-labelledby="connect-modal-title"
        >
            <header className="card-codigo-header">
                <span className="card-codigo-eyebrow">Nova conexão</span>
                <h2 id="connect-modal-title">
                    Conecte seu número ao{" "}
                    <span className="green-span">WhatsApp</span>
                </h2>
                <p>
                    Informe o número que deseja conectar. Na próxima etapa,
                    você fará a leitura do QR Code pelo WhatsApp.
                </p>
            </header>

            <div className="card-codigo-body">{children}</div>
        </div>
    );
}
