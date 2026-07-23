import "./CardCodigo.css";

export default function CardCodigo({ children, codeHidden }) {
    return (
        <div className="card-codigo-container" hidden={codeHidden}>
            <div className="card-codigo-title">
                <p className="card-codigo-title-p">Conecte seu número de <span className="green-span">WhatsApp</span></p>
            </div>
            <div className="card-codigo-conectar">
                <p className="card-codigo-conectar-p montserrat-bold">32TF - 69BC</p>
                <p>Copiar</p>
            </div>

            <div className="card-instrucoes">
                <p>Abra o <span className="green-span">WhatsApp</span></p>
                <p>Toque em aparelhos conectados <span className="green-span">conectar aparelho</span></p>
                <p>Toque em <span className="green-span">conectar com numero de celular</span></p>
                <p>Digite o codigo acima</p>
            </div>

            {children}
        </div>
    );
}