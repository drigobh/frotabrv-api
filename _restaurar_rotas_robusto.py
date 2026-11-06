import os
import re

pages_dir = os.path.join(os.getcwd(), "frontend", "src", "pages")
paginas_existentes = [f.replace(".tsx", "") for f in os.listdir(pages_dir) if f.endswith(".tsx")]

print("📄 Páginas encontradas:", paginas_existentes)

# Mapeamento de rotas para páginas
rotas = {
    "/abastecimentos": "Abastecimentos",
    "/operacao/pneus": "Pneus",
    "/cadastros/veiculos": "Veiculos",
    "/cadastros/veiculos/:id": "VeiculoDetalhe",
    "/admin/manutencoes": "Manutencoes",
    "/alertas": "CentralAlertas",
    "/operacao/relatorios-pneus": "RelatoriosPneus",
    "/gestao/veiculo-360": "BuscaVeiculo360",
    "/perfil": "Perfil",
    "/admin/usuarios": "Usuarios",
    "/admin/perfis": "Perfis",
    "/admin/parametrizacao": "Parametrizacao",
    "/agendamento": "Agendamento",
    "/admin/avisos": "Avisos",
    "/admin/auditoria": "Auditoria",
    "/admin/base": "Base",
    "/admin/empresa": "Empresa",
    "/admin/seguranca": "Seguranca",
    "/cadastros/acoplamentos": "Acoplamentos",
    "/cadastros/carretas": "Carretas",
    "/cadastros/chassi-templates": "ChassiTemplates",
    "/cadastros/combustiveis": "Combustiveis",
    "/cadastros/fornecedores": "Fornecedores",
    "/cadastros/motoristas": "Motoristas",
    "/cadastros/planos-manutencao": "PlanosManutencao",
    "/cadastros/pneu-marcas": "PneuMarcas",
    "/cadastros/pneu-medidas": "PneuMedidas",
    "/cadastros/pneu-modelos": "ModelosPneus",
    "/cadastros/tipos-fornecedores": "TiposFornecedores",
    "/financeiro": "Financeiro",
    "/operacao/estoque": "Estoque",
    "/relatorio-manutencao": "RelatorioManutencao",
    "/relatorios/estoque": "RelatorioEstoque",
    "/relatorios/fornecedores": "RelatorioFornecedores",
}

# Filtrar apenas as rotas que têm página existente
rotas_validas = {rota: page for rota, page in rotas.items() if page in paginas_existentes}
rotas_invalidas = {rota: page for rota, page in rotas.items() if page not in paginas_existentes}

print("\n✅ Rotas válidas:", len(rotas_validas))
print("❌ Rotas inválidas (página não existe):", rotas_invalidas)

# Gerar o App.tsx
imports = "\n".join([f'import {page} from "@/pages/{page}";' for page in rotas_validas.values()])
imports = 'import Login from "@/pages/Login";\nimport Dashboard from "@/pages/Dashboard";\n' + imports

rotas_jsx = []
for rota, page in rotas_validas.items():
    rotas_jsx.append(f'              <Route path="{rota}" element={{<{page} />}} />')

rotas_jsx_str = "\n".join(rotas_jsx)

conteudo = f'''import {{ BrowserRouter, Routes, Route, Navigate }} from "react-router-dom";
import {{ QueryClient, QueryClientProvider }} from "@tanstack/react-query";
import AppLayout from "@/components/layout/AppLayout";
import {{ ProtectedRoute }} from "@/components/auth/ProtectedRoute";

{imports}

const queryClient = new QueryClient();

export default function App() {{
  return (
    <QueryClientProvider client={{queryClient}}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={{<Login />}} />
          
          <Route element={{<AppLayout />}}>
            <Route path="/" element={{<Dashboard />}} />
            <Route path="/perfil" element={{<Perfil />}} />
            <Route path="/alertas" element={{<CentralAlertas />}} />

            <Route element={{<ProtectedRoute modulo="Abastecimentos" />}}>
              <Route path="/abastecimentos" element={{<Abastecimentos />}} />
            </Route>

            <Route element={{<ProtectedRoute modulo="Pneus" />}}>
              <Route path="/operacao/pneus" element={{<Pneus />}} />
            </Route>

            <Route element={{<ProtectedRoute modulo="Frota" />}}>
{rotas_jsx_str}
            </Route>

            <Route element={{<ProtectedRoute modulo="Manutenção" />}}>
              <Route path="/admin/manutencoes" element={{<Manutencoes />}} />
            </Route>

            <Route element={{<ProtectedRoute modulo="Relatórios" />}}>
              <Route path="/operacao/relatorios-pneus" element={{<RelatoriosPneus />}} />
              <Route path="/gestao/veiculo-360" element={{<BuscaVeiculo360 />}} />
            </Route>

            <Route element={{<ProtectedRoute modulo="Administração" />}}>
              <Route path="/admin/usuarios" element={{<Usuarios />}} />
              <Route path="/admin/perfis" element={{<Perfis />}} />
              <Route path="/admin/parametrizacao" element={{<Parametrizacao />}} />
            </Route>
          </Route>

          <Route path="*" element={{<Navigate to="/" replace />}} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}}
'''

# Salvar
path_app = os.path.join(os.getcwd(), "frontend", "src", "App.tsx")
with open(path_app, "w", encoding="utf-8") as f:
    f.write(conteudo)

print("\n✅ App.tsx gerado com sucesso!")
print(f"📄 {len(rotas_validas)} rotas incluídas.")