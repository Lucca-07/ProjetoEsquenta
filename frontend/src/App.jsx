import CardInfo from "./components/CardInfo/CardInfo";
import { FaFireAlt } from "react-icons/fa";
import { FaMobileAlt } from "react-icons/fa";

export default function App() {
  return (
    <>
    <CardInfo icon={<FaFireAlt/>} text={"12 Celulares Esquentando"}></CardInfo>
    <CardInfo icon={<FaMobileAlt/>} text={"45 Celulares Conectados"}></CardInfo>
    </>
  );
}