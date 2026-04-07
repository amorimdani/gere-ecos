"""
Pipeline Integrado V3 - Teste Completo: Content → Audio → Visual → Video Editado
Execute: python src/agents/test_pipeline_v3_complete.py
"""

import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.content_agent import create_content_agent
from agents.audio_agent import create_audio_agent
from agents.visual_agent import create_visual_agent
from agents.editor_agent import create_editor_agent
from config import Config
from config.logger import get_logger
from utils import FileManager

logger = get_logger(__name__)


class FullFactoryOrchestrator:
    """Orquestrador completo da Fábrica de Vídeos"""
    
    def __init__(self):
        self.config = Config()
        self.file_manager = FileManager()
        self.content_agent = create_content_agent()
        self.audio_agent = create_audio_agent()
        self.visual_agent = create_visual_agent()
        self.editor_agent = create_editor_agent()
    
    async def run_full_factory(self, theme: str = None) -> dict:
        """
        Executa fábrica completa: Content → Audio → Visual → Video
        
        Retorna:
            dict com resultado completo da produção
        """
        
        start_time = datetime.now()
        
        pipeline_data = {
            "theme": theme or "aleatório",
            "start_time": start_time.isoformat(),
            "stages": {}
        }
        
        # ESTÁGIO 1: Geração de Conteúdo
        print("\n" + "█"*80)
        print("█" + " "*78 + "█")
        print("█" + "   📝 ESTÁGIO 1: Geração de Conteúdo   ".center(78) + "█")
        print("█" + " "*78 + "█")
        print("█"*80 + "\n")
        
        content_payload = {"theme": theme} if theme else {}
        content_result = await self.content_agent.run(content_payload)
        
        if not content_result["success"]:
            print(f"❌ Erro: {content_result.get('error')}")
            return {"success": False, "error": "Falha no ContentAgent"}
        
        content = content_result["data"]
        stage1_time = (datetime.now() - start_time).total_seconds()
        
        pipeline_data["stages"]["content"] = {
            "success": True,
            "title": content["title"],
            "theme": content["theme"],
            "duration_minutes": content["metadata"]["estimated_duration_minutes"],
            "scene_count": content["metadata"]["scene_count"],
            "word_count": content["metadata"]["word_count"],
            "time_seconds": stage1_time
        }
        
        print(f"✅ Conteúdo gerado com sucesso!")
        print(f"   Título: {content['title']}")
        print(f"   Tema: {content['theme']}")
        print(f"   Duração: {content['metadata']['estimated_duration_minutes']:.1f} minutos")
        print(f"   Cenas: {content['metadata']['scene_count']}")
        print(f"   ⏱️  {stage1_time:.1f}s")
        
        # ESTÁGIO 2: Geração de Áudio
        print("\n" + "█"*80)
        print("█" + " "*78 + "█")
        print("█" + "   🎙️  ESTÁGIO 2: Geração de Áudio   ".center(78) + "█")
        print("█" + " "*78 + "█")
        print("█"*80 + "\n")
        
        stage2_start = datetime.now()
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
        stage2_time = (datetime.now() - stage2_start).total_seconds()
        
        pipeline_data["stages"]["audio"] = {
            "success": True,
            "output_filename": audio["output_filename"],
            "file_size_mb": audio["file_size"] / 1024 / 1024,
            "duration_seconds": audio["actual_duration_seconds"],
            "tts_provider": audio["tts_provider"],
            "time_seconds": stage2_time
        }
        
        print(f"✅ Áudio gerado com sucesso!")
        print(f"   Arquivo: {Path(audio['output_filename']).name}")
        print(f"   Duração: {audio['actual_duration_seconds']:.1f}s")
        print(f"   Tamanho: {audio['file_size']/1024/1024:.2f} MB")
        print(f"   ⏱️  {stage2_time:.1f}s")
        
        # ESTÁGIO 3: Geração de Imagens
        print("\n" + "█"*80)
        print("█" + " "*78 + "█")
        print("█" + "   🖼️  ESTÁGIO 3: Geração de Imagens   ".center(78) + "█")
        print("█" + " "*78 + "█")
        print("█"*80 + "\n")
        
        stage3_start = datetime.now()
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
        stage3_time = (datetime.now() - stage3_start).total_seconds()
        
        pipeline_data["stages"]["visual"] = {
            "success": True,
            "total_scenes": stats["total_scenes"],
            "generated": stats["total_generated"],
            "cached": stats["total_cached"],
            "failed": stats["total_failed"],
            "total_size_mb": stats["total_size_mb"],
            "time_seconds": stage3_time
        }
        
        print(f"✅ Imagens geradas com sucesso!")
        print(f"   Cenas: {stats['total_scenes']}")
        print(f"   Geradas: {stats['total_generated']}")
        print(f"   Do cache: {stats['total_cached']}")
        print(f"   Tamanho: {stats['total_size_mb']:.2f} MB")
        print(f"   ⏱️  {stage3_time:.1f}s")
        
        # ESTÁGIO 4: Edição de Vídeo (NOVO!)
        print("\n" + "█"*80)
        print("█" + " "*78 + "█")
        print("█" + "   🎬 ESTÁGIO 4: Edição de Vídeo com Ken Burns   ".center(78) + "█")
        print("█" + " "*78 + "█")
        print("█"*80 + "\n")
        
        stage4_start = datetime.now()
        editor_payload = {
            "audio_path": audio["output_filename"],
            "scenes": visual["scenes"],
            "video_title": content["title"],
            "theme": content["theme"],
            "use_ken_burns": True,
            "add_transitions": True
        }
        
        editor_result = await self.editor_agent.run(editor_payload)
        
        if not editor_result["success"]:
            print(f"❌ Erro: {editor_result.get('error')}")
            return {"success": False, "error": "Falha no EditorAgent"}
        
        editor = editor_result["data"]
        stage4_time = (datetime.now() - stage4_start).total_seconds()
        
        pipeline_data["stages"]["editor"] = {
            "success": True,
            "output_filename": editor["output_filename"],
            "file_size_mb": editor["file_size_mb"],
            "duration_seconds": editor["duration_seconds"],
            "resolution": editor["resolution"],
            "fps": editor["fps"],
            "time_seconds": stage4_time
        }
        
        print(f"✅ Vídeo editado com sucesso!")
        print(f"   Arquivo: {Path(editor['output_filename']).name}")
        print(f"   Resolução: {editor['resolution']}")
        print(f"   Duração: {editor['duration_seconds']:.1f}s")
        print(f"   Tamanho: {editor['file_size_mb']:.2f} MB")
        print(f"   FPS: {editor['fps']}")
        print(f"   ⏱️  {stage4_time:.1f}s")
        
        # RESULTADO FINAL
        pipeline_data["end_time"] = datetime.now().isoformat()
        pipeline_data["success"] = True
        
        total_time = (datetime.now() - start_time).total_seconds()
        pipeline_data["total_time_seconds"] = total_time
        
        # Consolidação final
        pipeline_data["summary"] = {
            "total_time_minutes": total_time / 60,
            "stage_1_content": stage1_time,
            "stage_2_audio": stage2_time,
            "stage_3_visual": stage3_time,
            "stage_4_editor": stage4_time,
            "final_video_file": editor["output_filename"],
            "final_video_size_mb": editor["file_size_mb"],
            "final_video_duration": editor["duration_seconds"]
        }
        
        return pipeline_data
    
    async def run_multiple_themes(self) -> dict:
        """Testa fábrica com todos os 4 temas"""
        
        print("\n" + "█"*80)
        print("█" + " "*78 + "█")
        print("█" + "   🎬🎬🎬 FÁBRICA DE VÍDEOS AUTÔNOMA - TESTE COMPLETO 🎬🎬🎬   ".center(78) + "█")
        print("█" + "   Content → Audio → Visual → Video   ".center(78) + "█")
        print("█" + " "*78 + "█")
        print("█"*80)
        
        themes = ["estoicismo", "cristianismo", "filosofia", "licoes_de_vida"]
        results = {
            "full_factory_runs": [],
            "summary": {}
        }
        
        overall_start = datetime.now()
        
        for i, theme in enumerate(themes, 1):
            print(f"\n\n{'█'*80}")
            print(f"█ [{i}/{len(themes)}] Processando: {theme.upper()}")
            print(f"{'█'*80}\n")
            
            try:
                factory_result = await self.run_full_factory(theme)
                results["full_factory_runs"].append(factory_result)
            except Exception as e:
                logger.error(f"Erro ao processar {theme}: {str(e)}", exc_info=True)
                results["full_factory_runs"].append({
                    "theme": theme,
                    "success": False,
                    "error": str(e)
                })
        
        # Resumo
        overall_time = (datetime.now() - overall_start).total_seconds()
        
        print("\n" + "█"*80)
        print("█" + " "*78 + "█")
        print("█" + "   ✅ RESUMO DA FÁBRICA DE VÍDEOS   ".center(78) + "█")
        print("█" + " "*78 + "█")
        print("█"*80 + "\n")
        
        successful = sum(1 for r in results["full_factory_runs"] if r.get("success"))
        failed = len(themes) - successful
        
        print(f"Total de temas processados: {len(themes)}")
        print(f"✅ Sucesso: {successful}")
        print(f"❌ Falhas: {failed}")
        print(f"Taxa de sucesso: {(successful/len(themes))*100:.1f}%")
        print(f"\n⏱️  Tempo total: {overall_time:.1f}s ({overall_time/60:.2f} min)")
        
        if successful > 0:
            avg_time = sum(
                r.get("total_time_seconds", 0)
                for r in results["full_factory_runs"]
                if r.get("success")
            ) / successful
            print(f"⏱️  Tempo médio por vídeo: {avg_time:.1f}s ({avg_time/60:.2f} min)")
            
            total_video_size = sum(
                r["summary"]["final_video_size_mb"]
                for r in results["full_factory_runs"]
                if r.get("success")
            )
            print(f"💾 Tamanho total gerado: {total_video_size:.2f} MB")
            
            total_duration = sum(
                r["summary"]["final_video_duration"]
                for r in results["full_factory_runs"]
                if r.get("success")
            )
            print(f"🎬 Duração total de vídeos: {total_duration:.1f}s ({total_duration/60:.2f} min)")
        
        # Salva resultados
        results["summary"] = {
            "total_themes": len(themes),
            "successful": successful,
            "failed": failed,
            "success_rate": f"{(successful/len(themes))*100:.1f}%",
            "total_time_seconds": overall_time,
            "total_time_minutes": overall_time / 60,
            "timestamp": datetime.now().isoformat()
        }
        
        output_file = Path(self.config.output_dir) / "factory_complete_results.json"
        self.file_manager.save_json(str(output_file), results)
        
        print(f"\n📁 Resultados salvos em: {output_file}\n")
        
        return results


async def main():
    """Executa fábrica completa"""
    
    orchestrator = FullFactoryOrchestrator()
    
    print("\n🚀 Iniciando Fábrica de Vídeos Autônoma...\n")
    
    # Pergunta: rodar um ou todos os temas?
    print("Opções:")
    print("1. Teste rápido (1 tema aleatório)")
    print("2. Teste completo (4 temas)")
    
    choice = input("\nEscolha (1 ou 2): ").strip()
    
    if choice == "2":
        result = await orchestrator.run_multiple_themes()
    else:
        result = await orchestrator.run_full_factory()
        
        if result.get("success"):
            print("\n" + "█"*80)
            print("█" + " "*78 + "█")
            print("█" + "   ✅ VÍDEO CRIADO COM SUCESSO!   ".center(78) + "█")
            print("█" + " "*78 + "█")
            print("█"*80)
            
            summary = result.get("summary", {})
            print(f"\n📁 Arquivo: {Path(summary.get('final_video_file', '')).name}")
            print(f"📊 Tamanho: {summary.get('final_video_size_mb', 0):.2f} MB")
            print(f"⏱️  Duração: {summary.get('final_video_duration', 0):.1f}s")
            print(f"⏳ Tempo total: {summary.get('total_time_minutes', 0):.2f} min")
        else:
            print(f"\n❌ Erro: {result.get('error')}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏸️  Fábrica interrompida pelo usuário")
    except Exception as e:
        logger.error(f"Erro: {e}", exc_info=True)
        print(f"\n❌ Erro: {e}")
