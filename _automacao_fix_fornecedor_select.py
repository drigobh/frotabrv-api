import os
import re

def fix_backend(raiz):
    caminho = os.path.join(raiz, "app", "backend", "server.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Garantir que o router de fornecedores está registrado
    if "fornecedores" not in c:
        c = c.replace("from routers import auth", "from routers import auth, fornecedores")
        c = c.replace("api_router.include_router(auth.router)", "api_router.include_router(auth.router)\napi_router.include_router(fornecedores.router)")
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: Router de Fornecedores registrado no server.py.")
    else:
        print("ℹ️ Backend: Router de Fornecedores já está registrado.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Manutencoes.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Garantir que a variável 'fornecedores' está sendo extraída da query
    if 'const fornecedores = fq.data' not in c:
        c = c.replace(
            'const fq = useQuery({ queryKey: ["fornecedores"], queryFn: () => apiGet<any[]>("/fornecedores") });',
            'const fq = useQuery({ queryKey: ["fornecedores"], queryFn: () => apiGet<any[]>("/fornecedores") });\n  const fornecedores = fq.data ?? [];'
        )

    # 2. Garantir que o FieldSelect do fornecedor existe e está mapeando corretamente
    # Vou substituir o bloco do campo "Oficina" pelo campo de Fornecedor de forma robusta
    padrao_oficina = re.compile(r'<div className="grid gap-1\.5"><Label>Oficina / prestador</Label>[\s\S]*?</div>', re.DOTALL)
    
    novo_campo_fornecedor = '''<div className="col-span-2 grid gap-1.5">
              <Label>Fornecedor / Oficina *</Label>
              <FieldSelect 
                value={form.fornecedor_id || ""} 
                onChange={(v) => setForm(s => ({ ...s, fornecedor_id: v }))} 
                options={fornecedores.map((f: any) => ({ value: f.id, label: f.nome }))} 
                placeholder="Selecione o prestador" 
                testId="manutencao-form-fornecedor" 
              />
            </div>'''
    
    if padrao_oficina.search(c):
        c = padrao_oficina.sub(novo_campo_fornecedor, c)

    # 3. Garantir que o fornecedor_id exista no estado inicial 'vazio'
    if 'fornecedor_id: "",' not in c:
        c = c.replace('oficina: "",', 'oficina: "",\n  fornecedor_id: "",')

    # 4. Garantir que o abrirEdicao carregue o fornecedor_id
    if 'fornecedor_id: (r as any).fornecedor_id || "",' not in c:
        c = c.replace('oficina: r.oficina || "",', 'oficina: r.oficina || "",\n      fornecedor_id: (r as any).fornecedor_id || "",')

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend: Select de Fornecedores corrigido.")

if __name__ == "__main__":
    raiz = os.getcwd()
    fix_backend(raiz)
    fix_frontend(raiz)