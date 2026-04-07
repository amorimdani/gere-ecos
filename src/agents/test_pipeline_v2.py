"""
Pipeline Test V2 - Testa pipeline completo: Conteúdo → Áudio → Visual
Execute: python src/agents/test_pipeline_v2.py
"""

import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.content_agent import create_content_agent
from agents.audio_agent import create_audio_agent
from agents.visual_agent import create_visual_agent
from config import Config
from config.logger import get_logger
from utils import FileManager

logger = get_logger(__name__)


class FullPipelineOrchestrator:
    """Orquestrador de teste do pipeline completo: Conteúdo → Áudio → Visual"""
    
    def __init__(self):
        self.config = Config()
        self.file_manager = FileManager()
        self.content_agent = create_content_agent()
        self.audio_agent = create_audio_agent()
        self.visual_agent = create_visual_agent()
    
    async def run_full_pipeline(self, theme: str = None) -> dict:
        """
        Executa pipeline completo: Conteúdo → Áudio → Visual
        
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
            "provider": content["metadata"]["llm_provider"]
        }
        
        print(f"✅ Conteúdo gerado com sucesso!")
        print(f"   Título: {content['title']}")
        print(f"   Tema: {content['theme']}")
        print(f"   Duração: {content['metadata']['estimated_duration_minutes']:.1f} minutos")
        print(f"   Palavras: {content['metadata']['word_count']}")
        print(f"   Cenas: {content['metadata']['scene_count']}")
        
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
            "provider": audio["tts_provider"]
        }
        
        print(f"✅ Áudio gerado com sucesso!")
        print(f"   Arquivo: {audio['output_filename']}")
        print(f"   Tamanho: {audio['file_size']/1024/1024:.2f} MB")
        print(f"   Duração: {audio['actual_duration_seconds']:.1f} segundos")
        print(f"   Velocidade: {audio['script_length']/(audio['actual_duration_seconds']/60):.1f} palavras/min")
        print(f"   TTS: {audio['tts_provider']}")
        
        # ESTÁGIO 3: Geração de Imagens
        print("\n" + "="*80)
        print("🖼️  ESTÁGIO 3: Geração de Imagens")
        print("="*80)
        
        visual_payload = {
            "scenes": content["scenes"],
            "theme": content["theme"],
            "use_cache": True
        }
        
        visual_result = await self.visual_agent.run(visual_payload)
        
        if not visual_result["success"]:
            print(f"❌ Erro: {visual_result.get('error')}")
            return {"success": False, "error": "Falha no VisualAgent"}
        
        visual = visual_result["data"]
        stats = visual["statistics"]
        pipeline_data["stages"]["visual"] = {
            "success": True,
            "total_scenes": stats["total_scenes"],
            "images_generated": stats["total_generated"],
            "images_from_cache": stats["total_cached"],
            "failed": stats["total_failed"],
            "total_size_mb": stats["total_size_mb"],
            "success_rate": stats["success_rate"]
        }
        
        print(f"✅ Imagens geradas com sucesso!")
        print(f"   Total de cenas: {stats['total_scenes']}")
        print(f"   Imagens geradas: {stats['total_generated']}")
        print(f"   Do cache: {stats['total_cached']}")
        print(f"   Falhas: {stats['total_failed']}")
        print(f"   Tamanho total: {stats['total_size_mb']:.2f} MB")
        print(f"   Taxa de sucesso: {stats['success_rate']}")
        
        # RESULTADO FINAL
        pipeline_data["end_time"] = datetime.now().isoformat()
        pipeline_data["success"] = True
        
        # Calcula tempos
        start = datetime.fromisoformat(pipeline_data["start_time"])
        end = datetime.fromisoformat(pipeline_data["end_time"])
        pipeline_data["total_time_seconds"] = (end - start).total_seconds()
        
        # Calcula estatísticas finais
        total_file_size = (
            audio["file_size"] +
            sum(s.get("image_size_mb", 0) * 1024 * 1024 
                for s in visual["scenes"] if s.get("image_generated"))
        )
        
        pipeline_data["final_stats"] = {
            "total_files": 1 + stats["total_generated"],  # 1 MP3 + N imagens
            "total_size_mb": total_file_size / 1024 / 1024,
            "scenes_with_audio": content["metadata"]["scene_count"],
            "scenes_with_images": stats["total_generated"],
            "completion_time_minutes": pipeline_data["total_time_seconds"] / 60
        }
        
        return pipeline_data
    
    async def run_multiple_themes(self) -> dict:
        """Testa pipeline com todos os temas"""
        
        print("\n" + "█"*80)
        print("█" + " "*78 + "█")
        print("█" + "   🎬 TESTE COMPLETO: Conteúdo → Áudio → Visual   ".center(78) + "█")
        print("█" + " "*78 + "█")
        print("█"*80)
        
        themes = ["estoicismo", "cristianismo", "filosofia", "licoes_de_vida"]
        results = {
            "pipeline_tests": [],
            "summary": {}
        }
        
        for i, theme in enumerate(themes, 1):
            print(f"\n\n[{i}/{len(themes)}] Processando: {theme.upper()}")
            print("█"*80)
            
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
        print("█" + "   ✅ RESUMO DO PIPELINE COMPLETO   ".center(78) + "█")
        print("█" + " "*78 + "█")
        print("█"*80 + "\n")
        
        successful = sum(1 for r in results["pipeline_tests"] if r.get("success"))
        failed = len(themes) - successful
        
        print(f"Total de temas testados: {len(themes)}")
        print(f"✅ Sucesso: {successful}")
        print(f"❌ Falhas: {failed}")
        print(f"Taxa de sucesso: {(successful/len(themes))*100:.1f}%")
        
        if successful > 0:
            total_time = sum(
                r.get("total_time_seconds", 0) 
                for r in results["pipeline_tests"] 
                if r.get("success")
            )
            avg_time = total_time / successful
            print(f"⏱️  Tempo médio por pipeline: {avg_time:.1f} segundos ({avg_time/60:.2f} minutos)")
            
            total_content_size = sum(
                r["final_stats"]["total_size_mb"]
                for r in results["pipeline_tests"]
                if r.get("success")
            )
            print(f"💾 Tamanho total gerado: {total_content_size:.2f} MB")
        
        # Salva resultados
        results["summary"] = {
            "total_themes": len(themes),
            "successful": successful,
            "failed": failed,
            "success_rate": f"{(successful/len(themes))*100:.1f}%",
            "timestamp": datetime.now().isoformat()
        }
        
        output_file = Path(self.config.output_dir) / "pipeline_full_results.json"
        self.file_manager.save_json(str(output_file), results)
        
        print(f"\n📁 Resultados salvos em: {output_file}")
        
        return results


async def main():
    """Executa testes do pipeline completo"""
    
    orchestrator = FullPipelineOrchestrator()
    
    # Teste rápido de um tema
    print("\n🚀 Iniciando teste do pipeline completo (tema aleatório)...\n")
    result = await orchestrator.run_full_pipeline()
    
    if result.get("success"):
        print("\n" + "="*80)
        print("✅ PIPELINE COMPLETO EXECUTADO COM SUCESSO!")
        print("="*80)
        
        final_stats = result.get("final_stats", {})
        print(f"\n📊 Estatísticas Finais:")
        print(f"   • Total de arquivos gerados: {final_stats.get('total_files', 0)}")
        print(f"   • Tamanho total: {final_stats.get('total_size_mb', 0):.2f} MB")
        print(f"   • Tempo total: {final_stats.get('completion_time_minutes', 0):.2f} minutos")
        print(f"   • Cenas com áudio: {final_stats.get('scenes_with_audio', 0)}")
        print(f"   • Cenas com imagens: {final_stats.get('scenes_with_images', 0)}")
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
