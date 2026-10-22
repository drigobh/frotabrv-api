import os
import shutil
import datetime
import zipfile
import requests

# Configurações
API_URL = "https://frotabrv-api.onrender.com/api"
EMAIL = "admin@frotabrv.com"
SENHA = "admin123"

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_migracao_{agora}.zip"
    caminho_zip = os.path.join(pasta_backups, nome_backup)
    
    print(f"📦 Criando Backup Full do Sistema...")
    ignorar = ['node_modules', '.git', '__pycache__', '.venv', 'venv', 'dist', 'build']
    
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for pasta_alvo in ['app', 'frontend']:
            caminho_pasta = os.path.join(raiz, pasta_alvo)
            for root, dirs, files in os.walk(caminho_pasta):
                dirs[:] = [d for d in dirs if d not in ignorar]
                for file in files:
                    caminho_completo = os.path.join(root, file)
                    caminho_relativo = os.path.relpath(caminho_completo, raiz)
                    try:
                        zipf.write(caminho_completo, caminho_relativo)
                    except Exception:
                        pass
    print(f"✅ Backup Full salvo em: _automacao/backups/{nome_backup}")

def forcar_logout_cookie():
    # Cria um arquivo HTML que apaga o cookie ao ser aberto
    caminho_html = "logout_automatico.html"
    with open(caminho_html, "w", encoding="utf-8") as f:
        f.write('''
        <html>
            <body>
                <script>
                    document.cookie = "frota_session=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
                    alert("Sessão limpa! Feche esta aba e volte ao sistema.");
                </script>
            </body>
        </html>
        ''')
    print(f"✅ Arquivo de logout gerado: {caminho_html}")
    print("👉 Abra o arquivo 'logout_automatico.html' no navegador para forçar a saída.")

def migrar_carretas():
    print("🔄 Iniciando migração de veículos SR para carretas...")
    session = requests.Session()
    
    # Login
    res = session.post(f"{API_URL}/auth/login", json={"email": EMAIL, "senha": SENHA})
    if res.status_code != 200:
        print(f"❌ Falha no login: {res.text}")
        return

    # Buscar veículos
    res = session.get(f"{API_URL}/veiculos")
    veiculos = res.json()
    
    migrados = 0
    for v in veiculos:
        # Verifica se o modelo contém "SR" (case insensitive)
        if "SR" in v.get("modelo", "").upper():
            print(f"🔄 Migrando: {v['placa']} - {v['modelo']}")
            
            # Criar carreta
            nova_carreta = {
                "codigo": v["placa"],
                "tipo": "Graneleiro", # Valor padrão
                "placa": v["placa"],
                "modelo": v["modelo"],
                "ano": v.get("ano"),
                "hodometro_km": v.get("hodometro_km", 0),
                "observacoes": "Migrado de Veículos (SR)"
            }
            res_c = session.post(f"{API_URL}/carretas", json=nova_carreta)
            
            if res_c.status_code == 201:
                # Deletar veículo antigo
                session.delete(f"{API_URL}/veiculos/{v['id']}")
                print(f"✅ Migrado e removido de veículos.")
                migrados += 1
            else:
                print(f"⚠️ Erro ao criar carreta: {res_c.text}")

    print(f"🎉 Migração concluída! {migrados} itens movidos.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Limpeza, Login e Migração...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    forcar_logout_cookie()
    migrar_carretas()

    print("\n🚀 Tudo pronto! Siga os passos abaixo:")
    print("1. Faça o commit e push para o Render.")
    print("2. Abra o arquivo 'logout_automatico.html' no navegador para forçar o logout.")
    print("3. Volte para localhost:3000 e faça login novamente.")

if __name__ == "__main__":
    executar()