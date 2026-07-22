import "./CardNumero.css"

export default function CardNumero ({numero}) {
    return (
        <div className="card-numero">
            <span className="montserrat-medium span-card-numero">{numero}</span>
            <input className="checkbox-card-numero" type="checkbox" />
        </div>
    )
}