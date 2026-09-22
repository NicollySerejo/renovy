import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Layout({ children }: { children: React.ReactNode }) {
  const { session, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="page">
      <div className="container">
        <div className="topbar">
          <Link to="/" className="brand">
            <span className="brand-mark">R</span> Portal de Renovação
          </Link>
          <div className="nav-links">
            {session ? (
              <>
                {session.role === "cliente" && <Link to="/dashboard" className="btn btn-ghost">Minha área</Link>}
                {(session.role === "funcionario" || session.role === "administrador") && (
                  <Link to="/admin" className="btn btn-ghost">Painel administrativo</Link>
                )}
                <button
                  className="btn btn-secondary"
                  onClick={() => {
                    logout();
                    navigate("/");
                  }}
                >
                  Sair
                </button>
              </>
            ) : (
              <Link to="/login" className="btn btn-primary">Acessar minha conta</Link>
            )}
          </div>
        </div>
        {children}
      </div>
    </div>
  );
}
