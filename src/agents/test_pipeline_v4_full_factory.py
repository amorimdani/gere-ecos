"""
Pipeline Integrado V4 - FACTORY COMPLETA: Content → Audio → Visual → Editor → Publisher
Execute: python src/agents/test_pipeline_v4_full_factory.py
"""

import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.content_agent import create_content_agent
from agents.audio_agent import create_audio_agent
from agents.visual_agent import create_visual_agent
from agents.editor_agent import create_editor_agent
from agents.publisher_agent import create_publisher_agent
from config import Config
from config.logger import get_logger
from utils import FileManager

logger = get_logger(__name__)


class FullVideoFactory:
    """Fábrica Autônoma de Vídeos Completa: C→A→V→E→P"""
    
    def __init__(self):
        self.config = Config()
        self.file_manager = FileManager()
        self.content_agent = create_content_agent()
        self.audio_agent = create_audio_agent()
        self.visual_agent = create_visual_agent()
        self.editor_agent = create_editor_agent()
        self.publisher_agent = create_publisher_agent()
    
    async def produce_and_publish(
        self,
        theme: str = None,
        publish: bool = False,
        privacy_status: str = "unlisted"
    ) -> dict:
        """
        Pipeline completo: Produção → Publicação
        
        Args:
            theme: Tema do vídeo
            publish: Se True, publica no YouTube
            privacy_status: 'private', 'unlisted', 'public'
            
        Returns:
            dict com resultado completo
        """
        
        start_time = datetime.now()
        
        result = {
            "theme": theme or "aleatório",
            "start_time": start_time.isoformat(),
            "stages": {},
            "success": False
        }
        
        # STAGE 1: CONTENT
        print("\n" + "█"*100)
        print("█" + " "*98 + "█")
        print("█" + "   📝 STAGE 1: CONTENT GENERATION   ".center(98) + "█")
        print("█" + " "*98 + "█")
        print("█"*100 + "\n")
        
        stage1_start = datetime.now()
        
        content_result = await self.content_agent.run({"theme": theme} if theme else {})
        
        if not content_result["success"]:
            result["error"] = "Content generation failed"
            return result
        
        content = content_result["data"]
        stage1_time = (datetime.now() - stage1_start).total_seconds()
        
        result["stages"]["content"] = {
            "success": True,
            "title": content["title"],
            "theme": content["theme"],
            "duration_min": content["metadata"]["estimated_duration_minutes"],
            "scenes": content["metadata"]["scene_count"],
            "time_sec": stage1_time
        }
        
        print(f"✅ Conteúdo gerado!")
        print(f"   Título: {content['title']}")
        print(f"   Tema: {content['theme']}")
        print(f"   Duração: {content['metadata']['estimated_duration_minutes']:.1f} min")
        print(f"   ⏱️  {stage1_time:.1f}s\n")
        
        # STAGE 2: AUDIO
        print("█"*100)
        print("█" + " "*98 + "█")
        print("█" + "   🎙️  STAGE 2: AUDIO GENERATION   ".center(98) + "█")
        print("█" + " "*98 + "█")
        print("█"*100 + "\n")
        
        stage2_start = datetime.now()
        
        audio_result = await self.audio_agent.run({
            "script": content["script"],
            "video_title": content["title"],
            "expected_duration_minutes": int(content["metadata"]["estimated_duration_minutes"])
        })
        
        if not audio_result["success"]:
            result["error"] = "Audio generation failed"
            return result
        
        audio = audio_result["data"]
        stage2_time = (datetime.now() - stage2_start).total_seconds()
        
        result["stages"]["audio"] = {
            "success": True,
            "file_size_mb": audio["file_size"] / 1024 / 1024,
            "duration_sec": audio["actual_duration_seconds"],
            "time_sec": stage2_time
        }
        
        print(f"✅ Áudio gerado!")
        print(f"   Duração: {audio['actual_duration_seconds']:.1f}s")
        print(f"   Tamanho: {audio['file_size']/1024/1024:.2f} MB")
        print(f"   ⏱️  {stage2_time:.1f}s\n")
        
        # STAGE 3: VISUAL
        print("█"*100)
        print("█" + " "*98 + "█")
        print("█" + "   🖼️  STAGE 3: VISUAL GENERATION   ".center(98) + "█")
        print("█" + " "*98 + "█")
        print("█"*100 + "\n")
        
        stage3_start = datetime.now()
        
        visual_result = await self.visual_agent.run({
            "scenes": content["scenes"],
            "theme": content["theme"],
            "use_cache": True
        })
        
        if not visual_result["success"]:
            result["error"] = "Visual generation failed"
            return result
        
        visual = visual_result["data"]
        stats = visual["statistics"]
        stage3_time = (datetime.now() - stage3_start).total_seconds()
        
        result["stages"]["visual"] = {
            "success": True,
            "total_scenes": stats["total_scenes"],
            "generated": stats["total_generated"],
            "cached": stats["total_cached"],
            "total_size_mb": stats["total_size_mb"],
            "time_sec": stage3_time
        }
        
        print(f"✅ Imagens geradas!")
        print(f"   Cenas: {stats['total_scenes']}")
        print(f"   Geradas: {stats['total_generated']}")
        print(f"   Do cache: {stats['total_cached']}")
        print(f"   Tamanho: {stats['total_size_mb']:.2f} MB")
        print(f"   ⏱️  {stage3_time:.1f}s\n")
        
        # STAGE 4: EDITOR
        print("█"*100)
        print("█" + " "*98 + "█")
        print("█" + "   🎬 STAGE 4: VIDEO EDITING   ".center(98) + "█")
        print("█" + " "*98 + "█")
        print("█"*100 + "\n")
        
        stage4_start = datetime.now()
        
        editor_result = await self.editor_agent.run({
            "audio_path": audio["output_filename"],
            "scenes": visual["scenes"],
            "video_title": content["title"],
            "theme": content["theme"],
            "use_ken_burns": True,
            "add_transitions": True
        })
        
        if not editor_result["success"]:
            result["error"] = "Video editing failed"
            return result
        
        editor = editor_result["data"]
        stage4_time = (datetime.now() - stage4_start).total_seconds()
        
        result["stages"]["editor"] = {
            "success": True,
            "file_size_mb": editor["file_size_mb"],
            "duration_sec": editor["duration_seconds"],
            "time_sec": stage4_time
        }
        
        print(f"✅ Vídeo editado!")
        print(f"   Resolução: {editor['resolution']}")
        print(f"   Duração: {editor['duration_seconds']:.1f}s")
        print(f"   Tamanho: {editor['file_size_mb']:.2f} MB")
        print(f"   ⏱️  {stage4_time:.1f}s\n")
        
        # STAGE 5: PUBLISHER (Opcional)
        if publish:
            print("█"*100)
            print("█" + " "*98 + "█")
            print("█" + "   📤 STAGE 5: YOUTUBE PUBLISHING   ".center(98) + "█")
            print("█" + " "*98 + "█")
            print("█"*100 + "\n")
            
            stage5_start = datetime.now()
            
            publisher_result = await self.publisher_agent.run({
                "video_path": editor["output_filename"],
                "title": content["title"],
                "description": self._generate_description(content),
                "tags": content["metadata"].get("tags", []),
                "theme": content["theme"],
                "privacy_status": privacy_status,
                "made_for_kids": False
            })
            
            if publisher_result["success"]:
                publisher = publisher_result["data"]
                stage5_time = (datetime.now() - stage5_start).total_seconds()
                
                result["stages"]["publisher"] = {
                    "success": True,
                    "video_id": publisher["video_id"],
                    "url": publisher["url"],
                    "time_sec": stage5_time
                }
                
                print(f"✅ Vídeo publicado!")
                print(f"   ID: {publisher['video_id']}")
                print(f"   URL: {publisher['url']}")
                print(f"   Status: {publisher['privacy_status']}")
                print(f"   ⏱️  {stage5_time:.1f}s\n")
            else:
                print(f"⚠️  Publicação não realizada: {publisher_result.get('error')}\n")
                result["stages"]["publisher"] = {"success": False}
        else:
            print("⏭️  Publicação desabilitada (use --publish para ativar)\n")
        
        # RESULTADO FINAL
        total_time = (datetime.now() - start_time).total_seconds()
        
        result["success"] = True
        result["end_time"] = datetime.now().isoformat()
        result["total_time_sec"] = total_time
        result["total_time_min"] = total_time / 60
        
        return result
    
    def _generate_description(self, content: dict) -> str:
        """Gera descrição para o vídeo"""
        
        theme = content.get("theme", "")
        theme_display = {
            "estoicismo": "Estoicismo",
            "cristianismo": "Cristianismo",
            "filosofia": "Filosofia",
            "licoes_de_vida": "Lições de Vida"
        }.get(theme, theme.capitalize())
        
        description = f"""
{content.get('title', 'Vídeo')}

Este vídeo foi produzido pela Fábrica Autônoma de Vídeos da série "Ecos de Sabedoria".

📌 TEMA: {theme_display}

🔗 INSCREVA-SE:
Para mais conteúdo sobre filosofia, sabedoria e transformação pessoal, inscreva-se no canal!

⏱️ DURAÇÃO: {content['metadata']['estimated_duration_minutes']:.0f} minutos

#EcosDeSabedoria #{theme} #Filosofia

---
Produzido por: Fábrica de Vídeos Autônoma
Data: {datetime.now().strftime('%d/%m/%Y')}
        """.strip()
        
        return description
    
    async def run_daily_schedule(self, num_videos: int = 1):
        """Executa fábrica em modo agendado (para cron)"""
        
        print("\n" + "█"*100)
        print("█" + " "*98 + "█")
        print("█" + f"   🏭 FÁBRICA AUTÔNOMA - EXECUÇÃO AGENDADA ({datetime.now()})   ".center(98) + "█")
        print("█" + " "*98 + "█")
        print("█"*100)
        
        themes = ["estoicismo", "cristianismo", "filosofia", "licoes_de_vida"]
        results = []
        
        for i in range(num_videos):
            theme = themes[i % len(themes)]
            
            print(f"\n[\n{i+1}/{num_videos}] Produzindo vídeo: {theme.upper()}")
            print("█"*100 + "\n")
            
            result = await self.produce_and_publish(
                theme=theme,
                publish=False,  # Modo seco - apenas produção
                privacy_status="unlisted"
            )
            
            results.append(result)
        
        # Resumo final
        print("\n" + "█"*100)
        print("█" + " "*98 + "█")
        print("█" + "   ✅ RESUMO DA EXECUÇÃO AGENDADA   ".center(98) + "█")
        print("█" + " "*98 + "█")
        print("█"*100 + "\n")
        
        successful = sum(1 for r in results if r.get("success"))
        
        print(f"Total de vídeos: {len(results)}")
        print(f"✅ Sucesso: {successful}")
        print(f"❌ Falhas: {len(results) - successful}")
        
        if successful > 0:
            total_time = sum(r.get("total_time_sec", 0) for r in results if r.get("success"))
            avg_time = total_time / successful
            
            print(f"\n⏱️  Tempo total: {total_time:.1f}s ({total_time/60:.2f} min)")
            print(f"⏱️  Tempo médio/vídeo: {avg_time:.1f}s ({avg_time/60:.2f} min)")
            
            total_size = sum(
                r.get("stages", {}).get("editor", {}).get("file_size_mb", 0)
                for r in results
                if r.get("success")
            )
            print(f"💾 Tamanho total: {total_size:.2f} MB")
        
        # Salva log
        output_file = Path(self.config.data_dir) / f"execution_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.file_manager.save_json(str(output_file), {
            "timestamp": datetime.now().isoformat(),
            "videos": results,
            "summary": {
                "total": len(results),
                "successful": successful,
                "failed": len(results) - successful
            }
        })
        
        print(f"\n📁 Log salvo: {output_file.name}\n")


async def main():
    """Main entry point"""
    
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Fábrica de Vídeos Autônoma - Produção Completa"
    )
    
    parser.add_argument(
        "--theme",
        choices=["estoicismo", "cristianismo", "filosofia", "licoes_de_vida", "random"],
        default="random",
        help="Tema do vídeo (padrão: random)"
    )
    
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Publica no YouTube (requer credentials.json)"
    )
    
    parser.add_argument(
        "--privacy",
        choices=["private", "unlisted", "public"],
        default="unlisted",
        help="Status de privacidade no YouTube"
    )
    
    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="Número de vídeos para produzir"
    )
    
    args = parser.parse_args()
    
    factory = FullVideoFactory()
    
    if args.count > 1:
        # Modo agendado
        await factory.run_daily_schedule(args.count)
    else:
        # Modo único
        theme = None if args.theme == "random" else args.theme
        
        result = await factory.produce_and_publish(
            theme=theme,
            publish=args.publish,
            privacy_status=args.privacy
        )
        
        # Exibe resultado final
        print("\n" + "█"*100)
        print("█" + " "*98 + "█")
        print("█" + "   ✅ FÁBRICA DE VÍDEOS CONCLUÍDA COM SUCESSO!   ".center(98) + "█")
        print("█" + " "*98 + "█")
        print("█"*100 + "\n")
        
        if result.get("success"):
            print("📊 RESULTADO FINAL:")
            print(f"   Tema: {result.get('theme')}")
            print(f"   Tempo total: {result.get('total_time_min', 0):.2f} minutos")
            print(f"\n📁 Vídeo: {Path(result['stages']['editor']['output_filename']).name}")
            print(f"   Tamanho: {result['stages']['editor']['file_size_mb']:.2f} MB")
            print(f"   Duração: {result['stages']['editor']['duration_seconds']:.1f}s")
            
            if args.publish and result.get("stages", {}).get("publisher", {}).get("success"):
                print(f"\n🎬 Publicado no YouTube:")
                print(f"   URL: {result['stages']['publisher']['url']}")
            
            print()
        else:
            print(f"❌ Erro: {result.get('error')}\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏸️  Fábrica interrompida pelo usuário")
    except Exception as e:
        logger.error(f"Erro: {e}", exc_info=True)
        print(f"\n❌ Erro: {e}")
