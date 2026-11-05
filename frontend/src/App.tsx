console.log("🔥🔥🔥 ATUALIZACAO FORCADA CARREGADA EM 20261104_220437 🔥🔥🔥");
import ChassiTemplates from "@/pages/ChassiTemplates";
import PneuMarcas from "@/pages/PneuMarcas";
import PneuMedidas from "@/pages/PneuMedidas";
import Frota from "@/pages/Frota";
import { BrowserRouter, Routes, Route, Navigate, Outlet } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "sonner";

import AppLayout from "@/components/layout/AppLayout";
import Login from "@/pages/Login";

import Dashboard from "@/pages/Dashboard";
import Abastecimentos from "@/pages/Abastecimentos";
import PlanosManutencao from "@/pages/PlanosManutencao";
import RelatorioManutencao from "@/pages/RelatorioManutencao";
import Agendamento from "@/pages/Agendamento";
import Manutencoes from "@/pages/Manutencoes";
import CentralAlertas from "@/pages/CentralAlertas";
import TiposFornecedores from "@/pages/TiposFornecedores";
import Fornecedores from "@/pages/Fornecedores";
import RelatorioFornecedores from "@/pages/RelatorioFornecedores";
import Veiculos from "@/pages/Veiculos";
import Carretas from "@/pages/Carretas";
import Motoristas from "@/pages/Motoristas";
import Combustiveis from "@/pages/Combustiveis";
import Acoplamentos from "@/pages/Acoplamentos";
import Empresa from "@/pages/Empresa";
import Parametrizacao from "@/pages/Parametrizacao";
import Perfil from "@/pages/Perfil";
import Base from "@/pages/Base";
import Financeiro from "@/pages/Financeiro";
import RelatorioCustosVeiculo from '@/pages/RelatorioCustosVeiculo';
import RelatorioEstoque from "@/pages/RelatorioEstoque";
import Estoque from "@/pages/Estoque";
import ModelosPneus from "@/pages/ModelosPneus";
import Pneus from "@/pages/Pneus";
import VeiculoDetalhe from "@/pages/VeiculoDetalhe";
import BuscaVeiculo360 from "@/pages/BuscaVeiculo360";
import RelatoriosPneus from "@/pages/RelatoriosPneus";
import Monitoramento from "@/pages/Monitoramento";
import Usuarios from "@/pages/Usuarios";
import Perfis from "@/pages/Perfis";
import Auditoria from "@/pages/Auditoria";
import Avisos from "@/pages/Avisos";
import Seguranca from "@/pages/Seguranca";
import { useMe } from "@/hooks/useSession";

const queryClient = new QueryClient();

function ProtectedRoute() {
  const { data: me, isLoading, isError } = useMe();

  if (isLoading) {
    return <div className="flex h-screen items-center justify-center bg-slate-950 text-slate-400">Carregando...</div>;
  }

  // Se der erro (401) ou não tiver usuário, manda pro login
  if (isError || !me) {
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
          <Route path="/alertas" element={<CentralAlertas />} />
              <Route path="/cadastros/pneu-medidas" element={<PneuMedidas />} />
              <Route path="/cadastros/pneu-marcas" element={<PneuMarcas />} />
              <Route path="/cadastros/chassi-templates" element={<ChassiTemplates />} />
              <Route path="/frota" element={<Frota />} />
              <Route path="/financeiro" element={<Financeiro />} />
              <Route path="/frota" element={<Frota />} />
              <Route path="/financeiro" element={<Financeiro />} />
              <Route path="/abastecimentos" element={<Abastecimentos />} />
              <Route path="/cadastros/planos-manutencao" element={<PlanosManutencao />} />
              <Route path="/relatorio-manutencao" element={<RelatorioManutencao />} />
              <Route path="/agendamento" element={<Agendamento />} />
              
              <Route path="/financeiro" element={<Financeiro />} />
              <Route path="/gestao/veiculo-360" element={<BuscaVeiculo360 />} />
          <Route path="/cadastros/veiculos/:id" element={<VeiculoDetalhe />} />
          <Route path="/cadastros/veiculos" element={<Veiculos />} />
              <Route path="/cadastros/carretas" element={<Carretas />} />
              <Route path="/cadastros/motoristas" element={<Motoristas />} />
              <Route path="/cadastros/combustiveis" element={<Combustiveis />} />
              <Route path="/cadastros/fornecedores" element={<Fornecedores />} />
              <Route path="/cadastros/tipos-fornecedores" element={<TiposFornecedores />} />
              <Route path="/cadastros/acoplamentos" element={<Acoplamentos />} />
              <Route path="/admin/empresa" element={<Empresa />} />
              <Route path="/perfil" element={<Perfil />} />
          
              <Route path="/admin/base" element={<Base />} />
              <Route path="/admin/manutencoes" element={<Manutencoes />} />
          
          
              <Route path="/admin/auditoria" element={<Auditoria />} />
              <Route path="/admin/avisos" element={<Avisos />} />
              <Route path="/admin/seguranca" element={<Seguranca />} />
              <Route path="/relatorios/custos-veiculo" element={<RelatorioCustosVeiculo />} />
              <Route path="/relatorios/estoque" element={<RelatorioEstoque />} />
              <Route path="/relatorios/fornecedores" element={<RelatorioFornecedores />} />
              <Route path="/operacao/estoque" element={<Estoque />} />
              <Route path="/cadastros/pneu-modelos" element={<ModelosPneus />} />
              <Route path="/operacao/pneus" element={<Pneus />} />
          <Route path="/operacao/relatorios-pneus" element={<RelatoriosPneus />} />
              <Route path="/operacao/monitoramento" element={<Monitoramento />} />
            </Route>
          </Route>
          
        {/* Rotas de Administração Protegidas */}
        <Route element={<ProtectedRoute modulo="Administração" />}>
          <Route path="/admin/usuarios" element={<Usuarios />} />
          <Route path="/admin/perfis" element={<Perfis />} />
          <Route path="/admin/parametrizacao" element={<Parametrizacao />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
      <Toaster position="top-right" richColors />
    </QueryClientProvider>
  );
}
