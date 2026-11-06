import socket
import io
import base64
from flask import Flask, render_template_string, request, jsonify

# Tenta importar a biblioteca de QR Code
try:
    import qrcode
except ImportError:
    import sys
    print("\n[ERRO] A biblioteca 'qrcode' não está instalada.")
    print("Execute no terminal: pip install qrcode pillow flask\n")
    sys.exit(1)

app = Flask(__name__)

# ==============================================================================
# CONFIGURAÇÃO DA PERGUNTA E OPÇÕES (EDITE AQUI SE DESEJAR)
# ==============================================================================
POLL_DATA = {
    "title": "Votação de Compliance & Licenciamento",
    "question": "Qual a principal exigência para o transporte regular de resíduos na sua região?",
    "options": [
        "A) MTR (Manifesto) e Licença da ANTT",
        "B) Apenas Nota Fiscal de Simples Remessa",
        "C) Alvará de Funcionamento Municipal",
        "D) Cadastro Básico de Fornecedores"
    ]
}

# Armazenamento de Votos em Memória
votes = {i: 0 for i in range(len(POLL_DATA["options"]))}
voted_ips = set()

# Função para identificar o IP local do computador na rede
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

# Função para gerar o QR Code em formato Base64 (100% offline)
def generate_qr_code(url):
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0f172a", back_color="#ffffff")
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

# ==============================================================================
# TEMPLATE HTML: TELA DE VOTAÇÃO NO CELULAR (OFFLINE)
# ==============================================================================
VOTE_HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Votação Interativa</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    body { background-color: #090d16; color: #f8fafc; min-height: 100vh; display: flex; flex-direction: column; justify-content: space-between; padding: 20px; }
    header { text-align: center; margin-bottom: 20px; border-b: 1px solid #1e293b; padding-bottom: 15px; }
    .badge { display: inline-block; background: rgba(16, 185, 129, 0.15); color: #34d399; font-size: 12px; font-weight: bold; padding: 4px 12px; rounded: 20px; border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 20px; margin-bottom: 8px; }
    h1 { font-size: 20px; color: #ffffff; }
    .card { background: #0f172a; border: 1px solid #1e293b; border-radius: 16px; padding: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
    .question { font-size: 17px; font-weight: 600; color: #38bdf8; margin-bottom: 20px; line-height: 1.4; }
    .options { display: flex; flex-direction: column; gap: 12px; }
    .btn-option { background: #1e293b; border: 2px solid #334155; color: #e2e8f0; padding: 16px; border-radius: 12px; font-size: 15px; font-weight: 600; text-align: left; cursor: pointer; transition: all 0.2s ease; display: flex; justify-content: space-between; align-items: center; }
    .btn-option:active { transform: scale(0.98); background: #0284c7; border-color: #38bdf8; color: #ffffff; }
    .btn-option.selected { background: #065f46; border-color: #10b981; color: #ffffff; }
    .thank-you { display: none; text-align: center; padding: 40px 10px; }
    .thank-you h2 { color: #34d399; font-size: 24px; margin-bottom: 10px; }
    .thank-you p { color: #94a3b8; font-size: 14px; }
    footer { display: flex; justify-content: space-between; font-size: 12px; color: #64748b; margin-top: 30px; font-weight: bold; }
  </style>
</head>
<body>
  <div>
    <header>
      <span class="badge">VOTAÇÃO OFFLINE</span>
      <h1>{{ title }}</h1>
    </header>

    <main class="card">
      <div id="poll-form">
        <p class="question">{{ question }}</p>
        <div class="options">
          {% for option in options %}
          <button class="btn-option" onclick="sendVote({{ loop.index0 }}, this)">
            <span>{{ option }}</span>
          </button>
          {% endfor %}
        </div>
      </div>

      <div id="thank-you" class="thank-you">
        <h2>✓ Voto Confirmado!</h2>
        <p>Acompanhe o resultado ao vivo no telão principal.</p>
      </div>
    </main>
  </div>

  <footer>
    <span>victor</span>
    <span>Dotta</span>
  </footer>

  <script>
    // Verifica se já votou neste celular
    if (localStorage.getItem('has_voted')) {
      showThankYou();
    }

    function sendVote(index, btn) {
      if (localStorage.getItem('has_voted')) return;

      btn.classList.add('selected');
      
      fetch('/api/vote', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ option: index })
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          localStorage.setItem('has_voted', 'true');
          setTimeout(showThankYou, 400);
        } else {
          alert(data.message);
        }
      })
      .catch(() => alert('Erro de conexão com o servidor local.'));
    }

    function showThankYou() {
      document.getElementById('poll-form').style.display = 'none';
      document.getElementById('thank-you').style.display = 'block';
    }
  </script>
</body>
</html>
"""

# ==============================================================================
# TEMPLATE HTML: PAINEL DE RESULTADOS NO PROJETOR / COMPUTADOR (`/dashboard`)
# ==============================================================================
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Painel em Tempo Real - Votação</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    body { background-color: #020617; color: #f8fafc; min-height: 100vh; padding: 30px; display: flex; flex-direction: column; justify-content: space-between; }
    header { display: flex; justify-content: space-between; align-items: center; border-b: 1px solid #1e293b; padding-bottom: 20px; margin-bottom: 30px; }
    h1 { font-size: 28px; color: #ffffff; }
    .total-badge { background: #0284c7; color: #ffffff; padding: 8px 18px; border-radius: 30px; font-weight: bold; font-size: 16px; }
    
    .main-grid { display: grid; grid-template-columns: 320px 1fr; gap: 40px; align-items: start; }
    
    .qr-card { background: #0f172a; border: 1px solid #1e293b; border-radius: 20px; padding: 25px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.6); }
    .qr-card img { width: 100%; max-width: 240px; border-radius: 12px; margin: 15px 0; border: 4px solid #ffffff; }
    .qr-url { background: #1e293b; color: #38bdf8; font-family: monospace; padding: 10px; border-radius: 8px; font-size: 15px; font-weight: bold; word-break: break-all; }
    
    .results-card { background: #0f172a; border: 1px solid #1e293b; border-radius: 20px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.6); }
    .question-title { font-size: 22px; font-weight: bold; color: #38bdf8; margin-bottom: 25px; }
    
    .bar-group { margin-bottom: 20px; }
    .bar-header { display: flex; justify-content: space-between; font-weight: 600; font-size: 16px; margin-bottom: 8px; }
    .bar-bg { background: #1e293b; height: 28px; border-radius: 8px; overflow: hidden; position: relative; }
    .bar-fill { background: linear-gradient(90deg, #0284c7, #10b981); height: 100%; width: 0%; transition: width 0.5s ease; border-radius: 8px; }
    
    .winner-highlight { border: 2px solid #10b981 !important; background: rgba(16, 185, 129, 0.05); }
    
    .controls { margin-top: 25px; display: flex; gap: 15px; }
    .btn { padding: 12px 24px; border-radius: 10px; border: none; font-weight: bold; cursor: pointer; font-size: 14px; transition: 0.2s; }
    .btn-reset { background: #ef4444; color: white; }
    .btn-reset:hover { background: #dc2626; }
    
    footer { display: flex; justify-content: space-between; font-size: 14px; color: #64748b; font-weight: bold; border-t: 1px solid #1e293b; padding-top: 20px; margin-top: 30px; }
  </style>
</head>
<body>
  <div>
    <header>
      <div>
        <h1>{{ title }}</h1>
        <p style="color: #94a3b8; font-size: 14px; margin-top: 4px;">Painel Transmissor Local (Offline)</p>
      </div>
      <div class="total-badge">Total de Votos: <span id="total-votes">0</span></div>
    </header>

    <div class="main-grid">
      <!-- Card do QR Code -->
      <div class="qr-card">
        <h3 style="font-size: 16px; color: #f8fafc;">Escaneie para Votar</h3>
        <img src="data:image/png;base64,{{ qr_code }}" alt="QR Code Votação">
        <p style="font-size: 12px; color: #94a3b8; margin-bottom: 8px;">Ou acesse pelo celular:</p>
        <div class="qr-url">{{ server_url }}</div>
      </div>

      <!-- Placar dos Resultados -->
      <div class="results-card">
        <div class="question-title">{{ question }}</div>
        
        <div id="results-container">
          {% for option in options %}
          <div class="bar-group" id="group-{{ loop.index0 }}">
            <div class="bar-header">
              <span>{{ option }}</span>
              <span id="text-{{ loop.index0 }}">0 votos (0%)</span>
            </div>
            <div class="bar-bg">
              <div class="bar-fill" id="bar-{{ loop.index0 }}"></div>
            </div>
          </div>
          {% endfor %}
        </div>

        <div class="controls">
          <button class="btn btn-reset" onclick="resetVotes()">Zerar Votação</button>
        </div>
      </div>
    </div>
  </div>

  <footer>
    <span>victor</span>
    <span>Dotta</span>
  </footer>

  <script>
    function updateResults() {
      fetch('/api/results')
        .then(res => res.json())
        .then(data => {
          document.getElementById('total-votes').textContent = data.total;
          
          let maxVotes = -1;
          let winnerIndex = -1;

          // Descobre o vencedor
          data.votes.forEach((count, i) => {
            if (count > maxVotes && count > 0) {
              maxVotes = count;
              winnerIndex = i;
            }
          });

          data.votes.forEach((count, i) => {
            const pct = data.total > 0 ? Math.round((count / data.total) * 100) : 0;
            document.getElementById(`bar-${i}`).style.width = pct + '%';
            document.getElementById(`text-${i}`).textContent = `${count} votos (${pct}%)`;

            const groupEl = document.getElementById(`group-${i}`);
            if (i === winnerIndex && data.total > 0) {
              groupEl.classList.add('winner-highlight');
            } else {
              groupEl.classList.remove('winner-highlight');
            }
          });
        });
    }

    function resetVotes() {
      if (confirm('Deseja zerar todos os votos acumulados?')) {
        fetch('/api/reset', { method: 'POST' }).then(() => updateResults());
      }
    }

    // Atualiza o placar a cada 1.5 segundos
    setInterval(updateResults, 1500);
    updateResults();
  </script>
</body>
</html>
"""

# ==============================================================================
# ROTAS DA APLICAÇÃO FLASK
# ==============================================================================

@app.route('/')
def vote_page():
    return render_template_string(VOTE_HTML, title=POLL_DATA["title"], question=POLL_DATA["question"], options=POLL_DATA["options"])

@app.route('/dashboard')
def dashboard_page():
    ip = get_local_ip()
    server_url = f"http://{ip}:5000"
    qr_b64 = generate_qr_code(server_url)
    return render_template_string(DASHBOARD_HTML, title=POLL_DATA["title"], question=POLL_DATA["question"], options=POLL_DATA["options"], qr_code=qr_b64, server_url=server_url)

@app.route('/api/vote', methods=['POST'])
def handle_vote():
    data = request.get_json()
    opt_index = data.get('option')
    user_ip = request.remote_addr

    if user_ip in voted_ips:
        return jsonify({"success": False, "message": "Você já votou a partir deste dispositivo."})

    if opt_index is not None and 0 <= opt_index < len(POLL_DATA["options"]):
        votes[opt_index] += 1
        voted_ips.add(user_ip)
        return jsonify({"success": True})
    
    return jsonify({"success": False, "message": "Opção inválida."})

@app.route('/api/results')
def get_results():
    total = sum(votes.values())
    return jsonify({"votes": [votes[i] for i in range(len(POLL_DATA["options"]))], "total": total})

@app.route('/api/reset', methods=['POST'])
def reset_poll():
    global votes, voted_ips
    votes = {i: 0 for i in range(len(POLL_DATA["options"]))}
    voted_ips.clear()
    return jsonify({"success": True})

# ==============================================================================
# EXECUÇÃO DO SERVIDOR LOCAL (0.0.0.0 PERMITE ACESSO PELA REDE WI-FI)
# ==============================================================================
if __name__ == '__main__':
    local_ip = get_local_ip()
    print("\n" + "="*60)
    print(" SERVIDOR DE VOTAÇÃO OFFLINE INICIADO COM SUCESSO!")
    print("="*60)
    print(f" ► NO COMPUTADOR / PROJETOR, ABRA:  http://localhost:5000/dashboard")
    print(f" ► LINK DA REDE LOCAL (CELULARES):   http://{local_ip}:5000")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)