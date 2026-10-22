from fastapi import APIRouter, Depends
from lib.db import db
from lib.security import require
from models.dashboard import Dashboard, Kpi, StatusFrota, CustoMes, Campeoes
from models.acoplamentos import HistoricoItem
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
    
    # Busca as últimas 5 movimentações de acoplamento
    hist_docs = await db.acoplamentos_historico.find({}, {"_id": 0}).sort("created_at", -1).to_list(5)
    historico_recente = [HistoricoItem(**h) for h in hist_docs]

    return Dashboard(
        kpis=kpis, status_frota=status_frota, custos=custos, 
        alertas=[], historico_recente=historico_recente, campeoes=campeoes
    )
