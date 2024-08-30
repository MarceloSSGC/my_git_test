# Função de posição para rótulos
def posicao_ext(ativo,
                base,
                tipo='label',
                mont_buy=1,
                desmont_buy=1,
                mont_sell=1,
                desmont_sell=1,
                serie_paralelo="serie",
                zero_option="mont"):
    
    import numpy as np

    base = base.copy()

    # Criando colunas que receberão posições
    nome_col_compra = 'posicao_Compra_' + tipo 
    nome_col_venda = 'posicao_Venda_' + tipo 

    # Inicializando colunas com zeros
    base[nome_col_compra] = np.zeros(len(base))
    base[nome_col_venda] = np.zeros(len(base))

    base['op_' + tipo + '_' + ativo] = np.repeat('Neutral', len(base))

    flag_buy_mont = False  # Indica se há operação de compra em andamento
    flag_buy_desmont = False  # Indica se há operação de compra em andamento
    flag_sell_mont = False  # Indica se há operação de venda em andamento
    flag_sell_desmont = False  # Indica se há operação de venda em andamento

    # =====================================================================
    # =====================================================================
    if zero_option == "mont":
        # Compra/Short Selling em Paralelo

        if serie_paralelo == "paralelo":
            for i in range(base.shape[0] - 1):  # i += 1

                # =============================================================
                # Buy

                # Inicia Montagem da Compra
                if base[tipo][i] > 0 and flag_buy_mont is False:
                    flag_buy_mont = True
                    flag_buy_desmont = False
                    base.at[i + 1, nome_col_compra] = min(base.at[i, nome_col_compra] + 1 / mont_buy, 1)

                # Continua Montagem da Compra
                elif base[tipo][i] >= 0 and flag_buy_mont is True:
                    base.at[i + 1, nome_col_compra] = min(base.at[i, nome_col_compra] + 1 / mont_buy, 1)

                # Inicia Desmontagem da Compra
                elif base[tipo][i] < 0 and flag_buy_mont is True:
                    flag_buy_mont = False
                    flag_buy_desmont = True
                    base.at[i + 1, nome_col_compra] = max(base.at[i, nome_col_compra] - 1 / desmont_buy, 0)

                # Continua Desmontagem da Compra
                elif base[tipo][i] <= 0 and flag_buy_desmont is True:
                    base.at[i + 1, nome_col_compra] = max(base.at[i, nome_col_compra] - 1 / desmont_buy, 0)
                    if base.at[i + 1, nome_col_compra] < 1e-5:
                        base.at[i + 1, nome_col_compra] = 0
                        flag_buy_desmont = False

                # =============================================================
                # Sell

                # Inicia Montagem do Short Selling
                if base[tipo][i] < 0 and flag_sell_mont is False:
                    flag_sell_mont = True
                    flag_sell_desmont = False
                    base.at[i + 1, nome_col_venda] = min(base.at[i, nome_col_venda] + 1 / mont_sell, 1)

                # Continua a Montagem do Short Selling
                elif base[tipo][i] <= 0 and flag_sell_mont is True:
                    base.at[i + 1, nome_col_venda] = min(base.at[i, nome_col_venda] + 1 / mont_sell, 1)

                # Inicia Desmontagem do Short Selling
                elif base[tipo][i] > 0 and flag_sell_mont is True:
                    flag_sell_mont = False
                    flag_sell_desmont = True
                    base.at[i + 1, nome_col_venda] = max(base.at[i, nome_col_venda] - 1 / desmont_sell, 0)

                # Continua a Desmontagem do Short Selling
                elif base[tipo][i] >= 0 and flag_sell_desmont is True:
                    base.at[i + 1, nome_col_venda] = max(base.at[i, nome_col_venda] - 1 / desmont_sell, 0)
                    if base.at[i + 1, nome_col_venda] < 1e-5:
                        base.at[i + 1, nome_col_venda] = 0
                        flag_sell_desmont = False

        # =============================================================
        # Compra/Short Selling em Serie

        if serie_paralelo == "serie":
            Init_Op = True
            Run_Op = None
            for i in range(base.shape[0] - 1):  # i += 1

                # Carregando valores do dia anterior
                base.at[i + 1, nome_col_compra] = base.at[i, nome_col_compra]
                base.at[i + 1, nome_col_venda] = base.at[i, nome_col_venda]

                # =============================================================
                if Init_Op is True:
                    # Buy

                    # Inicia Montagem da Compra
                    if base[tipo][i] > 0:
                        Init_Op = False
                        flag_buy_mont = True
                        Run_Op = "Buy"
                        base.at[i + 1, nome_col_compra] = min(base.at[i, nome_col_compra] + 1 / mont_buy, 1)

                    # Sell

                    # Inicia Montagem do Short Selling
                    elif base[tipo][i] < 0:
                        Init_Op = False
                        flag_sell_mont = True
                        Run_Op = "Sell"
                        base.at[i + 1, nome_col_venda] = min(base.at[i, nome_col_venda] + 1 / mont_sell, 1)
                # =============================================================
                # Buy
                if Run_Op == "Buy":

                    # Inicia Montagem da Compra
                    if base[tipo][i] > 0 and flag_buy_mont is False:
                        flag_buy_mont = True
                        flag_buy_desmont = False
                        base.at[i + 1, nome_col_compra] = min(base.at[i, nome_col_compra] + 1 / mont_buy, 1)

                    # Continua Montagem da Compra
                    elif base[tipo][i] >= 0 and flag_buy_mont is True:
                        base.at[i + 1, nome_col_compra] = min(base.at[i, nome_col_compra] + 1 / mont_buy, 1)

                    # Inicia Desmontagem da Compra
                    elif base[tipo][i] < 0 and flag_buy_mont is True:
                        flag_buy_mont = False
                        flag_buy_desmont = True
                        base.at[i + 1, nome_col_compra] = max(base.at[i, nome_col_compra] - 1 / desmont_buy, 0)

                        # Se sobrou residual desprezível ou posição zerou
                        if base.at[i + 1, nome_col_compra] <= 1e-5:
                            # Seta posição pra zero caso tenha sobrado residual
                            base.at[i + 1, nome_col_compra] = 0

                            # Muda tipo da operação
                            Run_Op = "Sell"

                            # Inicia montagem da venda
                            flag_sell_mont = True
                            flag_sell_desmont = False
                            base.at[i + 1, nome_col_venda] = min(base.at[i, nome_col_venda] + 1 / mont_sell, 1)

                    # Continua Desmontagem da Compra
                    elif base[tipo][i] <= 0 and flag_buy_desmont is True:
                        base.at[i + 1, nome_col_compra] = max(base.at[i, nome_col_compra] - 1 / desmont_buy, 0)

                        # Se sobrou residual desprezível ou posição zerou
                        if base.at[i + 1, nome_col_compra] <= 1e-5:
                            # Seta posição pra zero caso tenha sobrado residual
                            base.at[i + 1, nome_col_compra] = 0

                            # Muda tipo da operação
                            Run_Op = "Sell"

                            # Inicia montagem da venda
                            flag_sell_mont = True
                            flag_sell_desmont = False
                            base.at[i + 1, nome_col_venda] = min(base.at[i, nome_col_venda] + 1 / mont_sell, 1)

                # =============================================================
                # Sell
                if Run_Op == "Sell":

                    # Inicia Montagem do Short Selling
                    if base[tipo][i] < 0 and flag_sell_mont is False:
                        flag_sell_mont = True
                        flag_sell_desmont = False
                        base.at[i + 1, nome_col_venda] = min(base.at[i, nome_col_venda] + 1 / mont_sell, 1)

                    # Continua a Montagem do Short Selling
                    elif base[tipo][i] <= 0 and flag_sell_mont is True:
                        base.at[i + 1, nome_col_venda] = min(base.at[i, nome_col_venda] + 1 / mont_sell, 1)

                    # Inicia Desmontagem do Short Selling
                    elif base[tipo][i] > 0 and flag_sell_mont is True:
                        flag_sell_mont = False
                        flag_sell_desmont = True
                        base.at[i + 1, nome_col_venda] = max(base.at[i, nome_col_venda] - 1 / desmont_sell, 0)

                        # Se sobrou residual desprezível ou posição zerou
                        if base.at[i + 1, nome_col_venda] < 1e-5:
                            # Seta posição pra zero caso tenha sobrado residual
                            base.at[i + 1, nome_col_venda] = 0

                            # Muda tipo da operação
                            Run_Op = "Buy"

                            # Inicia montagem da compra
                            flag_buy_mont = True
                            flag_buy_desmont = False
                            base.at[i + 1, nome_col_compra] = min(base.at[i, nome_col_compra] + 1 / mont_buy, 1)

                    # Continua a Desmontagem do Short Selling
                    elif base[tipo][i] >= 0 and flag_sell_desmont is True:
                        base.at[i + 1, nome_col_venda] = max(base.at[i, nome_col_venda] - 1 / desmont_sell, 0)
                        Run_Op = "Buy" if base.at[i + 1, nome_col_venda] == 0 else "Sell"

                        # Se sobrou residual desprezível ou posição zerou
                        if base.at[i + 1, nome_col_venda] < 1e-5:
                            # Seta posição pra zero caso tenha sobrado residual
                            base.at[i + 1, nome_col_venda] = 0

                            # Muda tipo da operação
                            Run_Op = "Buy"

                            # Inicia montagem da compra
                            flag_buy_mont = True
                            flag_buy_desmont = False
                            base.at[i + 1, nome_col_compra] = min(base.at[i, nome_col_compra] + 1 / mont_buy, 1)

                # Colunas com operações do momento
                if Run_Op == "Buy":
                    base.at[i + 1, 'op_' + tipo + '_' + ativo] = 'Buy'

                elif Run_Op == "Sell":
                    base.at[i + 1, 'op_' + tipo + '_' + ativo] = 'Sell'

    # =====================================================================
    # =====================================================================
    if zero_option == "neutro":
        # Compra/Short Selling em Paralelo

        if serie_paralelo == "paralelo":
            for i in range(base.shape[0] - 1):  # i += 1

                # =============================================================
                # Buy

                # Montagem da Compra
                if base[tipo][i] > 0:
                    base.at[i + 1, nome_col_compra] = min(base.at[i, nome_col_compra] + 1 / mont_buy, 1)

                # Apenas mantem a Compra
                elif base[tipo][i] == 0:
                    base.at[i + 1, nome_col_compra] = base.at[i, nome_col_compra]

                # Desmontagem da Compra
                elif base[tipo][i] < 0:
                    base.at[i + 1, nome_col_compra] = max(base.at[i, nome_col_compra] - 1 / desmont_buy, 0)
                    if base.at[i + 1, nome_col_compra] < 1e-5:
                        base.at[i + 1, nome_col_compra] = 0

                # =============================================================
                # Sell

                # Inicia Montagem do Short Selling
                if base[tipo][i] < 0:
                    base.at[i + 1, nome_col_venda] = min(base.at[i, nome_col_venda] + 1 / mont_sell, 1)

                # Apenas mantem o Short Selling
                elif base[tipo][i] == 0:
                    base.at[i + 1, nome_col_venda] = base.at[i, nome_col_venda]

                # Continua a Desmontagem do Short Selling
                elif base[tipo][i] > 0:
                    base.at[i + 1, nome_col_venda] = max(base.at[i, nome_col_venda] - 1 / desmont_sell, 0)
                    if base.at[i + 1, nome_col_venda] < 1e-5:
                        base.at[i + 1, nome_col_venda] = 0
                        flag_sell_desmont = False

        # =============================================================
        # Compra/Short Selling em Serie

        if serie_paralelo == "serie":
            Init_Op = True
            Run_Op = None
            for i in range(base.shape[0] - 1):  # i += 1

                # Carregando valores do dia anterior
                base.at[i + 1, nome_col_compra] = base.at[i, nome_col_compra]
                base.at[i + 1, nome_col_venda] = base.at[i, nome_col_venda]

                # =============================================================
                if Init_Op is True:
                    # Buy

                    # Inicia Montagem da Compra
                    if base[tipo][i] > 0:
                        Init_Op = False
                        flag_buy_mont = True
                        Run_Op = "Buy"
                        base.at[i + 1, nome_col_compra] = min(base.at[i, nome_col_compra] + 1 / mont_buy, 1)

                    # Sell

                    # Inicia Montagem do Short Selling
                    elif base[tipo][i] < 0:
                        Init_Op = False
                        flag_sell_mont = True
                        Run_Op = "Sell"
                        base.at[i + 1, nome_col_venda] = min(base.at[i, nome_col_venda] + 1 / mont_sell, 1)
                # =============================================================
                # Buy
                if Run_Op == "Buy":

                    # Montagem da Compra
                    if base[tipo][i] > 0:
                        base.at[i + 1, nome_col_compra] = min(base.at[i, nome_col_compra] + 1 / mont_buy, 1)

                    # Apenas mantem a Compra
                    elif base[tipo][i] == 0:
                        base.at[i + 1, nome_col_compra] = base.at[i, nome_col_compra]

                    # Desmontagem da Compra
                    elif base[tipo][i] < 0:
                        base.at[i + 1, nome_col_compra] = max(base.at[i, nome_col_compra] - 1 / desmont_buy, 0)

                        # Se sobrou residual desprezível ou posição zerou
                        if base.at[i + 1, nome_col_compra] <= 1e-5:
                            # Seta posição pra zero caso tenha sobrado residual
                            base.at[i + 1, nome_col_compra] = 0

                            # Muda tipo da operação
                            Run_Op = "Sell"

                            # Inicia montagem da venda
                            base.at[i + 1, nome_col_venda] = min(base.at[i, nome_col_venda] + 1 / mont_sell, 1)

                # =============================================================
                # Sell
                if Run_Op == "Sell":

                    # Inicia Montagem do Short Selling
                    if base[tipo][i] < 0:
                        base.at[i + 1, nome_col_venda] = min(base.at[i, nome_col_venda] + 1 / mont_sell, 1)

                    # Continua a Montagem do Short Selling
                    elif base[tipo][i] == 0:
                        base.at[i + 1, nome_col_venda] = base.at[i, nome_col_venda]

                    # Continua a Desmontagem do Short Selling
                    elif base[tipo][i] > 0:
                        base.at[i + 1, nome_col_venda] = max(base.at[i, nome_col_venda] - 1 / desmont_sell, 0)
                        # Run_Op = "Buy" if base.at[i + 1, nome_col_venda] == 0 else "Sell"

                        # Se sobrou residual desprezível ou posição zerou
                        if base.at[i + 1, nome_col_venda] < 1e-5:
                            # Seta posição pra zero caso tenha sobrado residual
                            base.at[i + 1, nome_col_venda] = 0

                            # Muda tipo da operação
                            Run_Op = "Buy"

                            # Inicia montagem da compra
                            base.at[i + 1, nome_col_compra] = min(base.at[i, nome_col_compra] + 1 / mont_buy, 1)

                # Colunas com operações do momento
                if Run_Op == "Buy":
                    base.at[i + 1, 'cor_' + tipo] = 'Buy'

                elif Run_Op == "Sell":
                    base.at[i + 1, 'cor_' + tipo] = 'Sell'

    # =====================================================================
    # =====================================================================
    if zero_option == "desmont":
        # Compra/Short Selling em Paralelo

        if serie_paralelo == "paralelo":
            for i in range(base.shape[0] - 1):  # i += 1

                # =============================================================
                # Buy

                # Inicia Montagem da Compra
                if base[tipo][i] > 0:
                    base.at[i + 1, nome_col_compra] = min(base.at[i, nome_col_compra] + 1 / mont_buy, 1)
                    base.at[i + 1, 'op_' + tipo + '_' + ativo] = 'Buy'
                    
                # Desmontagem da Compra
                elif base[tipo][i] <= 0:
                    base.at[i + 1, nome_col_compra] = max(base.at[i, nome_col_compra] - 1 / desmont_buy, 0)
                    if base.at[i + 1, nome_col_compra] < 1e-5:
                        base.at[i + 1, nome_col_compra] = 0

                # =============================================================
                # Sell

                # Inicia Montagem do Short Selling
                if base[tipo][i] < 0:
                    base.at[i + 1, nome_col_venda] = min(base.at[i, nome_col_venda] + 1 / mont_sell, 1)
                    base.at[i + 1, 'op_' + tipo + '_' + ativo] = 'Sell'
                    
                # Desmontagem do Short Selling
                elif base[tipo][i] >= 0:
                    base.at[i + 1, nome_col_venda] = max(base.at[i, nome_col_venda] - 1 / desmont_sell, 0)
                    if base.at[i + 1, nome_col_venda] < 1e-5:
                        base.at[i + 1, nome_col_venda] = 0
                        
                # Registrando operação neutra
                if (base.at[i+1, nome_col_compra]==0) & (base.at[i+1, nome_col_venda]==0):
                    base.at[i+1, 'op_' + tipo + '_' + ativo] = 'Neutral'

        # =============================================================
        # Buy/Short Selling em Serie

        if serie_paralelo == "serie":
            Init_Op = True
            Run_Op = None
            for i in range(base.shape[0] - 1):  # i += 1

                # Carregando valores do dia anterior
                base.at[i+1, nome_col_compra] = base.at[i, nome_col_compra]
                base.at[i+1, nome_col_venda] = base.at[i, nome_col_venda]

                # =============================================================
                if Init_Op is True:
                    # Buy

                    # Inicia Montagem da Compra
                    if base[tipo][i] > 0:
                        Init_Op = False
                        flag_buy_mont = True
                        Run_Op = "Buy"
                        base.at[i + 1, nome_col_compra] = min(base.at[i, nome_col_compra] + 1 / mont_buy, 1)

                    # Sell

                    # Inicia Montagem do Short Selling
                    elif base[tipo][i] < 0:
                        Init_Op = False
                        flag_sell_mont = True
                        Run_Op = "Sell"
                        base.at[i + 1, nome_col_venda] = min(base.at[i, nome_col_venda] + 1 / mont_sell, 1)
                # =============================================================
                # Buy
                if Run_Op == "Buy":

                    # Inicia Montagem da Compra
                    if base[tipo][i] > 0 and flag_buy_mont is False:
                        flag_buy_mont = True
                        flag_buy_desmont = False
                        base.at[i + 1, nome_col_compra] = min(base.at[i, nome_col_compra] + 1 / mont_buy, 1)

                    # Continua Montagem da Compra
                    elif base[tipo][i] > 0 and flag_buy_mont is True:
                        base.at[i + 1, nome_col_compra] = min(base.at[i, nome_col_compra] + 1 / mont_buy, 1)

                    # Inicia Desmontagem da Compra
                    elif base[tipo][i] <= 0 and flag_buy_mont is True:
                        flag_buy_mont = False
                        flag_buy_desmont = True
                        base.at[i + 1, nome_col_compra] = max(base.at[i, nome_col_compra] - 1 / desmont_buy, 0)

                        # Se sobrou residual desprezível ou posição zerou
                        if base.at[i + 1, nome_col_compra] <= 1e-5:
                            # Seta posição pra zero caso tenha sobrado residual
                            base.at[i + 1, nome_col_compra] = 0

                            # Muda tipo da operação
                            Run_Op = "Sell"

                            # Inicia montagem da venda
                            flag_sell_mont = True
                            flag_sell_desmont = False
                            base.at[i + 1, nome_col_venda] = min(base.at[i, nome_col_venda] + 1 / mont_sell, 1)

                    # Continua Desmontagem da Compra
                    elif base[tipo][i] <= 0 and flag_buy_desmont is True:
                        base.at[i + 1, nome_col_compra] = max(base.at[i, nome_col_compra] - 1 / desmont_buy, 0)

                        # Se sobrou residual desprezível ou posição zerou
                        if base.at[i + 1, nome_col_compra] <= 1e-5:
                            # Seta posição pra zero caso tenha sobrado residual
                            base.at[i + 1, nome_col_compra] = 0

                            # Muda tipo da operação
                            Run_Op = "Sell"

                            # Inicia montagem da venda
                            flag_sell_mont = True
                            flag_sell_desmont = False
                            base.at[i + 1, nome_col_venda] = min(base.at[i, nome_col_venda] + 1 / mont_sell, 1)

                # =============================================================
                # Sell
                if Run_Op == "Sell":

                    # Inicia Montagem do Short Selling
                    if base[tipo][i] < 0 and flag_sell_mont is False:
                        flag_sell_mont = True
                        flag_sell_desmont = False
                        base.at[i + 1, nome_col_venda] = min(base.at[i, nome_col_venda] + 1 / mont_sell, 1)

                    # Continua a Montagem do Short Selling
                    elif base[tipo][i] < 0 and flag_sell_mont is True:
                        base.at[i + 1, nome_col_venda] = min(base.at[i, nome_col_venda] + 1 / mont_sell, 1)

                    # Inicia Desmontagem do Short Selling
                    elif base[tipo][i] >= 0 and flag_sell_mont is True:
                        flag_sell_mont = False
                        flag_sell_desmont = True
                        base.at[i + 1, nome_col_venda] = max(base.at[i, nome_col_venda] - 1 / desmont_sell, 0)

                        # Se sobrou residual desprezível ou posição zerou
                        if base.at[i + 1, nome_col_venda] < 1e-5:
                            # Seta posição pra zero caso tenha sobrado residual
                            base.at[i + 1, nome_col_venda] = 0

                            # Muda tipo da operação
                            Run_Op = "Buy"

                            # Inicia montagem da compra
                            flag_buy_mont = True
                            flag_buy_desmont = False
                            base.at[i + 1, nome_col_compra] = min(base.at[i, nome_col_compra] + 1 / mont_buy, 1)

                    # Continua a Desmontagem do Short Selling
                    elif base[tipo][i] >= 0 and flag_sell_desmont is True:
                        base.at[i + 1, nome_col_venda] = max(base.at[i, nome_col_venda] - 1 / desmont_sell, 0)
                        Run_Op = "Buy" if base.at[i + 1, nome_col_venda] == 0 else "Sell"

                        # Se sobrou residual desprezível ou posição zerou
                        if base.at[i + 1, nome_col_venda] < 1e-5:
                            # Seta posição pra zero caso tenha sobrado residual
                            base.at[i + 1, nome_col_venda] = 0

                            # Muda tipo da operação
                            Run_Op = "Buy"

                            # Inicia montagem da compra
                            flag_buy_mont = True
                            flag_buy_desmont = False
                            base.at[i+1, nome_col_compra] = min(base.at[i, nome_col_compra] + 1 / mont_buy, 1)

                # Registrando operação neutra
                if (base.at[i+1, nome_col_compra]==0) & (base.at[i+1, nome_col_venda]==0):
                    Run_Op == 'Neutral'
                
                # Colunas com operações do momento
                base.at[i+1, 'op_' + tipo + '_' + ativo] = Run_Op

    return base[[nome_col_compra,
                nome_col_venda,
                'op_' + tipo + '_' + ativo]]

# Função para log-retornos teóricos das posições compradas
def log_ret_compra(tipo,
                   base,
                   cenario,
                   thresh_in = 1,
                   thresh_out = -1,
                   slippage_compra = 0,
                   slippage_venda = 0):
    
    import numpy as np

    # Nome da coluna que receberá log-retornos calculados
    nome_col = 'log_ret_compra_' + tipo  

    # Inicializando coluna de log-retornos com zeros
    base[nome_col] = np.zeros(len(base)) 

    # Flag indicadora de posição comprada
    flag_buy = False 

    # Iterando para todas as linhas com exceção da última
    for i,row in enumerate(base.head(-1).itertuples()): 

        # Inicia operação de compra se não houver nenhuma de compra em andamento
        if row.media_in >= thresh_in and flag_buy == False: 
            preco_op = (1+slippage_compra) * base.at[i+1,cenario]
            flag_buy = True
            base.at[i+1,nome_col] = np.log(base.at[i+1,'Close']/preco_op)       
            
        # Encerra operação de compra se houver uma em andamento
        elif row.media_out <= thresh_out and flag_buy == True: 
            preco_op = (1-slippage_venda) * base.at[i+1,cenario]
            flag_buy = False
            base.at[i+1,nome_col] = np.log(preco_op/base.at[i,'Close'])
            
        # Operação de compra em andamento
        elif flag_buy == True:
            base.at[i+1,nome_col] = np.log(base.at[i+1,'Close']/base.at[i,'Close'])

    return base[nome_col]

# Função para log-retornos teóricos das posições vendidas
def log_ret_venda(tipo,
                  base,
                  cenario,
                  thresh_in = -1,
                  thresh_out = 1,
                  slippage_compra = 0,
                  slippage_venda = 0):
    
    import numpy as np

    # Nome da coluna que receberá log-retornos
    nome_col = 'log_ret_venda_' + tipo 

    # Inicializando coluna com zeros
    base[nome_col] = np.zeros(len(base)) 

    # Flag indicadora de posição vendida
    flag_sell = False 

    for i,row in enumerate(base.head(-1).itertuples()):

        # Inicia operação de venda se não houver nenhuma de venda em andamento 
        if row.media_in <= thresh_in and flag_sell == False: 
            preco_op = (1-slippage_venda) * base.at[i+1,cenario]
            flag_sell = True
            base.at[i+1,nome_col] = np.log(2 - base.at[i+1,'Close']/preco_op)
            
        elif row.media_out >= thresh_out and flag_sell == True:
            preco_op = (1+slippage_compra) * base.at[i+1,cenario]
            flag_sell = False
            base.at[i+1,nome_col] = np.log(2 - preco_op/base.at[i,'Close']) 
            
        # Operação de venda em andamento
        elif flag_sell == True:
            base.at[i+1,nome_col] = np.log(2 - base.at[i+1,'Close']/base.at[i,'Close'])

    return base[nome_col]


# Função para log-retornos
def log_ret(tipo,
            base,
            cenario,
            thresh_in_buy=1,
            thresh_out_buy=-1,
            thresh_in_sell=-1,
            thresh_out_sell=1,
            slippage_compra = 0,
            slippage_venda = 0,
            win_0_buy=1e6,
            win_0_sell=1e6):

    import numpy as np

    # Nomes das colunas que receberão log-retornos calculados
    nome_col_compra = 'log_ret_compra_' + tipo  
    nome_col_venda = 'log_ret_venda_' + tipo

    # Inicializando coluna de log-retornos com zeros
    base[nome_col_compra] = np.zeros(len(base)) 
    base[nome_col_venda] = np.zeros(len(base)) 
    base['log_ret_cdi'] = np.zeros(len(base))

    # Flags indicadoras de posição comprada
    flag_buy = False 
    flag_sell = False

    # Iterando para todas as linhas com exceção da última
    for i,row in enumerate(base.head(-1).itertuples()): 
        
        ##################################
        ## COMPRA

        # Inicia operação de compra se não houver nenhuma de compra em andamento
        if row.media_in >= thresh_in_buy and flag_buy == False: 
            preco_op = (1+slippage_compra) * base.at[i+1,cenario]
            flag_buy = True
            base.at[i+1,nome_col_compra] = np.log(base.at[i+1,'Close']/preco_op)       
            
        # Encerra operação de compra se houver uma em andamento
        elif row.media_out <= thresh_out_buy and flag_buy == True: 
            preco_op = (1-slippage_venda) * base.at[i+1,cenario]
            flag_buy = False
            base.at[i+1,nome_col_compra] = np.log(preco_op/base.at[i,'Close'])

        # Encerra operação de compra se últimos N rótulos forem 0
        elif i >= win_0_buy-1 and flag_buy == True and all([val == 0 for val in base[tipo].iloc[(i-win_0_buy+1):(i+1)]]):
            
            print(str(i) + 'Ativou Compra')
            preco_op = (1-slippage_venda) * base.at[i+1,cenario]
            flag_buy = False
            base.at[i+1,nome_col_compra] = np.log(preco_op/base.at[i,'Close'])
            
        # Operação de compra em andamento
        elif flag_buy == True:
            base.at[i+1,nome_col_compra] = np.log(base.at[i+1,'Close']/base.at[i,'Close'])

        ##################################
        ## VENDA

        # Inicia operação de venda se não houver nenhuma de venda em andamento 
        if row.media_in <= thresh_in_sell and flag_sell == False: 
            preco_op = (1-slippage_venda) * base.at[i+1,cenario]
            flag_sell = True
            base.at[i+1,nome_col_venda] = np.log(2 - base.at[i+1,'Close']/preco_op)
            
        elif row.media_out >= thresh_out_sell and flag_sell == True:
            preco_op = (1+slippage_compra) * base.at[i+1,cenario]
            flag_sell = False
            base.at[i+1,nome_col_venda] = np.log(2 - preco_op/base.at[i,'Close']) 

        # Encerra operação de compra se últimos N rótulos forem 0
        elif i >= win_0_sell-1 and flag_sell == True and all([val == 0 for val in base[tipo].iloc[(i-win_0_sell+1):(i+1)]]):
                
            print(str(i) + 'Ativou Venda')

            preco_op = (1+slippage_compra) * base.at[i+1,cenario]
            flag_sell = False
            base.at[i+1,nome_col_venda] = np.log(2 - preco_op/base.at[i,'Close']) 
            
        # Operação de venda em andamento
        elif flag_sell == True:
            base.at[i+1,nome_col_venda] = np.log(2 - base.at[i+1,'Close']/base.at[i,'Close'])

        ################################
        ## CDI

        if (flag_buy == False) and (flag_sell == False) and (i <= len(base)-3):
            base.at[i+2,'log_ret_cdi'] = np.log(base.at[i+1,'CDI'])

    return base[nome_col_compra] + base[nome_col_venda] + base['log_ret_cdi']

# Retornos teóricos       
def retornos_teoricos(
                      
                      # Geral
                      ativo='DAX',
                      period='Eval',
                      tipo='labelcl',
                      cenario = 'Open',

                      # Thresholds para médias móveis
                      thresh_in_buy = 1,
                      thresh_out_buy = -1,
                      thresh_in_sell = -1,
                      thresh_out_sell = 1,

                      # Tamanhos de janela para médias móveis
                      win_in = 1,
                      win_out = 1,
                      win_0_buy = 1e6,
                      win_0_sell = 1e6,

                      # Custos operacionais
                      slippage_compra = 0,
                      slippage_venda = 0):

                      # Datas de início e fim
                      #start_index=1700):
                
    import numpy as np
    import pandas as pd

    # Importando base do ativo
    base = pd.read_csv('bases_rotuladas/' + ativo + '-resultados.csv')

    # Recortando base para o período selecionado
    base = base[base['period']==period].reset_index(drop=True)
    #base = base.loc[1700:].reset_index(drop=True)

    # Calculando médias móveis de rótulos (entrada e saída)
    base['media_in'] = base[tipo].rolling(win_in).mean()
    base['media_out'] = base[tipo].rolling(win_out).mean()

    # Computa coluna com retornos totais (compra e venda)
    log_rets = log_ret(tipo=tipo,
                        base=base,
                        cenario=cenario,
                        thresh_in_buy=thresh_in_buy,
                        thresh_out_buy=thresh_out_buy,
                        thresh_in_sell=thresh_in_sell,
                        thresh_out_sell=thresh_out_sell,
                        slippage_compra =slippage_compra,
                        slippage_venda =slippage_venda,
                        win_0_buy=win_0_buy,
                        win_0_sell=win_0_sell)

    # Retornos líquidos (não é mais log-retorno)
    ret = log_rets.apply(lambda x: np.exp(x) - 1)
    
    return ret      


# Função que calcula métricas de avaliação para um grid de patrimônios gerado
def analise_grid(df,date,period):


    import quantstats as qs
    import pandas as pd
    import numpy as np
    import plotly.express as px
    
    ## Sharpe Ratio (BkTest)

    px.bar(df.apply(qs.stats.sharpe,axis='rows').sort_values().head(-1),
           labels = {'value':'Sharpe Ratio',
                     'index':''},
           title = 'Sharpe Ratio - ' + period).show()

    ## Sortino Ratio (BkTest)

    px.bar(df.apply(qs.stats.sortino,axis='rows').sort_values().head(-1),
           labels = {'value':'Sortino Ratio',
                     'index':''},
           title = 'Sortino Ratio - ' + period).show()

    ## Drawdown máximo (BkTest)

    px.bar(df.apply(qs.stats.max_drawdown,axis='rows').sort_values(),
           labels = {'value':'Drawdown Máximo',
                     'index':''},
           title = 'Drawdown máximo - ' + period).show()

    ## Retornos mensais (BkTest)

    df_month = df.copy()
    df_month.index = pd.to_datetime(date)
    df_month = df_month.apply(lambda x: np.exp(np.log(1+x.pct_change()).resample('21D').sum())-1,axis='rows')

    px.line(df_month,
            title = 'Retornos Mensais - ' + period).show()

    ## Porcentagem de meses acima do Buy & Hold

    df_alpha = df_month.apply(lambda x: x - df_month['Buy&Hold'])

    px.bar(df_alpha.apply(lambda x: len(x[x>0])/len(x),axis='rows').sort_values()).show()