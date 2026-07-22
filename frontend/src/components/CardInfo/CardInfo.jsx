import "./CardInfo.css"

export default function CardInfo ({icon, text}){
    return (
        <div className="card-info">
            <div className="icone-info">{icon}</div> {text}
        </div>
    )
}