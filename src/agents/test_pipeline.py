"""
Pipeline Test - Testa o pipeline completo: Conteúdo → Áudio
Execute: python src/agents/test_pipeline.py
"""

import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.content_agent import create_content_agent
from agents.audio_agent import create_audio_agent
from config import Config
from config.logger import get_logger
from utils import FileManager

logger = get_logger(__name__)


class PipelineTestOrchestrator:
    """Orquestrador de testes do pipeline completo"""
    
    def __init__(self):
        self.config = Config()
        self.file_manager = FileManager()
        self.content_agent = create_content_agent()
        self.audio_agent = create_audio_agent()
    
    async def run_full_pipeline(self, theme: str = None) -> dict:
        """
        Executa pipeline completo: Conteúdo → Áudio
        
        Args:
            theme: Tema para conteúdo (None para aleatório)
            
        Returns:
            dict: Resultado do pipeline completo
        """
        
        pipeline_data = {
            "theme": theme or "aleatório",
            "start_time": datetime.now().isoformat(),
            "stages": {}
        }
        
        # ESTÁGIO 1: Geração de Conteúdo
        print("\n" + "="*80)
        print("📝 ESTÁGIO 1: Geração de Conteúdo")
        print("="*80)
        
        content_payload = {"theme": theme} if theme else {}
        content_result = await self.content_agent.run(content_payload)
        
        if not content_result["success"]:
            print(f"❌ Erro: {content_result.get('error')}")
            return {"success": False, "error": "Falha no ContentAgent"}
        
        content = content_result["data"]
        pipeline_data["stages"]["content"] = {
            "success": True,
            "title": content["title"],
            "theme": content["theme"],
            "duration_minutes": content["metadata"]["estimated_duration_minutes"],
            "scene_count": content["metadata"]["scene_count"],
            "word_count": content["metadata"]["word_count"],
            "provider": content["metadata"]["llm_provider"],
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"✅ Conteúdo gerado com sucesso!")
        print(f"   Título: {content['title']}")
        print(f"   Tema: {content['theme']}")
        print(f"   Duração: {content['metadata']['estimated_duration_minutes']:.1f} minutos")
        print(f"   Palavras: {content['metadata']['word_count']}")
        print(f"   Cenas: {content['metadata']['scene_count']}")
        print(f"   Provider LLM: {content['metadata']['llm_provider']}")
        
        # ESTÁGIO 2: Geração de Áudio
        print("\n" + "="*80)
        print("🎙️  ESTÁGIO 2: Geração de Áudio")
        print("="*80)
        
        audio_payload = {
            "script": content["script"],
            "video_title": content["title"],
            "expected_duration_minutes": int(content["metadata"]["estimated_duration_minutes"])
        }
        
        audio_result = await self.audio_agent.run(audio_payload)
        
        if not audio_result["success"]:
            print(f"❌ Erro: {audio_result.get('error')}")
            return {"success": False, "error": "Falha no AudioAgent"}
        
        audio = audio_result["data"]
        pipeline_data["stages"]["audio"] = {
            "success": True,
            "output_filename": audio["output_filename"],
            "file_size_mb": audio["file_size"] / 1024 / 1024,
            "duration_seconds": audio["actual_duration_seconds"],
            "words_per_minute": audio["script_length"] / (audio["actual_duration_seconds"]/60),
            "provider": audio["tts_provider"],
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"✅ Áudio gerado com sucesso!")
        print(f"   Arquivo: {audio['output_filename']}")
        print(f"   Tamanho: {audio['file_size']/1024/1024:.2f} MB")
        print(f"   Duração: {audio['actual_duration_seconds']:.1f} segundos")
        print(f"   Velocidade: {audio['script_length']/(audio['actual_duration_seconds']/60):.1f} palabras/min")
        print(f"   Provider TTS: {audio['tts_provider']}")
        print(f"   Arquivo salvo em: {audio['audio_path']}")
        
        # Resultado Final
        pipeline_data["end_time"] = datetime.now().isoformat()
        pipeline_data["success"] = True
        
        # Calcula tempos
        start = datetime.fromisoformat(pipeline_data["start_time"])
        end = datetime.fromisoformat(pipeline_data["end_time"])
        pipeline_data["total_time_seconds"] = (end - start).total_seconds()
        
        return pipeline_data
    
    async def run_multiple_themes(self) -> dict:
        """Testa pipeline com todos os temas"""
        
        print("\n" + "█"*80)
        print("█" + " "*78 + "█")
        print("█" + "   🎬 TESTE COMPLETO DO PIPELINE: Múltiplos Temas   ".center(78) + "█")
        print("█" + " "*78 + "█")
        print("█"*80)
        
        themes = ["estoicismo", "cristianismo", "filosofia", "licoes_de_vida"]
        results = {
            "pipeline_tests": [],
            "summary": {}
        }
        
        for i, theme in enumerate(themes, 1):
            print(f"\n\n[{i}/{len(themes)}] Processando: {theme.upper()}")
            print("="*80)
            
            try:
                pipeline_result = await self.run_full_pipeline(theme)
                results["pipeline_tests"].append(pipeline_result)
            except Exception as e:
                logger.error(f"Erro ao processar {theme}: {str(e)}", exc_info=True)
                results["pipeline_tests"].append({
                    "theme": theme,
                    "success": False,
                    "error": str(e)
                })
        
        # Resumo
        print("\n" + "█"*80)
        print("█" + " "*78 + "█")
        print("█" + "   ✅ RESUMO DO TESTE DO PIPELINE   ".center(78) + "█")
        print("█" + " "*78 + "█")
        print("█"*80 + "\n")
        
        successful = sum(1 for r in results["pipeline_tests"] if r.get("success"))
        failed = len(themes) - successful
        
        print(f"Total de temas testados: {len(themes)}")
        print(f"✅ Sucesso: {successful}")
        print(f"❌ Falhas: {failed}")
        
        if successful > 0:
            total_time = sum(r["total_time_seconds"] for r in results["pipeline_tests"] if r.get("success"))
            avg_time = total_time / successful
            print(f"⏱️  Tempo médio por pipeline: {avg_time:.1f} segundos")
        
        # Salva resultados
        results["summary"] = {
            "total_themes": len(themes),
            "successful": successful,
            "failed": failed,
            "success_rate": f"{(successful/len(themes))*100:.1f}%",
            "timestamp": datetime.now().isoformat()
        }
        
        output_file = Path(self.config.output_dir) / "pipeline_test_results.json"
        self.file_manager.save_json(str(output_file), results)
        
        print(f"\n📁 Resultados salvos em: {output_file}")
        
        return results


async def main():
    """Executa testes do pipeline"""
    
    orchestrator = PipelineTestOrchestrator()
    
    # Opção 1: Teste de tema único
    # result = await orchestrator.run_full_pipeline("estoicismo")
    
    # Opção 2: Teste de múltiplos temas (comentado por padrão)
    # result = await orchestrator.run_multiple_themes()
    
    # Opção 3: Teste rápido
    print("\n🚀 Iniciando teste rápido do pipeline (tema aleatório)...\n")
    result = await orchestrator.run_full_pipeline()
    
    if result.get("success"):
        print("\n" + "="*80)
        print("✅ PIPELINE EXECUTADO COM SUCESSO!")
        print("="*80)
        print(f"Tempo total: {result['total_time_seconds']:.1f} segundos")
        print()
    else:
        print(f"\n❌ Erro no pipeline: {result.get('error')}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏸️  Teste interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro: {e}", exc_info=True)
        print(f"\n❌ Erro: {e}")
