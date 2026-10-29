import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_DISTANCIA_PDF_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    arquivos = [
        "frontend/src/pages/Fornecedores.tsx",
        "frontend/src/components/MapaFornecedores.tsx"
    ]
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_fornecedores_page(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Fornecedores.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Na função buscarCNPJ, adicionar lat/long se a API retornar
    if 'latitude: data.latitude' not in c:
        c = c.replace(
            'estado: data.uf || s.estado',
            'estado: data.uf || s.estado,\n        latitude: data.latitude || s.latitude,\n        longitude: data.longitude || s.longitude'
        )
        print("✅ Frontend Fornecedores: buscarCNPJ agora salva lat/long.")

    # 2. Na coluna de Rota, calcular a distância real (Haversine)
    padrao_rota = re.compile(r'<TableCell className="text-xs text-slate-400 text-center">\s*\{\(\(\) => \{[\s\S]*?Ver Rota[\s\S]*?</TableCell>', re.DOTALL)
    
    nova_rota = '''<TableCell className="text-xs text-slate-400 text-center">
                  {(() => {
                    if (!r.latitude || !r.longitude) return <span className="text-slate-600">—</span>;
                    const emp = empresas.find((e: any) => e.id === r.empresa_id);
                    if (!emp || !emp.latitude || !emp.longitude) return <span className="text-slate-600">—</span>;
                    
                    const R = 6371; // Raio da Terra em km
                    const dLat = (r.latitude - emp.latitude) * Math.PI / 180;
                    const dLon = (r.longitude - emp.longitude) * Math.PI / 180;
                    const a = Math.sin(dLat/2) * Math.sin(dLat/2) + Math.cos(emp.latitude * Math.PI / 180) * Math.cos(r.latitude * Math.PI / 180) * Math.sin(dLon/2) * Math.sin(dLon/2);
                    const dist = R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
                    
                    return (
                      <a 
                        href={`https://www.google.com/maps/dir/?api=1&origin=${emp.latitude},${emp.longitude}&destination=${r.latitude},${r.longitude}`} 
                        target="_blank" 
                        rel="noreferrer" 
                        className="text-sky-400 hover:underline flex items-center justify-center gap-1"
                        title="Abrir rota no Google Maps"
                      >
                        <MapPin className="size-3" /> {dist.toFixed(0)} km
                      </a>
                    );
                  })()}
                </TableCell>'''
    
    if padrao_rota.search(c):
        c = padrao_rota.sub(lambda m: nova_rota, c, count=1)
        print("✅ Frontend Fornecedores: coluna Rota agora calcula a distância real.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend Fornecedores.tsx atualizado.")

def fix_mapa(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "components", "MapaFornecedores.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Adicionar o botão "Exportar PDF" no rodapé do modal
    if 'Exportar PDF' not in c:
        # Encontra o botão "Fechar"
        alvo_botao = '''<button onClick={() => onOpenChange(false)} className="text-slate-400 hover:text-white">
            <X className="size-5" />
          </button>'''
        
        novo_botao = '''<div className="flex items-center gap-2">
            <Button 
              onClick={() => {
                const win = window.open('', '_blank');
                if (win) {
                  const html = `
                    <html><head><title>Fornecedores</title>
                    <style>body { font-family: sans-serif; padding: 20px; } table { width: 100%; border-collapse: collapse; } th, td { border: 1px solid #ccc; padding: 8px; text-align: left; } th { background: #0284c7; color: white; }</style>
                    </head><body>
                    <h1>Relatório de Fornecedores</h1>
                    <table>
                      <thead><tr><th>Nome</th><th>Cidade</th><th>UF</th><th>Tipo</th><th>Contato</th><th>WhatsApp</th></tr></thead>
                      <tbody>
                        ${fornecedoresFiltrados.map((f: any) => `
                          <tr>
                            <td>${f.nome}</td>
                            <td>${f.cidade || '-'}</td>
                            <td>${f.estado || '-'}</td>
                            <td>${tipos.find((t: any) => t.id === f.tipo_fornecedor_id)?.nome || '-'}</td>
                            <td>${f.contato || '-'}</td>
                            <td>${f.whatsapp || '-'}</td>
                          </tr>
                        `).join('')}
                      </tbody>
                    </table>
                    </body></html>
                  `;
                  win.document.write(html);
                  win.document.close();
                  win.print();
                }
              }} 
              className="bg-sky-600 hover:bg-sky-500 h-9"
            >
              Exportar PDF
            </Button>
            <button onClick={() => onOpenChange(false)} className="text-slate-400 hover:text-white">
              <X className="size-5" />
            </button>
          </div>'''
        
        if alvo_botao in c:
            c = c.replace(alvo_botao, novo_botao)
            print("✅ Botão 'Exportar PDF' adicionado ao modal do mapa.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend MapaFornecedores.tsx atualizado.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_fornecedores_page(raiz)
    fix_mapa(raiz)
    print("\n✅ Scripts aplicados! Faça o git push.")