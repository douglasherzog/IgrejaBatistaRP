import os
from PIL import Image

LOGO_PATH = "static/img/logo.png"
ICONS_DIR = "static/img/icons"
BG_COLOR = (139, 26, 26)  # #8B1A1A
SIZES = [16, 32, 180, 192, 512]

def gerar_icones():
    os.makedirs(ICONS_DIR, exist_ok=True)
    logo = Image.open(LOGO_PATH).convert("RGBA")
    lw, lh = logo.size
    max_dim = max(lw, lh)

    for size in SIZES:
        # Cria fundo quadrado na cor primaria
        bg = Image.new("RGBA", (size, size), BG_COLOR + (255,))
        # Redimensiona logo mantendo proporcao para caber dentro do quadrado
        scale = min(size * 0.85 / lw, size * 0.85 / lh)
        new_w = int(lw * scale)
        new_h = int(lh * scale)
        resized = logo.resize((new_w, new_h), Image.LANCZOS)
        x = (size - new_w) // 2
        y = (size - new_h) // 2
        bg.paste(resized, (x, y), resized)
        # Converte para RGB para reduzir tamanho
        rgb = Image.new("RGB", (size, size), BG_COLOR)
        rgb.paste(bg, mask=bg.split()[3])
        rgb.save(os.path.join(ICONS_DIR, f"icon-{size}x{size}.png"), "PNG")
        print(f"Gerado: icon-{size}x{size}.png")

if __name__ == "__main__":
    gerar_icones()
