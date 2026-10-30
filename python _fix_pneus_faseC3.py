import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_PNEUS_FASEC3_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    print(f"✅ Backup salvo: {caminho_zip}")

def criar_backend(raiz):
    # 1. Adicionar motivos de sucateamento como seed
    router_path = os.path.join(raiz, "app", "backend", "routers", "pneu_movimentacoes.py")
    with open(router_path, 'r', encoding='utf-8') as f:
        c = f.read()

    if '/motivos-descarte' not in c:
        rota = '''
@router.get("/motivos-descarte")
async def motivos_descarte(_u: dict = Depends(require("read"))):
    motivos = [
        {"codigo": "TAL-01", "descricao": "Quebra ou Deformação do Talão", "responsabilidade": "OFICINA"},
        {"codigo": "TAL-02", "descricao": "Queima / Ressecamento Térmico do Talão", "responsabilidade": "MECANICA"},
        {"codigo": "TAL-03", "descricao": "Rasgo / Dilaceração do Talão", "responsabilidade": "OFICINA"},
        {"codigo": "LAT-01", "descricao": "Bolha Lateral / Rompimento de Carcaça", "responsabilidade": "MOTORISTA"},
        {"codigo": "LAT-02", "descricao": "Corte / Dilaceração Lateral Transversal", "responsabilidade": "MOTORISTA"},
        {"codigo": "LAT-03", "descricao": "Desgaste por Atrito Lateral (Roçamento)", "responsabilidade": "MECANICA"},
        {"codigo": "LAT-04", "descricao": "Fadiga por Subpressão (Rodar Baixo/Murcho)", "responsabilidade": "MOTORISTA"},
        {"codigo": "BAN-01", "descricao": "Separação de Lonas / Cintas Metálicas", "responsabilidade": "MANUTENCAO"},
        {"codigo": "BAN-02", "descricao": "Arranque de Blocos (Picotamento Severo)", "responsabilidade": "GESTAO"},
        {"codigo": "BAN-03", "descricao": "Freiada Brusca / Escamamento Plano", "responsabilidade": "MOTORISTA"},
        {"codigo": "BAN-04", "descricao": "Fim de Vida Regular (Desgaste Natural)", "responsabilidade": "NATURAL"},
        {"codigo": "REC-01", "descricao": "Recusa Técnica na Raspagem (Carcaça Fadigada)", "responsabilidade": "NATURAL"},
        {"codigo": "REC-02", "descricao": "Descolamento de Banda Aplicada", "responsabilidade": "FORNECEDOR"},
        {"codigo": "REC-03", "descricao": "Excesso de Furos / Proximidade de Furos", "responsabilidade": "OPERACAO"},
    ]
    return motivos
'''
        c += rota
        with open(router_path, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Rota /motivos-descarte criada.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    criar_backend(raiz)
    print("\n✅ Fase C.3 (Motivos de Descarte) aplicada com sucesso!")