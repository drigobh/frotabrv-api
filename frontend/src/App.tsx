import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import AppLayout from "@/components/layout/AppLayout";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";

import Login from "@/pages/Login";
import Dashboard from "@/pages/Dashboard";
import Abastecimentos from "@/pages/Abastecimentos";
import Pneus from "@/pages/Pneus";
import Veiculos from "@/pages/Veiculos";
import VeiculoDetalhe from "@/pages/VeiculoDetalhe";
import Manutencoes from "@/pages/Manutencoes";
import CentralAlertas from "@/pages/CentralAlertas";
import RelatoriosPneus from "@/pages/RelatoriosPneus";
import Multas from "@/pages/Multas";
import LeitorQRCode from "@/pages/LeitorQRCode";
import BuscaVeiculo360 from "@/pages/BuscaVeiculo360";
import Perfil from "@/pages/Perfil";
import Usuarios from "@/pages/Usuarios";
import Perfis from "@/pages/Perfis";
import Parametrizacao from "@/pages/Parametrizacao";
import Agendamento from "@/pages/Agendamento";
import Avisos from "@/pages/Avisos";
import Auditoria from "@/pages/Auditoria";
import Base from "@/pages/Base";
import Empresa from "@/pages/Empresa";
import Seguranca from "@/pages/Seguranca";
import Acoplamentos from "@/pages/Acoplamentos";
import Carretas from "@/pages/Carretas";
import ChassiTemplates from "@/pages/ChassiTemplates";
import Combustiveis from "@/pages/Combustiveis";
import Fornecedores from "@/pages/Fornecedores";
import Motoristas from "@/pages/Motoristas";
import PlanosManutencao from "@/pages/PlanosManutencao";
import PneuMarcas from "@/pages/PneuMarcas";
import PneuMedidas from "@/pages/PneuMedidas";
import ModelosPneus from "@/pages/ModelosPneus";
import TiposFornecedores from "@/pages/TiposFornecedores";
import Financeiro from "@/pages/Financeiro";
import VisualizadorXML from "@/pages/VisualizadorXML";
import CadastrosFinanceiros from "@/pages/CadastrosFinanceiros";
import Estoque from "@/pages/Estoque";
import RelatorioManutencao from "@/pages/RelatorioManutencao";
import RelatorioEstoque from "@/pages/RelatorioEstoque";
import RelatorioFornecedores from "@/pages/RelatorioFornecedores";

const queryClient = new QueryClient();

export default function App() {
  if (typeof window !== 'undefined') {
    window.addEventListener('beforeunload', () => {
      localStorage.removeItem('token');
      sessionStorage.clear();
    });
  }

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />

          <Route element={<AppLayout />}>
            {/* Rotas Públicas (qualquer usuário logado) */}
            <Route path="/" element={<Dashboard />} />
            <Route path="/perfil" element={<Perfil />} />
            <Route path="/alertas" element={<CentralAlertas />} />
            <Route path="/financeiro" element={<Financeiro />} />
            <Route path="/financeiro/xml" element={<VisualizadorXML />} />
            <Route path="/cadastros/financeiro" element={<CadastrosFinanceiros />} />

            {/* Rotas Protegidas por Permissão */}
            <Route element={<ProtectedRoute modulo="Abastecimentos" />}>
              <Route path="/abastecimentos" element={<Abastecimentos />} />
            </Route>

            <Route element={<ProtectedRoute modulo="Pneus" />}>
              <Route path="/operacao/pneus" element={<Pneus />} />
            </Route>

            <Route element={<ProtectedRoute modulo="Frota" />}>
              <Route path="/cadastros/veiculos" element={<Veiculos />} />
              <Route path="/cadastros/veiculos/:id" element={<VeiculoDetalhe />} />
              <Route path="/admin/manutencoes" element={<Manutencoes />} />
              <Route path="/operacao/pneus/scanner" element={<LeitorQRCode />} />
              <Route path="/operacao/relatorios-pneus" element={<RelatoriosPneus />} />
              <Route path="/gestao/veiculo-360" element={<BuscaVeiculo360 />} />
              <Route path="/multas" element={<Multas />} />
              <Route path="/operacao/estoque" element={<Estoque />} />
              <Route path="/cadastros/acoplamentos" element={<Acoplamentos />} />
              <Route path="/cadastros/carretas" element={<Carretas />} />
              <Route path="/cadastros/chassi-templates" element={<ChassiTemplates />} />
              <Route path="/cadastros/combustiveis" element={<Combustiveis />} />
              <Route path="/cadastros/fornecedores" element={<Fornecedores />} />
              <Route path="/cadastros/motoristas" element={<Motoristas />} />
              <Route path="/cadastros/planos-manutencao" element={<PlanosManutencao />} />
              <Route path="/cadastros/pneu-marcas" element={<PneuMarcas />} />
              <Route path="/cadastros/pneu-medidas" element={<PneuMedidas />} />
              <Route path="/cadastros/pneu-modelos" element={<ModelosPneus />} />
              <Route path="/cadastros/tipos-fornecedores" element={<TiposFornecedores />} />
            </Route>

            <Route element={<ProtectedRoute modulo="Manutenção" />}>
              <Route path="/agendamento" element={<Agendamento />} />
            </Route>

            <Route element={<ProtectedRoute modulo="Relatórios" />}>
              <Route path="/relatorio-manutencao" element={<RelatorioManutencao />} />
              <Route path="/relatorios/estoque" element={<RelatorioEstoque />} />
              <Route path="/relatorios/fornecedores" element={<RelatorioFornecedores />} />
            </Route>

            <Route element={<ProtectedRoute modulo="Administração" />}>
              <Route path="/admin/usuarios" element={<Usuarios />} />
              <Route path="/admin/perfis" element={<Perfis />} />
              <Route path="/admin/parametrizacao" element={<Parametrizacao />} />
              <Route path="/admin/avisos" element={<Avisos />} />
              <Route path="/admin/auditoria" element={<Auditoria />} />
              <Route path="/admin/base" element={<Base />} />
              <Route path="/admin/empresa" element={<Empresa />} />
              <Route path="/admin/seguranca" element={<Seguranca />} />
            </Route>
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}