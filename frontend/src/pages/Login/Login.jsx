import { useNavigate } from "react-router-dom"
import { useState } from "react";
import "./Login.css"
export default function Login() {
    const navigate = useNavigate();
    const [logging, setLogging] = useState(false);
    function login() {
        setLogging(true);
        setTimeout(() => {
            setLogging(false);
            navigate("/esquenta");
        }, 1500);
    }
    return (
        <div className="login-container">
            <div className="login-form">
                <img src="../../../assets/simbolo_pl.svg" alt="Simbolo do PL" />
                <div className="login-text" style={{ textAlign: 'center' }}>
                    <p className="montserrat-semibold" style={{ fontSize: '1.75rem' }}>Bem vindo de volta!</p>
                    <p className="montserrat-regular" style={{ fontSize: '1rem', color: '#666666' }}>Faça login para continuar</p>
                </div>
                <div className="input-fields">
                    <div className="input-container">
                        <label htmlFor="email" className="montserrat-semibold">Email</label>
                        <input className="montserrat-medium-italic" type="email" id="email" name="email" placeholder="seuemail@gmail.com" />
                    </div>
                    <div className="input-container">
                        <label htmlFor="password" className="montserrat-semibold">Senha</label>
                        <input className="montserrat-medium-italic" type="password" id="password" name="password" placeholder="Digite sua senha" />
                    </div>
                </div>
                <div className="login-options">
                    <div className="remember-me">
                        <input type="checkbox" id="remember" name="remember" />
                        <label htmlFor="remember" className="montserrat-regular">Lembrar de mim</label>
                    </div>
                    <a href="#" className="montserrat-regular forgot-password">Esqueceu sua senha?</a>
                </div>
                <button className="login-button montserrat-semibold" onClick={() => { login() }} disabled={logging}>{logging ? "Acessando..." : "Acessar agora"}</button>

            </div>
        </div>
    )
}
