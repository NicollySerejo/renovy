"""Geracao do 'documento' do contrato.

Para o MVP o contrato e representado como um HTML auto-contido (facil de
visualizar no navegador e de imprimir/'salvar como PDF'). Uma integracao
futura com uma biblioteca de geracao de PDF real (ex: WeasyPrint, ReportLab)
pode consumir este mesmo HTML sem mudar o restante do sistema.
"""
from app import models


def render_contrato_html(contract: models.Contract) -> str:
    assinaturas_html = ""
    for sig in contract.signatures:
        assinaturas_html += (
            f"<p><strong>{sig.tipo.value.capitalize()}:</strong> {sig.nome_assinante} "
            f"— assinado em {sig.data_hora.strftime('%d/%m/%Y %H:%M')} "
            f"(ref: {sig.hash_confirmacao[:12]}...)</p>"
        )
    if not assinaturas_html:
        assinaturas_html = "<p><em>Ainda sem assinaturas registradas.</em></p>"

    return f"""
    <html>
      <head><meta charset="utf-8"><title>Contrato {contract.numero}</title></head>
      <body style="font-family: Arial, sans-serif; max-width: 720px; margin: 40px auto;">
        <h1>Contrato de Prestacao de Servicos</h1>
        <p><strong>Numero:</strong> {contract.numero}</p>
        <p><strong>Responsavel:</strong> {contract.client.nome} (CPF: {contract.client.cpf})</p>
        <p><strong>Paciente:</strong> {contract.patient.nome}</p>
        <p><strong>Vigencia:</strong> {contract.data_inicio.strftime('%d/%m/%Y')} ate {contract.data_fim.strftime('%d/%m/%Y')}</p>
        <p><strong>Valor:</strong> R$ {contract.valor:.2f}</p>
        <p><strong>Condicoes:</strong> {contract.condicoes or '-'}</p>
        <hr>
        <h3>Assinaturas</h3>
        {assinaturas_html}
      </body>
    </html>
    """


def render_aditivo_html(contract: models.Contract, renewal: models.Renewal, novos_dados: dict) -> str:
    return f"""
    <html>
      <head><meta charset="utf-8"><title>Aditivo - Contrato {contract.numero}</title></head>
      <body style="font-family: Arial, sans-serif; max-width: 720px; margin: 40px auto;">
        <h1>Termo Aditivo ao Contrato {contract.numero}</h1>
        <p><strong>Responsavel:</strong> {contract.client.nome} (CPF: {contract.client.cpf})</p>
        <p><strong>Paciente:</strong> {contract.patient.nome}</p>
        <h3>Dados atuais</h3>
        <p>Valor: R$ {contract.valor:.2f} | Vigencia: {contract.data_inicio.strftime('%d/%m/%Y')} a {contract.data_fim.strftime('%d/%m/%Y')}</p>
        <h3>Novos dados</h3>
        <p>Valor: R$ {novos_dados.get('novo_valor', contract.valor):.2f}</p>
        <p>Vigencia: {novos_dados.get('nova_data_inicio', '-')} a {novos_dados.get('nova_data_fim', '-')}</p>
      </body>
    </html>
    """
