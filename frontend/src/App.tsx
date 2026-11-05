import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createBrowserRouter, RouterProvider, Navigate } from "react-router-dom";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { AppLayout } from "@/components/layout/AppLayout";
import Login from "@/pages/Login";
import Dashboard from "@/pages/Dashboard";
import Abastecimentos from "@/pages/Abastecimentos";
import Pneus from "@/pages/Pneus";
import Veiculos from "@/pages/Veiculos";
import Manutencoes from "@/pages/Manutencoes";
import Parametrizacao from "@/pages/Parametrizacao";
import CentralAlertas from "@/pages/CentralAlertas";
import RelatoriosPneus from "@/pages/RelatoriosPneus";
import VeiculoDetalhe from "@/pages/VeiculoDetalhe";
import BuscaVeiculo360 from "@/pages/BuscaVeiculo360";
import Perfil from "@/pages/Perfil";
import Usuarios from "@/pages/Usuarios";
import Perfis from "@/pages/Perfis";

const queryClient = new QueryClient();

const router = createBrowserRouter([
  {
    path: "/login",
    element: <Login />,
  },
  {
    path: "/",
    element: <AppLayout />,
    children: [
      { index: true, element: <Dashboard /> },
      
      // Rotas de Operação
      {
        element: <ProtectedRoute modulo="Abastecimentos" />,
        children: [{ path: "abastecimentos", element: <Abastecimentos /> }]
      },
      {
        element: <ProtectedRoute modulo="Pneus" />,
        children: [{ path: "operacao/pneus", element: <Pneus /> }]
      },
      {
        element: <ProtectedRoute modulo="Frota" />,
        children: [
          { path: "cadastros/veiculos", element: <Veiculos /> },
          { path: "cadastros/veiculos/:id", element: <VeiculoDetalhe /> }
        ]
      },
      {
        element: <ProtectedRoute modulo="Manutenção" />,
        children: [{ path: "admin/manutencoes", element: <Manutencoes /> }]
      },
      
      // Rotas de Gestão
      {
        element: <ProtectedRoute modulo="Relatórios" />,
        children: [
          { path: "operacao/relatorios-pneus", element: <RelatoriosPneus /> },
          { path: "gestao/veiculo-360", element: <BuscaVeiculo360 /> }
        ]
      },
      {
        element: <ProtectedRoute modulo="Relatórios" />,
        children: [{ path: "alertas", element: <CentralAlertas /> }]
      },
      
      // Rotas de Administração (Protegidas)
      {
        element: <ProtectedRoute modulo="Administração" />,
        children: [
          { path: "admin/usuarios", element: <Usuarios /> },
          { path: "admin/perfis", element: <Perfis /> },
          { path: "admin/parametrizacao", element: <Parametrizacao /> },
        ]
      },

      // Perfil (todos podem acessar)
      { path: "perfil", element: <Perfil /> },
    ],
  },
  {
    path: "*",
    element: <Navigate to="/" replace />,
  },
]);

const App = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <RouterProvider router={router} />
      </TooltipProvider>
    </QueryClientProvider>
  );
};

export default App;
