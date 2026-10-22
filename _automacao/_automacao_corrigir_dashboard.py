import os
import shutil
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_fix_dashboard_{agora}.zip"
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

def criar_dashboard_se_faltar(raiz):
    pasta_routers = os.path.join(raiz, "app", "backend", "routers")
    os.makedirs(pasta_routers, exist_ok=True)
    
    caminho = os.path.join(pasta_routers, "dashboard.py")
    if os.path.exists(caminho):
        print("✅ O arquivo dashboard.py já existe.")
        return

    print("⚠️ Criando o arquivo dashboard.py que estava faltando...")
    codigo = '''from fastapi import APIRouter, Depends
from lib.db import db
from lib.security import require
from models.dashboard import Dashboard, Kpi, StatusFrota, CustoMes, Campeoes
from lib.campeoes import campeao_do_mes
from lib.dates import last_months, today_iso

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("", response_model=Dashboard)
async def get_dashboard(user: dict = Depends(require("read"))):
    veiculos = await db.veiculos.count_documents({"ativo": True})
    motoristas = await db.motoristas.count_documents({"ativo": True})
    acoplamentos = await db.acoplamentos.count_documents({"status": "ativo"})
    
    kpis = [
        Kpi(chave="veiculos", titulo="Veículos Ativos", valor=veiculos, serie=[]),
        Kpi(chave="motoristas", titulo="Motoristas Ativos", valor=motoristas, serie=[]),
        Kpi(chave="acoplamentos", titulo="Conjuntos Formados", valor=acoplamentos, serie=[]),
        Kpi(chave="km", titulo="KM Rodados (Mês)", valor=0, serie=[]),
    ]

    inativos = await db.veiculos.count_documents({"ativo": False})
    em_manutencao = await db.manutencoes.count_documents({"status": "em_execucao"})
    status_frota = StatusFrota(
        acoplados=acoplamentos, 
        disponiveis=max(0, veiculos - acoplamentos - em_manutencao), 
        em_manutencao=em_manutencao, 
        inativos=inativos
    )

    custos = [CustoMes(mes=m, combustivel=0, manutencao=0) for m in last_months(6)]

    mes_atual = today_iso()[:7]
    mes_ant = last_months(2)[0]
    c_atual = await campeao_do_mes(mes_atual)
    c_ant = await campeao_do_mes(mes_ant)
    campeoes = Campeoes(mes_atual=c_atual, mes_passado=c_ant)

    return Dashboard(
        kpis=kpis, status_frota=status_frota, custos=custos, 
        alertas=[], historico_recente=[], campeoes=campeoes
    )
'''
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✅ Arquivo dashboard.py criado com sucesso!")

def verificar_acoplamentos(raiz):
    pasta_routers = os.path.join(raiz, "app", "backend", "routers")
    caminho = os.path.join(pasta_routers, "acoplamentos.py")
    if os.path.exists(caminho):
        print("✅ O arquivo acoplamentos.py existe.")
    else:
        print("❌ Alerta: O arquivo acoplamentos.py também está faltando!")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Correção do Dashboard...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    criar_dashboard_se_faltar(raiz)
    verificar_acoplamentos(raiz)

    print("🚀 Automação concluída! Faça o commit e push para o Render.")

if __name__ == "__main__":
    executar()