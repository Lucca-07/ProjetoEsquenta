import "./CardCodeqr.css";
import { QRCodeSVG } from "qrcode.react";

export default function CardCode({
    children,
    codeHidden,
    qr,
    pairingCode,
    mode = "qr",
}) {
    const isPairingCode = mode === "code";

    return (
        <div
            className={`card-qrcode montserrat-medium ${isPairingCode ? "card-code-mode" : ""}`}
            hidden={codeHidden}
        >
            <div className="card-qrcode-title">
                <h1>
                    Conectar Número de{" "}
                    <span className="span-verde">WhatsApp</span>
                </h1>
            </div>

            <div className="card-qrcode-img">
                {pairingCode ? (
                    <div className="card-pairing-code">
                        <span>Código de conexão</span>
                        <strong>{pairingCode}</strong>
                        <p>Digite este código em Aparelhos conectados.</p>
                    </div>
                ) : !isPairingCode && qr ? (
                    <QRCodeSVG
                        value={qr}
                        alt="QR Code de conexão"
                        width={300}
                        height={300}
                    />
                ) : (
                    <p>
                        {isPairingCode
                            ? "Gerando código de conexão..."
                            : "Gerando QR code..."}
                    </p>
                )}
            </div>

            {!isPairingCode && !pairingCode && (
                <p style={{ marginTop: "10px" }}>
                    Aponte a câmera para{" "}
                    <span className="span-verde">Conectar</span>
                </p>
            )}

            <div className="card-instruct montserrat-medium">
                <p className="card-instruct-p">
                    Abra o <span className="span-verde">WhatsApp</span>
                </p>
                <p>
                    Toque em aparelhos conectados.{" "}
                    <span className="span-verde">Conectar aparelho</span>
                </p>
                <p>
                    {isPairingCode
                        ? "Escolha conectar com número de telefone e informe o código."
                        : "Escaneie o QR Code"}
                </p>
            </div>

            {children}
        </div>
    );
}
