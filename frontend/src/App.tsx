import { Navigate, Route, Routes } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
import AppLayout from "@/components/layout/AppLayout";
import Login from "@/pages/Login";
import Dashboard from "@/pages/Dashboard";
import Veiculos from "@/pages/Veiculos";
import Carretas from "@/pages/Carretas";
import Motoristas from "@/pages/Motoristas";
import Acoplamentos from "@/pages/Acoplamentos";
import Abastecimentos from "@/pages/Abastecimentos";
import Manutencoes from "@/pages/Manutencoes";
import Documentos from "@/pages/Documentos";
import Financeiro from "@/pages/Financeiro";
import Ranking from "@/pages/Ranking";
import Relatorios from "@/pages/Relatorios";
import Usuarios from "@/pages/Usuarios";
import Auditoria from "@/pages/Auditoria";
import Avisos from "@/pages/Avisos";
import Seguranca from "@/pages/Seguranca";

// Uma rota por menu; cada tela vive em src/pages/<Menu>.tsx.
export default function App() {
  return (
    <>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route element={<AppLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="cadastros/veiculos" element={<Veiculos />} />
          <Route path="cadastros/carretas" element={<Carretas />} />
          <Route path="cadastros/motoristas" element={<Motoristas />} />
          <Route path="acoplamentos" element={<Acoplamentos />} />
          <Route path="abastecimentos" element={<Abastecimentos />} />
          <Route path="manutencoes" element={<Manutencoes />} />
          <Route path="documentos" element={<Documentos />} />
          <Route path="financeiro" element={<Financeiro />} />
          <Route path="ranking" element={<Ranking />} />
          <Route path="relatorios" element={<Relatorios />} />
          <Route path="usuarios" element={<Usuarios />} />
          <Route path="auditoria" element={<Auditoria />} />
          <Route path="avisos" element={<Avisos />} />
          <Route path="seguranca" element={<Seguranca />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <Toaster richColors />
    </>
  );
}
