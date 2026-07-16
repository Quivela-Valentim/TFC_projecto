import requests
import pandas as pd 
import os 
import pymysql
from datetime import date 
import urllib3
from io import BytesIO
import math
import logging


logging.basicConfig(
    filename= "bodiva.log", 
    level= logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

try:
    logging.info("execução iniciada")
    
    # configurações 

    url = "https://www.bodiva.ao/reports/controllers/excel/Export/ResumoMercados.php"

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

    #Passo 1 - Download Excel 

    os.makedirs(PASTA_DOWNLOAD, exist_ok= True)
    hoje = date.today().isoformat()



    ficheiro_excel = f"{PASTA_DOWNLOAD}/ResumoMercados_{hoje}.xlsx"

    r = session.get(url, headers=headers, timeout=(60, 720), verify= False, stream=True)

    if r.status_code != 200:
        raise Exception(f"Erro ao baixar o documento Excel:{r.status_code}")

    with open(ficheiro_excel, "wb") as f:
        #f.write(r.content)
        for chunk in r.iter_content(8192):
            if chunk:
                f.write(chunk)
        
    print(f"Ficheiro descarregado com sucesso {ficheiro_excel}")


    # Passo 2:  Ler o ficheiro Excel 

    df = pd.read_excel(ficheiro_excel, skiprows=2, header=0 )


    if df.empty:
        print("Excel vazio. Nada para ser lido!") 
        exit()
        #normalizar as colunas
    
    df.columns = [
        "codigo",
        "mercado",
        "preco", 
        "variacao_percentual", 
        "quantidade",
        "num_negocios",
        "volume"
    ]     
    #df.columns = (
    # df.columns
    # .str.strip()
    # .str.lower()
    # .str.replace("", "_")
    # .str.replace("ã", "a")
        #.str.replace("ç", "c")
    # .str.replace("é", "e")
        

    #)

    df["data_referencia"] = hoje 

    print("ficheiro lido")
    print(df.columns)
    print(df.head())

    # Passo 3: Conexão com MySQL 

    #conn = mysql.connector.connect(**MYSQL_CONFIG)
    conn = pymysql.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()
        
    # Criar tabela 
    cursor.execute( """ CREATE TABLE IF NOT EXISTS resumo_mercados (
        id INT NOT NULL AUTO_INCREMENT, 
        codigo VARCHAR(50) NOT NULL,
        mercado VARCHAR(50) NOT NULL,
        preco DECIMAL(16,2),
        variacao_percentual DECIMAL(7,4),
        quantidade DECIMAL(16,2), 
        num_negocios INT NOT NULL,
        volume DECIMAL(16,2), 
        PRIMARY KEY (id), 
        data_referencia DATE NOT NULL, 
        UNIQUE KEY uk_codigo_data (codigo, data_referencia)
        ) ENGINE=InnoDB;
        
        """
        
    )

    records = df.to_dict(orient="records")


    def limpar_nan(registo):
        for k, v in registo.items():
            if isinstance(v, float) and math.isnan(v):
                registo[k] = None
        return registo

    records = [limpar_nan(r) for r in records]


    # Passo 4: Inserção 

    sql = """
    INSERT IGNORE INTO resumo_mercados (
        codigo,
        mercado,
        preco, 
        variacao_percentual, 
        quantidade,
        num_negocios,
        volume,  
        data_referencia
        
    ) VALUES(
        %(codigo)s,
        %(mercado)s,
        %(preco)s,
        %(variacao_percentual)s,
        %(quantidade)s,
        %(num_negocios)s,
        %(volume)s,
        %(data_referencia)s
        )

    """

    """
    for _, row in df.iterrows():
        cursor.execute(sql, (
            str(row.get("codigo", "")),
            row.get("mercado"),
            row.get("preco"),
            row.get("variacao_percentual"),
            row.get("quantidade"),
            row.get("num_negocios"),
            row.get("volume"), 
            hoje 
            
            
        ))
    """
    cursor.executemany(sql, records)
    cursor.close()
    conn.close()


    print("Dados guardados no MySQL com sucesso")
    logging.info("dados guardados com sucesso ")
        
except Exception as e:
    logging.error("erro na execução", exc_info=True)
    raise 