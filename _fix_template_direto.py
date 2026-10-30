import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_TEMPLATE_DIRETO_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    caminho_abs = os.path.join(raiz, "frontend", "src", "pages", "Pneus.tsx")
    if os.path.exists(caminho_abs):
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_abs, "frontend/src/pages/Pneus.tsx")
        print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Pneus.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Adicionar uma query direta para buscar os veículos (garantindo que o template_chassi_id venha)
    if 'const { data: veiculosApi = [] }' not in c:
        c = c.replace(
            'const { data: pneus = [] } = useQuery({ queryKey: ["pneus"], queryFn: () => apiGet<any[]>("/pneus") });',
            '''const { data: pneus = [] } = useQuery({ queryKey: ["pneus"], queryFn: () => apiGet<any[]>("/pneus") });
  const { data: veiculosApi = [] } = useQuery({ queryKey: ["veiculos"], queryFn: () => apiGet<any[]>("/veiculos") });'''
        )
        print("✅ Query direta de veículos adicionada.")

    # 2. Substituir a busca do veículo selecionado para usar a query direta
    c = c.replace(
        '''const veiculoSelecionado = 
    tipoAtivo === "cavalo" 
      ? veiculos.data?.find((v: any) => v.id === veiculoMapa)
      : carretas.find((c: any) => c.id === veiculoMapa);''',
        '''const veiculoSelecionado = 
    tipoAtivo === "cavalo" 
      ? veiculosApi.find((v: any) => v.id === veiculoMapa)
      : carretas.find((c: any) => c.id === veiculoMapa);
  
  // Debug: mostrar no console o que está vindo
  if (veiculoMapa) {
    console.log("Veículo selecionado:", veiculoSelecionado);
  }'''
    )
    print("✅ Busca do veículo selecionado agora usa a API direta.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Script aplicado com sucesso!")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)
    print("\n✅ Script aplicado com sucesso!")