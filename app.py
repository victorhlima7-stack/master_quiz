import streamlit as st
import streamlit.components.v1 as components
import qrcode
from io import BytesIO
import uuid

# Configuração Geral da Página
st.set_page_config(
    page_title="Plataforma de Compliance & Votação",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# BANCO DE DADOS EM MEMÓRIA PARA A VOTAÇÃO AO VIVO
# ==============================================================================
@st.cache_resource
def get_shared_db():
    return {
        "title": "Votação de Compliance & Licenciamento",
        "question": "Qual a principal exigência para o transporte regular de resíduos perigosos?",
        "options": [
            "A) MTR (Manifesto) e Licença da ANTT",
            "B) Apenas Nota Fiscal de Simples Remessa",
            "C) Alvará de Funcionamento Municipal",
            "D) Cadastro Básico de Fornecedores"
        ],
        "votes": {0: 0, 1: 0, 2: 0, 3: 0},
        "voted_users": set()
    }

db = get_shared_db()

if "user_token" not in st.session_state:
    st.session_state["user_token"] = str(uuid.uuid4())

user_token = st.session_state["user_token"]
has_voted = user_token in db["voted_users"]

def generate_qr(url):
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0f172a", back_color="#ffffff")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# ==============================================================================
# BARRA LATERAL - MENU PRINCIPAL
# ==============================================================================
st.sidebar.title("🛡️ Compliance Hub")
st.sidebar.caption("Plataforma Interativa de Treinamento")

modulo = st.sidebar.radio(
    "Selecione o Módulo:",
    [
        "🎯 Quiz de Compliance (Estudo)",
        "📱 Votar pelo Celular (Ao Vivo)",
        "📺 Painel do Telão / QR Code"
    ]
)

st.sidebar.divider()
st.sidebar.markdown("**Desenvolvido por:** victor & Dotta")

# ==============================================================================
# MÓDULO 1: QUIZ INTERATIVO COMPLETO (EMBUTIDO VIA HTML/JS)
# ==============================================================================
if modulo == "🎯 Quiz de Compliance (Estudo)":
    st.subheader("🎯 Quiz Interativo de Compliance & Licenciamento")
    st.caption("Responda às questões com diagnóstico imediato de fundamentação legal.")

    # Código HTML/CSS/JS do Quiz embutido
    quiz_html_code = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
      <meta charset="UTF-8">
      <script src="https://cdn.tailwindcss.com"></script>
      <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
      <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
      <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #0f172a; color: #f8fafc; }
      </style>
    </head>
    <body class="p-4">
      <div id="quiz-box" class="max-w-2xl mx-auto bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
        <div class="flex justify-between items-center mb-4">
          <span id="cat-badge" class="px-3 py-1 bg-emerald-500/20 text-emerald-400 text-xs font-bold rounded-full">Licenciamento</span>
          <span id="q-count" class="text-xs text-slate-400 font-semibold">Questão 1 de 5</span>
        </div>
        <h3 id="q-text" class="text-lg font-bold mb-4 text-white">Carregando...</h3>
        <div id="options" class="space-y-2 mb-4"></div>
        <div id="exp-box" class="hidden p-3 rounded-lg bg-slate-800 border border-slate-700 text-xs text-slate-300 mb-4">
          <strong>Explicação: </strong><span id="exp-text"></span>
        </div>
        <div class="flex justify-between items-center">
          <span class="text-xs text-slate-500 font-bold">victor & Dotta</span>
          <button id="btn-next" onclick="nextQ()" disabled class="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-sm rounded-lg opacity-50 cursor-not-allowed">Próxima</button>
        </div>
      </div>

      <div id="result-box" class="hidden max-w-2xl mx-auto bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl text-center">
        <h2 class="text-2xl font-bold text-white mb-2">Resultado Final</h2>
        <p id="score-val" class="text-4xl font-extrabold text-emerald-400 mb-4">0/5</p>
        <button onclick="restart()" class="px-6 py-2 bg-slate-800 hover:bg-slate-700 text-white font-bold rounded-lg text-sm border border-slate-700">Refazer Quiz</button>
      </div>

      <script>
        const questions = [
          { category: "Transporte & Fisco", q: "Qual documento é obrigatório para o transporte terrestre de resíduos perigosos?", opts: ["Apenas Nota Fiscal", "MTR (Manifesto) e Ficha de Emergência", "Certificado DETRAN", "Alvará Municipal"], correct: 1, exp: "O MTR emitido via SINIR é obrigatório para o rastreio de resíduos perigosos." },
          { category: "Licenciamento", q: "Qual licença autoriza o início efetivo das operações da empresa?", opts: ["Licença Prévia (LP)", "Licença de Instalação (LI)", "Licença de Operação (LO)", "Cadastro Técnico"], correct: 2, exp: "A Licença de Operação (LO) autoriza o funcionamento oficial do empreendimento." },
          { category: "Documentação Fiscal", q: "Qual documento fiscal acoberta a prestação do serviço de frete rodoviário?", opts: ["CT-e / MDF-e", "RPS Simples", "Declaração de Isenção", "Ordem de Serviço"], correct: 0, exp: "O Conhecimento de Transporte Eletrônico (CT-e) é a norma fiscal oficial." },
          { category: "Destinação Final", q: "Qual documento comprova o descarte ambientalmente adequado do resíduo?", opts: ["Certificado de Destinação Final (CDF)", "Contrato Social", "Comprovante de Pedágio", "Cadastro de Cliente"], correct: 0, exp: "O CDF emitido pelo destinador homologado comprova a destinação final ambiental." },
          { category: "ANTT", q: "Qual o registro obrigatório para transportadores de cargas perigosas na ANTT?", opts: ["RNTRC", "CREA", "Seguro RCF", "Alvará de Ambulante"], correct: 0, exp: "O RNTRC é o registro obrigatório fiscalizado pela ANTT." }
        ];

        let curr = 0, score = 0, answered = false;

        function load() {
          answered = false;
          document.getElementById('btn-next').disabled = true;
          document.getElementById('btn-next').classList.add('opacity-50', 'cursor-not-allowed');
          document.getElementById('exp-box').classList.add('hidden');
          
          const q = questions[curr];
          document.getElementById('cat-badge').textContent = q.category;
          document.getElementById('q-count').textContent = `Questão ${curr + 1} de ${questions.length}`;
          document.getElementById('q-text').textContent = q.q;
          
          const container = document.getElementById('options');
          container.innerHTML = '';
          q.opts.forEach((opt, i) => {
            const btn = document.createElement('button');
            btn.className = "w-full p-3 text-left rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-sm font-medium transition";
            btn.textContent = opt;
            btn.onclick = () => select(i, btn);
            container.appendChild(btn);
          });
        }

        function select(idx, btn) {
          if (answered) return;
          answered = true;
          const q = questions[curr];
          const allBtns = document.getElementById('options').children;

          if (idx === q.correct) {
            score++;
            btn.className = "w-full p-3 text-left rounded-lg bg-emerald-950 border-2 border-emerald-500 text-emerald-200 text-sm font-bold";
          } else {
            btn.className = "w-full p-3 text-left rounded-lg bg-rose-950 border-2 border-rose-500 text-rose-200 text-sm font-bold";
            allBtns[q.correct].className = "w-full p-3 text-left rounded-lg bg-emerald-950 border-2 border-emerald-500 text-emerald-200 text-sm font-bold";
          }

          document.getElementById('exp-text').textContent = q.exp;
          document.getElementById('exp-box').classList.remove('hidden');
          
          const nextBtn = document.getElementById('btn-next');
          nextBtn.disabled = false;
          nextBtn.classList.remove('opacity-50', 'cursor-not-allowed');
        }

        function nextQ() {
          curr++;
          if (curr < questions.length) {
            load();
          } else {
            document.getElementById('quiz-box').classList.add('hidden');
            document.getElementById('result-box').classList.remove('hidden');
            document.getElementById('score-val').textContent = `${score}/${questions.length}`;
          }
        }

        function restart() {
          curr = 0; score = 0;
          document.getElementById('result-box').classList.add('hidden');
          document.getElementById('quiz-box').classList.remove('hidden');
          load();
        }

        load();
      </script>
    </body>
    </html>
    """
    components.html(quiz_html_code, height=520, scrolling=False)

# ==============================================================================
# MÓDULO 2: VOTAÇÃO PELO CELULAR
# ==============================================================================
elif modulo == "📱 Votar pelo Celular (Ao Vivo)":
    st.title(db["title"])
    st.caption("Conectado via internet no celular")
    st.divider()

    if has_voted:
        st.success("✅ **Seu voto foi registrado com sucesso!**")
        st.info("Acompanhe o gráfico de apuração ao vivo na tela principal do telão.")
        if st.button("🔄 Atualizar Visualização"):
            st.rerun()
    else:
        st.subheader(db["question"])
        st.write("Escolha uma opção:")

        selected_option = st.radio(
            "Opções disponíveis:",
            options=list(range(len(db["options"]))),
            format_func=lambda i: db["options"][i],
            index=None
        )

        if st.button("📥 Confirmar Voto", type="primary", use_container_width=True):
            if selected_option is not None:
                db["votes"][selected_option] += 1
                db["voted_users"].add(user_token)
                st.success("Voto computado!")
                st.rerun()
            else:
                st.warning("Selecione uma opção antes de confirmar.")

# ==============================================================================
# MÓDULO 3: PAINEL DO TELÃO (RESULTADOS E QR CODE)
# ==============================================================================
else:
    st.title("📺 Painel de Apuração ao Vivo")
    
    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.subheader("📱 Escaneie para Votar")
        
        # Link do seu site no Streamlit Cloud
        app_url = st.text_input(
            "Cole a URL pública do seu app:",
            value="https://seu-app.streamlit.app"
        )
        
        qr_bytes = generate_qr(app_url)
        st.image(qr_bytes, caption="Aponta a câmera para votar", width=240)
        
        total_votes = sum(db["votes"].values())
        st.metric(label="Total de Votos Computados", value=total_votes)

        if st.button("🚨 Zerar Votação", type="secondary"):
            db["votes"] = {i: 0 for i in range(len(db["options"]))}
            db["voted_users"].clear()
            st.success("Votação zerada!")
            st.rerun()

    with col_right:
        st.subheader(db["question"])
        st.divider()

        total_votes = sum(db["votes"].values())
        max_votes = max(db["votes"].values()) if total_votes > 0 else -1

        for i, option_text in enumerate(db["options"]):
            count = db["votes"][i]
            pct = round((count / total_votes) * 100) if total_votes > 0 else 0
            
            is_winner = (count == max_votes and max_votes > 0)
            prefix = "🏆 " if is_winner else ""
            
            st.write(f"**{prefix}{option_text}**")
            st.progress(pct / 100)
            st.caption(f"{count} votos ({pct}%)")
            st.write("")

        if st.button("🔄 Atualizar Placar Ao Vivo", use_container_width=True):
            st.rerun()
