import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { authApi, saveSession } from "../../api/auth";
import "./Login.css";

export default function Login() {
    const navigate = useNavigate();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [logging, setLogging] = useState(false);
    const [erro, setErro] = useState("");

    if (localStorage.getItem("auth_token")) {
        return <Navigate to="/esquenta" replace />;
    }

    async function login(event) {
        event.preventDefault();
        setLogging(true);
        setErro("");
        try {
            const session = await authApi.login(email, password);
            saveSession(session);
            navigate("/esquenta", { replace: true });
        } catch (error) {
            setErro(error.message);
        } finally {
            setLogging(false);
        }
    }

    return (
        <div className="login-container">
            <form className="login-form" onSubmit={login}>
                <img src="../../../assets/simbolo_pl.svg" alt="Símbolo do PL" />
                <div className="login-text" style={{ textAlign: "center" }}>
                    <p
                        className="montserrat-semibold"
                        style={{ fontSize: "1.75rem" }}
                    >
                        Bem-vindo de volta!
                    </p>
                    <p
                        className="montserrat-regular"
                        style={{ fontSize: "1rem", color: "#666666" }}
                    >
                        Faça login para continuar
                    </p>
                </div>
                {erro && <p className="login-error">{erro}</p>}
                <div className="input-fields">
                    <div className="input-container">
                        <label htmlFor="email" className="montserrat-semibold">
                            Email
                        </label>
                        <input
                            type="email"
                            id="email"
                            value={email}
                            onChange={(event) => setEmail(event.target.value)}
                            placeholder="seuemail@gmail.com"
                            autoComplete="email"
                            required
                        />
                    </div>
                    <div className="input-container">
                        <label
                            htmlFor="password"
                            className="montserrat-semibold"
                        >
                            Senha
                        </label>
                        <input
                            type="password"
                            id="password"
                            value={password}
                            onChange={(event) => setPassword(event.target.value)}
                            placeholder="Digite sua senha"
                            autoComplete="current-password"
                            minLength={8}
                            required
                        />
                    </div>
                </div>
                <button
                    type="submit"
                    className="login-button montserrat-semibold"
                    disabled={logging}
                >
                    {logging ? "Acessando..." : "Acessar agora"}
                </button>
            </form>
        </div>
    );
}
