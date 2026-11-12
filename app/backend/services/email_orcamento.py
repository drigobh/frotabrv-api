import smtplib
import os
import urllib.parse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")

ZAPI_INSTANCE = os.getenv("ZAPI_INSTANCE", "")
ZAPI_TOKEN = os.getenv("ZAPI_TOKEN", "")
ZAPI_CLIENT_TOKEN = os.getenv("ZAPI_CLIENT_TOKEN", "")

def gerar_html(orcamento: dict, tipo: str, destinatario_nome: str) -> str:
    cor = "#22d3ee" if tipo == "comprador" else "#a855f7"
    cor_secundaria = "#a855f7" if tipo == "comprador" else "#22d3ee"
    titulo_acao = "Orçamento Criado com Sucesso" if tipo == "comprador" else "Ação Necessária: Aprovar Orçamento"
    subtitulo = "Seu orçamento foi registrado e enviado para aprovação." if tipo == "comprador" else "Você tem um novo orçamento aguardando sua análise."

    # Linhas das ofertas
    linhas = ""
    for of in orcamento.get("ofertas", []):
        vencedor = of.get("is_vencedor", False)
        bg = "#064e3b" if vencedor else "#1e293b"
        border = "#10b981" if vencedor else "#334155"
        tag = " 🏆 VENCEDOR" if vencedor else ""
        total = of.get("valor_unitario", 0) * of.get("quantidade", 0)
        linhas += f"""
        <tr style="background:{bg}; border-left: 3px solid {border};">
          <td style="padding:12px; color:#f1f5f9; font-weight:bold;">{of.get('fornecedor_nome')}{tag}</td>
          <td style="padding:12px; color:#94a3b8; text-align:center;">{of.get('quantidade')}</td>
          <td style="padding:12px; color:#22d3ee; text-align:right; font-weight:bold;">R$ {of.get('valor_unitario',0):.2f}</td>
          <td style="padding:12px; color:#10b981; text-align:right; font-weight:bold;">R$ {total:.2f}</td>
          <td style="padding:12px; color:#94a3b8; font-size:12px;">{of.get('prazo_entrega','-')}<br/>{of.get('forma_pagamento','-')} {of.get('parcelas','')}</td>
        </tr>
        """
    
    valor_total_geral = sum((of.get('valor_unitario', 0) * of.get('quantidade', 0)) for of in orcamento.get("ofertas", []))
    data_formatada = orcamento.get("data_criacao", "")[:19].replace("T", " ")

    return f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"></head>
    <body style="margin:0; padding:0; background:#0f172a; font-family: 'Segoe UI', Arial, sans-serif;">
      <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f172a; padding: 30px 10px;">
        <tr><td align="center">
          <table width="600" cellpadding="0" cellspacing="0" style="background:#1e293b; border-radius:16px; overflow:hidden; box-shadow: 0 20px 60px rgba(34,211,238,0.15);">
            
            <!-- HEADER -->
            <tr><td style="background: linear-gradient(135deg, {cor} 0%, {cor_secundaria} 100%); padding: 30px; text-align:center;">
              <div style="font-size:14px; letter-spacing:3px; color:rgba(255,255,255,0.8); text-transform:uppercase; font-weight:600;">Bravus Frota</div>
              <h1 style="margin:10px 0 5px 0; color:#ffffff; font-size:26px; font-weight:800;">{titulo_acao}</h1>
              <p style="margin:0; color:rgba(255,255,255,0.9); font-size:14px;">{subtitulo}</p>
            </td></tr>

            <!-- SAUDAÇÃO -->
            <tr><td style="padding: 30px 30px 15px 30px;">
              <p style="color:#cbd5e1; font-size:15px; margin:0;">Olá, <b style="color:{cor};">{destinatario_nome}</b>,</p>
            </td></tr>

            <!-- CARD DE RESUMO -->
            <tr><td style="padding: 0 30px;">
              <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f172a; border-radius:12px; border:1px solid #334155;">
                <tr>
                  <td style="padding:20px; border-right:1px solid #334155;">
                    <div style="color:#64748b; font-size:11px; text-transform:uppercase; letter-spacing:1px;">Nº Orçamento</div>
                    <div style="color:{cor}; font-size:20px; font-weight:800; font-family:monospace; margin-top:4px;">{orcamento.get('numero')}</div>
                  </td>
                  <td style="padding:20px;">
                    <div style="color:#64748b; font-size:11px; text-transform:uppercase; letter-spacing:1px;">Produto</div>
                    <div style="color:#f1f5f9; font-size:14px; font-weight:700; margin-top:4px;">{orcamento.get('produto')}</div>
                  </td>
                </tr>
                <tr>
                  <td style="padding:20px; border-right:1px solid #334155; border-top:1px solid #334155;">
                    <div style="color:#64748b; font-size:11px; text-transform:uppercase; letter-spacing:1px;">Criado por</div>
                    <div style="color:#f1f5f9; font-size:13px; margin-top:4px;">{orcamento.get('criado_por')}</div>
                  </td>
                  <td style="padding:20px; border-top:1px solid #334155;">
                    <div style="color:#64748b; font-size:11px; text-transform:uppercase; letter-spacing:1px;">Data</div>
                    <div style="color:#f1f5f9; font-size:13px; margin-top:4px;">{data_formatada}</div>
                  </td>
                </tr>
              </table>
            </td></tr>

            <!-- TABELA DE OFERTAS -->
            <tr><td style="padding: 25px 30px 10px 30px;">
              <h2 style="color:#f1f5f9; font-size:16px; font-weight:700; margin:0 0 12px 0;">📊 Ofertas Recebidas ({len(orcamento.get('ofertas', []))})</h2>
              <table width="100%" cellpadding="0" cellspacing="0" style="border-radius:10px; overflow:hidden;">
                <tr style="background:#0f172a;">
                  <th style="padding:10px; color:#64748b; font-size:11px; text-align:left; text-transform:uppercase;">Fornecedor</th>
                  <th style="padding:10px; color:#64748b; font-size:11px; text-align:center; text-transform:uppercase;">Qtd</th>
                  <th style="padding:10px; color:#64748b; font-size:11px; text-align:right; text-transform:uppercase;">Unitário</th>
                  <th style="padding:10px; color:#64748b; font-size:11px; text-align:right; text-transform:uppercase;">Total</th>
                  <th style="padding:10px; color:#64748b; font-size:11px; text-align:left; text-transform:uppercase;">Condições</th>
                </tr>
                {linhas}
              </table>
            </td></tr>

            <!-- TOTAL -->
            <tr><td style="padding: 15px 30px 30px 30px;">
              <div style="background: linear-gradient(135deg, {cor}22 0%, {cor_secundaria}22 100%); border: 1px solid {cor}; border-radius:12px; padding: 18px; display:flex; justify-content:space-between;">
                <span style="color:#cbd5e1; font-size:14px; font-weight:600;">💰 Valor Total Estimado (Menor Oferta)</span>
                <span style="color:{cor}; font-size:22px; font-weight:800; font-family:monospace;">R$ {valor_total_geral:.2f}</span>
              </div>
            </td></tr>

            <!-- CTA -->
            <tr><td style="padding: 0 30px 30px 30px; text-align:center;">
              <a href="https://frotabrv.onrender.com/orcamentos" style="display:inline-block; background: linear-gradient(135deg, {cor} 0%, {cor_secundaria} 100%); color:#0f172a; text-decoration:none; font-weight:800; padding:14px 32px; border-radius:10px; font-size:14px;">{'Ver Orçamento no Sistema' if tipo == 'comprador' else 'Analisar e Aprovar'}</a>
            </td></tr>

            <!-- FOOTER -->
            <tr><td style="background:#0f172a; padding:20px; text-align:center; border-top:1px solid #334155;">
              <p style="color:#475569; font-size:11px; margin:0;">Este é um e-mail automático do sistema <b style="color:{cor};">Bravus Frota</b>.</p>
              <p style="color:#475569; font-size:11px; margin:4px 0 0 0;">Dúvidas? Acesse o sistema e consulte o módulo de Compras.</p>
            </td></tr>

          </table>
        </td></tr>
      </table>
    </body>
    </html>
    """

def enviar_email(destinatario: str, assunto: str, html: str) -> bool:
    if not SMTP_HOST or not SMTP_USER:
        print(f"[EMAIL - MOCK] SMTP não configurado. Para: {destinatario} | Assunto: {assunto}")
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = assunto
        msg["From"] = SMTP_USER
        msg["To"] = destinatario
        msg.attach(MIMEText(html, "html"))
        
        if SMTP_PORT == 465:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
                server.login(SMTP_USER, SMTP_PASS)
                server.send_message(msg)
        else:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASS)
                server.send_message(msg)
        print(f"[EMAIL] Enviado para {destinatario}")
        return True
    except Exception as e:
        print(f"[EMAIL] Erro ao enviar para {destinatario}: {e}")
        return False

def gerar_texto_whatsapp(orcamento: dict, tipo: str, destinatario_nome: str) -> str:
    acao = "criado e aguardando aprovação" if tipo == "comprador" else "aguardando sua aprovação"
    texto = f"""*🚀 Bravus Frota - Orçamento {orcamento.get('numero')}*

Olá, *{destinatario_nome}*! O orçamento foi {acao}.

*📦 Produto:* {orcamento.get('produto')}
*👤 Solicitante:* {orcamento.get('criado_por')}
*📊 Ofertas:* {len(orcamento.get('ofertas', []))} fornecedores

"""
    for of in orcamento.get("ofertas", []):
        venc = " 🏆" if of.get("is_vencedor") else ""
        total = of.get("valor_unitario", 0) * of.get("quantidade", 0)
        texto += f"• {of.get('fornecedor_nome')}{venc}: R$ {of.get('valor_unitario',0):.2f} (Total R$ {total:.2f})
"
    
    texto += f"
*Acesse o sistema para {'ver' if tipo == 'comprador' else 'aprovar'}:* https://frotabrv.onrender.com/orcamentos"
    return texto

def enviar_whatsapp(numero: str, mensagem: str) -> str:
    """Se ZAPI configurada, envia direto. Senão, retorna link para abrir."""
    numero_limpo = "".join(filter(str.isdigit, numero))
    if len(numero_limpo) < 10:
        return None
    
    if ZAPI_INSTANCE and ZAPI_TOKEN:
        try:
            import requests
            url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}/send-text"
            headers = {"Client-Token": ZAPI_CLIENT_TOKEN, "Content-Type": "application/json"}
            requests.post(url, json={"phone": numero_limpo, "message": mensagem}, headers=headers, timeout=10)
            print(f"[WHATSAPP] Enviado para {numero_limpo}")
            return None
        except Exception as e:
            print(f"[WHATSAPP] Erro ZAPI: {e}")
            return f"https://wa.me/{numero_limpo}?text={urllib.parse.quote(mensagem)}"
    else:
        return f"https://wa.me/{numero_limpo}?text={urllib.parse.quote(mensagem)}"
