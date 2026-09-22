import { Routes, Route } from "react-router-dom";
import Landing from "./pages/Landing";
import FirstAccess from "./pages/FirstAccess";
import Login from "./pages/Login";
import ClientDashboard from "./pages/ClientDashboard";
import ContractView from "./pages/ContractView";
import History from "./pages/History";
import RenewalFlow from "./pages/RenewalFlow";
import AdminDashboard from "./pages/AdminDashboard";
import AdminClientNew from "./pages/AdminClientNew";
import ProtectedRoute from "./components/ProtectedRoute";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/primeiro-acesso" element={<FirstAccess />} />
      <Route path="/login" element={<Login />} />

      <Route path="/dashboard" element={<ProtectedRoute roles={["cliente"]}><ClientDashboard /></ProtectedRoute>} />
      <Route path="/historico" element={<ProtectedRoute roles={["cliente"]}><History /></ProtectedRoute>} />
      <Route path="/contratos/:id" element={<ProtectedRoute><ContractView /></ProtectedRoute>} />
      <Route path="/renovacao/:id" element={<ProtectedRoute><RenewalFlow /></ProtectedRoute>} />

      <Route path="/admin" element={<ProtectedRoute roles={["funcionario", "administrador"]}><AdminDashboard /></ProtectedRoute>} />
      <Route path="/admin/clientes/novo" element={<ProtectedRoute roles={["funcionario", "administrador"]}><AdminClientNew /></ProtectedRoute>} />

      <Route path="*" element={<Landing />} />
    </Routes>
  );
}
