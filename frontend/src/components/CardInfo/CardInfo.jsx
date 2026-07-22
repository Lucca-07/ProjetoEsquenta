import "./CardInfo.css"

export default function CardInfo ({icon, text}){
    return (
        <div className="card-info">
            <div className="icone-info">{icon}</div> <p className="text-info montserrat-semibold">{text}</p>
        </div>
    )
}