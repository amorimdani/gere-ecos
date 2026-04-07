"""
Teste do Content Agent - Demonstra uso do sistema de geração de conteúdo
Execute: python src/agents/test_content_agent.py
"""

import sys
import asyncio
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.content_agent import create_content_agent
from config import Config
from config.logger import get_logger

logger = get_logger(__name__)


async def test_content_generation():
    """Testa a geração de conteúdo completo"""
    
    print("\n" + "="*80)
    print("🎬 TESTE DO CONTENT AGENT - Fábrica de Vídeos Autônoma")
    print("="*80 + "\n")
    
    # Cria agente
    agent = create_content_agent()
    
    # Testa com tema específico
    print("📝 Teste 1: Gerando conteúdo com tema ESTOICISMO...")
    print("-" * 80)
    
    payload = {"theme": "estoicismo"}
    result = await agent.run(payload)
    
    if result["success"]:
        content = result["data"]
        
        print(f"\n✅ Conteúdo gerado com sucesso!")
        print(f"   Provedor LLM: {content['metadata']['llm_provider']}")
        print(f"   Duração estimada: {content['metadata']['estimated_duration_minutes']:.1f} min")
        print(f"   Número de cenas: {content['metadata']['scene_count']}")
        print(f"\n📌 TÍTULO:\n   {content['title']}\n")
        print(f"📝 DESCRIÇÃO:\n   {content['description'][:200]}...\n")
        print(f"🏷️  TAGS:\n   {', '.join(content['tags'][:10])}\n")
        
        # Salva resultado em arquivo JSON
        output_file = Path(__file__).parent.parent.parent / "output" / "conteudo_teste.json"
        output_file.parent.mkdir(exist_ok=True)
        
        # Salva de forma legível
        with open(output_file, 'w', encoding='utf-8') as f:
            # Prepara dados para JSON (remove fields muito grandes)
            output_data = {
                "title": content["title"],
                "theme": content["theme"],
                "description": content["description"],
                "tags": content["tags"],
                "metadata": content["metadata"],
                "scenes_count": len(content["scenes"]),
                "scenes_preview": [
                    {
                        "title": scene.get("title"),
                        "visual_prompt": scene.get("visual_prompt"),
                        "duration": scene.get("duration_seconds")
                    }
                    for scene in content["scenes"][:3]
                ]
            }
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Resultado salvo em: {output_file}\n")
        
        # Mostra primeiras cenas
        print("🎬 CENAS GERADAS:")
        print("-" * 80)
        for i, scene in enumerate(content["scenes"][:3], 1):
            print(f"\n[CENA {i}] {scene.get('title', 'Sem título')}")
            print(f"   📸 Visual: {scene.get('visual_prompt', 'N/A')[:100]}...")
    else:
        print(f"❌ Erro ao gerar conteúdo: {result.get('error')}")
    
    print("\n" + "="*80)
    
    # Teste 2: Tema aleatório
    print("\n📝 Teste 2: Gerando conteúdo com tema aleatório...")
    print("-" * 80)
    
    payload2 = {}  # Deixa aleatório
    result2 = await agent.run(payload2)
    
    if result2["success"]:
        content2 = result2["data"]
        print(f"\n✅ Tema selecionado: {content2['theme']}")
        print(f"   Título: {content2['title']}")
        print(f"   Duração: {content2['metadata']['estimated_duration_minutes']:.1f} min")
    else:
        print(f"❌ Erro: {result2.get('error')}")
    
    print("\n" + "="*80)
    print("✅ Testes concluídos!")
    print("="*80 + "\n")


async def test_with_available_providers():
    """Testa quais provedores estão disponíveis"""
    
    print("\n🔍 Verificando provedores disponíveis...")
    print("-" * 80)
    
    agent = create_content_agent()
    providers = agent.llm_manager.get_available_providers()
    
    if providers:
        print(f"✅ Provedores disponíveis: {', '.join(providers)}")
    else:
        print("⚠️  Nenhum provedor configurado!")
        print("\n   Para usar este sistema, configure:")
        print("   1. Google Gemini API: GOOGLE_API_KEY em .env")
        print("   2. Ollama local: OLLAMA_BASE_URL e OLLAMA_MODEL em .env")
    
    print()


if __name__ == "__main__":
    print("\n🚀 Iniciando testes do Content Agent...\n")
    
    # Executar teste de provedores
    asyncio.run(test_with_available_providers())
    
    # Executar teste principal
    try:
        asyncio.run(test_content_generation())
    except KeyboardInterrupt:
        print("\n\n⏸️  Testes interrompidos pelo usuário")
    except Exception as e:
        logger.error(f"Erro durante testes: {str(e)}", exc_info=True)
        print(f"\n❌ Erro: {e}")
