import streamlit as st
import pandas as pd
from collections import deque
import numpy as np

# -------------------------------
# Configurações Iniciais
# -------------------------------
st.set_page_config(page_title="Bac Bo Analyzer Pro", layout="wide")
st.title("🎲 Bac Bo Analyzer Pro")
st.write("Analise padrões do Bac Bo por **Cor**, **Soma** ou **Modo Inteligente** com detecção de padrões avançada.")

# Histórico global (90 jogadas = 10 linhas x 9 colunas)
if 'historico' not in st.session_state:
    st.session_state.historico = deque(maxlen=90)

# -------------------------------
# Configurações do Usuário
# -------------------------------
modo = st.radio("Escolha o modo de análise:", ["Cor", "Soma", "Inteligente"])
st.markdown("---")

# -------------------------------
# Entrada de Dados
# -------------------------------
colA, colB = st.columns([2,2])
if modo == "Cor":
    colA.subheader("Registrar Resultado por Cor")
    c1, c2, c3 = colA.columns(3)
    if c1.button("🔵 Player"):
        st.session_state.historico.append({"resultado": "Player", "soma": None})
    if c2.button("🔴 Banker"):
        st.session_state.historico.append({"resultado": "Banker", "soma": None})
    if c3.button("🟡 Tie"):
        st.session_state.historico.append({"resultado": "Tie", "soma": None})

elif modo == "Soma" or modo == "Inteligente":
    colA.subheader("Registrar Resultado por Soma")
    soma_player = colA.number_input("Soma Player", min_value=2, max_value=12, step=1, key='sp')
    soma_banker = colA.number_input("Soma Banker", min_value=2, max_value=12, step=1, key='sb')
    if colA.button("Registrar"):
        if soma_player > soma_banker:
            vencedor = "Player"
        elif soma_banker > soma_player:
            vencedor = "Banker"
        else:
            vencedor = "Tie"
        st.session_state.historico.append({"resultado": vencedor, "soma": (soma_player, soma_banker)})

# -------------------------------
# Funções de Análise Avançada (Aprimorada para incluir todos os padrões)
# -------------------------------
def detectar_padroes(historico, modo_analise):
    sugestoes = []
    
    if len(historico) < 2:
        return ["Aguardando mais dados para análise."]
    
    ultimos_resultados = [item['resultado'] for item in historico]
    ultimas_somas = [item['soma'] for item in historico if item['soma'] is not None]
    ultimas_somas_totais = [sum(s) for s in ultimas_somas]

    # --- Padrões de Cor (Sempre analisados para o modo "Cor" ou "Inteligente") ---
    if modo_analise in ["Cor", "Inteligente"]:
        # Padrão 1 – Alternância Controlada
        if len(ultimos_resultados) >= 4:
            if (ultimos_resultados[-4:] == ['Player', 'Banker', 'Player', 'Banker'] or 
                ultimos_resultados[-4:] == ['Banker', 'Player', 'Banker', 'Player']):
                sugestoes.append("Alternância: Padrão de zigue-zague detectado. A quebra pode vir em breve.")
        elif len(ultimos_resultados) >= 3:
            if (ultimos_resultados[-3:] == ['Player', 'Banker', 'Player'] or 
                ultimos_resultados[-3:] == ['Banker', 'Player', 'Banker']):
                sugestoes.append("Alternância: Mantenha a aposta no padrão até a 3ª jogada. Após isso, saia.")
        
        # Padrão 2 – Streak Longa (Tendência)
        streak_count = 0
        if len(ultimos_resultados) >= 2:
            cor_atual = ultimos_resultados[-1]
            for i in range(len(ultimos_resultados) - 2, -1, -1):
                if ultimos_resultados[i] == cor_atual:
                    streak_count += 1
                else:
                    break
            
            if 2 <= streak_count <= 4:
                sugestoes.append(f"Tendência: {cor_atual} está em sequência de {streak_count+1}. Entre com aposta leve.")
            elif streak_count >= 5:
                sugestoes.append(f"Tendência: {cor_atual} está em sequência longa. Aposte contra a tendência com cautela.")

        # Padrão 3 – Dupla Camuflada
        if len(ultimos_resultados) >= 4:
            if (ultimos_resultados[-1] == ultimos_resultados[-2] and
                ultimos_resultados[-3] == ultimos_resultados[-4] and
                ultimos_resultados[-1] != ultimos_resultados[-3]):
                sugestoes.append("Dupla Camuflada: Padrão de pares (PP-BB). Provável que venha outro par.")

    # --- Padrões de Soma (Sempre analisados para o modo "Soma" ou "Inteligente") ---
    if modo_analise in ["Soma", "Inteligente"]:
        def tipo_soma(soma_total):
            if 10 <= soma_total <= 12: return 'alta'
            if 2 <= soma_total <= 5: return 'baixa'
            return 'mediana'
        
        if len(ultimas_somas_totais) >= 2:
            # Padrão 4 – Ciclo de Altos/Baixos
            tipo_1 = tipo_soma(ultimas_somas_totais[-1])
            tipo_2 = tipo_soma(ultimas_somas_totais[-2])
            if tipo_1 == 'alta' and tipo_2 == 'alta':
                sugestoes.append("Soma: Duas somas altas consecutivas. O próximo resultado tende a ser baixo.")

        if len(ultimas_somas_totais) >= 3:
            # Padrão 5 – Equilíbrio Gradual
            tipos = [tipo_soma(s) for s in ultimas_somas_totais[-3:]]
            if all(t in ['alta', 'baixa'] for t in tipos):
                sugestoes.append("Soma: As últimas 3 somas foram extremas. Prepare-se para uma soma mediana.")

            # Padrão 6 – Quebra Estatística
            if (ultimas_somas_totais[-3] < ultimas_somas_totais[-2] < ultimas_somas_totais[-1] or
                ultimas_somas_totais[-3] > ultimas_somas_totais[-2] > ultimas_somas_totais[-1]):
                sugestoes.append("Soma: Sequência crescente/decrescente detectada. Espere uma quebra abrupta.")

    # --- Padrões do Empate (Sempre analisados para todos os modos) ---
    if len(ultimos_resultados) >= 2:
        # Padrão 9 – Duplo Empate Camuflado
        tie_indices = [i for i, r in enumerate(ultimos_resultados) if r == 'Tie']
        if len(tie_indices) >= 1:
            ultimo_tie_idx = tie_indices[-1]
            if (len(ultimos_resultados) - 1) - ultimo_tie_idx <= 2:
                sugestoes.append("Tie: Um Tie recente. Considere uma segunda aposta leve no Tie.")
        
        # Padrão 7 – Âncora após Streak
        if len(ultimos_resultados) >= 4:
            streak_count = 0
            cor_atual = ultimos_resultados[-2]
            for i in range(len(ultimos_resultados) - 3, -1, -1):
                if ultimos_resultados[i] == cor_atual:
                    streak_count += 1
                else:
                    break
            if streak_count >= 3 and ultimos_resultados[-1] != cor_atual:
                sugestoes.append("Tie: Uma streak longa foi quebrada. Aposta leve em Tie pode ser uma boa opção.")

        # Padrão 8 – Tie após Reversão
        if len(ultimos_resultados) >= 4:
            if (ultimos_resultados[-2] == 'Player' and ultimos_resultados[-1] == 'Banker') or \
               (ultimos_resultados[-2] == 'Banker' and ultimos_resultados[-1] == 'Player'):
                sugestoes.append("Tie: Quebra de tendência detectada. Tie tem alta probabilidade nos próximos lançamentos.")

    # --- Padrão de Combinação (Apenas para modo "Inteligente") ---
    if modo_analise == "Inteligente" and len(ultimos_resultados) >= 4 and len(ultimas_somas) >= 4:
        resultados_streak = ultimos_resultados[-4:]
        somas_totais_streak = [sum(s) for s in ultimas_somas[-4:]]
        
        if resultados_streak == ['Player', 'Player', 'Player', 'Player'] and all(s > 8 for s in somas_totais_streak):
            sugestoes.append("Combinação: Alta chance de Tie ou Banker. Sugere-se 80% Banker e 20% Tie.")

    return sugestoes if sugestoes else ["Nenhum padrão forte detectado."]

# -------------------------------
# Exibir Histórico em Grade
# -------------------------------
colB.subheader("Histórico Visual")
if st.session_state.historico:
    resultados = [item['resultado'] for item in st.session_state.historico]
    cores_emoji = {"Player": "🔵", "Banker": "🔴", "Tie": "🟡"}
    
    # Criar uma grade de 10x9 usando colunas
    grid_rows = [resultados[i:i+9] for i in range(0, len(resultados), 9)]
    
    # Preencher espaços vazios para completar a grade
    while len(grid_rows) < 10:
        grid_rows.append(['' for _ in range(9)])

    for row in grid_rows:
        cols = st.columns(9)
        for i, res in enumerate(row):
            if res:
                cols[i].write(cores_emoji[res])


# -------------------------------
# Análise e Estratégia
# -------------------------------
st.markdown("---")
st.subheader("📊 Análise Avançada")

# Chamando a função aprimorada
sugestoes_analise = detectar_padroes(st.session_state.historico, modo)

# Exibindo as sugestões
if sugestoes_analise:
    for sugestao in sugestoes_analise:
        if "Tendência" in sugestao or "Combinação" in sugestao:
            st.success(sugestao)
        elif "Alternância" in sugestao or "Soma" in sugestao:
            st.info(sugestao)
        elif "Tie" in sugestao:
            st.warning(sugestao)
        else:
            st.write(sugestao)
else:
    st.warning("Adicione mais jogadas para iniciar a análise.")

# -------------------------------
# Botões Extras
# -------------------------------
st.markdown("---")
c4, c5 = st.columns(2)
if c4.button("🔄 Resetar Histórico"):
    st.session_state.historico.clear()
if c5.button("⬇️ Exportar Histórico"):
    df = pd.DataFrame(st.session_state.historico)
    st.download_button("Baixar CSV", df.to_csv(index=False), file_name="historico_bacbo.csv")
