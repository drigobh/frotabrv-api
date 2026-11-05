import os
import re

# ==========================================
# 1. INJETAR A PROP "extraActions" NO CADASTROTABLE
# ==========================================
path_table = os.path.join(os.getcwd(), "frontend", "src", "components", "cadastros", "CadastroTable.tsx")

with open(path_table, "r", encoding="utf-8") as f:
    c_table = f.read()

# Adiciona a prop extraActions na tipagem (interface ou type)
if "extraActions?:" not in c_table:
    # Procura a definição das Props
    match_props = re.search(r'(type\s+\w*Props\s*<.*?>\s*=\s*\{|interface\s+\w*Props\s*<.*?>\s*\{)', c_table)
    if match_props:
        c_table = c_table.replace(match_props.group(1), match_props.group(1) + "\n  extraActions?: (row: T) => React.ReactNode;")
    else:
        # Fallback se a tipagem for diferente
        c_table = c_table.replace("export function CadastroTable", "type ExtraProps<T> = { extraActions?: (row: T) => React.ReactNode };\nexport function CadastroTable")

# Adiciona a renderização do extraActions na célula de ações
# Vamos procurar a tag <TableCell> que tem o botão de excluir ou editar
if "extraActions" not in c_table.split("return (")[1]:
    # Padrão comum do Shadcn: <div className="flex ..."> <Edit/> <Delete/> </div>
    padrao_acoes = re.search(r'(<div[^>]*className="[^"]*flex[^"]*items-center[^"]*"[^>]*>\s*)(.*?)(</div>)', c_table, re.DOTALL)
    
    if padrao_acoes:
        # Injeta o extraActions logo no início da div de ações
        c_table = c_table.replace(padrao_acoes.group(1), padrao_acoes.group(1) + "\n                {extraActions && extraActions(row)}")
        print("✅ Renderização de extraActions injetada na tabela.")
    else:
        print("⚠️ Não achei a div de ações no CadastroTable. Verifique o arquivo.")

# Adicionar extraActions na desestruturação das props (onde recebe os parâmetros)
if "extraActions," not in c_table:
    # Procura a função do componente
    match_func = re.search(r'export function CadastroTable<[^>]+>\(\{([^}]+)\}\)', c_table)
    if match_func:
        c_table = c_table.replace(match_func.group(1), match_func.group(1) + ", extraActions")
        
with open(path_table, "w", encoding="utf-8") as f:
    f.write(c_table)
print("✅ CadastroTable.tsx atualizado!")

# ==========================================
# 2. USAR O extraActions NO VEICULOS.TSX
# ==========================================
path_veiculos = os.path.join(os.getcwd(), "frontend", "src", "pages", "Veiculos.tsx")

with open(path_veiculos, "r", encoding="utf-8") as f:
    c_veic = f.read()

# Garantir imports do useNavigate e Eye
if "useNavigate" not in c_veic:
    c_veic = c_veic.replace('import { useQuery } from "@tanstack/react-query";', 'import { useNavigate } from "react-router-dom";\nimport { useQuery } from "@tanstack/react-query";')
if "Eye" not in c_veic:
    c_veic = c_veic.replace('import { num } from "@/lib/format";', 'import { Eye } from "lucide-react";\nimport { Button } from "@/components/ui/button";\nimport { num } from "@/lib/format";')

# Adicionar a prop extraActions passando o botão
if "extraActions={" not in c_veic:
    # Vamos inserir dentro do componente <CadastroTable>
    ancora = 'searchKeys={["placa", "modelo"]}'
    novo_codigo = ancora + '''
      extraActions={(v) => (
        <Button size="icon-sm" variant="ghost" onClick={() => navigate(`/cadastros/veiculos/${v.id}`)} title="Visão 360º">
          <Eye className="size-4 text-emerald-400" />
        </Button>
      )}'''
    c_veic = c_veic.replace(ancora, novo_codigo)

with open(path_veiculos, "w", encoding="utf-8") as f:
    f.write(c_veic)
print("✅ Veiculos.tsx atualizado com o botão 'Visão 360º'!")