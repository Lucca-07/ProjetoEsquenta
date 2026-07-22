import "./CardCodigo.css";

export default function CardCodigo() {
  return (
    <div className="card-codigo-container">
        <div className="card-codigo-title">
            <h1>Conectar número de <span className="span-verde">WhatsApp</span></h1>

            <div className="card-codigo-codigo">
                <h3>32TF - 69BC</h3>
                <p>Copiar</p>
            </div>

            <div className="card-instrucoes">
                <p>Abra o <span className="span-verde">WhatsApp</span></p>
                <p>Toque em aparelhos conectados <span className="span-verde">conectar aparelho</span></p>
                <p>Toque em <span className="span-verde">conectar com numero de celular</span></p>
                <p>Digite o codigo acima</p>
            </div>

            <p>Voltar</p>
        </div>
    </div>
  );
}