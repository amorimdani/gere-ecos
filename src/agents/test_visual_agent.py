"""
Teste do Visual Agent - Demonstra uso do sistema de geração de imagens
Execute: python src/agents/test_visual_agent.py
"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.visual_agent import create_visual_agent
from agents.content_agent import create_content_agent
from config import Config
from config.logger import get_logger

logger = get_logger(__name__)


async def test_visual_generation():
    """Testa a geração de imagens para cenas"""
    
    print("\n" + "="*80)
    print("🖼️  TESTE DO VISUAL AGENT - Fábrica de Vídeos Autônoma")
    print("="*80 + "\n")
    
    config = Config()
    
    # Teste 1: Gera conteúdo + cenas + imagens
    print("📝 Teste 1: Gerando conteúdo + imagens para 5 cenas...\n")
    print("-" * 80)
    
    # Cria conteúdo
    content_agent = create_content_agent()
    content_result = await content_agent.run({"theme": "estoicismo"})
    
    if not content_result["success"]:
        print(f"❌ Erro ao gerar conteúdo: {content_result.get('error')}")
        return
    
    content = content_result["data"]
    print(f"✅ Conteúdo gerado: {content['title']}")
    print(f"   Cenas: {len(content['scenes'])}")
    print(f"   Tema: {content['theme']}\n")
    
    # Gera imagens
    print("🖼️  Gerando imagens para cada cena...")
    visual_agent = create_visual_agent()
    
    payload = {
        "scenes": content["scenes"],
        "theme": content["theme"],
        "use_cache": True
    }
    
    visual_result = await visual_agent.run(payload)
    
    if visual_result["success"]:
        visual_data = visual_result["data"]
        stats = visual_data["statistics"]
        
        print(f"\n✅ Imagens geradas com sucesso!")
        print(f"\n   Estatísticas:")
        print(f"   • Total de cenas: {stats['total_scenes']}")
        print(f"   • Imagens geradas: {stats['total_generated']}")
        print(f"   • Do cache: {stats['total_cached']}")
        print(f"   • Falhas: {stats['total_failed']}")
        print(f"   • Tamanho total: {stats['total_size_mb']:.2f} MB")
        print(f"   • Taxa de sucesso: {stats['success_rate']}")
        
        # Mostra detalhes de cada imagem
        print(f"\n   Detalhes das imagens:")
        for i, scene in enumerate(visual_data["scenes"], 1):
            if scene.get("image_generated"):
                cache_status = "📦 CACHE" if scene.get("image_from_cache") else "🆕 NEW"
                print(f"   [{i}] {cache_status} {scene.get('image_filename', 'N/A')}")
                print(f"       → {scene.get('image_provider', 'N/A')}")
                print(f"       → {scene.get('image_size_mb', 0):.2f} MB")
            else:
                print(f"   [{i}] ❌ {scene.get('image_error', 'Erro desconhecido')}")
        
        # Cache stats
        cache_stats = visual_data["cache_stats"]
        print(f"\n   Cache Stats:")
        print(f"   • Imagens em cache: {cache_stats['cached_images']}")
        print(f"   • Tamanho do cache: {cache_stats['total_size_mb']:.2f} MB")
        
    else:
        print(f"❌ Erro ao gerar imagens: {visual_result.get('error')}")
        return
    
    # Teste 2: Teste de cache (mesmas cenas devem vir do cache)
    print("\n" + "="*80)
    print("\n📝 Teste 2: Testando cache (processando mesmas cenas novamente)...\n")
    print("-" * 80)
    
    print("🖼️  Regenerando imagens (devem vir do cache)...")
    
    visual_result2 = await visual_agent.run(payload)
    
    if visual_result2["success"]:
        visual_data2 = visual_result2["data"]
        stats2 = visual_data2["statistics"]
        
        cached_from_second_run = sum(
            1 for scene in visual_data2["scenes"] 
            if scene.get("image_from_cache", False)
        )
        
        print(f"\n✅ Teste de cache concluído!")
        print(f"   • Imagens do cache: {cached_from_second_run}/{stats2['total_scenes']}")
        print(f"   • Esperado: {stats2['total_scenes']} (todas do cache)")
        
        if cached_from_second_run == stats2['total_scenes']:
            print(f"   ✅ CACHE FUNCIONANDO PERFEITAMENTE!")
        else:
            print(f"   ⚠️  Nem todas vieram do cache")
    
    print("\n" + "="*80)
    print("✅ Testes concluídos!")
    print("="*80 + "\n")


async def test_with_available_providers():
    """Testa quais provedores estão disponíveis"""
    
    print("\n🔍 Verificando provedores de imagem disponíveis...")
    print("-" * 80)
    
    visual_agent = create_visual_agent()
    providers = visual_agent.image_manager.get_available_providers()
    
    if providers:
        print(f"✅ Provedores disponíveis: {', '.join(providers)}")
        print("\n   Prioridade de uso:")
        for i, provider in enumerate(providers, 1):
            status = "PRIMARY" if i == 1 else "FALLBACK"
            print(f"   {i}. {provider:25} ({status})")
    else:
        print("⚠️  Nenhum provedor configurado!")
        print("\n   Para usar este sistema, os seguintes são necessários:")
        print("   • Pollinations.ai (online, recomendado)")
        print("   • HuggingFace/Stable Diffusion (local, opcional)")
        print("\n   Para instalar Stable Diffusion:")
        print("   pip install diffusers transformers torch")
    
    print()


async def test_image_quality():
    """Testa qualidade e dimensões de imagem"""
    
    print("\n📐 Teste de Qualidade de Imagem...")
    print("-" * 80)
    
    print(f"✅ Configurações de imagem:")
    print(f"   • Resolução: {create_visual_agent().IMAGE_WIDTH}x{create_visual_agent().IMAGE_HEIGHT} (Full HD+)")
    print(f"   • Estilo: {create_visual_agent().IMAGE_STYLE}")
    print(f"   • Formato: PNG")
    print(f"   • Cache: Automático\n")


if __name__ == "__main__":
    print("\n🚀 Iniciando testes do Visual Agent...\n")
    
    # Executar testes de provedores
    asyncio.run(test_with_available_providers())
    
    # Teste de qualidade
    asyncio.run(test_image_quality())
    
    # Teste principal
    try:
        asyncio.run(test_visual_generation())
    except KeyboardInterrupt:
        print("\n\n⏸️  Testes interrompidos pelo usuário")
    except Exception as e:
        logger.error(f"Erro durante testes: {str(e)}", exc_info=True)
        print(f"\n❌ Erro: {e}")
