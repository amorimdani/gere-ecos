#!/usr/bin/env python
"""Teste MINIMALISTA - Gera vídeo de verdade (sem agentes complexos)"""

import sys
from pathlib import Path
import numpy as np
from datetime import datetime
import moviepy.editor as mpy
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import Config

print("\n" + "="*70)
print("🎬 TESTE MINIMALISTA - Gerando Vídeo MP4 de Verdade")
print("="*70)

config = Config()
print(f"\n✅ Config carregada")

# Timestamp único
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = Path(config.output_dir) / f"video_minimalista_{timestamp}.mp4"
Path(config.output_dir).mkdir(exist_ok=True)

print(f"\n🖼️  STEP 1: Criando 5 imagens...")

# Criar 5 imagens simples
image_files = []
for i in range(5):
    print(f"   • Criando imagem {i+1}/5...")
    
    # Criar imagem com gradiente
    img = Image.new('RGB', (1280, 720))
    pixels = img.load()
    
    # Gradiente simples
    for y in range(720):
        for x in range(1280):
            r = int(50 + (x / 1280) * 100 + (i * 20))
            g = int(100 + (y / 720) * 100)
            b = int(150 - (x / 1280) * 50)
            pixels[x, y] = (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))
    
    # Adicionar texto
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 72)
    except:
        font = ImageFont.load_default()
    
    text = f"Frame {i+1}"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    x = (1280 - text_width) // 2
    draw.text((x, 300), text, fill=(255, 255, 255), font=font)
    
    # Salvar
    img_path = Path(config.data_dir) / f"frame_{i:02d}.png"
    Path(config.data_dir).mkdir(exist_ok=True)
    img.save(img_path)
    image_files.append(str(img_path))
    print(f"      ✅ Salvo: {img_path.name}")

print(f"\n✅ {len(image_files)} imagens criadas")

print(f"\n🎞️  STEP 2: Montando vídeo com moviepy...")

# Criar clips de cada imagem (3 segundos cada)
clips = []
for i, img_path in enumerate(image_files):
    print(f"   • Carregando imagem {i+1}/5...")
    clip = mpy.ImageClip(img_path).set_duration(3)
    clips.append(clip)

print(f"\n   • Concatenando {len(clips)} clips...")
video = mpy.concatenate_videoclips(clips)

print(f"\n💾 Salvando vídeo (espera um pouco...)...")
print(f"   Arquivo: {output_file.name}")

try:
    video.write_videofile(
        str(output_file),
        fps=24,
        codec='libx264',
        audio_codec='aac',
        verbose=False,
        logger=None
    )
    
    video.close()
    
    # Resultado
    size_mb = output_file.stat().st_size / 1024 / 1024
    print(f"\n" + "="*70)
    print("✅✅✅ SUCESSO! VÍDEO GERADO COM SUCESSO!")
    print("="*70)
    print(f"   📁 Arquivo: {output_file.name}")
    print(f"   📊 Tamanho: {size_mb:.2f} MB")
    print(f"   ⏱️  Duração: 15 segundos (5 frames x 3s)")
    print(f"   🎬 Qualidade: 1280x720 @ 24fps")
    print("="*70 + "\n")
    
except Exception as e:
    print(f"\n❌ Erro ao salvar: {e}")
    import traceback
    traceback.print_exc()
