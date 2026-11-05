import os

# 1. Backend: Rota de Atualização do Perfil
path_backend = os.path.join(os.getcwd(), "app", "backend", "routers", "auth.py")

with open(path_backend, "r", encoding="utf-8") as f:
    c = f.read()

if "/perfil" not in c:
    rota = '''

@router.put("/perfil")
async def atualizar_perfil(body: dict, _u: dict = Depends(require("read"))):
    # Atualiza nome e telefone
    update_data = {}
    if "nome" in body: update_data["nome"] = body["nome"]
    if "telefone" in body: update_data["telefone"] = body["telefone"]
    
    if update_data:
        await db.usuarios.update_one({"id": _u["id"]}, {"$set": update_data})
    
    # Atualiza senha (se fornecida)
    if body.get("nova_senha"):
        import bcrypt
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(body["nova_senha"].encode('utf-8'), salt)
        await db.usuarios.update_one(
            {"id": _u["id"]}, 
            {"$set": {"senha": hashed.decode('utf-8')}}
        )
    
    return {"status": "ok", "message": "Perfil atualizado com sucesso!"}
'''
    c += rota
    if "import bcrypt" not in c:
        c = "import bcrypt\n" + c
    with open(path_backend, "w", encoding="utf-8") as f:
        f.write(c)
    print("✅ Backend: Rota PUT /auth/perfil criada.")

# 2. Frontend: Conectar o botão Salvar
path_front = os.path.join(os.getcwd(), "frontend", "src", "pages", "Perfil.tsx")

with open(path_front, "r", encoding="utf-8") as f:
    c_front = f.read()

# Importar apiPut
if "apiPut" not in c_front:
    c_front = c_front.replace(
        'import { toast } from "sonner";',
        'import { apiPut } from "@/lib/api";\nimport { toast } from "sonner";'
    )

# Adicionar a mutation de salvar
if "const salvarPerfil" not in c_front:
    c_front = c_front.replace(
        'const [abaAtiva, setAbaAtiva] = useState<typeof abas[number]>("Meus Dados");',
        '''const [abaAtiva, setAbaAtiva] = useState<typeof abas[number]>("Meus Dados");
  const [nome, setNome] = useState(me?.nome || "");
  const [telefone, setTelefone] = useState("(11) 99999-9999");
  const [senhaAtual, setSenhaAtual] = useState("");
  const [novaSenha, setNovaSenha] = useState("");
  
  const salvarPerfil = async () => {
    try {
      const payload: any = { nome, telefone };
      if (novaSenha && novaSenha === senhaAtual) payload.nova_senha = novaSenha;
      
      await apiPut("/auth/perfil", payload);
      toast.success("Perfil atualizado com sucesso!");
    } catch (e: any) {
      toast.error(e.message || "Erro ao salvar perfil");
    }
  };'''
    )

# Conectar o botão "Salvar Alterações"
c_front = c_front.replace(
    'onClick={() => toast.success("Alterações salvas com sucesso!")}',
    'onClick={salvarPerfil}'
)

# Conectar os inputs aos estados
c_front = c_front.replace(
    '<Input defaultValue={me?.nome || "Rodrigo Admin"} className="bg-slate-950 border-slate-700 h-10" />',
    '<Input value={nome} onChange={(e) => setNome(e.target.value)} className="bg-slate-950 border-slate-700 h-10" />'
)
c_front = c_front.replace(
    '<Input defaultValue="(11) 99999-9999" className="bg-slate-950 border-slate-700 h-10" />',
    '<Input value={telefone} onChange={(e) => setTelefone(e.target.value)} className="bg-slate-950 border-slate-700 h-10" />'
)

with open(path_front, "w", encoding="utf-8") as f:
    f.write(c_front)
    print("✅ Frontend: Tela de Perfil conectada ao backend.")