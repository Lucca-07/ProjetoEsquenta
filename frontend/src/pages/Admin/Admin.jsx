import { useEffect, useState } from "react";
import { authApi } from "../../api/auth";
import Navbar from "../../components/Navbar/Navbar";
import "./Admin.css";

const INITIAL_FORM = {
    name: "",
    email: "",
    password: "",
    role: "USER",
};

export default function Admin() {
    const [users, setUsers] = useState([]);
    const [form, setForm] = useState(INITIAL_FORM);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [erro, setErro] = useState("");
    const [sucesso, setSucesso] = useState("");

    async function loadUsers() {
        try {
            setUsers(await authApi.listUsers());
            setErro("");
        } catch (error) {
            setErro(error.message);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        const initialLoad = setTimeout(loadUsers, 0);
        return () => clearTimeout(initialLoad);
    }, []);

    function updateField(event) {
        const { name, value } = event.target;
        setForm((current) => ({ ...current, [name]: value }));
    }

    async function createUser(event) {
        event.preventDefault();
        setSaving(true);
        setErro("");
        setSucesso("");
        try {
            const created = await authApi.createUser(form);
            setUsers((current) => [created, ...current]);
            setForm(INITIAL_FORM);
            setSucesso(`Conta de ${created.name} criada com sucesso.`);
        } catch (error) {
            setErro(error.message);
        } finally {
            setSaving(false);
        }
    }

    return (
        <div className="admin-layout">
            <Navbar />
            <main className="admin-content">
                <div className="admin-container">
                    <header className="admin-header">
                        <span>Administração</span>
                        <h1>Contas de acesso</h1>
                        <p>
                            Crie contas e defina quem terá acesso administrativo
                            ao sistema.
                        </p>
                    </header>

                    <section className="admin-grid">
                        <form className="admin-form-card" onSubmit={createUser}>
                            <div>
                                <h2>Nova conta</h2>
                                <p>Preencha os dados do novo acesso.</p>
                            </div>
                            {erro && <p className="admin-message error">{erro}</p>}
                            {sucesso && (
                                <p className="admin-message success">{sucesso}</p>
                            )}
                            <label>
                                Nome
                                <input
                                    name="name"
                                    value={form.name}
                                    onChange={updateField}
                                    minLength={2}
                                    required
                                />
                            </label>
                            <label>
                                Email
                                <input
                                    name="email"
                                    type="email"
                                    value={form.email}
                                    onChange={updateField}
                                    required
                                />
                            </label>
                            <label>
                                Senha inicial
                                <input
                                    name="password"
                                    type="password"
                                    value={form.password}
                                    onChange={updateField}
                                    minLength={8}
                                    required
                                />
                            </label>
                            <label>
                                Cargo
                                <select
                                    name="role"
                                    value={form.role}
                                    onChange={updateField}
                                >
                                    <option value="USER">Usuário</option>
                                    <option value="ADMIN">Administrador</option>
                                </select>
                            </label>
                            <button type="submit" disabled={saving}>
                                {saving ? "Criando..." : "Criar conta"}
                            </button>
                        </form>

                        <section className="admin-users-card">
                            <div className="admin-users-header">
                                <div>
                                    <h2>Usuários cadastrados</h2>
                                    <p>{users.length} conta(s)</p>
                                </div>
                            </div>
                            <div className="admin-users-list">
                                {loading && <p>Carregando...</p>}
                                {!loading &&
                                    users.map((user) => (
                                        <article
                                            className="admin-user-row"
                                            key={user.id}
                                        >
                                            <div className="admin-user-avatar">
                                                {user.name[0].toUpperCase()}
                                            </div>
                                            <div className="admin-user-info">
                                                <strong>{user.name}</strong>
                                                <span>{user.email}</span>
                                            </div>
                                            <span
                                                className={`admin-role ${user.role.toLowerCase()}`}
                                            >
                                                {user.role === "ADMIN"
                                                    ? "ADM"
                                                    : "Usuário"}
                                            </span>
                                        </article>
                                    ))}
                            </div>
                        </section>
                    </section>
                </div>
            </main>
        </div>
    );
}
