import os
import re

raiz = os.getcwd()

# ============================================================
# 1. BACKEND: Garantir que a rota PUT está calculando os itens
# ============================================================
path_back = os.path.join(raiz, "app", "backend", "routers", "checklist.py")
with open(path_back, "r", encoding="utf-8") as f:
    c_back = f.read()

# Procura a rota PUT inteira
padrao_put = r'@router\.put\("/\{id\}"\)[\s\S]*?(?=@router|\Z)'
match = re.search(padrao_put, c_back)

if match:
    rota_atual = match.group(0)
    if "itens_corrigidos" not in rota_atual:
        print("⚠️ Rota PUT antiga encontrada. Substituindo por versão com detalhamento...")
        
        nova_rota = '''@router.put("/{id}")
async def editar_checklist(id: str, payload: ChecklistViagemCreate, _u: dict = Depends(require("write"))):
    try:
        antigo = await db.checklists.find_one({"id": id})
        if not antigo:
            raise HTTPException(404, "Checklist não encontrado")
            
        tem_falha = any(i.status == "Falha" for i in payload.itens)
        risco = "Alto" if tem_falha else "Baixo"
        
        estava_reprovado = antigo.get("status_geral") == "Reprovado"
        esta_aprovado = payload.status_geral == "Aprovado"
        
        update_data = {
            "veiculo_id": payload.veiculo_id,
            "motorista_id": payload.motorista_id,
            "itens": [item.model_dump() for item in payload.itens],
            "observacoes_gerais": payload.observacoes_gerais,
            "status_geral": payload.status_geral,
            "risco": risco
        }

        # Se foi corrigido (passou de Reprovado para Aprovado)
        if estava_reprovado and esta_aprovado:
            update_data["aprovado_por"] = _u.get("nome", "Sistema")
            update_data["data_aprovacao"] = datetime.now().isoformat()
            
            # Verifica exatamente quais itens mudaram de Falha para OK/N/A
            itens_corrigidos = []
            for item_novo in payload.itens:
                item_antigo = next((i for i in antigo["itens"] if i["nome"] == item_novo.nome and i["categoria"] == item_novo.categoria), None)
                if item_antigo and item_antigo["status"] == "Falha" and item_novo.status != "Falha":
                    itens_corrigidos.append({
                        "item": item_novo.nome,
                        "categoria": item_novo.categoria,
                        "de": "Falha",
                        "para": item_novo.status
                    })

            historico_antigo = antigo.get("historico_correcoes", [])
            historico_antigo.append({
                "data": datetime.now().isoformat(),
                "usuario": _u.get("nome", "Sistema"),
                "acao": "Correção e Aprovação",
                "veiculo_id": payload.veiculo_id,
                "motorista_id": payload.motorista_id,
                "itens_corrigidos": itens_corrigidos
            })
            update_data["historico_correcoes"] = historico_antigo

        await db.checklists.update_one({"id": id}, {"$set": update_data})
        return {"ok": True}
    except Exception as e:
        raise HTTPException(400, f"Erro ao editar checklist: {str(e)}")
'''
        c_back = c_back.replace(rota_atual, nova_rota)
        with open(path_back, "w", encoding="utf-8", newline="\n") as f:
            f.write(c_back)
        print("✅ Backend: Rota PUT atualizada para gravar detalhes.")
    else:
        print("ℹ️ Backend: Rota PUT já está com o detalhamento.")
else:
    print("❌ Backend: Rota PUT não encontrada.")

# ============================================================
# 2. FRONTEND: Garantir que o modal exibe os itens
# ============================================================
path_front = os.path.join(raiz, "frontend", "src", "pages", "ChecklistViagem.tsx")
with open(path_front, "r", encoding="utf-8") as f:
    c_front = f.read()

if "h.itens_corrigidos" not in c_front:
    print("⚠️ Frontend: Modal não está exibindo os detalhes. Injetando...")
    # Procura o bloco do histórico no modal
    padrao_hist = r'<div key=\{i\} className="bg-slate-800/50 p-3 rounded-lg border border-slate-700">[\s\S]*?</div>\n\s*\)\)}'
    match_hist = re.search(padrao_hist, c_front)
    
    if match_hist:
        novo_bloco_hist = '''<div key={i} className="bg-slate-800/50 p-3 rounded-lg border border-slate-700">
                  <p className="text-sm font-bold text-emerald-400">{h.acao} por {h.usuario}</p>
                  <p className="text-xs text-slate-400 mt-1">{new Date(h.data).toLocaleString("pt-BR")}</p>
                  <p className="text-xs text-slate-300 mt-2">Veículo: {veiculos.find((v: any) => v.id === h.veiculo_id)?.placa} | Motorista: {motoristas.find((m: any) => m.id === h.motorista_id)?.nome}</p>
                  
                  {h.itens_corrigidos && h.itens_corrigidos.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-slate-700">
                      <p className="text-[10px] uppercase text-slate-500 font-bold mb-2">O que foi corrigido:</p>
                      <ul className="space-y-1">
                        {h.itens_corrigidos.map((ic: any, j: number) => (
                          <li key={j} className="text-xs text-slate-300 flex items-center gap-2">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                            <span><b>{ic.categoria}:</b> {ic.item} (de {ic.de} para {ic.para})</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}'''
        c_front = c_front.replace(match_hist.group(0), novo_bloco_hist)
        with open(path_front, "w", encoding="utf-8", newline="\n") as f:
            f.write(c_front)
        print("✅ Frontend: Modal atualizado para exibir detalhes.")
    else:
        print("❌ Frontend: Padrão do histórico no modal não encontrado.")
else:
    print("ℹ️ Frontend: Modal já está exibindo os detalhes.")

print("✅ Script concluído. Faça o commit e push.")