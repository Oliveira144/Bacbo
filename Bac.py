import streamlit as st
import json
import os
from datetime import datetime

class BacBoAnalyzer:
    def __init__(self):
        self.history = []
        self.signals = []
        self.performance = {'total': 0, 'hits': 0, 'misses': 0}
        self.load_data()

    def add_outcome(self, outcome):
        """Adiciona um novo resultado ao histórico e dispara a análise."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.history.append((timestamp, outcome))
        is_correct = self.verify_previous_prediction(outcome)
        pattern, prediction = self.detect_pattern()

        if pattern is not None:
            self.signals.append({
                'time': timestamp,
                'pattern': pattern,
                'prediction': prediction,
                'correct': None
            })

        self.save_data()
        return pattern, prediction, is_correct

    def verify_previous_prediction(self, current_outcome):
        """Verifica se a última sugestão foi correta e atualiza as métricas."""
        for i in reversed(range(len(self.signals))):
            signal = self.signals[i]
            if signal.get('correct') is None:
                if signal['prediction'] == current_outcome:
                    self.performance['hits'] += 1
                    self.performance['total'] += 1
                    signal['correct'] = "✅"
                    return "✅"
                else:
                    self.performance['misses'] += 1
                    self.performance['total'] += 1
                    signal['correct'] = "❌"
                    return "❌"
        return None

    def undo_last(self):
        """Desfaz o último resultado e a última sugestão."""
        if self.history:
            removed_time, _ = self.history.pop()
            if self.signals and self.signals[-1]['time'] == removed_time:
                removed_signal = self.signals.pop()
                if removed_signal.get('correct') == "✅":
                    self.performance['hits'] = max(0, self.performance['hits'] - 1)
                    self.performance['total'] = max(0, self.performance['total'] - 1)
                elif removed_signal.get('correct') == "❌":
                    self.performance['misses'] = max(0, self.performance['misses'] - 1)
                    self.performance['total'] = max(0, self.performance['total'] - 1)
            self.save_data()
            return True
        return False

    def clear_history(self):
        """Limpa todo o histórico e as métricas."""
        self.history = []
        self.signals = []
        self.performance = {'total': 0, 'hits': 0, 'misses': 0}
        self.save_data()

    def detect_pattern(self):
        """
        Detecta padrões no histórico com base na lista de 30 padrões fornecida,
        priorizando os mais longos e mais fortes.
        (H=Player, A=Banker, T=Tie)
        """
        if len(self.history) < 2:
            return None, None

        outcomes = [outcome for _, outcome in self.history]
        n = len(outcomes)

        # ----------------------------------------------------
        # Padrões mais longos e de maior prioridade
        # ----------------------------------------------------

        # Padrão 29: Tie x4 ou mais
        if n >= 4 and outcomes[-4:] == ['T', 'T', 'T', 'T']:
            return 29, 'H'

        # Padrão 26: Banker x3 - Tie - Player x3
        if n >= 7 and outcomes[-7:] == ['A', 'A', 'A', 'T', 'H', 'H', 'H']:
            return 26, 'H'

        # Padrão 25: Player x3 - Tie - Banker x3
        if n >= 7 and outcomes[-7:] == ['H', 'H', 'H', 'T', 'A', 'A', 'A']:
            return 25, 'A'
            
        # Padrão 24: Banker x2 - Tie - Player x2
        if n >= 5 and outcomes[-5:] == ['A', 'A', 'T', 'H', 'H']:
            return 24, 'H'

        # Padrão 23: Player x2 - Tie - Banker x2
        if n >= 5 and outcomes[-5:] == ['H', 'H', 'T', 'A', 'A']:
            return 23, 'A'

        # Padrão 18: Tie - Player - Tie - Banker - Tie
        if n >= 5 and outcomes[-5:] == ['T', 'H', 'T', 'A', 'T']:
            return 18, 'T'
            
        # Padrão 16: Tie - Tie - Player
        if n >= 3 and outcomes[-3:] == ['T', 'T', 'H']:
            return 16, 'H'

        # Padrão 17: Tie - Tie - Banker
        if n >= 3 and outcomes[-3:] == ['T', 'T', 'A']:
            return 17, 'A'

        # Padrão 7: Player x4 ou mais
        if n >= 4 and outcomes[-4:] == ['H', 'H', 'H', 'H']:
            return 7, 'H'

        # Padrão 8: Banker x4 ou mais
        if n >= 4 and outcomes[-4:] == ['A', 'A', 'A', 'A']:
            return 8, 'A'

        # Padrão 27: Tie x2
        if n >= 2 and outcomes[-2:] == ['T', 'T']:
            return 27, 'T'

        # ----------------------------------------------------
        # Padrões de Média Prioridade
        # ----------------------------------------------------
        
        # Padrão 4: Player x3
        if n >= 3 and outcomes[-3:] == ['H', 'H', 'H']:
            return 4, 'H'

        # Padrão 5: Banker x3
        if n >= 3 and outcomes[-3:] == ['A', 'A', 'A']:
            return 5, 'A'

        # Padrão 6: Tie x3
        if n >= 3 and outcomes[-3:] == ['T', 'T', 'T']:
            return 6, 'T'

        # Padrão 12: Player - Tie - Player
        if n >= 3 and outcomes[-3:] == ['H', 'T', 'H']:
            return 12, 'H'
        
        # Padrão 13: Banker - Tie - Banker
        if n >= 3 and outcomes[-3:] == ['A', 'T', 'A']:
            return 13, 'A'

        # Padrão 14: Player - Tie - Banker
        if n >= 3 and outcomes[-3:] == ['H', 'T', 'A']:
            return 14, 'A' # Aposta equilibrada no Banker

        # Padrão 15: Banker - Tie - Player
        if n >= 3 and outcomes[-3:] == ['A', 'T', 'H']:
            return 15, 'H' # Aposta equilibrada no Player

        # Padrão 19: Player - Player - Tie - Player
        if n >= 4 and outcomes[-4:] == ['H', 'H', 'T', 'H']:
            return 19, 'H'
        
        # Padrão 21: Banker - Tie - Banker - Tie - Banker
        if n >= 5 and outcomes[-5:] == ['A', 'T', 'A', 'T', 'A']:
            return 21, 'A'

        # Padrão 22: Player - Tie - Player - Tie - Player
        if n >= 5 and outcomes[-5:] == ['H', 'T', 'H', 'T', 'H']:
            return 22, 'H'

        # Padrão 30: Player - Banker - Player (sanduíche)
        if n >= 3 and outcomes[-3:] == ['H', 'A', 'H']:
            return 30, 'A'
        
        # ----------------------------------------------------
        # Padrões de Menor Prioridade
        # ----------------------------------------------------

        # Padrão 1: Player x2
        if n >= 2 and outcomes[-2:] == ['H', 'H']:
            return 1, 'H'

        # Padrão 2: Banker x2
        if n >= 2 and outcomes[-2:] == ['A', 'A']:
            return 2, 'A'

        # Padrão 3: Tie x2
        if n >= 2 and outcomes[-2:] == ['T', 'T']:
            return 3, 'T'

        # Padrão 9: Player - Banker - Player - Banker
        if n >= 4 and outcomes[-4:] == ['H', 'A', 'H', 'A']:
            return 9, 'H'

        # Padrão 10: Banker - Player - Banker - Player
        if n >= 4 and outcomes[-4:] == ['A', 'H', 'A', 'H']:
            return 10, 'A'

        # Padrão 11: Tie - Player - Tie - Banker
        if n >= 4 and outcomes[-4:] == ['T', 'H', 'T', 'A']:
            return 11, 'T'

        # Padrão 20: Player - Tie - Banker - Tie - Player
        if n >= 5 and outcomes[-5:] == ['H', 'T', 'A', 'T', 'H']:
            return 20, 'T'

        # Padrão 28: Tie x3
        if n >= 3 and outcomes[-3:] == ['T', 'T', 'T']:
            return 28, 'H'
            
        return None, None

    def load_data(self):
        """Carrega os dados salvos de um arquivo JSON."""
        if os.path.exists('analyzer_data.json'):
            with open('analyzer_data.json', 'r') as f:
                try:
                    data = json.load(f)
                    self.history = data.get('history', [])
                    self.signals = data.get('signals', [])
                    self.performance = data.get('performance', {'total': 0, 'hits': 0, 'misses': 0})
                except json.JSONDecodeError:
                    st.warning("Arquivo de dados corrompido. Reiniciando o histórico.")
                    self.history = []
                    self.signals = []
                    self.performance = {'total': 0, 'hits': 0, 'misses': 0}
        else:
            self.save_data()

    def save_data(self):
        """Salva o estado atual do histórico e das métricas em um arquivo JSON."""
        data = {
            'history': self.history,
            'signals': self.signals,
            'performance': self.performance
        }
        with open('analyzer_data.json', 'w') as f:
            json.dump(data, f, indent=4)

    def get_accuracy(self):
        """Calcula a acurácia do sistema."""
        if self.performance['total'] == 0:
            return 0.0
        return (self.performance['hits'] / self.performance['total']) * 100

# Inicialização do aplicativo
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = BacBoAnalyzer()

# Interface do Streamlit
st.set_page_config(page_title="Bac Bo Analyzer", layout="wide", page_icon="🎲")
st.title("🎲 Bac Bo Analyzer Pro")
st.subheader("Sistema de detecção de padrões para Bac Bo")

st.markdown("---")

## Registrar Resultado da Rodada

st.write("Para registrar o resultado da última rodada, selecione uma das opções abaixo:")
st.markdown("<br>", unsafe_allow_html=True)
st.write("**Qual foi o resultado da última rodada?**")

cols_outcome = st.columns(3)
with cols_outcome[0]:
    # Botão para JOGADOR (AZUL)
    if st.button("🔵 Jogador", use_container_width=True, type="primary"):
        st.session_state.analyzer.add_outcome('H')
        st.rerun()
with cols_outcome[1]:
    # Botão para BANCA (VERMELHO)
    if st.button("🔴 Banca", use_container_width=True):
        st.session_state.analyzer.add_outcome('A')
        st.rerun()
with cols_outcome[2]:
    # Botão para EMPATE (AMARELO)
    if st.button("🟡 Empate", use_container_width=True):
        st.session_state.analyzer.add_outcome('T')
        st.rerun()

st.markdown("---")
st.subheader("Controles do Histórico")
cols_controls = st.columns(2)
with cols_controls[0]:
    if st.button("↩️ Desfazer Último", use_container_width=True):
        st.session_state.analyzer.undo_last()
        st.rerun()
with cols_controls[1]:
    if st.button("🗑️ Limpar Tudo", use_container_width=True, type="secondary"):
        st.session_state.analyzer.clear_history()
        st.rerun()

st.markdown("---")

## Sugestão para a Próxima Rodada

current_pattern, current_prediction = st.session_state.analyzer.detect_pattern()

if current_prediction:
    display_prediction = ""
    bg_color_prediction = ""
    if current_prediction == 'H':
        display_prediction = "🔵 JOGADOR"
        # Cor de fundo para o Jogador (Azul)
        bg_color_prediction = "rgba(0, 0, 255, 0.2)"
    elif current_prediction == 'A':
        display_prediction = "🔴 BANCA"
        # Cor de fundo para a Banca (Vermelho)
        bg_color_prediction = "rgba(255, 0, 0, 0.2)"
    else:
        display_prediction = "🟡 EMPATE"
        # Cor de fundo para o Empate (Amarelo)
        bg_color_prediction = "rgba(255, 255, 0, 0.2)"

    st.markdown(f"""
    <div style="
        background: {bg_color_prediction};
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
        border: 2px solid #fff;
    ">
        <div style="font-size: 20px; font-weight: bold; margin-bottom: 10px;">
            Sugestão Baseada no Padrão {current_pattern}:
        </div>
        <div style="font-size: 40px; font-weight: bold; color: #fff; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">
            {display_prediction}
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("Registre pelo menos 2 resultados para ver uma sugestão para a próxima rodada.")

st.markdown("---")

## Métricas de Desempenho

accuracy = st.session_state.analyzer.get_accuracy()
col1, col2, col3 = st.columns(3)
col1.metric("Acurácia", f"{accuracy:.2f}%" if st.session_state.analyzer.performance['total'] > 0 else "0%")
col2.metric("Total de Previsões", st.session_state.analyzer.performance['total'])
col3.metric("Acertos", st.session_state.analyzer.performance['hits'])

st.markdown("---")

## Histórico de Resultados

st.caption("Mais recente → Mais antigo (esquerda → direita)")

if st.session_state.analyzer.history:
    outcomes = [outcome for _, outcome in st.session_state.analyzer.history][::-1][:72]
    total = len(outcomes)
    
    num_cols = 9
    num_rows = (total + num_cols - 1) // num_cols
    
    for row in range(num_rows):
        cols = st.columns(num_cols)
        start = row * num_cols
        end = min(start + num_cols, total)

        for i in range(start, end):
            outcome = outcomes[i]
            # Atualiza os emojis para refletir as novas cores
            emoji = "🔵" if outcome == 'H' else "🔴" if outcome == 'A' else "🟡"
            with cols[i - start]:
                st.markdown(f"<div style='font-size: 24px; text-align: center;'>{emoji}</div>", unsafe_allow_html=True)
else:
    st.info("Nenhum resultado registrado. Use os botões acima para começar.")

st.markdown("---")

## Últimas Sugestões/Previsões

if st.session_state.analyzer.signals:
    for signal in st.session_state.analyzer.signals[-5:][::-1]:
        display = ""
        bg_color = ""
        if signal['prediction'] == 'H':
            display = "🔵 JOGADOR"
            # Cor de fundo para o Jogador (Azul)
            bg_color = "rgba(0, 0, 255, 0.1)"
        elif signal['prediction'] == 'A':
            display = "🔴 BANCA"
            # Cor de fundo para a Banca (Vermelho)
            bg_color = "rgba(255, 0, 0, 0.1)"
        else:
            display = "🟡 EMPATE"
            # Cor de fundo para o Empate (Amarelo)
            bg_color = "rgba(255, 255, 0, 0.1)"

        status = signal.get('correct', '')
        color = "green" if status == "✅" else "red" if status == "❌" else "gray"

        st.markdown(f"""
        <div style="
            background: {bg_color};
            border-radius: 10px;
            padding: 12px;
            margin: 10px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        ">
            <div><strong>Padrão {signal['pattern']}</strong></div>
            <div style="font-size: 24px; font-weight: bold;">{display}</div>
            <div style="color: {color}; font-weight: bold; font-size: 24px;">{status}</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("Registre resultados para gerar sugestões. Após 2+ rodadas, as previsões aparecerão aqui.")

