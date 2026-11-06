import os
import re

# ==========================================
# 1. BACKEND: ATUALIZAR A ROTA DE BANCOS
# ==========================================
path_back = os.path.join(os.getcwd(), "app", "backend", "routers", "cadastros_financeiros.py")

with open(path_back, "r", encoding="utf-8") as f:
    b_c = f.read()

# Atualiza a função criar_banco para aceitar todos os campos
nova_funcao = '''
@router.post("/bancos")
async def criar_banco(body: dict, _u: dict = Depends(require("write"))):
    novo = {
        "id": str(uuid.uuid4()),
        "nome": body.get("nome"),
        "agencia": body.get("agencia", ""),
        "numero_agencia": body.get("numero_agencia", ""),
        "conta": body.get("conta", ""),
        "telefone": body.get("telefone", ""),
        "contato": body.get("contato", ""),
        "whatsapp": body.get("whatsapp", ""),
        "saldo_inicial": float(body.get("saldo_inicial", 0))
    }
    await db.bancos.insert_one(novo)
    novo.pop("_id", None)
    return novo
'''

# Substitui a função antiga (se existir)
padrao = r'@router\.post\("/bancos"\)[\s\S]*?(?=@router|\Z)'
if re.search(padrao, b_c):
    b_c = re.sub(padrao, nova_funcao.strip() + "\n\n", b_c)
else:
    b_c += nova_funcao

with open(path_back, "w", encoding="utf-8") as f:
    f.write(b_c)
print("✅ Backend: Rota de bancos atualizada com os novos campos.")

# ==========================================
# 2. FRONTEND: ATUALIZAR O MODAL DE BANCO
# ==========================================
path_front = os.path.join(os.getcwd(), "frontend", "src", "pages", "CadastrosFinanceiros.tsx")

with open(path_front, "r", encoding="utf-8") as f:
    c = f.read()

# Atualizar o estado do formulário do banco
c = c.replace(
    'const [formBanco, setFormBanco] = useState({ nome: "", agencia: "", conta: "", saldo_inicial: "" });',
    'const [formBanco, setFormBanco] = useState({ nome: "", agencia: "", numero_agencia: "", conta: "", telefone: "", contato: "", whatsapp: "" });'
)

# Atualizar a função abrirNovo para incluir os campos
c = c.replace(
    'setFormBanco({ nome: "", agencia: "", conta: "", saldo_inicial: "" });',
    'setFormBanco({ nome: "", agencia: "", numero_agencia: "", conta: "", telefone: "", contato: "", whatsapp: "" });'
)

# Atualizar o modal para renderizar os novos campos
padrao_modal = r'\{/\* Modal de Banco \*/\}[\s\S]*?\{/\* Modal de Categoria \*/\}'

novo_modal = '''
      {/* Modal de Banco */}
      {modalBancoOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-md p-6">
            <h2 className="text-lg font-bold text-slate-100 mb-4">Novo Banco</h2>
            <div className="space-y-4">
              <div className="grid gap-1.5"><Label>Nome do Banco *</Label><Input value={formBanco.nome} onChange={(e) => setFormBanco(s => ({ ...s, nome: e.target.value }))} /></div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-1.5"><Label>Agência</Label><Input value={formBanco.agencia} onChange={(e) => setFormBanco(s => ({ ...s, agencia: e.target.value }))} /></div>
                <div className="grid gap-1.5"><Label>Nº da Agência</Label><Input value={formBanco.numero_agencia} onChange={(e) => setFormBanco(s => ({ ...s, numero_agencia: e.target.value }))} /></div>
              </div>
              
              <div className="grid gap-1.5"><Label>Conta</Label><Input value={formBanco.conta} onChange={(e) => setFormBanco(s => ({ ...s, conta: e.target.value }))} /></div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-1.5"><Label>Telefone</Label><Input value={formBanco.telefone} onChange={(e) => setFormBanco(s => ({ ...s, telefone: e.target.value }))} /></div>
                <div className="grid gap-1.5"><Label>WhatsApp</Label><Input value={formBanco.whatsapp} onChange={(e) => setFormBanco(s => ({ ...s, whatsapp: e.target.value }))} /></div>
              </div>
              
              <div className="grid gap-1.5"><Label>Contato</Label><Input value={formBanco.contato} onChange={(e) => setFormBanco(s => ({ ...s, contato: e.target.value }))} /></div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <Button variant="outline" onClick={() => setModalBancoOpen(false)}>Cancelar</Button>
              <Button onClick={() => salvarBanco.mutate(formBanco)} disabled={!formBanco.nome} className="bg-emerald-600 hover:bg-emerald-500 text-white">Salvar</Button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Categoria */}
'''

c = re.sub(padrao_modal, novo_modal, c)

with open(path_front, "w", encoding="utf-8") as f:
    f.write(c)
print("✅ Frontend: Modal de banco atualizado com todos os campos solicitados.")

print("\n✅ Tudo pronto! Faça o git push.")