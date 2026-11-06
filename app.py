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
# BANCO DE DADOS EM MEMÓRIA COMPARTILHADO
# ==============================================================================
@st.cache_resource
def get_shared_db():
    return {
        # 5 Perguntas Regulares do Quiz
        "questions": [
            {
                "category": "Transporte de Resíduos",
                "question": "Qual documento ambiental é obrigatório para o transporte terrestre de resíduos perigosos no Brasil?",
                "options": [
                    "Apenas a Nota Fiscal da empresa geradora",
                    "Manifesto de Transporte de Resíduos (MTR) e Ficha de Emergência",
                    "Certificado de Registro Cadastral do DETRAN",
                    "Alvará de Funcionamento Municipal simples"
                ],
                "correct": 1,
                "explanation": "O MTR emitido via SINIR é o documento nacional obrigatório para o rastreamento de resíduos perigosos."
            },
            {
                "category": "Licenciamento Ambiental",
                "question": "Qual etapa do Licenciamento Ambiental autoriza o início efetivo das operações da empresa?",
                "options": [
                    "Licença Prévia (LP)",
                    "Licença de Instalação (LI)",
                    "Licença de Operação (LO)",
                    "Cadastro Técnico Federal (CTF)"
                ],
                "correct": 2,
                "explanation": "A Licença de Operação (LO) autoriza o funcionamento oficial da atividade após a verificação das exigências."
            },
            {
                "category": "Documentação Fiscal",
                "question": "Qual documento fiscal acoberta a prestação do serviço de frete rodoviário de resíduos?",
                "options": [
                    "Conhecimento de Transporte Eletrônico (CT-e) / MDF-e",
                    "Recibo de Prestação de Serviços (RPS) simples",
                    "Declaração de Isenção de Inscrição Estadual",
                    "Ordem de Serviço de Oficina"
                ],
                "correct": 0,
                "explanation": "O CT-e e o MDF-e são os documentos fiscais hábeis exigidos pelo Fisco para serviços de frete."
            },
            {
                "category": "Destinação Final",
                "question": "Qual documento comprova o correto descarte e tratamento final do resíduo?",
                "options": [
                    "Certificado de Destinação Final (CDF)",
                    "Cópia do Contrato Social do Destinador",
                    "Comprovante de Pagamento do Pedágio",
                    "Ficha de Cadastro de Clientes"
                ],
                "correct": 0,
                "explanation": "O CDF emitido pelo destinador homologado comprova juridicamente a destinação ambientalmente adequada."
            },
            {
                "category": "Regulamentação ANTT",
                "question": "Veículos que transportam cargas e resíduos perigosos precisam ter qual cadastro ativo?",
                "options": [
                    "RNTRC (Registro Nacional de Transportadores Rodoviários de Cargas) da ANTT",
                    "Inscrição no Conselho Regional de Engenharia (CREA)",
                    "Apenas Seguro Contra Terceiros (RCF)",
                    "Licença Comercial de Vendedor Ambulante"
                ],
                "correct": 0,
                "explanation": "O RNTRC é o registro obrigatório para transportadores de carga fiscalizado pela ANTT."
            }
        ],

        # 6ª PERGUNTA: RESERVADA EXCLUSIVAMENTE PARA CASOS DE EMPATE
        "tiebreaker_question": {
            "category": "⚠️ QUESTÃO DE DESEMPATE - ALTA COMPLEXIDADE",
            "question": "Em caso de infração por transporte irregular de resíduos com risco ambiental grave, qual o prazo legal padrão para apresentação de Defesa Prévia após a autuação pelo órgão ambiental (Lei 9.605/98 / Dec. 6.514/08)?",
            "options": [
                "5 dias corridos",
                "20 dias",
                "45 dias úteis",
                "60 dias"
            ],
            "correct": 1,
            "explanation": "Conforme o Decreto Federal 6.514/08, o autuado tem o prazo de 20 dias para apresentar defesa formal contados da data da ciência da autuação."
        },

        # Controle Global de Desempate Manual (pode ser ativado pelo admin)
        "force_tiebreaker_mode": False,

        # Tabela do Ranking: {"nickname": {"score": X, "tb_score": Y, "total": 5, "percentage": Z, "time": "14:30"}}
        "leaderboard": {}
    }

db = get_shared_db()

# Função para Gerar QR Code
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
    # Retorna True se mais de 1 pessoa tiver a pontuação máxima no ranking
    top_count = sum(1 for s in scores if s == max_score)
    return top_count > 1 and max_score > 0

# ==============================================================================
# MENU LATERAL
# ==============================================================================
st.sidebar.title("🛡️ Compliance Hub")
st.sidebar.caption("Quiz com Rodada de Desempate")

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

        # Regra de Elegibilidade para a 6ª Pergunta (Desempate)
        is_top_tied = check_top_tie()
        lb = db["leaderboard"]
        top_score = max([v["score"] for v in lb.values()]) if lb else 0
        
        # Qualifica para o desempate se estiver empatado na pontuação máxima ou se o modo manual estiver ativo
        eligible_for_tb = (
            (user_score == top_score and user_score > 0 and is_top_tied) 
            or db["force_tiebreaker_mode"]
        )

        # FIM DAS 5 QUESTÕES REGULARES
        if step >= len(questions):
            
            # Atualiza primeiro os dados padrão no leaderboard
            if nickname not in db["leaderboard"] or db["leaderboard"][nickname]["score"] != user_score:
                db["leaderboard"][nickname] = {
                    "score": user_score,
                    "tb_score": st.session_state.get("tb_score", 0),
                    "tb_answered": st.session_state.get("tb_answered", False),
                    "total": len(questions),
                    "percentage": round((user_score / len(questions)) * 100),
                    "time": datetime.datetime.now().strftime("%H:%M:%S")
                }

            # SE FOR CASO DE EMPATE E O PARTICIPANTE AINDA NÃO RESPONDEU A 6ª PERGUNTA
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

                        # Atualiza no leaderboard compartilhado
                        db["leaderboard"][nickname]["tb_score"] = tb_val
                        db["leaderboard"][nickname]["tb_answered"] = True
                        
                        st.rerun()
                    else:
                        st.warning("Selecione uma opção para desempate.")

            # SE JÁ CONCLUIU (SEM EMPATE OU APÓS RESPONDER A 6ª)
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

        # QUESTÕES REGULARES (1 a 5)
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

    # Alerta de Empate no Telão
    has_tie = check_top_tie()
    if has_tie:
        st.warning("⚠️ **ATENÇÃO: EMPATE DETECTADO NO 1º LUGAR!** A Pergunta 6 de Desempate foi ativada nos celulares dos líderes.")

    if not leaderboard:
        st.info("Aguardando os primeiros envios dos participantes...")
    else:
        # ORDENAÇÃO: 1º por Acertos Principais, 2º por Acerto na Questão 6 (tb_score), 3º por %
        sorted_ranking = sorted(
            leaderboard.items(),
            key=lambda item: (item[1]["score"], item[1].get("tb_score", 0), item[1]["percentage"]),
            reverse=True
        )

        # Destaque do Top 3
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
            p3_name, p3_data = sorted_ranking[3 - 1]
            tb_txt = " (Desempate 🎯)" if p3_data.get("tb_score", 0) == 1 else ""
            col3.metric("🥉 3º Lugar", p3_name, f"{p3_data['score']}/{p3_data['total']}{tb_txt}")

        st.divider()
        st.subheader("📋 Tabela Oficial de Pontuação")

        ranking_table = []
        for rank, (nick, data) in enumerate(sorted_ranking, 1):
            
            # Status da 6ª Pergunta
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
                "Horário": data['time']
            })

        st.table(ranking_table)

    st.divider()
    col_act1, col_act2, col_act3 = st.columns([2, 2, 1])
    
    with col_act1:
        if st.button("🔄 Atualizar Ranking", use_container_width=True):
            st.rerun()
            
    with col_act2:
        # Botão para o Apresentador liberar a 6ª pergunta para TODO MUNDO se desejar
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
        app_url = st.text_input(
            "Link público do seu app:",
            value="https://seu-app.streamlit.app"
        )
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
