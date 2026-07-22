import "./CardInfo.css"

export default function CardInfo ({icon, text}){
    return (
        <div className="card-info">
            {icon} {text}
        </div>
    )
}