"""
Teste do Publisher Agent - Upload para YouTube
Execute: python src/agents/test_publisher_agent.py
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.publisher_agent import create_publisher_agent
from agents.youtube_manager import YouTubeManager
from config import Config
from config.logger import get_logger

logger = get_logger(__name__)


async def test_youtube_credentials():
    """Testa se credenciais do YouTube estão configuradas"""
    
    print("\n" + "="*80)
    print("🔐 TESTE 1: Validação de Credenciais YouTube")
    print("="*80 + "\n")
    
    config = Config()
    
    credentials_file = Path("credentials.json")
    token_file = Path(config.data_dir) / "youtube_token.json"
    
    print("Verificando credenciais:")
    print(f"  • credentials.json: {'✅' if credentials_file.exists() else '❌'} ({credentials_file})")
    print(f"  • youtube_token.json: {'✅' if token_file.exists() else '❌'} ({token_file})")
    
    if not credentials_file.exists():
        print("\n⚠️  SETUP NECESSÁRIO:")
        print("  1. Acesse: https://console.cloud.google.com/apis/credentials")
        print("  2. Crie uma chave OAuth 2.0 (tipo: Desktop Application)")
        print("  3. Baixe o JSON")
        print("  4. Salve como: credentials.json (na raiz do projeto)")
        print("  5. Execute novamente este teste\n")
        return False
    
    print("\n✅ Credenciais encontradas!")
    
    # Tenta autenticação
    print("\nTentando autenticação...")
    
    yt_manager = YouTubeManager()
    
    if await yt_manager.authenticate():
        print("✅ Autenticado no YouTube API!")
        
        # Obtém info do canal
        channel_info = await yt_manager.get_channel_info()
        
        if channel_info:
            print(f"\n📺 Informações do Canal:")
            print(f"   • Título: {channel_info.get('title')}")
            print(f"   • Inscritos: {channel_info.get('subscribers')}")
            print(f"   • Visualizações: {channel_info.get('view_count')}")
            print(f"   • Vídeos: {channel_info.get('video_count')}\n")
            return True
    else:
        print("❌ Falha na autenticação\n")
        return False


async def test_metadata_preparation():
    """Testa preparação de metadados"""
    
    print("\n" + "="*80)
    print("📝 TESTE 2: Preparação de Metadados")
    print("="*80 + "\n")
    
    from agents.youtube_manager import VideoMetadata
    
    metadata = VideoMetadata(
        title="Estoicismo: A Filosofia de Calma",
        description="Um guia completo sobre os princípios do estoicismo...",
        tags=["estoicismo", "filosofia", "motivação", "sabedoria"],
        category_id="22",  # People & Blogs
        privacy_status="private",
        made_for_kids=False
    )
    
    print(f"✅ Metadados preparados:")
    print(f"   • Título: {metadata.title}")
    print(f"   • Descrição: {metadata.description[:50]}...")
    print(f"   • Tags: {', '.join(metadata.tags)}")
    print(f"   • Categoria: {metadata.category_id}")
    print(f"   • Privacidade: {metadata.privacy_status}")
    print(f"   • Made for Kids: {metadata.made_for_kids}\n")


async def test_publisher_agent_dry_run():
    """Teste seco do PublisherAgent (sem fazer upload real)"""
    
    print("\n" + "="*80)
    print("🎬 TESTE 3: Simulação de Publicação (Dry Run)")
    print("="*80 + "\n")
    
    config = Config()
    
    # Cria arquivo de vídeo fictício para teste
    test_video_path = Path(config.output_dir) / "test_video_dummy.mp4"
    
    if not test_video_path.exists():
        print(f"Criando arquivo de teste: {test_video_path.name}")
        test_video_path.write_bytes(b"dummy video data")
    
    print(f"✅ Arquivo de teste criado: {test_video_path.name}")
    
    publisher = create_publisher_agent()
    
    # Prepara payload para teste
    payload = {
        "video_path": str(test_video_path),
        "title": "Teste: Estoicismo Explicado",
        "description": "Este é um vídeo de teste da fábrica de vídeos autônoma.",
        "tags": ["teste", "estoicismo", "fábrica-de-vídeos"],
        "theme": "estoicismo",
        "privacy_status": "unlisted",  # Publicado mas não listado
        "made_for_kids": False
    }
    
    print(f"\nPayload preparado:")
    print(f"  • Vídeo: {Path(payload['video_path']).name}")
    print(f"  • Título: {payload['title']}")
    print(f"  • Status: {payload['privacy_status']}")
    print(f"\n⚠️  Este teste validará a estrutura mas NÃO fará upload real")
    print(f"   (requer autenticação YouTube)\n")


async def test_published_videos_log():
    """Testa log de vídeos publicados"""
    
    print("\n" + "="*80)
    print("📊 TESTE 4: Log de Vídeos Publicados")
    print("="*80 + "\n")
    
    publisher = create_publisher_agent()
    
    videos = await publisher.get_published_videos()
    
    if videos:
        print(f"✅ {len(videos)} vídeo(s) publicado(s):\n")
        
        for i, video in enumerate(videos[-5:], 1):  # Últimos 5
            print(f"  [{i}] {video.get('title', 'N/A')}")
            print(f"      ID: {video.get('video_id', 'N/A')}")
            print(f"      URL: {video.get('url', 'N/A')}")
            print(f"      Tema: {video.get('theme', 'N/A')}")
            print(f"      Data: {video.get('published_at', 'N/A')}\n")
    else:
        print("ℹ️  Nenhum vídeo publicado ainda\n")


async def test_channel_stats():
    """Testa obtenção de estatísticas do canal"""
    
    print("\n" + "="*80)
    print("📈 TESTE 5: Estatísticas do Canal")
    print("="*80 + "\n")
    
    publisher = create_publisher_agent()
    
    stats = await publisher.get_channel_stats()
    
    if stats:
        print(f"✅ Estatísticas do canal:\n")
        
        for key, value in stats.items():
            print(f"  • {key}: {value}")
        
        print()
    else:
        print("⚠️  Não foi possível obter estatísticas\n")


async def main():
    """Executa suite de testes"""
    
    print("\n🚀 Iniciando testes do Publisher Agent...\n")
    
    # Teste 1: Credenciais
    credentials_ok = await test_youtube_credentials()
    
    if not credentials_ok:
        print("\n⚠️  Teste de credenciais falhou")
        print("   Configure as credenciais do YouTube e tente novamente\n")
        return
    
    # Teste 2: Metadados
    await test_metadata_preparation()
    
    # Teste 3: Dry run
    await test_publisher_agent_dry_run()
    
    # Teste 4: Log
    await test_published_videos_log()
    
    # Teste 5: Stats
    await test_channel_stats()
    
    print("\n" + "="*80)
    print("✅ Testes concluídos!")
    print("="*80 + "\n")
    
    print("Próximos passos:")
    print("  • Configure credenciais.json")
    print("  • Execute: python src/agents/test_pipeline_v4_full_factory.py")
    print("  • Para publicar um vídeo ao vivo!\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏸️  Testes interrompidos pelo usuário")
    except Exception as e:
        logger.error(f"Erro: {e}", exc_info=True)
        print(f"\n❌ Erro: {e}")
