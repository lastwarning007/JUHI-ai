import os
import time
import random
import hashlib
import base64
import requests
import urllib3
from flask import Flask, request, jsonify, render_template_string, Response

urllib3.disable_warnings()

app = Flask(__name__)

# ---------- Helper functions (unchanged) ----------
def _h(s):
    return hashlib.sha256(s.encode()).hexdigest()[:16]

def _c(p):
    return base64.b64encode(p.encode()).decode()

def _gt():
    headers = {
        'Content-Type': 'application/json',
        'X-Android-Package': 'com.photoroom.app',
        'X-Android-Cert': '0424A4898A4B33940D8BF16E44251B876E97F8D0',
        'Accept-Language': 'en-US',
        'X-Client-Version': 'Android/Fallback/X23002000/FirebaseCore-Android',
        'X-Firebase-GMPID': '1:456289768976:android:30c90b24b80bc2d1bfdc95',
        'X-Firebase-Client': 'H4sIAAAAAAAAAKtWykhNLCpJSk0sKVayio7VUSpLLSrOzM9TslIyUqoFAFyivEQfAAAA',
        'X-Firebase-AppCheck': 'eyJlcnJvciI6IlVOS05PV05fRVJST1IifQ==',
        'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 12)',
        'Host': 'www.googleapis.com'
    }
    params = {'key': 'AIzaSyAJGrgbFGB_-h8V2oJLr4b-_ipetqM0duU'}
    payload = {'clientType': 'CLIENT_TYPE_ANDROID'}
    r = requests.post('https://www.googleapis.com/identitytoolkit/v3/relyingparty/signupNewUser',
                      headers=headers, params=params, json=payload)
    return r.json()["idToken"]

ANGLES = ["frnt_vw", "sd_vw", "bck_vw", "tp_vw", "btm_vw", "prspctv", "wd_ang", "mcr_sh", "aerl",
          "fsh_lns", "tlt_shft", "dth_ang", "ovrhd", "ye_lvl", "brd_ye", "wrm_ye"]
LIGHTS = ["gldn_hr", "nn_ngh", "std_soft", "drm_shdw", "vlmtrc_fg", "rm_lght", "cnmtc_amb", "bl_md",
          "wrm_snst", "cld_wntr", "snrse", "mnlght", "cndl_lght", "flsh_ph", "rng_lght", "b_lmnsnt",
          "lsr_lght", "fr_lght", "twlght", "mdngh", "ovrcst", "hrsh_sn", "bcklght", "sllht"]
MOODS = ["epc", "clm", "mystr", "rmntc", "drk_hrr", "drmy", "ftrsc", "vntg_rtr", "grng", "mnmlst",
         "lxry", "brtlst", "chc", "pcfl", "mlnchlc", "jyfl", "hpfl", "dsp", "agrsv", "plyfl", "elgnt",
         "rw", "ethrl", "scr", "mjstc", "ntmt"]
FILTERS = ["kdk_prtr", "fj_prv", "lfrd_bw", "cnstl_800", "plrd_nst", "lmchrm", "gf_vst", "hssbl_nat",
           "lc_m10", "zs_dstgn", "vntg_1970", "nstgrm", "vsc_c1", "snpsd_drm", "lgrm_cnm", "dn_tbl_fm",
           "anlg_stl", "rdsc", "nfrrd", "crss_prc", "blch_bps"]
CAMERAS = ["sony_a7riv", "canon_r5", "nikon_z9", "fujifilm_gfx100", "hasselblad_h6d", "leica_m11",
           "iphone_15_pro", "google_pixel_8", "samsung_s24_ultra", "xiaomi_14_ultra", "oneplus_12",
           "vivo_x100", "huawei_p60", "oppo_find_x7", "realme_gt5", "pixel_fold", "iphone_16_pro"]
ARTISTS = ["picasso", "vangogh", "monet", "rembrandt", "da_vinci", "michelangelo", "dali", "kandinsky",
           "klimt", "hopper", "vermeer", "caravaggio", "botticelli", "raphael", "goya", "munch", "magritte",
           "frida_kahlo", "banksy", "warhol", "haring", "basquiat", "pollock", "rothko", "mondrian", "malevich",
           "cezanne", "degas", "renoir", "seurat", "toulouse", "gauguin", "modigliani", "chagall", "marc",
           "klee", "schiele", "friedrich", "turner", "constable", "hokusai", "hiroshige", "utamaro", "eisen", "sharaku"]

ASPECT_MAP = {
    "1:1": "SQUARE_HD", "4:5": "PORTRAIT_4_3", "16:9": "LANDSCAPE_16_9", "9:16": "PORTRAIT_16_9",
    "4:3": "LANDSCAPE_4_3", "3:4": "PORTRAIT_4_3", "2:1": "LANDSCAPE_16_9", "21:9": "LANDSCAPE_16_9",
    "32:9": "LANDSCAPE_16_9", "5:4": "LANDSCAPE_4_3"
}

STYLES = [
    ("anime", "🎌 Anime"), ("realistic", "📸 Realistic"), ("oil_painting", "🖼 Oil Painting"),
    ("watercolor", "💧 Watercolor"), ("sketch", "✏️ Sketch"), ("pixel", "📟 Pixel"),
    ("3d_render", "🎮 3D Render"), ("cyberpunk", "🤖 Cyberpunk"), ("steampunk", "⚙️ Steampunk"),
    ("fantasy", "🐉 Fantasy"), ("gothic", "🦇 Gothic"), ("cartoon", "📺 Cartoon"),
    ("comic", "💥 Comic"), ("glitch", "📺 Glitch"), ("vaporwave", "🌴 Vaporwave")
]
ASPECTS = [("1:1", "Square"), ("4:5", "Portrait"), ("16:9", "Cinema"), ("9:16", "Story"),
           ("4:3", "Classic"), ("3:4", "Vertical"), ("2:1", "Panorama"), ("21:9", "Wide"),
           ("32:9", "Super Wide"), ("5:4", "Photo")]

def _enh(prompt, style_id):
    angle = random.choice(ANGLES).replace("_", " ")
    light = random.choice(LIGHTS).replace("_", " ")
    mood = random.choice(MOODS).replace("_", " ")
    film = random.choice(FILTERS).replace("_", " ")
    camera = random.choice(CAMERAS).replace("_", " ")
    is_art = style_id in ["oil_painting", "impressionist", "surrealist", "cubist", "expressionist",
                          "renaissance", "baroque", "watercolor", "sketch", "mandala", "calligraphy"]
    artist = random.choice(ARTISTS) if is_art else ""
    artist_txt = f" style of {artist}" if artist else ""
    quality = random.choice([8, 12, 16, 24, 32, 48, 64])
    return (f"{prompt}, {angle} view, {light} lighting, {mood} atmosphere, {film} film, "
            f"{camera} camera{artist_txt}, ultra hd {quality}k, masterpiece, award winning, "
            "trending on artstation, behance featured, cgsociety, highres, extremely detailed, "
            "professional, national geographic")

def _gen(prompt, style_id, aspect):
    size = ASPECT_MAP.get(aspect, "SQUARE_HD")
    token = _gt()
    request_id = _h(f"{time.time()}{random.random()}{prompt[:10]}")
    headers = {
        'Host': 'serverless-api.photoroom.com',
        'Accept': 'text/event-stream',
        'Authorization': token,
        'Content-Type': 'application/json; charset=utf-8',
        'User-Agent': 'okhttp/4.12.0',
        'Pr-App-Version': '2025.47.03 (2180)',
        'Pr-Platform': 'android',
        'X-Request-ID': request_id,
        'X-Enhanced': _c('true')
    }
    payload = {
        "userPrompt": _enh(prompt, style_id),
        "appId": "expert",
        "styleId": style_id,
        "sizeId": size,
        "numberOfImages": 4,
        "cfgScale": 9,
        "steps": 45,
        "sampler": "dpmpp_2m_karras",
        "seed": random.randint(1, 999999999),
        "clip_skip": 2,
        "hires_fix": True,
        "denoising": 0.75,
        "face_restore": True,
        "upscale": 2
    }
    response = requests.post(
        "https://serverless-api.photoroom.com/v2/ai-tools/generate-images",
        headers=headers, json=payload, stream=True, verify=False, timeout=180
    )
    images = []
    no_bg = []
    for line in response.iter_lines():
        if not line:
            continue
        decoded = line.decode(errors='ignore')
        if '"eventType":"aiImageResult"' in decoded:
            start = decoded.find('"imageUrl":"') + 12
            end = decoded.find('"', start)
            if start > 12:
                images.append(decoded[start:end])
        if '"eventType":"aiImageWithoutBackgroundResult"' in decoded:
            start = decoded.find('"imageUrl":"') + 12
            end = decoded.find('"', start)
            if start > 12:
                no_bg.append(decoded[start:end])
    return images, no_bg

# ---------- Flask Web UI with Premium Look ----------
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
    <title>JUHI AI | Premium AI Image Generator</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,300;14..32,400;14..32,500;14..32,600;14..32,700;14..32,800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
        :root {
            --bg-dark: #0a0c14;
            --glass-bg: rgba(18, 20, 32, 0.65);
            --glass-border: rgba(255, 255, 255, 0.08);
            --primary: #8b5cf6;
            --primary-glow: rgba(139, 92, 246, 0.4);
            --secondary: #3b82f6;
            --accent: #ec4899;
            --text: #f1f5f9;
            --text-dim: #94a3b8;
        }
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Inter', sans-serif;
            background: radial-gradient(ellipse at 30% 10%, #111827 0%, #030712 100%);
            color: var(--text);
            line-height: 1.5;
            min-height: 100vh;
        }
        .glass {
            background: var(--glass-bg);
            backdrop-filter: blur(16px);
            border-radius: 2rem;
            border: 1px solid var(--glass-border);
            box-shadow: 0 20px 40px rgba(0,0,0,0.3), 0 0 0 1px rgba(255,255,255,0.02) inset;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .glass:hover {
            box-shadow: 0 25px 45px rgba(0,0,0,0.4);
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 1.5rem 2rem 4rem;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            margin-bottom: 3rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        .logo h1 {
            font-size: 2.3rem;
            font-weight: 800;
            background: linear-gradient(135deg, #fff, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            letter-spacing: -0.02em;
        }
        .logo p {
            font-size: 0.85rem;
            color: var(--text-dim);
        }
        .telegram-round {
            background: rgba(30, 35, 50, 0.8);
            border-radius: 50%;
            width: 48px;
            height: 48px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-decoration: none;
            color: white;
            transition: all 0.2s;
            border: 1px solid rgba(88, 101, 242, 0.5);
            backdrop-filter: blur(4px);
        }
        .telegram-round:hover {
            background: #5865f2;
            transform: scale(1.08) rotate(5deg);
            border-color: transparent;
        }
        .main-grid {
            display: grid;
            grid-template-columns: 1fr 1.2fr;
            gap: 2rem;
        }
        @media (max-width: 900px) {
            .main-grid { grid-template-columns: 1fr; }
            .container { padding: 1rem; }
        }
        .selector-row {
            display: flex;
            gap: 1rem;
            margin-bottom: 1.8rem;
        }
        .selector-btn {
            flex: 1;
            background: linear-gradient(135deg, rgba(30,32,48,0.9), rgba(20,22,38,0.95));
            border: 1px solid rgba(139,92,246,0.3);
            padding: 1rem 0.5rem;
            border-radius: 1.5rem;
            font-size: 1rem;
            font-weight: 600;
            color: white;
            cursor: pointer;
            transition: all 0.2s cubic-bezier(0.2, 0.9, 0.4, 1.1);
            text-align: center;
            backdrop-filter: blur(4px);
        }
        .selector-btn i {
            margin-right: 10px;
            font-size: 1.1rem;
            color: var(--primary);
        }
        .selector-btn:hover {
            background: linear-gradient(135deg, #4c1d95, #6d28d9);
            border-color: transparent;
            transform: translateY(-3px);
            box-shadow: 0 12px 20px -10px rgba(139,92,246,0.5);
        }
        .selected-value {
            font-size: 0.85rem;
            margin-top: 0.5rem;
            padding: 0.5rem;
            background: rgba(0,0,0,0.3);
            border-radius: 1rem;
            text-align: center;
            color: var(--text-dim);
            font-weight: 500;
        }
        .form-group {
            margin-bottom: 1.8rem;
        }
        label {
            display: block;
            font-weight: 500;
            margin-bottom: 0.6rem;
            font-size: 0.9rem;
            color: var(--text-dim);
        }
        textarea {
            width: 100%;
            padding: 1rem 1.2rem;
            background: rgba(0,0,0,0.45);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 1.25rem;
            color: white;
            font-size: 0.95rem;
            font-family: 'Inter', monospace;
            min-height: 120px;
            resize: vertical;
            transition: 0.2s;
        }
        textarea:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px var(--primary-glow);
        }
        .random-prompt {
            background: rgba(139,92,246,0.15);
            border: 1px dashed var(--primary);
            border-radius: 1.2rem;
            padding: 0.75rem;
            text-align: center;
            cursor: pointer;
            margin-bottom: 1rem;
            font-size: 0.85rem;
            transition: 0.2s;
        }
        .random-prompt:hover {
            background: rgba(139,92,246,0.3);
            border-style: solid;
        }
        .generate-btn {
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            border: none;
            font-weight: 700;
            font-size: 1.05rem;
            padding: 1rem;
            width: 100%;
            border-radius: 1.5rem;
            cursor: pointer;
            transition: 0.2s;
            box-shadow: 0 8px 20px rgba(59,130,246,0.3);
            color: white;
        }
        .generate-btn:hover {
            transform: translateY(-2px);
            filter: brightness(1.05);
            box-shadow: 0 12px 25px rgba(139,92,246,0.4);
        }
        .loading {
            display: none;
            text-align: center;
            margin: 1.5rem 0;
        }
        .spinner {
            width: 44px;
            height: 44px;
            border: 3px solid rgba(255,255,255,0.15);
            border-top: 3px solid var(--primary);
            border-radius: 50%;
            animation: spin 0.9s linear infinite;
            margin: 0 auto 0.8rem;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .result-panel {
            padding: 1.8rem;
        }
        .image-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 1.2rem;
            margin-top: 1.5rem;
        }
        .image-card {
            position: relative;
            background: rgba(0,0,0,0.5);
            border-radius: 1.5rem;
            overflow: hidden;
            transition: all 0.25s ease;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .image-card:hover {
            transform: scale(0.98);
            border-color: var(--primary);
            box-shadow: 0 10px 25px -5px rgba(0,0,0,0.5);
        }
        .image-card img {
            width: 100%;
            height: auto;
            aspect-ratio: 1;
            object-fit: cover;
            display: block;
        }
        .download-icon {
            position: absolute;
            top: 12px;
            right: 12px;
            background: rgba(0,0,0,0.65);
            backdrop-filter: blur(6px);
            border-radius: 50%;
            width: 34px;
            height: 34px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            color: white;
            transition: 0.2s;
            opacity: 0.85;
            z-index: 2;
        }
        .download-icon:hover {
            background: var(--primary);
            transform: scale(1.1);
            opacity: 1;
        }
        .no-results {
            text-align: center;
            padding: 3rem;
            color: var(--text-dim);
        }
        .bg-remove-btn {
            margin-top: 1.5rem;
            background: rgba(45, 47, 66, 0.8);
            border: none;
            padding: 0.75rem;
            border-radius: 2rem;
            font-size: 0.85rem;
            width: 100%;
            cursor: pointer;
            font-weight: 500;
            transition: 0.2s;
        }
        .bg-remove-btn:hover {
            background: #3b3f5c;
        }
        .info-text {
            font-size: 0.75rem;
            margin-top: 1rem;
            text-align: center;
            color: var(--text-dim);
        }
        footer {
            text-align: center;
            margin-top: 3rem;
            font-size: 0.7rem;
            opacity: 0.5;
        }
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.85);
            backdrop-filter: blur(8px);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }
        .modal-content {
            background: rgba(18, 20, 32, 0.98);
            backdrop-filter: blur(20px);
            border-radius: 2rem;
            width: 90%;
            max-width: 550px;
            max-height: 80vh;
            overflow-y: auto;
            padding: 1.8rem;
            border: 1px solid rgba(139,92,246,0.3);
            box-shadow: 0 30px 50px rgba(0,0,0,0.5);
            animation: modalFadeIn 0.2s ease-out;
        }
        @keyframes modalFadeIn {
            from { opacity: 0; transform: scale(0.96); }
            to { opacity: 1; transform: scale(1); }
        }
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
            font-size: 1.4rem;
            font-weight: 700;
            background: linear-gradient(135deg, #fff, var(--primary));
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }
        .close-modal {
            cursor: pointer;
            font-size: 2rem;
            line-height: 1;
            color: var(--text-dim);
            transition: 0.1s;
        }
        .close-modal:hover {
            color: white;
        }
        .modal-options {
            display: flex;
            flex-wrap: wrap;
            gap: 0.8rem;
        }
        .modal-option {
            background: rgba(30,32,48,0.7);
            border: 1px solid rgba(255,255,255,0.1);
            padding: 0.7rem 1.2rem;
            border-radius: 2rem;
            cursor: pointer;
            transition: all 0.15s;
            font-size: 0.9rem;
            font-weight: 500;
        }
        .modal-option:hover {
            background: var(--primary);
            transform: translateY(-2px);
            box-shadow: 0 5px 12px rgba(139,92,246,0.4);
            border-color: transparent;
        }
        ::-webkit-scrollbar {
            width: 6px;
        }
        ::-webkit-scrollbar-track {
            background: rgba(0,0,0,0.3);
            border-radius: 10px;
        }
        ::-webkit-scrollbar-thumb {
            background: var(--primary);
            border-radius: 10px;
        }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <div class="logo">
            <h1>JUHI AI ✦</h1>
            <p>premium neural · cinematic intelligence</p>
        </div>
        <a href="https://t.me/hardhacker007" target="_blank" class="telegram-round" aria-label="Telegram">
            <i class="fab fa-telegram-plane fa-lg"></i>
        </a>
    </div>

    <div class="main-grid">
        <div class="glass input-panel" style="padding: 1.8rem;">
            <h2 style="margin-bottom: 1.8rem; font-weight: 600;"><i class="fas fa-sliders-h" style="margin-right: 8px;"></i> Configure</h2>
            <div class="selector-row">
                <div class="selector-btn" id="choose-style-btn">
                    <i class="fas fa-palette"></i> Choose Style
                </div>
                <div class="selector-btn" id="choose-aspect-btn">
                    <i class="fas fa-expand-alt"></i> Choose Aspect
                </div>
            </div>
            <div id="style-display" class="selected-value">🎨 Selected style: Anime</div>
            <div id="aspect-display" class="selected-value">📐 Selected aspect: Square (1:1)</div>

            <div class="form-group" style="margin-top: 1.8rem;">
                <label><i class="fas fa-feather-alt"></i> Prompt</label>
                <div class="random-prompt" id="random-prompt-btn">
                    <i class="fas fa-dice-d6"></i> Random prompt idea
                </div>
                <textarea id="prompt" placeholder="Describe your vision... e.g., a cosmic dragon floating through a nebula, cyberpunk, ethereal lighting"></textarea>
            </div>
            <button class="generate-btn" id="generate-btn"><i class="fas fa-sparkles"></i> Generate Images</button>
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <div style="font-size: 0.85rem;">Crafting your artwork...</div>
            </div>
            <div class="info-text">4 high‑resolution images • AI‑enhanced lighting & composition</div>
        </div>

        <div class="glass result-panel">
            <h2 style="margin-bottom: 1rem; font-weight: 600;"><i class="fas fa-images"></i> Gallery</h2>
            <div id="image-gallery" class="image-grid">
                <div class="no-results">✨ Your generated images will appear here</div>
            </div>
            <button id="remove-bg-btn" class="bg-remove-btn" style="display:none;"><i class="fas fa-eraser"></i> Remove background (if available)</button>
        </div>
    </div>
    <footer>JUHI AI — advanced generative engine • style transfer & ultra HD</footer>
</div>

<div id="style-modal" class="modal">
    <div class="modal-content">
        <div class="modal-header">
            <span><i class="fas fa-palette"></i> Choose Style</span>
            <span class="close-modal" data-modal="style-modal">&times;</span>
        </div>
        <div class="modal-options" id="style-modal-options">
            {% for val, name in styles %}
            <div class="modal-option" data-style="{{ val }}" data-name="{{ name }}">{{ name }}</div>
            {% endfor %}
        </div>
    </div>
</div>

<div id="aspect-modal" class="modal">
    <div class="modal-content">
        <div class="modal-header">
            <span><i class="fas fa-expand-alt"></i> Choose Aspect Ratio</span>
            <span class="close-modal" data-modal="aspect-modal">&times;</span>
        </div>
        <div class="modal-options" id="aspect-modal-options">
            {% for val, name in aspects %}
            <div class="modal-option" data-aspect="{{ val }}" data-name="{{ name }}">{{ name }} ({{ val }})</div>
            {% endfor %}
        </div>
    </div>
</div>

<script>
    let selectedStyle = "anime";
    let selectedStyleName = "🎌 Anime";
    let selectedAspect = "1:1";
    let selectedAspectName = "Square (1:1)";

    const styleDisplay = document.getElementById('style-display');
    const aspectDisplay = document.getElementById('aspect-display');
    const chooseStyleBtn = document.getElementById('choose-style-btn');
    const chooseAspectBtn = document.getElementById('choose-aspect-btn');
    const styleModal = document.getElementById('style-modal');
    const aspectModal = document.getElementById('aspect-modal');
    const closeModals = document.querySelectorAll('.close-modal');

    chooseStyleBtn.onclick = () => styleModal.style.display = 'flex';
    chooseAspectBtn.onclick = () => aspectModal.style.display = 'flex';
    closeModals.forEach(btn => {
        btn.onclick = () => {
            const modalId = btn.getAttribute('data-modal');
            document.getElementById(modalId).style.display = 'none';
        };
    });
    window.onclick = (e) => {
        if (e.target === styleModal) styleModal.style.display = 'none';
        if (e.target === aspectModal) aspectModal.style.display = 'none';
    };

    document.querySelectorAll('#style-modal-options .modal-option').forEach(opt => {
        opt.addEventListener('click', () => {
            selectedStyle = opt.dataset.style;
            selectedStyleName = opt.dataset.name;
            styleDisplay.innerText = `🎨 Selected style: ${selectedStyleName}`;
            styleModal.style.display = 'none';
        });
    });
    document.querySelectorAll('#aspect-modal-options .modal-option').forEach(opt => {
        opt.addEventListener('click', () => {
            selectedAspect = opt.dataset.aspect;
            selectedAspectName = opt.dataset.name;
            aspectDisplay.innerText = `📐 Selected aspect: ${selectedAspectName} (${selectedAspect})`;
            aspectModal.style.display = 'none';
        });
    });

    const randomPrompts = [
        "ethereal forest spirit with glowing antlers", "cyberpunk samurai under neon rain", "golden hour over ancient ruins",
        "steampunk airship floating above clouds", "magical girl surrounded by cosmic butterflies", "dragon perched on futuristic Tokyo tower",
        "ancient Egyptian queen as a hologram", "cosmic whale swimming through nebula", "glass lotus flower floating in space",
        "mecha anime battle scene at sunset", "portrait of a sad android with glowing tears", "bioluminescent deep sea creature"
    ];
    document.getElementById('random-prompt-btn').addEventListener('click', () => {
        const r = randomPrompts[Math.floor(Math.random() * randomPrompts.length)];
        document.getElementById('prompt').value = r;
    });

    let currentImages = [];
    let currentNoBg = [];

    // FIXED: download uses backend proxy
    function downloadImage(url, filename = 'juhi_ai_image.jpg') {
        const proxyUrl = `/download?url=${encodeURIComponent(url)}`;
        window.location.href = proxyUrl;
    }

    function renderImages(urls, isNoBgMode = false) {
        const gallery = document.getElementById('image-gallery');
        if (!urls || urls.length === 0) {
            gallery.innerHTML = '<div class="no-results">⚠️ No images generated. Try again.</div>';
            return;
        }
        let html = '';
        urls.forEach((url, idx) => {
            const filename = `juhi_${Date.now()}_${idx}.jpg`;
            html += `
                <div class="image-card">
                    <div class="download-icon" data-url="${url}" data-filename="${filename}">
                        <i class="fas fa-download"></i>
                    </div>
                    <img src="${url}" alt="AI generated" loading="lazy">
                </div>
            `;
        });
        gallery.innerHTML = html;
        document.querySelectorAll('.download-icon').forEach(icon => {
            icon.addEventListener('click', (e) => {
                e.stopPropagation();
                downloadImage(icon.dataset.url, icon.dataset.filename);
            });
        });
        const removeBtn = document.getElementById('remove-bg-btn');
        if (currentNoBg && currentNoBg.length && !isNoBgMode) {
            removeBtn.style.display = 'block';
            removeBtn.textContent = "🎭 Remove background";
        } else {
            removeBtn.style.display = 'none';
        }
    }

    const generateBtn = document.getElementById('generate-btn');
    const loadingDiv = document.getElementById('loading');
    generateBtn.addEventListener('click', async () => {
        const prompt = document.getElementById('prompt').value.trim();
        if (!prompt) {
            alert("Please enter a prompt or use a random idea.");
            return;
        }
        loadingDiv.style.display = 'block';
        generateBtn.disabled = true;
        const galleryDiv = document.getElementById('image-gallery');
        galleryDiv.innerHTML = '<div class="no-results"><div class="spinner"></div> Generating...</div>';
        try {
            const response = await fetch('/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ style: selectedStyle, aspect: selectedAspect, prompt })
            });
            const data = await response.json();
            if (data.success) {
                currentImages = data.images || [];
                currentNoBg = data.no_bg || [];
                renderImages(currentImages, false);
            } else {
                galleryDiv.innerHTML = `<div class="no-results">❌ Error: ${data.error || 'unknown'}</div>`;
            }
        } catch (err) {
            console.error(err);
            galleryDiv.innerHTML = '<div class="no-results">❌ Network error. Please try again.</div>';
        } finally {
            loadingDiv.style.display = 'none';
            generateBtn.disabled = false;
        }
    });

    const removeBgBtn = document.getElementById('remove-bg-btn');
    let bgToggleState = false;
    removeBgBtn.addEventListener('click', () => {
        if (currentNoBg && currentNoBg.length) {
            if (!bgToggleState) {
                renderImages(currentNoBg, true);
                removeBgBtn.textContent = "🖼 Show original";
                bgToggleState = true;
            } else {
                renderImages(currentImages, false);
                removeBgBtn.textContent = "🎭 Remove background";
                bgToggleState = false;
            }
        } else {
            alert("No background-removed version available for these images.");
        }
    });
</script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, styles=STYLES[:15], aspects=ASPECTS)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    style = data.get('style')
    aspect = data.get('aspect')
    prompt = data.get('prompt')
    if not all([style, aspect, prompt]):
        return jsonify({'success': False, 'error': 'Missing fields'}), 400
    try:
        images, no_bg = _gen(prompt, style, aspect)
        return jsonify({'success': True, 'images': images, 'no_bg': no_bg})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# NEW: Download proxy endpoint
@app.route('/download')
def download_image():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    try:
        # Fetch the image from the external URL
        resp = requests.get(url, stream=True, verify=False, timeout=30)
        # Return as attachment
        return Response(
            resp.iter_content(chunk_size=8192),
            headers={
                'Content-Disposition': 'attachment; filename="juhi_ai_image.jpg"',
                'Content-Type': resp.headers.get('Content-Type', 'image/jpeg')
            }
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
