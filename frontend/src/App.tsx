import { BrowserRouter, Routes, Route, Navigate, Outlet } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "sonner";

import AppLayout from "@/components/layout/AppLayout";
import Login from "@/pages/Login";

import Dashboard from "@/pages/Dashboard";
import Abastecimentos from "@/pages/Abastecimentos";
import Manutencoes from "@/pages/Manutencoes";
import Fornecedores from "@/pages/Fornecedores";
import RelatorioFornecedores from "@/pages/RelatorioFornecedores";
import Veiculos from "@/pages/Veiculos";
import Carretas from "@/pages/Carretas";
import Motoristas from "@/pages/Motoristas";
import Combustiveis from "@/pages/Combustiveis";
import Acoplamentos from "@/pages/Acoplamentos";
import Base from "@/pages/Base";
import Pneus from "@/pages/Pneus";
import Monitoramento from "@/pages/Monitoramento";
import Estoque from "@/pages/Estoque";
import Financeiro from "@/pages/Financeiro";

const queryClient = new QueryClient();

function ProtectedRoute() {
  const token = localStorage.getItem("token");
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return <Outlet />;
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route element={<ProtectedRoute />}>
            <Route element={<AppLayout />}>
              <Route path="/" element={<Dashboard />} />
              <Route path="/abastecimentos" element={<Abastecimentos />} />
              <Route path="/manutencoes" element={<Manutencoes />} />
              <Route path="/operacao/pneus" element={<Pneus />} />
              <Route path="/operacao/monitoramento" element={<Monitoramento />} />
              <Route path="/operacao/estoque" element={<Estoque />} />
              <Route path="/financeiro" element={<Financeiro />} />
              <Route path="/cadastros/veiculos" element={<Veiculos />} />
              <Route path="/cadastros/carretas" element={<Carretas />} />
              <Route path="/cadastros/motoristas" element={<Motoristas />} />
              <Route path="/cadastros/combustiveis" element={<Combustiveis />} />
              <Route path="/cadastros/fornecedores" element={<Fornecedores />} />
              <Route path="/cadastros/acoplamentos" element={<Acoplamentos />} />
              <Route path="/admin/base" element={<Base />} />
              <Route path="/relatorios/fornecedores" element={<RelatorioFornecedores />} />
            </Route>
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
      <Toaster position="top-right" richColors />
    </QueryClientProvider>
  );
}
