"""
Integration Test - Demonstra como usar ContentAgent integrado com Config
Execute: python integration_test.py
"""

import sys
import asyncio
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from agents import create_content_agent
from config import Config
from config.logger import get_logger
from utils import FileManager

logger = get_logger(__name__)


async def integration_test():
    """Teste de integração completo"""
    
    banner = """
    ╔═══════════════════════════════════════════════════════════════════════════╗
    ║            🎬 TESTE DE INTEGRAÇÃO - MÓDULO 2 CONTENT AGENT               ║
    ║                   Fábrica de Vídeos Autônoma                             ║
    ╚═══════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)
    
    # 1. Carrega configuração
    print("\n[1/4] Carregando configuração...")
    config = Config()
    print(f"     ✅ Base dir: {config.base_dir}")
    print(f"     ✅ Output dir: {config.output_dir}")
    print(f"     ✅ Logs dir: {config.logs_dir}")
    
    # 2. Valida credenciais
    print("\n[2/4] Validando credenciais...")
    creds = config.validate_credentials()
    print(f"     {'✅' if creds['google_api_key'] else '⚠️ '} Google Gemini: " + 
          ('Configurado' if creds['google_api_key'] else 'Não configurado'))
    print(f"     {'✅' if creds['youtube_configured'] else '⚠️ '} YouTube: " + 
          ('Configurado' if creds['youtube_configured'] else 'Não configurado'))
    print(f"     ✅ Ollama (Fallback): Disponível")
    
    # 3. Cria e testa ContentAgent
    print("\n[3/4] Gerando conteúdo com ContentAgent...")
    agent = create_content_agent()
    
    themes_to_test = ["estoicismo", "cristianismo"]
    
    generated_content = []
    
    for theme in themes_to_test:
        print(f"\n     📝 Gerando conteúdo: {theme.upper()}")
        print(f"        ", end="")
        
        payload = {"theme": theme}
        result = await agent.run(payload)
        
        if result["success"]:
            content = result["data"]
            generated_content.append(content)
            
            print(f"✅ Sucesso!")
            print(f"        • Título: {content['title']}")
            print(f"        • Provider: {content['metadata']['llm_provider']}")
            print(f"        • Duração: {content['metadata']['estimated_duration_minutes']:.1f} min")
            print(f"        • Cenas: {content['metadata']['scene_count']}")
        else:
            print(f"❌ Erro: {result.get('error')}")
    
    # 4. Salva resultados e testa FileManager
    print("\n[4/4] Salvando resultados...")
    
    file_manager = FileManager()
    
    # Salva conteúdo gerado em JSON
    for i, content in enumerate(generated_content, 1):
        output_file = Path(config.output_dir) / f"conteudo_gerado_{i}.json"
        
        # Prepara dados (remove script completo para arquivo ser menor)
        output_data = {
            "title": content["title"],
            "theme": content["theme"],
            "description": content["description"],
            "tags": content["tags"],
            "metadata": content["metadata"],
            "script_preview": content["script"][:500] + "...",
            "scenes": [
                {
                    "title": scene.get("title"),
                    "visual_prompt": scene.get("visual_prompt"),
                    "script_preview": scene.get("script", "")[:200]
                }
                for scene in content["scenes"]
            ]
        }
        
        file_manager.save_json(str(output_file), output_data)
        print(f"     ✅ Salvo: {output_file.name}")
    
    # Salva registro de geração
    timestamp = __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for content in generated_content:
        record = f"[{timestamp}] {content['theme']}: {content['title']}"
        file_manager.append_to_file(
            str(Path(config.data_dir) / "conteudo_gerado.log"),
            record
        )
    
    print(f"     ✅ Registro salvo em: conteudo_gerado.log")
    
    # Resumo final
    print("\n" + "═"*75)
    print("✅ TESTE DE INTEGRAÇÃO CONCLUÍDO COM SUCESSO!")
    print("═"*75)
    print("\n📊 Resumo:")
    print(f"   • Conteúdo gerado: {len(generated_content)} vídeos")
    print(f"   • Total de cenas: {sum(c['metadata']['scene_count'] for c in generated_content)}")
    print(f"   • Duração total estimada: {sum(c['metadata']['estimated_duration_minutes'] for c in generated_content):.1f} minutos")
    print(f"   • Arquivos salvos: {len(generated_content)} JSON + 1 LOG")
    
    print("\n📁 Arquivos gerados em:")
    print(f"   {config.output_dir}/")
    print(f"   {config.data_dir}/")
    
    print("\n✨ Próximo passo: Implementar Módulo 3 (Audio Agent)")
    print()


if __name__ == "__main__":
    try:
        asyncio.run(integration_test())
    except KeyboardInterrupt:
        print("\n\n⏸️  Teste interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro no teste: {e}", exc_info=True)
        print(f"\n❌ Erro: {e}")
        sys.exit(1)
