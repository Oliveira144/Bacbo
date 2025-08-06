import streamlit as st
import collections

# --- Classe de Detecção de Padrões (a mesma lógica, mas integrada) ---
class AnalisadorDePadroes:
    def __init__(self, historico):
        self.historico = historico

    def analisar_padroes(self, tipo_analise):
        if len(self.historico) < 2:
            return ["Aguardando mais dados para análise."]

        sugestoes = []

        if tipo_analise == 'cor':
            sugestoes.extend(self._analisar_cor())
        elif tipo_analise == 'soma':
            sugestoes.extend(self._analisar_soma())
        elif tipo_analise == 'tie':
            sugestoes.extend(self._analisar_tie())
        elif tipo_analise == 'combinacao':
            sugestoes.extend(self._analisar_combinacao())
        else:
            sugestoes.extend(self._analisar_cor())
            sugestoes.extend(self._analisar_soma())
            sugestoes.extend(self._analisar_tie())
            sugestoes.extend(self._analisar_combinacao())

        return sugestoes

    def _analisar_cor(self):
        sugestoes = []
        ultimos_resultados = [j['resultado'] for j in self.historico]

        # Padrão 1 – Alternância Controlada
        if len(ultimos_resultados) >= 3 and ultimos_resultados[-1] != ultimos_resultados[-2] and ultimos_resultados[-2] != ultimos_resultados[-3]:
            if len(ultimos_resultados) >= 4 and ultimos_resultados[-3] != ultimos_resultados[-4]:
                sugestoes.append("Padrão 1 (Alternância): A alternância de 4 jogadas foi quebrada. Não siga o padrão de zigue-zague.")
            else:
                sugestoes.append("Padrão 1 (Alternância): Mantenha a aposta no padrão até a 3ª jogada. Após isso, saia.")
        
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
                sugestoes.append(f"Padrão 2 (Streak Longa): {cor_atual} está em sequência de {streak_count+1}. Entre com aposta leve.")
            elif streak_count >= 5:
                sugestoes.append(f"Padrão 2 (Streak Longa): {cor_atual} está em sequência longa de {streak_count+1}. Aposte contra a tendência com cautela.")

        # Padrão 3 – Dupla Camuflada
        if len(ultimos_resultados) >= 4:
            if (ultimos_resultados[-1] == ultimos_resultados[-2] and
                ultimos_resultados[-3] == ultimos_resultados[-4] and
                ultimos_resultados[-1] != ultimos_resultados[-3]):
                sugestoes.append("Padrão 3 (Dupla Camuflada): Detectado pares seguidos. Provável que venha outro par.")
        
        return sugestoes

    def _analisar_soma(self):
        sugestoes = []
        ultimas_somas = [j['soma'] for j in self.historico]

        def tipo_soma(soma):
            if 10 <= soma <= 12: return 'alta'
            if 2 <= soma <= 5: return 'baixa'
            return 'mediana'

        # Padrão 4 – Ciclo de Altos/Baixos
        if len(ultimas_somas) >= 2:
            tipo_1 = tipo_soma(ultimas_somas[-1])
            tipo_2 = tipo_soma(ultimas_somas[-2])
            if tipo_1 == 'alta' and tipo_2 == 'alta':
                sugestoes.append("Padrão 4 (Altos/Baixos): Duas somas altas consecutivas. Próximo resultado tende a ser baixo.")

        # Padrão 5 – Equilíbrio Gradual
        if len(ultimas_somas) >= 3:
            tipos = [tipo_soma(s) for s in ultimas_somas[-3:]]
            if all(t in ['alta', 'baixa'] for t in tipos):
                sugestoes.append("Padrão 5 (Equilíbrio): As últimas 3 somas foram extremas. Prepare-se para uma soma mediana.")

        # Padrão 6 – Quebra Estatística
        if len(ultimas_somas) >= 3:
            if (ultimas_somas[-3] < ultimas_somas[-2] < ultimas_somas[-1] or
                ultimas_somas[-3] > ultimas_somas[-2] > ultimas_somas[-1]):
                sugestoes.append("Padrão 6 (Quebra Estatística): Sequência crescente/decrescente detectada. Espere uma quebra abrupta.")
        
        return sugestoes
    
    def _analisar_tie(self):
        sugestoes = []
        ultimos_resultados = [j['resultado'] for j in self.historico]
        
        if 'T' in ultimos_resultados:
            # Padrão 9 – Duplo Empate Camuflado
            tie_indices = [i for i, r in enumerate(ultimos_resultados) if r == 'T']
            if len(tie_indices) >= 1:
                ultimo_tie_idx = tie_indices[-1]
                if (len(ultimos_resultados) - 1) - ultimo_tie_idx <= 2:
                    sugestoes.append("Padrão 9 (Duplo Tie): Um Tie recente. Considere uma segunda aposta leve no Tie.")
        
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
                sugestoes.append("Padrão 7 (Tie após Streak): Uma streak longa foi quebrada. Aposta leve em Tie pode ser uma boa opção.")

        # Padrão 8 – Tie após Reversão
        if len(ultimos_resultados) >= 4:
            if (ultimos_resultados[-2] == 'P' and ultimos_resultados[-1] == 'B') or \
               (ultimos_resultados[-2] == 'B' and ultimos_resultados[-1] == 'P'):
                sugestoes.append("Padrão 8 (Tie após Reversão): Quebra de tendência detectada. Tie tem alta probabilidade nos próximos lançamentos.")
        
        return sugestoes

    def _analisar_combinacao(self):
        sugestoes = []
        ultimos_resultados = [j['resultado'] for j in self.historico]
        ultimas_somas = [j['soma'] for j in self.historico]
        
        if len(ultimos_resultados) >= 4:
            resultados_streak = ultimos_resultados[-4:]
            somas_streak = ultimas_somas[-4:]
            
            if resultados_streak == ['P', 'P', 'P', 'P'] and all(s > 8 for s in somas_streak):
                sugestoes.append("Combinação (Cor + Soma): Histórico de P(11), P(9), P(10), P(8). Alta chance de Tie ou Banker. Aposte 80% Banker e 20% Tie.")

        return sugestoes

# --- Interface do Usuário (Streamlit) ---
st.set_page_config(page_title="Analisador de Padrões", layout="wide")

st.title("Analisador de Padrões de Apostas")
st.markdown("""
Esta ferramenta ajuda a identificar padrões em jogos para auxiliar suas decisões de aposta.
Basta inserir o resultado de cada rodada.
""")

# Inicializa o histórico no estado da sessão do Streamlit
if 'historico' not in st.session_state:
    st.session_state.historico = collections.deque(maxlen=10)

# Sidebar para exibir o histórico
st.sidebar.header("Histórico Recente")
for jogada in list(st.session_state.historico):
    st.sidebar.write(f"**{jogada['resultado']}** (Soma: {jogada['soma']})")

# Widget para selecionar o tipo de análise
st.header("1. Selecione o Tipo de Análise")
tipo_analise = st.radio(
    "Escolha uma estratégia:",
    ('Cor', 'Soma', 'Tie', 'Combinação', 'Análise Completa')
)

# Formulário para adicionar uma nova jogada
st.header("2. Insira o Resultado da Rodada")
with st.form("nova_jogada"):
    col1, col2 = st.columns(2)
    with col1:
        resultado = st.selectbox("Resultado", ('P', 'B', 'T'))
    with col2:
        soma = st.number_input("Soma", min_value=2, max_value=12, value=8)
    
    submitted = st.form_submit_button("Adicionar Rodada")
    if submitted:
        st.session_state.historico.append({'resultado': resultado, 'soma': soma})
        st.success(f"Rodada adicionada: **{resultado}** (Soma: {soma})")
        # Força a reexecução para atualizar o histórico
        st.rerun()

# Executa a análise e exibe as sugestões
if st.session_state.historico:
    st.header("3. Sugestões de Aposta")
    analisador = AnalisadorDePadroes(st.session_state.historico)
    sugestoes = analisador.analisar_padroes(tipo_analise.lower())

    if sugestoes and sugestoes[0] != "Aguardando mais dados para análise.":
        for sugestao in sugestoes:
            st.info(sugestao)
    else:
        st.warning("Nenhum padrão detectado no momento. Mantenha a cautela.")

