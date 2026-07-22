import "./CardNumero.css"

export default function CardNumero ({numero}) {
    return (
        <div className="numero-card">
            {numero}
            <input type="checkbox" />
        </div>
    )
}