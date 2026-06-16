from flask import Flask, render_template, request, redirect, flash, session, url_for, Response, jsonify
from functools import wraps
from waitress import serve
from datetime import timedelta
from ldap3 import Server, Connection, ALL, NTLM
from urllib.parse import unquote

app = Flask(__name__, template_folder=r"C:\Procesos\Ejecutables_Python\pages",
                static_folder=r"C:\Procesos\Ejecutables_Python\Imagenes")
app.secret_key = "supersecretkey"
app.permanent_session_lifetime = timedelta(minutes=15)


AD_SERVER = 'ldap://192.168.88.106'
AD_DOMAIN = '@integraretail.pe'

def autenticar_ad(usuario, password):
    try:
        usuario_ad = f"{AD_DOMAIN}\\{usuario}"
        server = Server(AD_SERVER, get_info=ALL)
        conn = Connection(server, user=usuario_ad, password=password, authentication=NTLM)
        if conn.bind():
            conn.unbind()
            return True
        return False
    except:
        return False

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if 'usuario' not in session:

            # Peticiones AJAX / iframe
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":

                return jsonify({
                    "session_expired": True,
                    "redirect": url_for('index')
                }), 401

            # Navegación normal
            flash('Tu sesión ha expirado o no has iniciado sesión ⚠️', 'warning')

            return redirect(url_for('index'))

        return f(*args, **kwargs)

    return decorated_function

def render_powerbi(url):
    return f"""
    <html>
        <body style='margin:0;padding:0;overflow:hidden'>
            <iframe 
                src="{url}" 
                width="100%" 
                height="100%" 
                frameborder="0"
                allowfullscreen="true">
            </iframe>
        </body>
    </html>
    """

modulos = {
    "ventas": {
        "template": "ventas.html",
        "subreportes": {
            "ventas_general": "https://app.powerbi.com/view?r=eyJrIjoiMjdmNDY0OTMtMjQxNS00YTI0LTkwNmUtNGYxNmQ3ZTViMjYzIiwidCI6IjAyMDhhY2YzLTJiYjQtNGMzYi04MGQ5LTM2YTY4M2Y3OWZkNiJ9&pageName=ede5488ac25193833161",
            "recuperos": "https://app.powerbi.com/view?r=eyJrIjoiMzkwZTY2NTQtMWJmNy00MzA5LTk2OWMtNWM2Mjg2MWY4MTJjIiwidCI6IjAyMDhhY2YzLTJiYjQtNGMzYi04MGQ5LTM2YTY4M2Y3OWZkNiJ9",
            "ventas_qt":"https://app.powerbi.com/view?r=eyJrIjoiZDEwZWI3NjgtMTE0Mi00NmNmLWI3NTctMmUzY2Y0NzVmZTQ4IiwidCI6IjAyMDhhY2YzLTJiYjQtNGMzYi04MGQ5LTM2YTY4M2Y3OWZkNiJ9&pageName=2b13e294406015565300",
            "solicitudes": "https://app.powerbi.com/view?r=eyJrIjoiOWU1ODAwZGEtNjIxZi00Y2RhLTg4ZTAtZTJjODNkYzNjMTk2IiwidCI6IjAyMDhhY2YzLTJiYjQtNGMzYi04MGQ5LTM2YTY4M2Y3OWZkNiJ9",
            "sell_in_sell_out": "https://app.powerbi.com/view?r=eyJrIjoiNTk3NzE0MjUtMWNkZC00ZWU2LWJjNmEtMzEwYmU3ODZiNmQwIiwidCI6IjAyMDhhY2YzLTJiYjQtNGMzYi04MGQ5LTM2YTY4M2Y3OWZkNiJ9&pageName=df57814b2a58150150cc",
            "marcas_propias": "https://app.powerbi.com/view?r=eyJrIjoiYzY5OTY1ZGEtNzUzOC00MzllLTkxMmEtMDNhZThmYTZlMzA1IiwidCI6IjAyMDhhY2YzLTJiYjQtNGMzYi04MGQ5LTM2YTY4M2Y3OWZkNiJ9&pageName=2b13e294406015565300"
        }
    },
    "inventario": {"template": "inventario.html",
        "subreportes": {
            "stock_disponible": "https://app.powerbi.com/view?r=eyJrIjoiNmMyZTY4MGYtOTdmNy00ZmQ0LWE1NTUtNWRlNTcyYTYwZTMzIiwidCI6IjAyMDhhY2YzLTJiYjQtNGMzYi04MGQ5LTM2YTY4M2Y3OWZkNiJ9&pageName=292ae778bac2770a61f7",
            "fill_rate": "https://app.powerbi.com/view?r=eyJrIjoiMzkwZTY2NTQtMWJmNy00MzA5LTk2OWMtNWM2Mjg2MWY4MTJjIiwidCI6IjAyMDhhY2YzLTJiYjQtNGMzYi04MGQ5LTM2YTY4M2Y3OWZkNiJ9",
            "quiebres": "https://app.powerbi.com/view?r=eyJrIjoiOWZhOGRlYzYtOWM2Ny00MzJhLTgzYWQtZjMzYWJkNmJhNjA2IiwidCI6IjAyMDhhY2YzLTJiYjQtNGMzYi04MGQ5LTM2YTY4M2Y3OWZkNiJ9",
            "compras":"https://app.powerbi.com/view?r=eyJrIjoiNzFlMDdlZGEtNWVlMS00YWYxLTgwZDItYWE1ZTI1MmZiMTcxIiwidCI6IjAyMDhhY2YzLTJiYjQtNGMzYi04MGQ5LTM2YTY4M2Y3OWZkNiJ9",
            "ppto_compras": "https://app.powerbi.com/view?r=eyJrIjoiZDRjMDUxNWUtZjYwYS00ZjEyLThlYmEtMjNkYzhlMDk4Nzc3IiwidCI6IjAyMDhhY2YzLTJiYjQtNGMzYi04MGQ5LTM2YTY4M2Y3OWZkNiJ9&pageName=2b72ffdab510190cb2cc"
        }
    },
    "logistica": {"template": "logistica.html",
        "subreportes": {
            "envios&recepcion": "https://app.powerbi.com/view?r=eyJrIjoiMjdmNDY0OTMtMjQxNS00YTI0LTkwNmUtNGYxNmQ3ZTViMjYzIiwidCI6IjAyMDhhY2YzLTJiYjQtNGMzYi04MGQ5LTM2YTY4M2Y3OWZkNiJ9&pageName=ede5488ac25193833161",
            "almacenes": "https://app.powerbi.com/view?r=eyJrIjoiMzkwZTY2NTQtMWJmNy00MzA5LTk2OWMtNWM2Mjg2MWY4MTJjIiwidCI6IjAyMDhhY2YzLTJiYjQtNGMzYi04MGQ5LTM2YTY4M2Y3OWZkNiJ9"
        }
    },
    "rrhh": {"template": "rrhh.html",
        "subreportes": {
            "rotacion_personal": "https://app.powerbi.com/view?r=eyJrIjoiN2IxOWIyMGYtNzU3Zi00NGFkLWE2YTgtMzFjY2YzNGY5NDUwIiwidCI6IjAyMDhhY2YzLTJiYjQtNGMzYi04MGQ5LTM2YTY4M2Y3OWZkNiJ9&amp;pageName=56c2c2061a5be9b06dc4",
            "calendario_IR": "https://app.powerbi.com/view?r=eyJrIjoiMjdmNDY0OTMtMjQxNS00YTI0LTkwNmUtNGYxNmQ3ZTViMjYzIiwidCI6IjAyMDhhY2YzLTJiYjQtNGMzYi04MGQ5LTM2YTY4M2Y3OWZkNiJ9&pageName=ede5488ac25193833161"
        }
    },
    "finanzas": {"template": "finanzas.html",
        "subreportes": {
            "ap_ebs": "https://app.powerbi.com/view?r=eyJrIjoiMjdmNDY0OTMtMjQxNS00YTI0LTkwNmUtNGYxNmQ3ZTViMjYzIiwidCI6IjAyMDhhY2YzLTJiYjQtNGMzYi04MGQ5LTM2YTY4M2Y3OWZkNiJ9&pageName=ede5488ac25193833161",
            "ar_ebs": "https://app.powerbi.com/view?r=eyJrIjoiMjdmNDY0OTMtMjQxNS00YTI0LTkwNmUtNGYxNmQ3ZTViMjYzIiwidCI6IjAyMDhhY2YzLTJiYjQtNGMzYi04MGQ5LTM2YTY4M2Y3OWZkNiJ9&pageName=ede5488ac25193833161"
        }
    },
    "ejecutivo": {"template": "ejecutivo.html",
        "subreportes": {
            "KPIs_clave": "https://app.powerbi.com/view?r=eyJrIjoiMjdmNDY0OTMtMjQxNS00YTI0LTkwNmUtNGYxNmQ3ZTViMjYzIiwidCI6IjAyMDhhY2YzLTJiYjQtNGMzYi04MGQ5LTM2YTY4M2Y3OWZkNiJ9&pageName=ede5488ac25193833161",
            "supply_chain": "https://app.powerbi.com/view?r=eyJrIjoiMjdmNDY0OTMtMjQxNS00YTI0LTkwNmUtNGYxNmQ3ZTViMjYzIiwidCI6IjAyMDhhY2YzLTJiYjQtNGMzYi04MGQ5LTM2YTY4M2Y3OWZkNiJ9&pageName=ede5488ac25193833161"
        }
    }
}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']

        if autenticar_ad(usuario, password):
            session['usuario'] = usuario
            flash("✅ Inicio de sesión exitoso.", "success")
            return redirect(url_for('login'))
        else:
            flash("❌ Credenciales inválidas.", "danger")

    return render_template('index.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente 👋', 'info')
    return redirect(url_for('index'))


@app.route('/Index_GrupoCarsa/Reportes')
@login_required
def index():
    usuario = session.get('usuario', 'Desconocido')
    return render_template('login.html', usuario=usuario, modulos=modulos)


@app.route('/Index_GrupoCarsa/Reportes/<modulo>')
@login_required
def vista_modulo(modulo):
    config = modulos.get(modulo)
    if not config:
        return "Módulo no existe", 404
    usuario = session.get('usuario', 'Desconocido')
    return render_template(config["template"], usuario=usuario, modulo=modulo, modulos=modulos)


@app.route("/powerbi_proxy/<path:modulo>")
@login_required
def powerbi_proxy(modulo):
    modulo = unquote(modulo)  
    
    for mod, conf in modulos.items():
        if "subreportes" in conf:
            if modulo in conf["subreportes"]:
                return render_powerbi(conf["subreportes"][modulo])

    return """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background: linear-gradient(135deg, #f8fafc, #eef2f7);
            font-family: 'Segoe UI', sans-serif;
        }

        .container { text-align: center; animation: fadeIn 0.8s ease; }

        .electro-scene {
            position: relative;
            width: 340px;
            height: 230px;
            margin: 0 auto 25px;
        }

        /* TV - Pantalla con engranajes */
        .tv {
            position: absolute;
            width: 145px; 
            height: 92px;
            background: #1f2937;
            border-radius: 14px;
            left: 95px; 
            top: 5px;
            border: 6px solid #374151;
            overflow: hidden;
            box-shadow: 0 18px 35px rgba(0,0,0,.25);
            animation: floattv 4s ease-in-out infinite;
        }

        .screen {
            position: absolute;
            inset: 8px;
            background: #111827;
            border-radius: 6px;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .gears {
            position: relative;
            width: 70px;
            height: 70px;
        }

        .gear {
            position: absolute;
            background: #60a5fa;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 18px;
            font-weight: bold;
        }

        .gear1 {
            width: 48px; height: 48px;
            top: 8px; left: 8px;
            animation: spin 2.5s linear infinite;
        }

        .gear2 {
            width: 32px; height: 32px;
            top: 35px; right: 5px;
            animation: spin 1.8s linear infinite reverse;
        }

        .gear3 {
            width: 22px; height: 22px;
            bottom: 8px; left: 12px;
            animation: spin 3s linear infinite;
        }

        .tv::after {
            content: '';
            position: absolute;
            bottom: -18px; left: 54px;
            width: 24px; height: 18px;
            background: #4b5563;
            border-radius: 0 0 5px 5px;
        }

        /* Reemplazo del refrigerador → Animación "En Proceso" */
        .process {
            position: absolute;
            width: 82px; 
            height: 140px;
            background: linear-gradient(#f8fafc, #e2e8f0);
            right: 0; 
            top: 35px;
            border-radius: 14px;
            box-shadow: 0 12px 30px rgba(0,0,0,.15);
            animation: floatfridge 3s ease-in-out infinite;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 12px;
            padding: 15px;
            border: 3px solid #64748b;
        }

        .process-title {
            font-size: 11px;
            font-weight: 700;
            color: #334155;
            letter-spacing: 1px;
        }

        .loading-circle {
            width: 48px;
            height: 48px;
            border: 5px solid #e2e8f0;
            border-top: 5px solid #3b82f6;
            border-radius: 50%;
            animation: spin 1.4s linear infinite;
        }

        .progress-bar {
            width: 55px;
            height: 6px;
            background: #e2e8f0;
            border-radius: 10px;
            overflow: hidden;
        }

        .progress {
            width: 65%;
            height: 100%;
            background: linear-gradient(90deg, #3b82f6, #60a5fa);
            animation: progressAnim 2.5s ease-in-out infinite;
        }

        /* Chart y Doc se mantienen */
        .chart {
            position: absolute;
            width: 82px; height: 84px;
            background: linear-gradient(#fff, #f0f4ff);
            left: 0; bottom: 0;
            border-radius: 14px;
            box-shadow: 0 12px 30px rgba(0,0,0,.15);
            animation: floatwasher 4s ease-in-out infinite;
            display: flex;
            align-items: flex-end;
            justify-content: center;
            gap: 5px;
            padding: 10px 8px;
        }

        .bar {
            width: 12px;
            border-radius: 4px 4px 0 0;
            background: linear-gradient(#ff4d4d, #d90429);
        }
        .bar1 { height: 35px; animation: barUp 1.2s ease-in-out infinite; }
        .bar2 { height: 50px; animation: barUp 1.2s ease-in-out infinite 0.2s; }
        .bar3 { height: 25px; animation: barUp 1.2s ease-in-out infinite 0.4s; }
        .bar4 { height: 42px; animation: barUp 1.2s ease-in-out infinite 0.6s; }

        .doc {
            position: absolute;
            width: 45px; height: 95px;
            background: linear-gradient(#ffffff, #e8edf5);
            left: 130px; bottom: 0;
            border-radius: 8px;
            box-shadow: 0 12px 30px rgba(0,0,0,.15);
            animation: floatspeaker 3.5s ease-in-out infinite;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 6px;
            padding: 8px 6px;
        }

        .doc-line {
            width: 30px; height: 5px;
            border-radius: 3px;
            background: #d1d5db;
        }
        .doc-line.red {
            background: #ff4d4d;
            animation: pulse 1.5s ease-in-out infinite;
        }
        .doc-line.short { width: 20px; }

        h2 {
            font-size: 30px;
            font-weight: 800;
            color: #dc3545;
            margin-bottom: 12px;
        }

        p {
            font-size: 16px;
            color: #6b7280;
            max-width: 400px;
            margin: 0 auto;
            line-height: 1.7;
        }

        @keyframes floattv     { 0%,100%{transform:translateY(0)}   50%{transform:translateY(-10px)} }
        @keyframes floatfridge { 0%,100%{transform:translateY(0)}   50%{transform:translateY(-8px)}  }
        @keyframes floatwasher { 0%,100%{transform:translateY(0)}   50%{transform:translateY(-12px)} }
        @keyframes floatspeaker{ 0%,100%{transform:translateY(0)}   50%{transform:translateY(-6px)}  }
        @keyframes spin        { from{transform:rotate(0deg)} to{transform:rotate(360deg)} }
        @keyframes barUp       { 0%,100%{transform:scaleY(1)} 50%{transform:scaleY(1.4)} }
        @keyframes pulse       { 0%,100%{opacity:1} 50%{opacity:0.2} }
        @keyframes progressAnim{ 0%{width:40%} 50%{width:85%} 100%{width:40%} }
        @keyframes fadeIn      { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:translateY(0)} }
    </style>
</head>
<body>
    <div class="container">
        <div class="electro-scene">
            <!-- TV con engranajes -->
            <div class="tv">
                <div class="screen">
                    <div class="gears">
                        <div class="gear gear1">⚙</div>
                        <div class="gear gear2">⚙</div>
                        <div class="gear gear3">⚙</div>
                    </div>
                </div>
            </div>

            <!-- Nueva animación "En Proceso" -->
            <div class="process">
                <div class="process-title">EN PROCESO</div>
                <div class="loading-circle"></div>
                <div class="progress-bar">
                    <div class="progress"></div>
                </div>
            </div>

            <!-- Chart -->
            <div class="chart">
                <div class="bar bar1"></div>
                <div class="bar bar2"></div>
                <div class="bar bar3"></div>
                <div class="bar bar4"></div>
            </div>

            <!-- Documento -->
            <div class="doc">
                <div class="doc-line red"></div>
                <div class="doc-line"></div>
                <div class="doc-line short"></div>
                <div class="doc-line red"></div>
                <div class="doc-line short"></div>
                <div class="doc-line"></div>
            </div>
        </div>

        <h2>Reporte en Desarrollo</h2>
        <p>Este reporte aún no está disponible.<br>Estamos trabajando en ello, pronto lo tendrás.</p>
    </div>
</body>
</html>""", 404

@app.route("/actualizar_url", methods=["POST"])
@login_required
def actualizar_url():

    modulo = request.form.get("modulo")
    url = request.form.get("url")

    if not modulo or not url:
        return jsonify({
            "status": "error",
            "message": "⚠️ Debes enviar el módulo y la URL."
        }), 400

    if modulo not in modulos:
        return jsonify({
            "status": "error",
            "message": f"❌ El módulo '{modulo}' no existe."
        }), 404

    modulos[modulo]["url"] = url

    return jsonify({
        "status": "success",
        "message": "✅ URL actualizada correctamente.",
        "modulo": modulo
    }), 200

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8080)
