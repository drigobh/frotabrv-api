import os
import re

def fix_backend(raiz):
    # 1. Atualizar Modelo de Fornecedores
    model_path = os.path.join(raiz, "app", "backend", "models", "fornecedores.py")
    with open(model_path, 'w', encoding='utf-8') as f:
        f.write('''from pydantic import BaseModel, Field
from typing import Optional

class FornecedorCreate(BaseModel):
    nome: str = Field(min_length=2)
    cnpj: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    atividade: Optional[str] = None
    ativo: bool = True

class Fornecedor(FornecedorCreate):
    id: str
''')
    print("✅ Backend: Modelo de Fornecedor atualizado.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Fornecedores.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Corrigir o mapeamento da API no buscarCnpj
    c = c.replace(
        'cidade: data.municipio || s.cidade,\n        estado: data.uf || s.estado,',
        'cidade: data.municipio || data.cidade || s.cidade,\n        estado: data.uf || data.estado || s.estado,'
    )

    # 2. Atualizar o Grid para incluir CNPJ, Telefone, Cidade/UF e CNAE
    old_grid = '''<TableHead className="text-xs uppercase text-slate-500">Nome</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">CNPJ</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Cidade/UF</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Atividade</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-center">Ações</TableHead>'''
    
    new_grid = '''<TableHead className="text-xs uppercase text-slate-500">Nome / CNPJ</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Telefone</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Cidade/UF</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">CNAE / Atividade</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-center">Ações</TableHead>'''
    
    if old_grid in c:
        c = c.replace(old_grid, new_grid)

    # 3. Atualizar as células do Grid
    old_cells = '''<TableCell className="font-medium text-slate-200">{r.nome}</TableCell>
                <TableCell className="text-slate-400 font-mono text-xs">{r.cnpj || "—"}</TableCell>
                <TableCell className="text-slate-400 text-xs">{r.cidade ? `${r.cidade}/${r.estado}` : "—"}</TableCell>
                <TableCell className="text-slate-400 text-xs truncate max-w-[200px]" title={r.atividade}>{r.atividade || "—"}</TableCell>'''
    
    new_cells = '''<TableCell className="font-medium text-slate-200">
                  <div>{r.nome}</div>
                  <div className="text-slate-500 font-mono text-xs">{r.cnpj || "—"}</div>
                </TableCell>
                <TableCell className="text-slate-400 text-xs">{r.telefone || "—"}</TableCell>
                <TableCell className="text-slate-400 text-xs">{r.cidade ? `${r.cidade}/${r.estado}` : "—"}</TableCell>
                <TableCell className="text-slate-400 text-xs truncate max-w-[250px]" title={r.atividade}>{r.atividade || "—"}</TableCell>'''
    
    if old_cells in c:
        c = c.replace(old_cells, new_cells)

    # 4. Ajustar o colSpan da linha "Nenhum fornecedor"
    c = c.replace('colSpan={5}', 'colSpan={5}')

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend: Fornecedores corrigidos (Cidade/Estado e Grid).")

if __name__ == "__main__":
    raiz = os.getcwd()
    fix_backend(raiz)
    fix_frontend(raiz)