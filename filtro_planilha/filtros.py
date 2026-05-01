from conexao import Conexao

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import re


class Filtros:
    def __init__(self, coluna, token_planilha, sheet_and_range):
        self.coluna = coluna#NFE ENTRADA, NFE SAIDA, NFCE SAIDA, CTE ENTRADA, CTE SAIDA, NFSe - PRESTADAS, NFSe - TOMADAS
        self.__SAMPLE_SPREADSHEET_ID = token_planilha
        self.__SAMPLE_RANGE_NAME = sheet_and_range


    def normalizar_texto(self, valor):
        if not valor:
            return ""
        return str(valor).replace("\xa0", " ").strip()
    

    def limpar_cnpj(self, valor):
        if not valor:
            return None

        valor = str(valor).split("#")[0]
        valor = re.sub(r"\D", "", valor)

        if len(valor) != 14:
            return None

        return valor
    

    def dataFrame(self):
        try:
            creds = Conexao.credenciais()
            service = build("sheets", "v4", credentials=creds)

            # Call the Sheets API
            sheet = service.spreadsheets()
            result = (
                sheet.values()
                .get(spreadsheetId=self.__SAMPLE_SPREADSHEET_ID, range=self.__SAMPLE_RANGE_NAME)
                .execute()
            )
            values = result.get("values", [])
            
            if not values:
                print("No data found.")
                return
        
            return values
        
        except HttpError as err:
            print(err)
        

    #Busca as notas de cada coluna
    def filtroNotas(self, certificado: bool):

        values = self.dataFrame()

        header = values[0]
        rows = values[1:]

        idx_cnpj = header.index("CNPJ")
        idx_nota = header.index(self.coluna)
        idx_certificado = header.index("CERTIFICADO")

        resultados = []

        for i, row in enumerate(rows, start=2):
            if not row:
                continue

            # Garante o tamanho da linha
            row = row + [""] * (len(header) - len(row))

            cnpj = self.limpar_cnpj(row[idx_cnpj])
            if not cnpj:
                print(f"Linha {i} ignorada (CNPJ inválido): {repr(row[idx_cnpj])}")
                continue

            notas = self.normalizar_texto(row[idx_nota]).lower()
            cert_valor = self.normalizar_texto(row[idx_certificado]).upper()

            nota_valida = "agencia net" in notas or "iss net" in notas

            # Validação do certificado
            if certificado:
                certificado_valido = cert_valor == "IMPOSTO"
            else:
                certificado_valido = cert_valor == ""

            if nota_valida and certificado_valido:
                resultados.append(cnpj)

        for r in resultados:
            print(r)

        print("Total:", len(resultados))
        return resultados


    def filtroPrioritarias(self, prioritarias: str, certificado: bool):

        values = self.dataFrame()

        header = values[0]
        rows = values[1:]

        idx_cnpj = header.index("CNPJ")
        idx_nota = header.index(self.coluna)
        idx_prioridade = header.index("PRIORITARIAS")
        idx_certificado = header.index("CERTIFICADO")

        resultados = []

        for i, row in enumerate(rows, start=2):
            if not row:
                continue

            row = row + [""] * (len(header) - len(row))

            cnpj = self.limpar_cnpj(row[idx_cnpj])
            if not cnpj:
                print(f"Linha {i} ignorada (CNPJ inválido): {repr(row[idx_cnpj])}")
                continue

            notas = self.normalizar_texto(row[idx_nota]).lower()
            prioridade = self.normalizar_texto(row[idx_prioridade]).upper()
            cert_valor = self.normalizar_texto(row[idx_certificado]).upper()

            nota_valida = "agencia net" in notas or "iss net" in notas

            if certificado:
                certificado_valido = cert_valor == "IMPOSTO"
            else:
                certificado_valido = cert_valor == ""

            if nota_valida and prioridade == prioritarias and certificado_valido:
                resultados.append(cnpj)

        for r in resultados:
            print(r)

        print("Total:", len(resultados))
        return resultados
    

    def prioridade_maxima_imposto(self):
        return self.filtroPrioritarias(
            prioritarias="PRIORIDADE MAXIMA",
            certificado=True
        )
    
    def prioridade_maxima_gomide(self):
        return self.filtroPrioritarias(
            prioritarias="PRIORIDADE MAXIMA",
            certificado=False
        )
    

    def prioridades(self):
        return self.filtroPrioritarias(
            prioritarias="PRIORITARIAS",
            certificado=False
        )


    def notas_imposto(self):
        return self.filtroNotas(
            certificado=True
        )
    

    def notas_gomide(self):
        return self.filtroNotas(
            certificado=False
        )
    
    
    def semanal_condor(self):
        return self.filtroPrioritarias(
            prioritarias="SEMANAL_C",
            certificado=False
        )
    

    def semanal_drogaria(self):
        return self.filtroPrioritarias(
            prioritarias="SEMANAL_D",
            certificado=False
        )
    
    
    def semanal_schipper(self):
        return self.filtroPrioritarias(
            prioritarias="SEMANAL_S",
            certificado=False
        )