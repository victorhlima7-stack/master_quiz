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
# BANCO DE DADOS EM MEMÓRIA COMPARTILHADO ENTRE TODOS OS CELULARES
# ==============================================================================
@st.cache_resource
def get_shared_db():
    return {
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
        # Armazena o ranking: {"nickname": {"score": X, "total": Y, "time": "14:30"}}
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

# ==============================================================================
# MENU LATERAL
# ==============================================================================
st.sidebar.title("🛡️ Compliance Hub")
st.sidebar.caption("Sistema de Quiz & Ranking ao Vivo")

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
# PAINEL 1: RESPONDER QUIZ NO CELULAR (COM NICKNAME)
# ==============================================================================
if modulo == "📱 Responder Quiz (Celular)":
    st.title("🎯 Quiz de Compliance")

    # Passo 1: Cadastro de Nickname
    if "user_nickname" not in st.session_state:
        st.subheader("Para começar, digite seu Apelido / Nickname:")
        
        nick_input = st.text_input("Seu Nickname:", placeholder="Ex: Victor_Compliance", max_chars=20)
        
        if st.button("🚀 Iniciar Quiz", type="primary", use_container_width=True):
            if nick_input.strip() != "":
                st.session_state["user_nickname"] = nick_input.strip()
                st.session_state["quiz_step"] = 0
                st.session_state["score"] = 0
                st.session_state["answered"] = False
                st.rerun()
            else:
                st.warning("Por favor, digite um nickname válido.")

    # Passo 2: Execução do Quiz
    else:
        nickname = st.session_state["user_nickname"]
        step = st.session_state.get("quiz_step", 0)
        questions = db["questions"]

        # Se já respondeu todas as perguntas
        if step >= len(questions):
            st.balloons()
            st.success(f"🎉 **Parabéns, {nickname}! Você concluiu o Quiz!**")
            
            final_score = st.session_state["score"]
            total = len(questions)
            pct = round((final_score / total) * 100)
            
            st.metric("Sua Pontuação Final", f"{final_score} de {total} ({pct}%)")

            # Salva a pontuação no banco compartilhado
            db["leaderboard"][nickname] = {
                "score": final_score,
                "total": total,
                "percentage": pct,
                "time": datetime.datetime.now().strftime("%H:%M:%S")
            }

            st.info("Acompanhe a sua posição no Ranking Geral exibido no Telão!")

            if st.button("🔄 Responder Novamente com outro Nickname"):
                del st.session_state["user_nickname"]
                st.rerun()

        # Apresentação da pergunta atual
        else:
            q = questions[step]
            
            st.caption(f"Participante: **{nickname}** | Questão {step + 1} de {len(questions)}")
            st.progress((step) / len(questions))
            
            st.markdown(f"**[{q['category']}]**")
            st.subheader(q["question"])

            # Opções de Resposta
            selected_option = st.radio(
                "Selecione a alternativa correta:",
                options=list(range(len(q["options"]))),
                format_func=lambda i: q["options"][i],
                index=None,
                disabled=st.session_state.get("answered", False)
            )

            # Botão de confirmação de resposta
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

            # Exibição do feedback pós-resposta
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
# PAINEL 2: RANKING AO VIVO (EXIBIDO NO TELÃO / PROJETOR)
# ==============================================================================
elif modulo == "🏆 Ranking de Acertos (Telão/Admin)":
    st.title("🏆 Ranking de Desempenho ao Vivo")
    st.caption("Classificação dos participantes que responderam pelo celular")
    st.divider()

    leaderboard = db["leaderboard"]

    if not leaderboard:
        st.info("Ainda nenhum participante concluiu o quiz. Os resultados aparecerão aqui em tempo real assim que os envios começarem!")
    else:
        # Ordena o ranking por maior pontuação (e maior porcentagem)
        sorted_ranking = sorted(
            leaderboard.items(),
            key=lambda item: (item[1]["score"], item[1]["percentage"]),
            reverse=True
        )

        # Destaque dos 3 Primeiros Colocados
        col1, col2, col3 = st.columns(3)
        
        if len(sorted_ranking) >= 1:
            p1_name, p1_data = sorted_ranking[0]
            col1.metric("🥇 1º Lugar", p1_name, f"{p1_data['score']}/{p1_data['total']} acertos ({p1_data['percentage']}%)")
        
        if len(sorted_ranking) >= 2:
            p2_name, p2_data = sorted_ranking[1]
            col2.metric("🥈 2º Lugar", p2_name, f"{p2_data['score']}/{p2_data['total']} acertos ({p2_data['percentage']}%)")
            
        if len(sorted_ranking) >= 3:
            p3_name, p3_data = sorted_ranking[2]
            col3.metric("🥉 3º Lugar", p3_name, f"{p3_data['score']}/{p3_data['total']} acertos ({p3_data['percentage']}%)")

        st.divider()
        st.subheader("📋 Tabela Geral de Pontuação")

        # Monta a tabela geral
        ranking_table = []
        for rank, (nick, data) in enumerate(sorted_ranking, 1):
            ranking_table.append({
                "Posição": f"#{rank}",
                "Nickname": nick,
                "Acertos": f"{data['score']} / {data['total']}",
                "Aproveitamento": f"{data['percentage']}%",
                "Horário de Envio": data['time']
            })

        st.table(ranking_table)

    st.divider()
    col_act1, col_act2 = st.columns([2, 1])
    with col_act1:
        if st.button("🔄 Atualizar Ranking Manualmente", use_container_width=True):
            st.rerun()
    with col_act2:
        if st.button("🚨 Zerar Ranking / Novo Raciocínio", type="secondary", use_container_width=True):
            db["leaderboard"].clear()
            st.success("Ranking zerado com sucesso!")
            st.rerun()

# ==============================================================================
# PAINEL 3: QR CODE PARA OS CELULARES
# ==============================================================================
else:
    st.title("📺 Acesso à Votação & Quiz")
    st.caption("Projete este QR Code na tela para os participantes escanearem")
    st.divider()

    col_qr, col_info = st.columns([1, 2])

    with col_qr:
        app_url = st.text_input(
            "Cole o link público do seu app no Streamlit Cloud:",
            value="https://seu-app.streamlit.app"
        )
        qr_bytes = generate_qr(app_url)
        st.image(qr_bytes, caption="Escaneie para informar o Nickname e iniciar", width=280)

    with col_info:
        st.subheader("Instruções para a Plenária:")
        st.markdown("""
        1. Aponte a câmera do celular para o **QR Code ao lado**.
        2. Digite seu **Apelido / Nickname** ao abrir a página.
        3. Responda às **5 questões de Compliance**.
        4. Confira a sua colocação final no **Ranking em Tempo Real** do telão!
        """)
