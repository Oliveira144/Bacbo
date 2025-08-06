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
    soma_player = colA.number_input("Soma Player", min_value=2, max_value=12, step=1)
    soma_banker = colA.number_input("Soma Banker", min_value=2, max_value=12, step=1)
    if colA.button("Registrar"):
        if soma_player > soma_banker:
            vencedor = "Player"
        elif soma_banker > soma_player:
            vencedor = "Banker"
        else:
            vencedor = "Tie"
        st.session_state.historico.append({"resultado": vencedor, "soma": (soma_player, soma_banker)})

# -------------------------------
# Funções de Análise Avançada
# -------------------------------
def detectar_padroes(historico):
    analise = ""
    chance_tie = 6  # base real de probabilidade
    sugestao = "Sem padrão forte"
    risco_quebra = "Baixo"
    
    ultimos = [item['resultado'] for item in historico]
    
    if len(ultimos) < 6:
        return sugestao, chance_tie, risco_quebra
    
    # Últimos 6 para análise
    seq = ultimos[-6:]
    
    # 1. Streak longa
    if len(set(seq[-4:])) == 1 and seq[-1] != "Tie":
        sugestao = f"Tendência detectada: {seq[-1]}"
        chance_tie += 12
        risco_quebra = "Alto" if len(set(seq[-5:])) == 1 else "Médio"
    
    # 2. Alternância
    if seq[-4:] == ["Player","Banker","Player","Banker"] or seq[-4:] == ["Banker","Player","Banker","Player"]:
        sugestao = "Alternância detectada"
        chance_tie += 10
        risco_quebra = "Médio"
    
    # 3. Tie recente
    if seq[-1] == "Tie":
        chance_tie += 15
    if "Tie" in seq[-3:]:
        chance_tie += 10
    
    # 4. Dupla camuflada
    if seq[-2:] == ["Player","Player"] or seq[-2:] == ["Banker","Banker"]:
        sugestao = f"Possível padrão de pares ({seq[-2]} dupla)"
    
    # 5. Soma inteligente (se disponível)
    somas = [item['soma'] for item in historico if item['soma'] is not None][-4:]
    if len(somas) >= 3:
        medias = [sum(x)/2 for x in somas]
        if all(m > 9 for m in medias):  # altos consecutivos
            chance_tie += 8
            sugestao += " | Sequência de somas altas"
        if all(m < 5 for m in medias):  # baixos consecutivos
            chance_tie += 8
            sugestao += " | Sequência de somas baixas"
    
    return sugestao, min(chance_tie, 70), risco_quebra

# -------------------------------
# Exibir Histórico em Grade
# -------------------------------
colB.subheader("Histórico Visual")
if st.session_state.historico:
    resultados = [item['resultado'] for item in st.session_state.historico]
    grid = [resultados[i:i+9] for i in range(0, len(resultados), 9)]
    for linha in grid:
        for res in linha:
            cor = "🔵" if res == "Player" else "🔴" if res == "Banker" else "🟡"
            st.write(cor, end=" ")
        st.write("")

# -------------------------------
# Análise e Estratégia
# -------------------------------
st.markdown("---")
sugestao, chance_tie, risco_quebra = detectar_padroes(st.session_state.historico)
st.subheader("📊 Análise Avançada")
st.write(f"**Sugestão:** {sugestao}")
st.write(f"**Chance de Tie:** {chance_tie}%")
st.write(f"**Risco de quebra:** {risco_quebra}")

# Estratégia recomendada
if "Tendência" in sugestao:
    st.success("Sugestão: Apostar na tendência com stake moderada. Tie opcional com valor baixo.")
elif "Alternância" in sugestao:
    st.info("Sugestão: Apostar na inversão ou manter padrão curto (até 2 jogadas).")
else:
    st.warning("Sugestão: Aposte leve ou aguarde padrão mais forte.")

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
