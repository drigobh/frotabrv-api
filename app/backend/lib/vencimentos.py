"""Regra única de vencimento (documentos, CNH, contas): janela de alerta de 30 dias."""

from datetime import date

ALERTA_DIAS = 30


def dias_para(validade: str, hoje: str) -> int:
    return (date.fromisoformat(validade) - date.fromisoformat(hoje)).days


def situacao(validade: str, hoje: str) -> str:
    dias = dias_para(validade, hoje)
    if dias < 0:
        return "vencido"
    if dias <= ALERTA_DIAS:
        return "vencendo"
    return "vigente"
