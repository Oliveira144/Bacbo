import streamlit as st
import collections

# --- Lógica de Análise (Aprimorada para retornar dicionário) ---
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
        if len(ultimos_resultados) >= 3 and ultimos_resultados[-1] != ultimos_resultados[-2] and ultimos_resultados[-2] != ultimos_resultados[-3]:
            if len(ultimos_resultados) >= 4 and ultimos_resultados[-3] != ultimos_resultados[-4]:
                sugestoes.append("Alternância quebrada. Não siga o zigue-zague.")
            else:
                sugestoes.append("Alternância: Mantenha a aposta no padrão até a 3ª jogada.")
        
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
                sugestoes.append(f"Streak Longa: {cor_atual} está em sequência de {streak_count+1}. Entre com aposta leve.")
            elif streak_count >= 5:
                sugestoes.append(f"Streak Longa: {cor_atual} está em sequência longa. Aposte contra com cautela.")

        # Padrão 3 – Dupla Camuflada
        if len(ultimos_resultados) >= 4:
            if (ultimos_resultados[-1] == ultimos_resultados[-2] and
                ultimos_resultados[-3] == ultimos_resultados[-4] and
                ultimos_resultados[-1] != ultimos_resultados[-3]):
                sugestoes.append("Dupla Camuflada: Pares seguidos. Provável que venha outro par.")
        
        return sugestoes

    def _analisar_soma(self):
        sugestoes = []
        ultimas_somas = [j['soma'] for j in self.historico]

        def tipo_soma(soma):
            if 10 <= soma <= 12: return 'alta'
            if 2 <= soma <= 5: return 'baixa'
            return 'mediana'

        if len(ultimas_somas) >= 2:
            tipo_1 = tipo_soma(ultimas_somas[-1])
            tipo_2 = tipo_soma(ultimas_somas[-2])
            if tipo_1 == 'alta' and tipo_2 == 'alta':
                sugestoes.append("Altos/Baixos: Duas somas altas. O próximo tende a ser baixo.")

        if len(ultimas_somas) >= 3:
            tipos = [tipo_soma(s) for s in ultimas_somas[-3:]]
            if all(t in ['alta', 'baixa'] for t in tipos):
                sugestoes.append("Equilíbrio: Últimas 3 somas extremas. Prepare-se para uma mediana.")

        if len(ultimas_somas) >= 3:
            if (ultimas_somas[-3] < ultimas_somas[-2] < ultimas_somas[-1] or
                ultimas_somas[-3] > ultimas_somas[-2] > ultimas_somas[-1]):
                sugestoes.append("Quebra Estatística: Sequência detectada. Espere uma quebra abrupta.")
        
        return sugestoes
    
    def _analisar_tie(self):
        sugestoes = []
        ultimos_resultados = [j['resultado'] for j in self.historico]
        
        if 'T' in ultimos_resultados:
            tie_indices = [i for i, r in enumerate(ultimos_resultados) if r == 'T']
            if len(tie_indices) >= 1:
                ultimo_tie_idx = tie_indices[-1]
                if (len(ultimos_resultados) - 1) - ultimo_tie_idx <= 2:
                    sugestoes.append("Duplo Tie: Um Tie recente. Considere outra aposta leve.")
        
        if len(ultimos_resultados) >= 4:
            streak_count = 0
            cor_atual = ultimos_resultados[-2]
            for i in range(len(ultimos_resultados) - 3, -1, -1):
                if ultimos_resultados[i] == cor_atual:
                    streak_count += 1
                else:
                    break
            if streak_count >= 3 and ultimos_resultados[-1] != cor_atual:
                sugestoes.append("Tie após Streak: Uma streak longa foi quebrada. Aposta leve em Tie.")

        if len(ultimos_resultados) >= 4:
            if (ultimos_resultados[-2] == 'P' and ultimos_resultados[-1] == 'B') or \
               (ultimos_resultados[-2] == 'B' and ultimos_resultados[-1] == 'P'):
                sugestoes.append("Tie após Reversão: Quebra de tendência detectada. Tie tem alta probabilidade.")
        
        return sugestoes

    def _analisar_combinacao(self):
        sugestoes = []
        ultimos_resultados = [j['resultado'] for j in self.historico]
        ultimas_somas = [j['soma'] for j in self.historico]
        
        if len(ultimos_resultados) >= 4:
            resultados_streak = ultimos_resultados[-4:]
            somas_streak = ultimas_somas[-4:]
            
            if resultados_streak == ['P', 'P', 'P', 'P'] and all(s > 8 for s in somas_streak):
                sugestoes.append("Combinação: Histórico de P(11), P(9), P(10), P(8). Alta chance de Tie ou Banker. Sugere-se 80% Banker e 20% Tie.")

        return sugestoes

# --- Interface do Usuário (Streamlit) ---
st.set_page_config(page_title="Analisador de Padrões", layout="wide")

st.title("Analisador de Padrões de Apostas")
st.markdown("""
Esta ferramenta analisa o histórico de jogadas, focando nas somas e cores para identificar padrões e auxiliar suas decisões.
""")

if 'historico' not in st.session_state:
    st.session_state.historico = collections.deque(maxlen=10)

# Visualização do Histórico
st.header("Histórico Recente")
historico_cols = st.columns(len(st.session_state.historico) or 1)
for idx, jogada in enumerate(list(st.session_state.historico)):
    if jogada['resultado'] == 'P':
        color = '#d63333'  # Player (Vermelho)
    elif jogada['resultado'] == 'B':
        color = '#0072b2'  # Banker (Azul)
    else:
        color = '#a0a0a0'  # Tie (Cinza)
    historico_cols[idx].markdown(f"<div style='text-align: center; border-radius: 5px; background-color:{color}; padding: 5px; color: white;'><b>{jogada['resultado']}</b><br><small>({jogada['soma']})</small></div>", unsafe_allow_html=True)

# Formulário para adicionar nova jogada
with st.form("nova_jogada", clear_on_submit=True):
    st.header("Insira a Nova Rodada")
    col1, col2 = st.columns([1, 2])
    with col1:
        resultado = st.selectbox("Resultado", ('P', 'B', 'T'), label_visibility="collapsed")
    with col2:
        soma = st.number_input("Soma", min_value=2, max_value=12, value=8, label_visibility="collapsed")
    
    submitted = st.form_submit_button("Adicionar Rodada")
    if submitted:
        st.session_state.historico.append({'resultado': resultado, 'soma': soma})
        st.rerun()

# Análise de Padrões
if st.session_state.historico:
    st.header("Análise Detalhada")
    analisador = AnalisadorDePadroes(st.session_state.historico)
    analise = analisador.analisar_tudo()

    if analise and any(analise.values()):
        # Exibe sugestões de Cor
        if analise['cor']:
            st.subheader("Análise de Padrões de Cor")
            for sugestao in analise['cor']:
                st.info(sugestao)
        
        # Exibe sugestões de Soma
        if analise['soma']:
            st.subheader("Análise de Padrões de Soma")
            for sugestao in analise['soma']:
                st.info(sugestao)

        # Exibe sugestões de Tie (Empate)
        if analise['tie']:
            st.subheader("Análise de Padrões de Tie")
            for sugestao in analise['tie']:
                st.info(sugestao)

        # Exibe sugestões de Combinação
        if analise['combinacao']:
            st.subheader("Análise de Padrões Combinados")
            for sugestao in analise['combinacao']:
                st.success(sugestao)
    else:
        st.warning("O histórico ainda é muito curto para detectar padrões.")
