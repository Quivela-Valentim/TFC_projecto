import requests 
import pymysql
import  os 
import pandas as pd
import math
from datetime import date
import logging
import urllib3



# Criação do logging 
logging.basicConfig(
    filename= "bodiva_livros.log",
    level= logging.INFO, 
    format= "%(asctime)s %(levelname)s %(message)s"
)

try:
    logging.info("Execução  iniciada ")
    
    # PASSO 1:  CONFIGURAÇÕES
    
    url = "https://www.bodiva.ao/reports/controllers/excel/Export/excel.php"
    
    PASTA_DOWNLOAD = "downloads"
    
    MYSQL_CONFIG = {
        "host": "localhost",
        "user": "root",
        "password": "!TCyber#2709@",
        "database": "MeuBanco_bodiva",
        "port": 3306, 
        "charset": "utf8mb4",
        "autocommit": True
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36", 
        
        "Accept":"*/*",
        "Accept-Language": "pt-PT,pt;q=0.9",
        "Connection": "keep-alive",
        "Referer": "https://www.bodiva.ao/",

    }
    
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    session = requests.Session()
    
    #PASSO 2: DOWNLOADS DO EXCEL 
    
    os.makedirs(PASTA_DOWNLOAD, exist_ok= True)
    hoje= date.today().isoformat()
    
    Mylivro = f"{PASTA_DOWNLOAD}/LivrosDeOrdens_{hoje}.xlsx"
    
    response = session.get(url, headers=headers, timeout=(60,720), verify=False, stream=True)
    
    if response.status_code != 200:
        raise Exception( f"Erro ao descarregar o ficheiro:{response.status_code}")
    
    with open( Mylivro, "wb") as f: 
        for chunk in response.iter_content(8192):
            if chunk: 
                f.write(chunk)
                
    print(f"Ficheiro descarregado com sucesso {Mylivro}")
    
    #PASSO 3: LER O FICHEIRO.
    
    df = pd.read_excel( Mylivro, skiprows=2, header=0 )
    if df.empty: 
        print("Ficheiro vazio. Não há nada para ser lido!")
        exit()
    
    # Normalizar as colunas 
    """print(len(df.columns))
    print(df.columns)"""
   
    df.columns = [
        # Identificação (comum a todas as abas)
        "codigo",
        "isin",
        "tipologia",
        

        # Dados financeiros do instrumento (Taxas / Preço Médio)
        "dividendos",
        "taxa_de_cupao",
        "data_de_emissao",
        "data_de_vencimento",
        "ultima_cotacao",

        # Livro de Ordens (como aparece no site)
        "quantidade_de_compra",
        "preco_de_compra",
        "yield_compra",
        "quantidade_de_venda",
        "preco_de_venda",
        "yield_venda"
    ]

    # agora sim, adiciona uma coluna nova
    df["data_referencia"] = hoje

    
    print("Ficheiro lido")

    print(df.head())
    
    #PASSO 4: CRIAÇÃO DA BASE DE DADOS (CONEXÃO COM MYSQL)
    
    conn = pymysql.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()
    
    #Criação da tabela
    
    cursor.execute(""" CREATE TABLE IF NOT EXISTS livros_de_ordens(
        
        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, 
        codigo VARCHAR(20) NOT NULL, 
        isin VARCHAR(12), 
        tipologia VARCHAR(30) NOT NULL,
        dividendos DECIMAL(16,2),
        taxa_de_cupao DECIMAL(6,2),
        data_de_emissao DATE, 
        data_de_vencimento DATE, 
        ultima_cotacao DECIMAL(16,2),
        quantidade_de_compra DECIMAL(18,2),
        preco_de_compra DECIMAL(16,2),
        yield_compra DECIMAL(8,4),
        quantidade_de_venda DECIMAL(18,2),
        preco_de_venda DECIMAL(16,2),
        yield_venda DECIMAL(8,4), 
        
        data_referencia DATE NOT NULL, 
        UNIQUE KEY uk_livros_ordens (codigo, data_referencia)
        
        
        
        ) ENGINE= InnoDB;
        """
        )
    
    records = df.to_dict(orient= "records")
    
    def limpar_nan(registo):
        for k, v in registo.items():
            if isinstance(v, float) and math.isnan(v):
                registo[k]= None
        return registo         
    
    records = [limpar_nan(regist) for regist in records]
    
    #PASSO 5: INSERÇÃO DOS DADOS
    
    sql = """ 
        INSERT IGNORE INTO livros_de_ordens (
            codigo, 
            isin,
            tipologia,
            dividendos,
            taxa_de_cupao,
            data_de_emissao,
            data_de_vencimento,
            ultima_cotacao, 
            quantidade_de_compra,
            preco_de_compra,
            yield_compra,
            quantidade_de_venda,
            preco_de_venda,
            yield_venda, 
            data_referencia
        ) VALUES(
            %(codigo)s,
            %(isin)s,
            %(tipologia)s,
            %(dividendos)s, 
            %(taxa_de_cupao)s,
            %(data_de_emissao)s,
            %(data_de_vencimento)s,
            %(ultima_cotacao)s,
            %(quantidade_de_compra)s,
            %(preco_de_compra)s,
            %(yield_compra)s,
            %(quantidade_de_venda)s,
            %(preco_de_venda)s,
            %(yield_venda)s,
            %(data_referencia)s
            )
    """
    cursor.executemany(sql, records)
    cursor.close()
    conn.close()
    
    print("Dados salvos no MYSQL com sucesso")
    
    logging.info("Execução terminada. Dados com sucesso")
    
    
     
except Exception as e:
    logging.error("Erro de execução", exc_info= True)
    raise