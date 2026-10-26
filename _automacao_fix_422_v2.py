import os

def fix_backend(raiz):
    # 1. Tornar 'posto' opcional no Modelo
    caminho_model = os.path.join(raiz, "app", "backend", "models", "abastecimentos.py")
    with open(caminho_model, 'r', encoding='utf-8') as f:
        c = f.read()
    
    if 'posto: str = Field(min_length=1)' in c:
        c = c.replace('posto: str = Field(min_length=1)', 'posto: str | None = None')
        with open(caminho_model, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: Campo 'posto' agora é opcional.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Atualizar o payload de salvamento para enviar o fornecedor como posto e remover campos extras
    padrao_payload = r'const payload = \{ data: form.data, veiculo_id: form.veiculo_id,.*?\};'
    novo_payload = '''const payload = { 
        data: form.data, 
        veiculo_id: form.veiculo_id, 
        motorista_id: form.motorista_id === NENHUM ? null : form.motorista_id, 
        litros: Number(form.litros.replace(",", ".")), 
        preco_litro: Number(form.preco_litro.replace(",", ".")), 
        posto: form.fornecedor || "Importado", // <-- Garante que o campo obrigatório seja preenchido
        km: Number(form.km), 
        observacoes: form.observacoes, 
        numero_nf: form.numero_nf || null, 
        chave_nfe: form.chave_nfe || null, 
        hora: form.hora || null, 
        cnpj: form.cnpj || null, 
        fornecedor: form.fornecedor || null, 
        cidade: form.cidade || null,
        estado: form.estado || null,
        produto: form.produto || "DIESEL",
        origem: form.origem 
      };'''
    import re
    c = re.sub(padrao_payload, novo_payload, c, flags=re.DOTALL)

    # 2. Ajustar o DialogContent para não ter barra de rolagem ou ser mais compacto
    c = c.replace(
        '<DialogContent className="sm:max-w-lg max-h-[90vh] overflow-y-auto">',
        '<DialogContent className="sm:max-w-xl max-h-[95vh] overflow-y-auto p-4 sm:p-6">'
    )

    # 3. Reduzir o espaçamento do formulário e juntar alguns campos
    c = c.replace('className="grid grid-cols-2 gap-3"', 'className="grid grid-cols-2 gap-2"')
    
    # 4. Deixar o campo de avaliação mais compacto (inline)
    c = c.replace(
        '''<div className="col-span-2 grid gap-1.5">
              <Label>Avaliação do Fornecedor</Label>
              <div className="flex gap-2 items-center">
                {[1, 2, 3, 4, 5].map(star => (
                  <button type="button" key={star} onClick={() => setForm(s => ({ ...s, avaliacao: star }))} className="focus:outline-none hover:scale-110">
                    <Star className={`size-5 ${star <= form.avaliacao ? 'fill-amber-400 text-amber-400' : 'text-slate-600'}`} />
                  </button>
                ))}
                <span className="text-xs text-slate-400 ml-2">{form.avaliacao === 0 ? "Sem avaliação" : `${form.avaliacao} de 5`}</span>
              </div>
            </div>''',
        '''<div className="col-span-2 flex items-center gap-3 bg-slate-900/30 p-2 rounded-lg border border-slate-800">
              <Label className="text-xs text-slate-400">Avaliação:</Label>
              <div className="flex gap-1 items-center">
                {[1, 2, 3, 4, 5].map(star => (
                  <button type="button" key={star} onClick={() => setForm(s => ({ ...s, avaliacao: star }))} className="focus:outline-none hover:scale-110">
                    <Star className={`size-4 ${star <= form.avaliacao ? 'fill-amber-400 text-amber-400' : 'text-slate-600'}`} />
                  </button>
                ))}
                <span className="text-[10px] text-slate-500 ml-1">{form.avaliacao === 0 ? "" : `${form.avaliacao}/5`}</span>
              </div>
            </div>'''
    )

    # 5. Diminuir a altura dos inputs para caber melhor
    c = c.replace('className="w-full p-2', 'className="w-full p-1.5')

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend: Payload corrigido, layout compactado e sem barra de rolagem.")

if __name__ == "__main__":
    raiz = os.getcwd()
    fix_backend(raiz)
    fix_frontend(raiz)