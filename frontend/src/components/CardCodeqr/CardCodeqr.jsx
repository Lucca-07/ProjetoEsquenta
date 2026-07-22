import "./CardCodeqr.css"

export default function CardCode (){
    return (
        <div className="card-qrcode">
            <div className="card-qrcode-title">
                <h1>Conectar Número de <span className="span-verde">WhatsApp</span></h1>
            </div>

            <div className="card-qrcode-img">
                <h3>Qr code</h3>
            </div>

            <p>Aponte a camera para Conectar</p>

            <div className="card-instruct">
                <p>Abra o <span className="span-verde">WhatsApp</span></p>
                <p>Toque em aparelhos conectados <span className="span-verde">Conectar aparelho</span></p>
                <p>Escaneie o Qr Code</p>
            </div>

            <p>Conectar com Codigo</p>
        </div>
    )
}