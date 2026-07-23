import "./CardCodeqr.css"
import { FaArrowRight } from "react-icons/fa";

export default function CardCode ({children, codeHidden}){
    return (
        <div className="card-qrcode montserrat-medium" hidden={codeHidden}>
            <div className="card-qrcode-title">
                <h1>Conectar Número de <span className="span-verde">WhatsApp</span></h1>
            </div>

            <div className="card-qrcode-img">
                
            </div>

            <p style={{marginTop: "10px"}}>Aponte a camera para <span className="span-verde">Conectar</span></p>

            <div className="card-instruct montserrat-medium">
                <p className="card-instruct-p">Abra o <span className="span-verde">WhatsApp</span></p>
                <p>Toque em aparelhos conectados. <span className="span-verde">Conectar aparelho</span></p>
                <p>Escaneie o Qr Code</p>
            </div>

            {children}
        </div>
    )
}