import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_POPUP_PURO_{agora}.zip")
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

    # 1. Substituir o conteúdo do Popup por HTML puro com estilos inline
    padrao_popup = re.compile(r'<Popup>[\s\S]*?</Popup>')
    
    novo_popup = '''<Popup>
                      <div style={{ fontFamily: 'Arial, sans-serif', fontSize: '13px', lineHeight: '1.4' }}>
                        <div style={{ fontWeight: 'bold', fontSize: '14px', borderBottom: '1px solid #ccc', paddingBottom: '4px', marginBottom: '6px' }}>
                          {f.nome}
                        </div>
                        <div style={{ marginBottom: '4px' }}>
                          <strong>Endereço:</strong> {f.endereco || "—"}
                        </div>
                        <div style={{ marginBottom: '4px' }}>
                          <strong>Cidade:</strong> {f.cidade} - {f.estado}
                        </div>
                        <div style={{ marginBottom: '4px' }}>
                          <strong>Contato:</strong> {f.contato || "—"}
                        </div>
                        <div style={{ marginBottom: '4px' }}>
                          <strong>WhatsApp:</strong> {f.whatsapp || "—"}
                        </div>
                        {isFocado && ultimoAbastecimento && !ultimoAbastecimento.mensagem && (
                          <div style={{ marginTop: '8px', paddingTop: '6px', borderTop: '1px solid #ccc' }}>
                            <div style={{ fontWeight: 'bold', color: '#0284c7', marginBottom: '4px' }}>Último Abastecimento:</div>
                            <div><strong>Data:</strong> {new Date(ultimoAbastecimento.data).toLocaleDateString('pt-BR')}</div>
                            <div><strong>Combustível:</strong> {ultimoAbastecimento.produto}</div>
                            <div><strong>Motorista:</strong> {ultimoAbastecimento.motorista_label || "—"}</div>
                            <div><strong>Cavalo:</strong> {ultimoAbastecimento.veiculo_label || "—"}</div>
                            <div><strong>Carreta:</strong> {ultimoAbastecimento.carreta_label || "—"}</div>
                          </div>
                        )}
                      </div>
                    </Popup>'''
    
    if padrao_popup.search(c):
        c = padrao_popup.sub(lambda m: novo_popup, c, count=1)
        print("✅ Popup substituído por HTML puro (estilos inline).")
    else:
        print("⚠️ Não foi possível encontrar o bloco do Popup.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Componente atualizado.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)
    print("\n✅ Script aplicado com sucesso!")