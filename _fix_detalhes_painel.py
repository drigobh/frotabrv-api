import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_DETALHES_PAINEL_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    caminho_abs = os.path.join(raiz, "frontend", "src", "components", "MapaFornecedores.tsx")
    if os.path.exists(caminho_abs):
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_abs, "frontend/src/components/MapaFornecedores.tsx")
        print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "components", "MapaFornecedores.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Remover o <Popup> do Marker (para não depender dele)
    padrao_popup = re.compile(r'<Popup>[\s\S]*?</Popup>')
    c = padrao_popup.sub('', c)
    print("✅ Popups removidos dos marcadores.")

    # 2. Adicionar o Painel de Detalhes flutuante
    # Ele vai aparecer quando 'fornecedorFocado' estiver setado
    painel_html = '''
        {/* Painel de Detalhes do Fornecedor Focado */}
        {fornecedorFocado && (
          <div className="absolute bottom-4 left-4 right-4 z-[1000] bg-slate-900/95 border border-slate-700 rounded-xl shadow-2xl p-4 backdrop-blur-sm">
            <div className="flex justify-between items-start mb-2">
              <h3 className="text-lg font-bold text-slate-100">{fornecedorFocado.nome}</h3>
              <button onClick={() => setFornecedorFocado(null)} className="text-slate-400 hover:text-white">
                <X className="size-5" />
              </button>
            </div>
            
            <div className="grid grid-cols-2 gap-4 text-sm text-slate-300">
              <div>
                <p><strong className="text-slate-400">Endereço:</strong> {fornecedorFocado.endereco || "—"}</p>
                <p><strong className="text-slate-400">Cidade:</strong> {fornecedorFocado.cidade} - {fornecedorFocado.estado}</p>
                <p><strong className="text-slate-400">Contato:</strong> {fornecedorFocado.contato || "—"}</p>
                <p><strong className="text-slate-400">WhatsApp:</strong> {fornecedorFocado.whatsapp || "—"}</p>
              </div>
              
              {/* Se for do tipo Combustível, mostra o último abastecimento */}
              {ultimoAbastecimento && !ultimoAbastecimento.mensagem && (
                <div className="border-l border-slate-700 pl-4">
                  <p className="font-bold text-sky-400 mb-1">Último Abastecimento:</p>
                  <p><strong className="text-slate-400">Data:</strong> {new Date(ultimoAbastecimento.data).toLocaleDateString('pt-BR')}</p>
                  <p><strong className="text-slate-400">Combustível:</strong> {ultimoAbastecimento.produto}</p>
                  <p><strong className="text-slate-400">Motorista:</strong> {ultimoAbastecimento.motorista_label || "—"}</p>
                  <p><strong className="text-slate-400">Cavalo:</strong> {ultimoAbastecimento.veiculo_label || "—"}</p>
                  <p><strong className="text-slate-400">Carreta:</strong> {ultimoAbastecimento.carreta_label || "—"}</p>
                </div>
              )}
            </div>
          </div>
        )}
'''
    
    # Adiciona o painel antes do fechamento da div do mapa
    if 'Painel de Detalhes do Fornecedor Focado' not in c:
        c = c.replace(
            '          </div>\n        </div>\n      </div>\n    </div>\n  );',
            '          </div>\n' + painel_html + '        </div>\n      </div>\n    </div>\n  );'
        )
        print("✅ Painel de Detalhes adicionado.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Componente atualizado.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)
    print("\n✅ Script aplicado com sucesso!")