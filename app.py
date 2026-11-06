import datetime
from io import BytesIO
import qrcode
import streamlit as st

# Configuração Geral da Página
st.set_page_config(
    page_title="Plataforma de Compliance & Ranking",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# BANCO DE DADOS EM MEMÓRIA COMPARTILHADO
# ==============================================================================
@st.cache_resource
def get_shared_db():
    return {
        # 5 PERGUNTAS REGULARES
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
st.sidebar.caption("Quiz Midori e Desempate")

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

    else:
        nickname = st.session_state["user_nickname"]
        step = st.session_state.get("quiz_step", 0)
        questions = db["questions"]
        user_score = st.session_state["score"]

        is_top_tied = check_top_tie()
        lb = db["leaderboard"]
        top_score = max([v["score"] for v in lb.values()]) if lb else 0

        eligible_for_tb = (user_score == top_score and user_score > 0 and is_top_tied) or db["force_tiebreaker_mode"]

        if step >= len(questions):
            user_data = {
                "score": user_score,
                "tb_score": st.session_state.get("tb_score", 0),
                "tb_answered": st.session_state.get("tb_answered", False),
                "total": len(questions),
                "percentage": round((user_score / len(questions)) * 100),
                "time": datetime.datetime.now().strftime("%H:%M:%S")
            }
            db["leaderboard"][nickname] = user_data

            if eligible_for_tb and not st.session_state.get("tb_answered", False):
                st.warning("⚡ **EMPATE DETECTADO NO TOP 1 DO RANKING!**")
                st.subheader("🔥 Pergunta 6 de Desempate Liberada!")
                st.caption("Responda à questão decisiva para definir o vencedor supremo:")

                tb_q = db["tiebreaker_question"]
                st.markdown(f"**[{tb_q['category']}]**")
                st.error(tb_q["question"])

                selected_tb = st.radio(
                    "Escolha a resposta de desempate:",
                    options=list(range(len(tb_q["options"]))),
                    format_func=lambda i: tb_q["options"][i],
                    index=None,
                    key="tb_radio"
                )

                if st.button("⚔️ Enviar Resposta de Desempate", type="primary", use_container_width=True):
                    if selected_tb is not None:
                        is_correct = (selected_tb == tb_q["correct"])
                        tb_val = 1 if is_correct else 0

                        st.session_state["tb_score"] = tb_val
                        st.session_state["tb_answered"] = True

                        db["leaderboard"][nickname]["tb_score"] = tb_val
                        db["leaderboard"][nickname]["tb_answered"] = True

                        st.rerun()
                    else:
                        st.warning("Selecione uma opção para desempate.")

            else:
                st.balloons()
                st.success(f"🎉 **Parabéns, {nickname}! Suas respostas foram computadas.**")

                total = len(questions)
                pct = round((user_score / total) * 100)

                st.metric("Sua Pontuação Principal", f"{user_score} de {total} ({pct}%)")

                if st.session_state.get("tb_answered", False):
                    tb_status = "🎯 ACERTOU a Pergunta 6!" if st.session_state["tb_score"] == 1 else "❌ ERROU a Pergunta 6."
                    st.info(f"**Resultado do Desempate:** {tb_status}")

                st.info("Acompanhe o Ranking Final atualizado no Telão!")

                if st.button("🔄 Responder Novamente com outro Nickname"):
                    del st.session_state["user_nickname"]
                    st.rerun()

        else:
            q = questions[step]
            st.caption(f"Participante: **{nickname}** | Questão {step + 1} de {len(questions)}")
            st.progress((step) / len(questions))

            st.markdown(f"**[{q['category']}]**")
            st.subheader(q["question"])

            selected_option = st.radio(
                "Selecione a alternativa correta:",
                options=list(range(len(q["options"]))),
                format_func=lambda i: q["options"][i],
                index=None,
                disabled=st.session_state.get("answered", False)
            )

            if not st.session_state.get("answered", False):
                if st.button("Confirmar Resposta", type="primary", use_container_width=True):
                    if selected_option is not None:
                        st.session_state["answered"] = True
                        st.session_state["last_selected"] = selected_option
                        if selected_option == q["correct"]:
                            st.session_state["score"] += 1
                        st.rerun()
                    else:
                        st.warning("Escolha uma alternativa antes de confirmar.")
            else:
                last_sel = st.session_state.get("last_selected")
                if last_sel == q["correct"]:
                    st.success("✅ **Resposta Correta!**")
                else:
                    st.error(f"❌ **Resposta Incorreta!** A opção certa era: {q['options'][q['correct']]}")

                st.info(f"💡 **Fundamentação:** {q['explanation']}")

                if st.button("Próxima Questão ➔", type="primary", use_container_width=True):
                    st.session_state["quiz_step"] += 1
                    st.session_state["answered"] = False
                    st.rerun()

# ==============================================================================
# PAINEL 2: RANKING AO VIVO NO TELÃO
# ==============================================================================
elif modulo == "🏆 Ranking de Acertos (Telão/Admin)":
    st.title("🏆 Ranking de Desempenho ao Vivo")
    st.caption("Classificação com critério automático para a 6ª Pergunta de Desempate")
    st.divider()

    leaderboard = db["leaderboard"]

    has_tie = check_top_tie()
    if has_tie:
        st.warning("⚠️ **ATENÇÃO: EMPATE DETECTADO NO 1º LUGAR!** A Pergunta 6 de Desempate foi ativada nos celulares dos líderes.")

    if not leaderboard:
        st.info("Aguardando os primeiros envios dos participantes...")
    else:
        sorted_ranking = sorted(
            leaderboard.items(),
            key=lambda item: (
                item[1]["score"],
                item[1].get("tb_score", 0),
                item[1]["percentage"]
            ),
            reverse=True
        )

        col1, col2, col3 = st.columns(3)

        if len(sorted_ranking) >= 1:
            p1_name, p1_data = sorted_ranking[0]
            tb_txt = " (Desempate 🎯)" if p1_data.get("tb_score", 0) == 1 else ""
            col1.metric("🥇 1º Lugar", p1_name, f"{p1_data['score']}/{p1_data['total']}{tb_txt}")

        if len(sorted_ranking) >= 2:
            p2_name, p2_data = sorted_ranking[1]
            tb_txt = " (Desempate 🎯)" if p2_data.get("tb_score", 0) == 1 else ""
            col2.metric("🥈 2º Lugar", p2_name, f"{p2_data['score']}/{p2_data['total']}{tb_txt}")

        if len(sorted_ranking) >= 3:
            p3_name, p3_data = sorted_ranking[2]
            tb_txt = " (Desempate 🎯)" if p3_data.get("tb_score", 0) == 1 else ""
            col3.metric("🥉 3º Lugar", p3_name, f"{p3_data['score']}/{p3_data['total']}{tb_txt}")

        st.divider()
        st.subheader("📋 Tabela Oficial de Pontuação")

        ranking_table = []
        for rank, (nick, data) in enumerate(sorted_ranking, 1):
            if data.get("tb_answered", False):
                tb_status = "🎯 Acertou (Q6)" if data.get("tb_score", 0) == 1 else "❌ Errou (Q6)"
            else:
                tb_status = "⏳ Não foi necessário"

            ranking_table.append({
                "Posição": f"#{rank}",
                "Nickname": nick,
                "Acertos Principais": f"{data['score']} / {data['total']}",
                "6ª Pergunta (Desempate)": tb_status,
                "Aproveitamento": f"{data['percentage']}%",
                "Horário": data["time"]
            })

        st.table(ranking_table)

    st.divider()
    col_act1, col_act2, col_act3 = st.columns([2, 2, 1])

    with col_act1:
        if st.button("🔄 Atualizar Ranking", use_container_width=True):
            st.rerun()

    with col_act2:
        btn_txt = "🔒 Bloquear 6ª Pergunta" if db["force_tiebreaker_mode"] else "🔓 Forçar 6ª Pergunta para Todos"
        if st.button(btn_txt, use_container_width=True):
            db["force_tiebreaker_mode"] = not db["force_tiebreaker_mode"]
            st.rerun()

    with col_act3:
        if st.button("🚨 Zerar Ranking", type="secondary", use_container_width=True):
            db["leaderboard"].clear()
            db["force_tiebreaker_mode"] = False
            st.success("Ranking zerado!")
            st.rerun()

# ==============================================================================
# PAINEL 3: QR CODE PARA OS CELULARES
# ==============================================================================
else:
    st.title("📺 Acesso ao Quiz & Desempate")
    st.caption("Projete este QR Code na tela principal")
    st.divider()

    col_qr, col_info = st.columns([1, 2])

    with col_qr:
        app_url = st.text_input("Link público do seu app:", value="https://seu-app.streamlit.app")
        qr_bytes = generate_qr(app_url)
        st.image(qr_bytes, caption="Escaneie para responder pelo celular", width=280)

    with col_info:
        st.subheader("Regras da Votação & Desempate:")
        st.markdown("""
        1. Aponte a câmera do celular para o **QR Code**.
        2. Cadastre o seu **Nickname**.
        3. Responda às **5 questões regulares**.
        4. **Rodada de Desempate:** Se você ficar empatado em 1º lugar no ranking, a **6ª Pergunta** será liberada automaticamente na sua tela para definir o vencedor!
        """)
