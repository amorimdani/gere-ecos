"""
Teste do Audio Agent - Demonstra uso do sistema de geração de áudio
Execute: python src/agents/test_audio_agent.py
"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.audio_agent import create_audio_agent
from agents.content_agent import create_content_agent
from config import Config
from config.logger import get_logger

logger = get_logger(__name__)


async def test_audio_generation():
    """Testa a geração de áudio completo"""
    
    print("\n" + "="*80)
    print("🎙️  TESTE DO AUDIO AGENT - Fábrica de Vídeos Autônoma")
    print("="*80 + "\n")
    
    config = Config()
    
    # Teste 1: Gera conteúdo e depois áudio
    print("📝 Teste 1: Gerando conteúdo + áudio (Estoicismo)...")
    print("-" * 80)
    
    # Cria conteúdo
    content_agent = create_content_agent()
    content_result = await content_agent.run({"theme": "estoicismo"})
    
    if not content_result["success"]:
        print(f"❌ Erro ao gerar conteúdo: {content_result.get('error')}")
        return
    
    content = content_result["data"]
    print(f"✅ Conteúdo gerado: {content['title']}")
    print(f"   Duração esperada: {content['metadata']['estimated_duration_minutes']:.1f} min")
    
    # Gera áudio
    print("\n🎙️  Gerando áudio...")
    audio_agent = create_audio_agent()
    
    payload = {
        "script": content["script"],
        "video_title": content["title"],
        "expected_duration_minutes": int(content['metadata']['estimated_duration_minutes']),
        "output_filename": "teste_estoicismo.mp3"
    }
    
    audio_result = await audio_agent.run(payload)
    
    if audio_result["success"]:
        audio_data = audio_result["data"]
        
        print(f"\n✅ Áudio gerado com sucesso!")
        print(f"   Arquivo: {audio_data['output_filename']}")
        print(f"   Tamanho: {audio_data['file_size']:,} bytes ({audio_data['file_size']/1024/1024:.2f} MB)")
        print(f"   Provedor TTS: {audio_data['tts_provider']}")
        print(f"   Duração estimada: {audio_data['actual_duration_seconds']:.1f} segundos")
        print(f"   Velocidade: {audio_data['script_length'] / (audio_data['actual_duration_seconds']/60):.1f} palavras/min")
        
        # Mostra caminho completo
        print(f"\n📁 Salvo em: {audio_data['audio_path']}")
        
    else:
        print(f"❌ Erro ao gerar áudio: {audio_result.get('error')}")
        return
    
    # Teste 2: Múltiplos temas
    print("\n" + "="*80)
    print("\n📝 Teste 2: Gerando áudios para múltiplos temas...")
    print("-" * 80)
    
    themes = ["cristianismo", "filosofia"]
    
    for theme in themes:
        print(f"\n   🎯 {theme.upper()}")
        
        # Conteúdo
        content_result = await content_agent.run({"theme": theme})
        if not content_result["success"]:
            print(f"      ❌ Erro: {content_result.get('error')}")
            continue
        
        content = content_result["data"]
        
        # Áudio
        payload = {
            "script": content["script"],
            "video_title": content["title"],
            "expected_duration_minutes": int(content['metadata']['estimated_duration_minutes'])
        }
        
        audio_result = await audio_agent.run(payload)
        
        if audio_result["success"]:
            audio_data = audio_result["data"]
            print(f"      ✅ Áudio: {audio_data['output_filename']}")
            print(f"         {audio_data['file_size']/1024/1024:.2f} MB ({audio_data['tts_provider']})")
        else:
            print(f"      ❌ Erro: {audio_result.get('error')}")
    
    print("\n" + "="*80)
    print("✅ Testes concluídos!")
    print("="*80 + "\n")


async def test_with_available_providers():
    """Testa quais provedores estão disponíveis"""
    
    print("\n🔍 Verificando provedores TTS disponíveis...")
    print("-" * 80)
    
    audio_agent = create_audio_agent()
    providers = audio_agent.tts_manager.get_available_providers()
    
    if providers:
        print(f"✅ Provedores disponíveis: {', '.join(providers)}")
        print("\n   Prioridade de uso:")
        for i, provider in enumerate(providers, 1):
            status = "PRIMARY" if i == 1 else "FALLBACK"
            print(f"   {i}. {provider:15} ({status})")
    else:
        print("⚠️  Nenhum provedor configurado!")
        print("\n   Para usar este sistema, os seguintes pacotes devem estar instalados:")
        print("   • edge-tts (recomendado): pip install edge-tts")
        print("   • gtts (fallback): pip install gtts")
    
    print()


async def test_script_cleaning():
    """Testa a limpeza e formatação de scripts"""
    
    print("\n🧹 Teste de Limpeza de Script (Parsing)...")
    print("-" * 80)
    
    audio_agent = create_audio_agent()
    
    # Script de teste com marcações
    test_script = """
    [HOOK] - Abertura Impactante
    Você já parou para pensar que a maioria das pessoas...
    
    [CENA 1] - Desenvolvimento
    Então vamos explorar isso mais profundamente...
    Esta é uma história muito interessante.
    
    [PLOT TWIST] - Reviravolta
    Mas aqui está o que ninguém espera...
    
    [FINAL] - Conclusão
    Portanto, baseado nisso tudo...
    """
    
    cleaned = audio_agent._clean_script(test_script)
    
    print("Original:")
    print(test_script[:200] + "...\n")
    print("Limpo:")
    print(cleaned[:200])
    print(f"\n✅ Script processado: {len(cleaned.split())} palavras")
    
    print()


if __name__ == "__main__":
    print("\n🚀 Iniciando testes do Audio Agent...\n")
    
    # Executar testes de provedores
    asyncio.run(test_with_available_providers())
    
    # Teste de limpeza
    asyncio.run(test_script_cleaning())
    
    # Teste principal
    try:
        asyncio.run(test_audio_generation())
    except KeyboardInterrupt:
        print("\n\n⏸️  Testes interrompidos pelo usuário")
    except Exception as e:
        logger.error(f"Erro durante testes: {str(e)}", exc_info=True)
        print(f"\n❌ Erro: {e}")
