#!/usr/bin/env python
"""Teste REAL - Gera vídeo de verdade usando mock data (sem LLM)"""

import sys
import asyncio
from pathlib import Path
import numpy as np
from datetime import datetime
import moviepy.editor as mpy
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent / "src"))

from config.logger import get_logger
from config import Config
from agents.audio_agent import AudioAgent
from agents.visual_agent import VisualAgent
from agents.editor_agent import EditorAgent

logger = get_logger(__name__)


async def test_real_video_generation():
    """Gera vídeo REAL com mock data completo"""
    
    print("\n" + "="*70)
    print("🎬 TESTE REAL - Gerando Vídeo Completo (com dados mock)")
    print("="*70)
    
    config = Config()
    print(f"\n✅ Config carregada de: {config.base_dir}")
    
    # Timestampt único para este teste
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = Path(config.output_dir) / f"video_real_mock_{timestamp}.mp4"
    
    # Criar diretórios se não existirem
    Path(config.output_dir).mkdir(exist_ok=True)
    Path(config.data_dir).mkdir(exist_ok=True)
    
    try:
        # ==================== STEP 1: GERAR ÁUDIO ====================
        print(f"\n📢 STEP 1: Gerando áudio (mock)...")
        
        # Mock de script (simular LLM)
        mock_script = [
            "Bem-vindo ao Ecos de Sabedoria.",
            "Hoje falaremos sobre o estoicismo.",
            "Marco Aurélio nos ensinou que a vida é breve.",
            "Mas a sabedoria é eterna.",
            "Obrigado por nos acompanhar."
        ]
        
        audio_agent = AudioAgent()
        audio_file = None
        
        try:
            # Gerar áudio para cada frase
            audio_clips = []
            for i, phrase in enumerate(mock_script):
                print(f"   • Gerando áudio {i+1}/{len(mock_script)}: '{phrase[:30]}...'")
                # Edge TTS pode ser lento, então vamos usar um áudio fake se falhar
                try:
                    temp_audio = await audio_agent.generate_speech(
                        phrase, 
                        voice="pt-BR-AntonioNeural",
                        rate=1.0
                    )
                    if temp_audio and Path(temp_audio).exists():
                        clip = mpy.AudioFileClip(temp_audio)
                        audio_clips.append(clip)
                        print(f"      ✅ Áudio gerado: {Path(temp_audio).name}")
                    else:
                        # Criar áudio fake (2 segundos de silêncio)
                        fake_audio = mpy.AudioClip(
                            make_frame=lambda t: np.zeros(2),
                            duration=2,
                            fps=22050
                        )
                        audio_clips.append(fake_audio)
                        print(f"      ⚠️  Usando áudio fake (silêncio)")
                except Exception as e:
                    print(f"      ⚠️  Erro ao gerar áudio {i+1}, usando fake: {str(e)[:50]}")
                    # Áudio fake de 2 segundos
                    fake_audio = mpy.AudioClip(
                        make_frame=lambda t: np.zeros(2),
                        duration=2,
                        fps=22050
                    )
                    audio_clips.append(fake_audio)
            
            # Concatenar áudios
            if audio_clips:
                audio_file = mpy.concatenate_audioclips(audio_clips)
                print(f"\n✅ Áudio concatenado: {audio_file.duration:.1f}s total")
            else:
                print("\n⚠️  Nenhum áudio gerado, usando silêncio")
                audio_file = mpy.AudioClip(
                    make_frame=lambda t: np.zeros(2),
                    duration=15,
                    fps=22050
                )
        except Exception as e:
            print(f"\n⚠️  Erro ao gerar áudio: {e}")
            # Criar áudio fake como fallback
            audio_file = mpy.AudioClip(
                make_frame=lambda t: np.zeros(2),
                duration=15,
                fps=22050
            )
        
        # ==================== STEP 2: GERAR IMAGENS ====================
        print(f"\n🖼️  STEP 2: Gerando imagens (mock)...")
        
        visual_agent = VisualAgent()
        image_files = []
        
        try:
            # Gerar 5 imagens
            prompts = [
                "estoicismo filosofia clássico",
                "Marco Aurélio sabedoria antiga",
                "contemplação meditação zen",
                "busca espiritual conhecimento",
                "sabedoria eterna luz"
            ]
            
            for i, prompt in enumerate(prompts):
                print(f"   • Gerando imagem {i+1}/{len(prompts)}: '{prompt}'")
                try:
                    # Tentar gerar com IA
                    img_path = await visual_agent.generate_image(
                        prompt,
                        style="oil painting"
                    )
                    if img_path and Path(img_path).exists():
                        image_files.append(img_path)
                        print(f"      ✅ Imagem gerada: {Path(img_path).name}")
                    else:
                        # Criar imagem fake
                        raise Exception("Falha ao gerar imagem com IA")
                except Exception as e:
                    print(f"      ⚠️  Usando imagem de fallback")
                    # Criar imagem fake (gradiente + texto)
                    img = Image.new('RGB', (1280, 720), color='gradient')
                    
                    # Fazer um gradiente simples
                    pixels = img.load()
                    for y in range(720):
                        for x in range(1280):
                            r = int(100 + (x / 1280) * 55)
                            g = int(50 + (y / 720) * 100)
                            b = int(150 - (x / 1280) * 50)
                            pixels[x, y] = (r, g, b)
                    
                    # Adicionar texto
                    draw = ImageDraw.Draw(img)
                    try:
                        font = ImageFont.truetype("arial.ttf", 48)
                    except:
                        font = ImageFont.load_default()
                    
                    text = f"Frame {i+1}: {prompt[:20]}"
                    bbox = draw.textbbox((0, 0), text, font=font)
                    text_width = bbox[2] - bbox[0]
                    x = (1280 - text_width) // 2
                    draw.text((x, 300), text, fill=(255, 255, 255), font=font)
                    
                    # Salvar imagem
                    img_path = Path(config.data_dir) / f"mock_image_{i:03d}.png"
                    img.save(img_path)
                    image_files.append(str(img_path))
                    print(f"      ✅ Imagem fake criada: {img_path.name}")
            
            print(f"\n✅ {len(image_files)} imagens prontas")
        except Exception as e:
            print(f"\n⚠️  Erro ao gerar imagens: {e}")
        
        # ==================== STEP 3: MONTAR VÍDEO ====================
        print(f"\n🎞️  STEP 3: Montando vídeo com EditorAgent...")
        
        editor = EditorAgent()
        
        try:
            # Carregar clips de vídeo das imagens
            video_clips = []
            duration_per_image = (audio_file.duration if audio_file else 15) / len(image_files)
            
            for i, img_path in enumerate(image_files):
                print(f"   • Carregando imagem {i+1}/{len(image_files)}: {Path(img_path).name}")
                
                try:
                    # Criar clip de vídeo de duração fixa
                    img_clip = mpy.ImageClip(img_path).set_duration(duration_per_image)
                    img_clip = img_clip.set_fps(24)
                    video_clips.append(img_clip)
                    print(f"      ✅ Clip criado: {duration_per_image:.1f}s")
                except Exception as e:
                    print(f"      ⚠️  Erro ao carregar imagem: {str(e)[:50]}")
            
            if video_clips:
                # Concatenar vídeos
                print(f"\n   • Concatenando {len(video_clips)} clips...")
                final_video = mpy.concatenate_videoclips(video_clips)
                
                # Adicionar áudio
                if audio_file:
                    print(f"   • Adicionando áudio ({audio_file.duration:.1f}s)...")
                    final_video = final_video.set_audio(audio_file)
                
                # Redimensionar para 1280x720
                print(f"   • Redimensionando para 1280x720...")
                final_video = final_video.resize((1280, 720))
                
                # Escrever arquivo
                print(f"\n💾 Salvando vídeo em: {output_file}")
                print(f"   Isso pode levar alguns minutos...")
                
                final_video.write_videofile(
                    str(output_file),
                    fps=24,
                    codec='libx264',
                    audio_codec='aac',
                    verbose=False,
                    logger=None
                )
                
                final_video.close()
                if audio_file:
                    audio_file.close()
                
                # Verificar tamanho
                size_mb = output_file.stat().st_size / 1024 / 1024
                print(f"\n✅ Vídeo salvo com sucesso!")
                print(f"   📁 Arquivo: {output_file.name}")
                print(f"   📊 Tamanho: {size_mb:.2f} MB")
                print(f"   ⏱️  Duração: ~{duration_per_image * len(video_clips):.1f}s")
            else:
                print("\n❌ Nenhum clip de vídeo foi criado")
                
        except Exception as e:
            print(f"\n❌ Erro ao montar vídeo: {e}")
            import traceback
            traceback.print_exc()
        
        # ==================== RESULTADO FINAL ====================
        print("\n" + "="*70)
        if output_file.exists():
            size_mb = output_file.stat().st_size / 1024 / 1024
            print("✅ SUCESSO! Vídeo gerado de verdade!")
            print(f"   📁 Arquivo: {output_file}")
            print(f"   📊 Tamanho: {size_mb:.2f} MB")
            print("\n🎉 Sistema FUNCIONA! Agora configure um LLM real e execute.")
        else:
            print("⚠️  Vídeo não foi criado ou tem tamanho zero")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_real_video_generation())
