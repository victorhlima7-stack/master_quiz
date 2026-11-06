import streamlit as st
import qrcode
from io import BytesIO
import datetime

# Configuração Geral da Página
st.set_page_config(
    page_title="Plataforma de Compliance & Ranking",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# BANCO DE DADOS EM MEMÓRIA COMPARTILHADO (PERGUNTAS ATUALIZADAS)
# ==============================================================================
@st.cache_resource
def get_shared_db():
    return {
        # 5 PERGUNTAS DO SEU ARQUIVO
        "questions": [
            {
                "category": "Transporte de Resíduos",
                "question": "1. Uma empresa de couro automotivo contratou uma transportadora para retirar resíduos de couro. Qual deve ser a primeira preocupação da empresa?",
                "options": [
                    "Verificar se a regulamentação e a adequação do transporte",
                    "Avaliar a capacidade de carga do veículo, priorizando o volume transportado",
                    "Confirmar se a empresa possui contrato de coleta, deixando a verificação das licenças para depois"
                ],
                "correct": 0,
                "explanation": "A primeira preocupação deve ser a verificação do licenciamento, da regulamentação e da adequação do transporte."
            },
            {
                "category": "Adequação de Veículo",
                "question": "2. Uma transportadora possui licença ambiental, mas utiliza um caminhão inadequado para transportar determinado resíduo. Qual é a situação?",
                "options": [
                    "O transporte pode estar permitido se o resíduo estiver identificado",
                    "O transporte pode estar correto se o motorista for experiente",
                    "O transporte pode estar irregular por falta de adequação do veículo"
                ],
                "correct": 2,
                "explanation": "Mesmo com licença, utilizar veículo inadequado para o tipo de resíduo torna o transporte irregular."
            },
            {
                "category": "Documentação & Destinação",
                "question": "3. Qual documento comprova que o resíduo recebeu sua destinação final?",
                "options": [
                    "Licença Ambiental",
                    "NF-e",
                    "CDF (Certificado de Destinação Final)"
                ],
                "correct": 2,
                "explanation": "O CDF (Certificado de Destinação Final) é o documento oficial que comprova o tratamento/descarte ambiental correto."
            },
            {
                "category": "Identificação de Resíduos",
                "question": "4. A identificação dos resíduos ajuda a evitar erros na separação e na destinação.",
                "options": [
                    "Verdadeiro",
                    "Falso"
                ],
                "correct": 0,
                "explanation": "Verdadeiro. Identificar os resíduos é indispensável para evitar contaminações e garantir a destinação adequada."
            },
            {
                "category": "Reciclagem & Licenciamento",
                "question": "5. A Midori separou corretamente as sobras de couro e contratou uma empresa para reciclá-las. Qual cuidado é importante antes de enviar esses resíduos?",
                "options": [
                    "Escolher a empresa que oferece o transporte mais barato.",
                    "Verificar se a empresa está autorizada a receber esse tipo de resíduo.",
                    "Enviar os resíduos sem registrar a movimentação."
                ],
                "correct": 1,
                "explanation": "É fundamental certificar-se de que a empresa recebedora possui licença ambiental válida para esse tipo de resíduo."
            }
        ],

        # 6ª PERGUNTA: RESERVADA EXCLUSIVAMENTE PARA CASOS DE EMPATE
        "tiebreaker_question": {
            "category": "⚠️ QUESTÃO DE DESEMPATE - ALTA COMPLEXIDADE",
            "question": "Em caso de fiscalização ambiental sobre transporte de resíduos sem a devida documentação (MTR/CDF), quem responde legalmente pelas irregularidades?",
            "options": [
                "Apenas a transportadora contratada",
                "Apenas o motorista do veículo",
                "Solidariamente a empresa geradora, a transportadora e o destinador final",
                "Somente o órgão emissor da licença"
            ],
            "correct": 2,
            "explanation": "Na legislação ambiental brasileira, a responsabilidade é solidária entre o gerador, o transportador e o destinador."
        },

        "force_tiebreaker_mode": False,
        "leaderboard": {}
    }

db = get_shared_db()

# Gerador de QR Code
def generate_qr(url):
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0f172a", back_color="#ffffff")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# Função para verificar se há empate no topo do ranking
def check_top_tie():
    lb = db["leaderboard"]
    if not lb:
        return False
    scores = [v["score"] for v in lb.values()]
    max_score = max(scores)
    top_count = sum(1 for s in scores if s == max_score)
    return top_count > 1 and max_score > 0

# ==============================================================================
# MENU LATERAL
# ==============================================================================
st.sidebar.title("🛡️ Compliance Hub")
st.sidebar.caption("Quiz Midori & Desempate")

modulo = st.sidebar.radio(
    "Selecione o Painel:",
    [
        "📱 Responder Quiz (Celular)",
        "🏆 Ranking de Acertos (Telão/Admin)",
        "📺 QR Code para Acesso"
    ]
)

st.sidebar.divider()
st.sidebar.markdown("**Desenvolvido por:** victor & Dotta")

# ==============================================================================
# PAINEL 1: RESPONDER QUIZ NO CELULAR
# ==============================================================================
if modulo == "📱 Responder Quiz (Celular)":
    st.title("🎯 Quiz de Compliance")

    # Passo 1: Cadastro do Nickname
    if "user_nickname" not in st.session_state:
        st.subheader("Para começar, digite seu Apelido / Nickname:")
        nick_input = st.text_input("Seu Nickname:", placeholder="Ex: Victor_Compliance", max_chars=20)
        
        if st.button("🚀 Iniciar Quiz", type="primary", use_container_width=True):
            if nick_input.strip() != "":
                st.session_state["user_nickname"] = nick_input.strip()
                st.session_state["quiz_step"] = 0
                st.session_state["score"] = 0
                st.session_state["answered"] = False
                st.session_state["tb_score"] = 0
                st.session_state["tb_answered"] = False
                st.rerun()
            else:
                st.warning("Por favor, digite um nickname válido.")

    # Passo 2: Execução das Questões
    else:
        nickname = st.session_state["user_nickname"]
        step = st.session_state.get("quiz_step", 0)
        questions = db["questions"]
        user_score = st.session_state["score"]

        is_top_tied = check_top_tie()
        lb = db["leaderboard"]
        top_score = max([v["score"] for v in lb.values()]) if lb else 0
        
        eligible_for_tb = (
            (user_score == top_score and user_score > 0 and is_top_tied) 
            or db["force_tiebreaker_mode"]
        )

        # FIM DAS 5 QUESTÕES REGULARES
        if step >= len(questions):
            
            if nickname not in db["leaderboard"] or db["leaderboard"][nickname]["score"] != user_score:
                db["leaderboard"][nickname] = {
                    "score": user_score,
                    "tb_score": st.session_state.get("tb_score", 0),
                    "tb_answered": st.session_state.get("tb_answered", False),
