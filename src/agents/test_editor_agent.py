"""
Teste do Editor Agent - Integração completa: Conteúdo → Áudio → Visual → Vídeo Editado
Execute: python src/agents/test_editor_agent.py
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.editor_agent import create_editor_agent, KenBurnsEffect
from agents.content_agent import create_content_agent
from agents.audio_agent import create_audio_agent
from agents.visual_agent import create_visual_agent
from config import Config
from config.logger import get_logger

logger = get_logger(__name__)


async def test_ken_burns_effect():
    """Testa efeito Ken Burns em isolamento"""
    
    print("\n" + "="*80)
    print("🎬 TESTE 1: Ken Burns Effect")
    print("="*80 + "\n")
    
    print("Configurações do Ken Burns:")
    print("  • Duration: 10.0 segundos")
    print("  • Zoom Factor: 1.3x (30% de zoom)")
    print("  • FPS: 30")
    print("  • Frames: 300")
    print("\n✅ Ken Burns Effect está pronto para uso\n")
    
    # Demonstra cálculo de crop region
    kb = KenBurnsEffect(duration=10.0, zoom_factor=1.3)
    
    print("Exemplos de crop regions em diferentes frames:")
    frames_to_test = [0, 75, 150, 225, 299]  # 0%, 25%, 50%, 75%, 100%
    
    for frame_num in frames_to_test:
        x1, y1, x2, y2 = kb.calculate_crop_region(
            frame_num, 300, 1920, 1080
        )
        width = x2 - x1
        height = y2 - y1
        progress = (frame_num / 299) * 100
        print(f"  Frame {frame_num:3d} ({progress:5.1f}%): "
              f"Crop ({width}x{height}) at ({x1}, {y1})")


async def test_editor_with_pipeline():
    """Testa pipeline completo: Conteúdo → Áudio → Visual → Vídeo"""
    
    print("\n" + "="*80)
    print("🎬 TESTE 2: Pipeline Completo (Content → Audio → Visual → Video)")
    print("="*80 + "\n")
    
    config = Config()
    
    # STAGE 1: Content
    print("📝 STAGE 1: Gerando conteúdo...")
    print("-" * 80)
    
    content_agent = create_content_agent()
    content_result = await content_agent.run({"theme": "estoicismo"})
    
    if not content_result["success"]:
        print(f"❌ Erro: {content_result.get('error')}")
        return
    
    content = content_result["data"]
    print(f"✅ Conteúdo gerado: {content['title']}")
    print(f"   Cenas: {len(content['scenes'])}")
    print(f"   Duração: {content['metadata']['estimated_duration_minutes']:.1f} min\n")
    
    # STAGE 2: Audio
    print("🎙️  STAGE 2: Gerando áudio...")
    print("-" * 80)
    
    audio_agent = create_audio_agent()
    audio_result = await audio_agent.run({
        "script": content["script"],
        "video_title": content["title"],
        "expected_duration_minutes": int(content["metadata"]["estimated_duration_minutes"])
    })
    
    if not audio_result["success"]:
        print(f"❌ Erro: {audio_result.get('error')}")
        return
    
    audio = audio_result["data"]
    print(f"✅ Áudio gerado: {Path(audio['output_filename']).name}")
    print(f"   Duração: {audio['actual_duration_seconds']:.1f}s\n")
    
    # STAGE 3: Visual
    print("🖼️  STAGE 3: Gerando imagens...")
    print("-" * 80)
    
    visual_agent = create_visual_agent()
    visual_result = await visual_agent.run({
        "scenes": content["scenes"],
        "theme": content["theme"],
        "use_cache": True
    })
    
    if not visual_result["success"]:
        print(f"❌ Erro: {visual_result.get('error')}")
        return
    
    visual = visual_result["data"]
    stats = visual["statistics"]
    print(f"✅ Imagens geradas: {stats['total_generated']}")
    print(f"   Do cache: {stats['total_cached']}")
    print(f"   Tamanho: {stats['total_size_mb']:.2f} MB\n")
    
    # STAGE 4: Editor
    print("🎬 STAGE 4: Editando vídeo com Ken Burns...")
    print("-" * 80)
    
    editor_agent = create_editor_agent()
    
    editor_result = await editor_agent.run({
        "audio_path": audio["output_filename"],
        "scenes": visual["scenes"],
        "video_title": content["title"],
        "theme": content["theme"],
        "use_ken_burns": True,
        "add_transitions": True
    })
    
    if editor_result["success"]:
        video_data = editor_result["data"]
        
        print(f"✅ Vídeo renderizado com sucesso!")
        print(f"\n   📁 Arquivo: {Path(video_data['output_filename']).name}")
        print(f"   📊 Resolução: {video_data['resolution']}")
        print(f"   ⏱️  Duração: {video_data['duration_seconds']:.1f}s")
        print(f"   📹 FPS: {video_data['fps']}")
        print(f"   💾 Tamanho: {video_data['file_size_mb']:.2f} MB")
        print(f"   🎨 Tema: {video_data['theme']}")
        
        print("\n" + "="*80)
        print("✅✅✅ PIPELINE COMPLETO CONCLUÍDO!")
        print("="*80)
        
        return video_data
    else:
        print(f"❌ Erro na edição: {editor_result.get('error')}")


async def test_editor_quick():
    """Teste rápido do Editor com imagens de teste"""
    
    print("\n" + "="*80)
    print("🎬 TESTE 3: Editor Quick (sem pipeline completo)")
    print("="*80 + "\n")
    
    config = Config()
    
    # Cria imagem de teste simples
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np
    
    test_image_path = Path(config.output_dir) / "test_image.png"
    
    # Cria imagem com texto
    img = Image.new('RGB', (1920, 1080), color=(30, 30, 60))  # Azul escuro
    draw = ImageDraw.Draw(img)
    
    # Desenha gradiente (simula fundo)
    for y in range(1080):
        r = int(30 + (y / 1080) * 50)
        g = int(30 + (y / 1080) * 70)
        b = int(60 + (y / 1080) * 100)
        draw.line([(0, y), (1920, y)], fill=(r, g, b))
    
    # Adiciona texto
    draw.text((960, 540), "Test Frame", fill=(255, 255, 255), anchor="mm")
    
    img.save(test_image_path)
    print(f"✅ Imagem de teste criada: {test_image_path.name}\n")
    
    # Se houver áudio do teste anterior, usar
    audio_files = list(Path(config.output_dir).glob("audio_*.mp3"))
    
    if audio_files:
        audio_path = str(audio_files[0])
        print(f"Usando áudio existente: {Path(audio_path).name}\n")
        
        # Cria scenes para teste
        test_scenes = [
            {
                "scene_number": 1,
                "image_path": str(test_image_path),
                "visual_prompt": "Test Scene 1"
            },
            {
                "scene_number": 2,
                "image_path": str(test_image_path),
                "visual_prompt": "Test Scene 2"
            },
            {
                "scene_number": 3,
                "image_path": str(test_image_path),
                "visual_prompt": "Test Scene 3"
            }
        ]
        
        editor_agent = create_editor_agent()
        result = await editor_agent.run({
            "audio_path": audio_path,
            "scenes": test_scenes,
            "video_title": "Test Video",
            "theme": "test",
            "use_ken_burns": True,
            "add_transitions": True
        })
        
        if result["success"]:
            video_data = result["data"]
            print(f"\n✅ Vídeo de teste gerado!")
            print(f"   Arquivo: {Path(video_data['output_filename']).name}")
            print(f"   Tamanho: {video_data['file_size_mb']:.2f} MB")
        else:
            print(f"❌ Erro: {result.get('error')}")
    else:
        print("⚠️  Nenhum áudio de teste encontrado")
        print("   Execute test_pipeline_v2.py primeiro\n")


if __name__ == "__main__":
    print("\n🚀 Iniciando testes do Editor Agent...\n")
    
    try:
        # Teste 1: Ken Burns
        asyncio.run(test_ken_burns_effect())
        
        # Teste 2: Pipeline completo
        print("\nDeseja testar o pipeline completo? (Content → Audio → Visual → Video)")
        print("Aviso: Isso pode levar alguns minutos...")
        
        resp = input("\nProsseguir? (s/n): ").lower()
        if resp == 's':
            asyncio.run(test_editor_with_pipeline())
        else:
            print("Pulando pipeline completo\n")
            
            # Teste 3: Quick test
            print("Executando teste rápido com imagem de teste...")
            asyncio.run(test_editor_quick())
        
    except KeyboardInterrupt:
        print("\n\n⏸️  Testes interrompidos pelo usuário")
    except Exception as e:
        logger.error(f"Erro: {e}", exc_info=True)
        print(f"\n❌ Erro: {e}")
