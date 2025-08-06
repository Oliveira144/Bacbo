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
# Classes para Detecção de Padrões (Refatorada)
# -------------------------------
class AnalisadorDePadroes:
    def __init__(self, historico):
        self.historico = historico

    def analisar_tudo(self):
        """Analisa todos os padrões e retorna um dicionário organizado."""
        if len(self.historico) < 2:
            return None
        
        return {
            'cor': self._analisar_cor(),
            'soma': self._analisar_soma(),
            'tie': self._analisar_tie(),
            'combinacao': self._analisar_combinacao()
        }

    def _analisar_cor(self):
        sugestoes = []
        ultimos_resultados = [j['resultado'] for j in self.historico]

        # Padrão 1 – Alternância Controlada
        if len(ultimos_resultados) >= 4:
            if ultimos_resultados[-4:] == ['Player', 'Banker', 'Player', 'Banker'] or ultimos_resultados[-4:] == ['Banker', 'Player', 'Banker', 'Player']:
                sugestoes.append("Alternância: Padrão de zigue-zague detectado. A quebra pode vir em breve.")
            elif ultimos_resultados[-3:] == ['Player', 'Banker', 'Player'] or ultimos_resultados[-3:] == ['Banker', 'Player', 'Banker']:
                sugestoes.append("Alternância: Mantenha a aposta no padrão até a 3ª jogada. Após isso, saia.")
        
        # Padrão 2 – Streak Longa
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
        
        return sugestoes

    def _analisar_soma(self):
        sugestoes = []
        ultimas_somas_totais = [sum(j['soma']) for j in self.historico if j['soma'] is not None]

        def tipo_soma(soma_total):
            if 10 <= soma_total <= 12: return 'alta'
            if 2 <= soma_total <= 5: return 'baixa'
            return 'mediana'

        # Padrão 4 – Ciclo de Altos/Baixos
        if len(ultimas_somas_totais) >= 2:
            tipo_1 = tipo_soma(ultimas_somas_totais[-1])
            tipo_2 = tipo_soma(ultimas_somas_totais[-2])
            if tipo_1 == 'alta' and tipo_2 == 'alta':
                sugestoes.append("Soma: Duas somas altas consecutivas. O próximo resultado tende a ser baixo.")

        # Padrão 5 – Equilíbrio Gradual
        if len(ultimas_somas_totais) >= 3:
            tipos = [tipo_soma(s) for s in ultimas_somas_totais[-3:]]
            if all(t in ['alta', 'baixa'] for t in tipos):
                sugestoes.append("Soma: As últimas 3 somas foram extremas. Prepare-se para uma soma mediana.")

        # Padrão 6 – Quebra Estatística
        if len(ultimas_somas_totais) >= 3:
            if (ultimas_somas_totais[-3] < ultimas_somas_totais[-2] < ultimas_somas_totais[-1] or
                ultimas_somas_totais[-3] > ultimas_somas_totais[-2] > ultimas_somas_totais[-1]):
                sugestoes.append("Soma: Sequência crescente/decrescente detectada. Espere uma quebra abrupta.")
        
        return sugestoes
    
    def _analisar_tie(self):
        sugestoes = []
        ultimos_resultados = [j['resultado'] for j in self.historico]
        
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
        
        return sugestoes

    def _analisar_combinacao(self):
        sugestoes = []
        ultimos_resultados = [j['resultado'] for j in self.historico]
        ultimas_somas = [j['soma'] for j in self.historico if j['soma'] is not None]
        
        if len(ultimos_resultados) >= 4 and len(ultimas_somas) >= 4:
            resultados_streak = ultimos_resultados[-4:]
            somas_totais_streak = [sum(s) for s in ultimas_somas[-4:]]
            
            if resultados_streak == ['Player', 'Player', 'Player', 'Player'] and all(s > 8 for s in somas_totais_streak):
                sugestoes.append("Combinação: Histórico de P(11), P(9), P(10), P(8). Alta chance de Tie ou Banker. Sugere-se 80% Banker e 20% Tie.")

        return sugestoes

# -------------------------------
# Exibir Histórico em Grade
# -------------------------------
colB.subheader("Histórico Visual")
if st.session_state.historico:
    resultados = [item['resultado'] for item in st.session_state.historico]
    cores = {"Player": "🔵", "Banker": "🔴", "Tie": "🟡"}
    
    # Criar uma grade de 10x9
    grid_data = list(resultados)
    
    # Preencher espaços vazios para completar a grade
    if len(grid_data) < 90:
        grid_data.extend(['' for _ in range(90 - len(grid_data))])
        
    grid_df = pd.DataFrame(np.array(grid_data).reshape(10, 9))
    
    # Estilização para as cores
    def color_cell(val):
        color_map = {'Player': 'blue', 'Banker': 'red', 'Tie': 'yellow'}
        return f'background-color: {color_map.get(val, "white")}; color: black'

    st.dataframe(grid_df.style.applymap(color_cell), height=400)


# -------------------------------
# Análise e Estratégia
# -------------------------------
st.markdown("---")
st.subheader("📊 Análise Avançada")

analisador = AnalisadorDePadroes(st.session_state.historico)
analise = analisador.analisar_tudo()

if analise:
    if modo == "Cor":
        if analise['cor']:
            st.info("--- Padrões de Cor Detectados ---")
            for sugestao in analise['cor']:
                st.write(f"- {sugestao}")
        else:
            st.info("Nenhum padrão de cor detectado no momento.")
    
    elif modo == "Soma":
        if analise['soma']:
            st.info("--- Padrões de Soma Detectados ---")
            for sugestao in analise['soma']:
                st.write(f"- {sugestao}")
        else:
            st.info("Nenhum padrão de soma detectado no momento.")
    
    elif modo == "Inteligente":
        if analise['combinacao']:
            st.success("--- Padrões Combinados (Cor + Soma) ---")
            for sugestao in analise['combinacao']:
                st.write(f"- {sugestao}")

        st.info("--- Análise Completa ---")
        todas_sugestoes = analise['cor'] + analise['soma'] + analise['tie']
        if todas_sugestoes:
            for sugestao in todas_sugestoes:
                st.write(f"- {sugestao}")
        else:
            st.write("Nenhum padrão forte detectado. Aposte leve ou aguarde.")
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

