import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import AppLayout from "@/components/layout/AppLayout";
import Login from "@/pages/Login";
import Dashboard from "@/pages/Dashboard";
import Abastecimentos from "@/pages/Abastecimentos";
import Pneus from "@/pages/Pneus";
import Veiculos from "@/pages/Veiculos";
import VeiculoDetalhe from "@/pages/VeiculoDetalhe";
import Manutencoes from "@/pages/Manutencoes";
import CentralAlertas from "@/pages/CentralAlertas";
import RelatoriosPneus from "@/pages/RelatoriosPneus";
import BuscaVeiculo360 from "@/pages/BuscaVeiculo360";
import Perfil from "@/pages/Perfil";
import Usuarios from "@/pages/Usuarios";
import Perfis from "@/pages/Perfis";
import Parametrizacao from "@/pages/Parametrizacao";

const queryClient = new QueryClient();

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          
          {/* Layout principal com Sidebar e Header */}
          <Route element={<AppLayout />}>
            {/* Rotas Públicas (qualquer usuário logado) */}
            <Route path="/" element={<Dashboard />} />
            <Route path="/perfil" element={<Perfil />} />
            <Route path="/alertas" element={<CentralAlertas />} />

            {/* Rotas Protegidas por Perfil */}
            <Route element={<ProtectedRoute modulo="Abastecimentos" />}>
              <Route path="/abastecimentos" element={<Abastecimentos />} />
            </Route>

            <Route element={<ProtectedRoute modulo="Pneus" />}>
              <Route path="/operacao/pneus" element={<Pneus />} />
            </Route>

            <Route element={<ProtectedRoute modulo="Frota" />}>
              <Route path="/cadastros/veiculos" element={<Veiculos />} />
              <Route path="/cadastros/veiculos/:id" element={<VeiculoDetalhe />} />
            </Route>

            <Route element={<ProtectedRoute modulo="Manutenção" />}>
              <Route path="/admin/manutencoes" element={<Manutencoes />} />
            </Route>

            <Route element={<ProtectedRoute modulo="Relatórios" />}>
              <Route path="/operacao/relatorios-pneus" element={<RelatoriosPneus />} />
              <Route path="/gestao/veiculo-360" element={<BuscaVeiculo360 />} />
            </Route>

            <Route element={<ProtectedRoute modulo="Administração" />}>
              <Route path="/admin/usuarios" element={<Usuarios />} />
              <Route path="/admin/perfis" element={<Perfis />} />
              <Route path="/admin/parametrizacao" element={<Parametrizacao />} />
            </Route>
          </Route>

          {/* Redirecionamento para rotas não encontradas */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
