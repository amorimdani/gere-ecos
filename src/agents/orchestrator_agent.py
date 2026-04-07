"""
Orchestrator Agent - Orquestração completa da fábrica de vídeos
Responsável por: Coordenação de todos os agentes, agendamento, monitoramento
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import asyncio
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from .base_agent import BaseAgent
from .content_agent import create_content_agent
from .audio_agent import create_audio_agent
from .visual_agent import create_visual_agent
from .editor_agent import create_editor_agent
from .publisher_agent import create_publisher_agent
from .schedule_manager import ScheduleManager, ScheduleEntry
from .health_monitor import HealthMonitor
from config.logger import get_logger
from utils import FileManager

logger = get_logger(__name__)


class OrchestratorAgent(BaseAgent):
    """
    Agente orquestrador - coordena todo o pipeline C→A→V→E→P
    Responsável por: Agendamento, monitoramento, execução coordenada
    """
    
    def __init__(self):
        super().__init__(agent_name="OrchestratorAgent")
        
        self.schedule_manager = ScheduleManager()
        self.health_monitor = HealthMonitor()
        self.file_manager = FileManager()
        
        # Agentes do pipeline
        self.content_agent = None
        self.audio_agent = None
        self.visual_agent = None
        self.editor_agent = None
        self.publisher_agent = None
        
        # Estado
        self.execution_count = 0
        self.last_themes_executed = []
        self.stats_file = Path("data") / "orchestrator_stats.json"
        
        logger.info("OrchestratorAgent inicializado")
    
    async def initialize_agents(self):
        """Inicializa todos os agentes do pipeline"""
        
        logger.info("Inicializando agentes do pipeline...")
        
        try:
            self.content_agent = create_content_agent()
            self.audio_agent = create_audio_agent()
            self.visual_agent = create_visual_agent()
            self.editor_agent = create_editor_agent()
            self.publisher_agent = create_publisher_agent()
            
            logger.info("✅ Todos os agentes inicializados")
            return True
        
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar agentes: {e}")
            return False
    
    async def execute(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Executa orquestração completa
        
        Params:
            - action: "run_once", "check_schedule", "health_check", "get_stats"
            - theme: tema específico (opcional)
            - publish: publicar no YouTube? (default: True)
        """
        
        params = params or {}
        action = params.get("action", "run_once")
        
        if action == "run_once":
            return await self._run_production_cycle(params)
        
        elif action == "check_schedule":
            return await self._check_and_execute_schedule(params)
        
        elif action == "health_check":
            return await self._perform_health_check(params)
        
        elif action == "get_stats":
            return await self._get_execution_stats(params)
        
        else:
            return {
                "success": False,
                "data": {},
                "error": f"Ação desconhecida: {action}"
            }
    
    async def _run_production_cycle(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Executa um ciclo completo de produção C→A→V→E→P"""
        
        logger.info("=" * 70)
        logger.info("🏭 INICIANDO CICLO DE PRODUÇÃO")
        logger.info("=" * 70)
        
        cycle_start = datetime.now()
        
        # Verificar saúde do sistema
        health = self.health_monitor.check_system_health()
        if not health.healthy:
            logger.warning(f"⚠️ Sistema com problemas: {health.alerts}")
            if len(health.alerts) > 2:
                return {
                    "success": False,
                    "data": {"health_status": health.__dict__},
                    "error": "Sistema com problemas críticos"
                }
        
        # Obter tema
        theme = params.get("theme")
        if not theme:
            theme = self._select_next_theme()
        
        logger.info(f"📌 Tema selecionado: {theme}")
        
        # Inicializar agentes se necessário
        if not self.content_agent:
            await self.initialize_agents()
        
        cycle_data = {
            "cycle_id": f"{datetime.now().isoformat()}",
            "theme": theme,
            "stages": {}
        }
        
        try:
            # STAGE 1: Conteúdo
            logger.info("\n[1/5] Gerando conteúdo...")
            content_data = await self.content_agent.execute({
                "theme": theme
            })
            cycle_data["stages"]["content"] = {"data": content_data}
            logger.info("✅ Conteúdo gerado")
            
            # STAGE 2: Áudio
            logger.info("\n[2/5] Gerando áudio...")
            audio_result = await self.audio_agent.execute({
                "script": content_data.get("script", ""),
                "video_title": content_data.get("title", f"Video sobre {theme}"),
                "expected_duration_minutes": 11  # 11 minutos para ficar entre 10-12 min
            })
            cycle_data["stages"]["audio"] = {"data": audio_result}
            logger.info("✅ Áudio gerado")
            
            # STAGE 3: Visual
            logger.info("\n[3/5] Gerando imagens...")
            visual_result = await self.visual_agent.execute({
                "theme": content_data.get("theme", theme),
                "scenes": content_data.get("scenes", [])
            })
            cycle_data["stages"]["visual"] = {"data": visual_result}
            logger.info("✅ Imagens geradas")
            
            # STAGE 4: Edição
            logger.info("\n[4/5] Editando vídeo...")
            editor_result = await self.editor_agent.execute({
                "audio_path": audio_result.get("audio_path", ""),
                "scenes": visual_result.get("scenes", []),
                "video_title": content_data.get("title", f"Video sobre {theme}"),
                "theme": content_data.get("theme", theme),
                "add_transitions": True,
                "add_subtitles": True,
                "use_ken_burns": True
            })
            
            if not editor_result["success"]:
                raise Exception(f"Erro ao editar vídeo: {editor_result['error']}")
            
            cycle_data["stages"]["editor"] = editor_result
            logger.info("✅ Vídeo editado")
            
            # STAGE 5: Publicação
            publish = params.get("publish", True)
            
            if publish:
                logger.info("\n[5/5] Publicando no YouTube...")
                
                publisher_result = await self.publisher_agent.execute({
                    "video_path": editor_result["data"].get("output_filename", ""),
                    "title": content_data.get("title", "Video"),
                    "description": f"{content_data.get('description', '')}\n\nTema: {theme}",
                    "tags": content_data.get("tags", []),
                    "theme": theme
                })
                
                if not publisher_result["success"]:
                    logger.warning(f"⚠️ Erro ao publicar: {publisher_result['error']}")
                else:
                    cycle_data["stages"]["publisher"] = publisher_result
                    logger.info("✅ Vídeo publicado")
            else:
                logger.info("\n[5/5] Publicação desativada - pulando...")
            
            # Registrar execução
            self.execution_count += 1
            self.last_themes_executed.append(theme)
            self._save_execution_stats()
            
            cycle_end = datetime.now()
            delta = (cycle_end - cycle_start).total_seconds()
            
            logger.info("\n" + "=" * 70)
            logger.info(f"✅ CICLO CONCLUÍDO COM SUCESSO (~{delta:.0f}s)")
            logger.info("=" * 70)
            
            return {
                "success": True,
                "data": {
                    "cycle_data": cycle_data,
                    "duration_seconds": delta,
                    "execution_count": self.execution_count
                },
                "error": ""
            }
        
        except Exception as e:
            logger.error(f"\n❌ ERRO NO CICLO: {e}")
            logger.error("=" * 70)
            
            return {
                "success": False,
                "data": {
                    "cycle_data": cycle_data,
                    "stages_completed": len(cycle_data["stages"])
                },
                "error": str(e)
            }
    
    async def _check_and_execute_schedule(
        self,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Verifica agendamento e executa se necessário"""
        
        should_execute = self.schedule_manager.should_execute_now(
            threshold_seconds=params.get("threshold_seconds", 60)
        )
        
        if should_execute:
            _, theme, description = should_execute
            logger.info(f"🕐 Hora agendada: {description}")
            
            return await self._run_production_cycle({
                "theme": theme,
                "publish": params.get("publish", True)
            })
        
        return {
            "success": True,
            "data": {
                "executed": False,
                "next_execution": self.schedule_manager.get_next_execution()
            },
            "error": ""
        }
    
    async def _perform_health_check(
        self,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Realiza verificação de saúde do sistema"""
        
        logger.info("🏥 Verificando saúde do sistema...")
        
        health_status = self.health_monitor.check_system_health()
        api_quotas = self.health_monitor.check_api_quotas()
        
        # Salvar relatório
        self.health_monitor.save_health_report(health_status)
        
        return {
            "success": health_status.healthy,
            "data": {
                "system": {
                    "healthy": health_status.healthy,
                    "components": health_status.components,
                    "messages": health_status.messages,
                    "alerts": health_status.alerts
                },
                "api_quotas": api_quotas
            },
            "error": "Problemas detectados" if health_status.alerts else ""
        }
    
    async def _get_execution_stats(
        self,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Retorna estatísticas de execução"""
        
        try:
            stats = {}
            
            if self.stats_file.exists():
                with open(self.stats_file, "r") as f:
                    stats = json.load(f)
            
            return {
                "success": True,
                "data": {
                    "execution_count": self.execution_count,
                    "last_themes": self.last_themes_executed[-10:],
                    "statistics": stats
                },
                "error": ""
            }
        
        except Exception as e:
            return {
                "success": False,
                "data": {},
                "error": str(e)
            }
    
    def _select_next_theme(self) -> str:
        """Seleciona próximo tema (rotação, sem repetição consecutiva)"""
        
        available_themes = self.schedule_manager.THEMES.copy()
        
        # Remover último tema para não repetir
        if self.last_themes_executed:
            last = self.last_themes_executed[-1]
            if last in available_themes:
                available_themes.remove(last)
        
        # Preferivelmente usar o tema da hora
        now_hour = datetime.now().hour
        time_schedules = self.schedule_manager.get_all_schedules()
        
        for schedule in time_schedules:
            sched_hour = int(schedule["time"].split(":")[0])
            if sched_hour == now_hour:
                theme = schedule["theme"]
                if theme in available_themes:
                    return theme
        
        # Se não encontrou por hora, usar o primeiro disponível
        return available_themes[0] if available_themes else "estoicismo"
    
    def _save_execution_stats(self):
        """Salva estatísticas de execução"""
        
        try:
            stats = {
                "total_executions": self.execution_count,
                "last_execution": datetime.now().isoformat(),
                "themes_executed": self.last_themes_executed[-100:],
                "created_at": datetime.now().isoformat()
            }
            
            self.stats_file.parent.mkdir(exist_ok=True)
            
            with open(self.stats_file, "w") as f:
                json.dump(stats, f, indent=2)
            
            logger.debug("Estatísticas salvas")
        
        except Exception as e:
            logger.error(f"Erro ao salvar estatísticas: {e}")
    
    def get_schedule_info(self) -> str:
        """Retorna informações de agendamento formatado"""
        return self.schedule_manager.format_schedule_for_display()
    
    def get_health_report(self) -> str:
        """Retorna relatório de saúde formatado"""
        
        status = self.health_monitor.check_system_health()
        return self.health_monitor.format_health_report(status)
    
    def set_custom_schedule(self, times: list):
        """Define agendamento customizado
        
        times: lista de {"time": "HH:MM:SS", "theme": "tema"}
        """
        
        entries = [
            ScheduleEntry(
                time_of_day=entry["time"],
                theme=entry["theme"],
                description=f"{entry['time']} - {entry['theme']}"
            )
            for entry in times
        ]
        
        self.schedule_manager.set_custom_schedule(entries)


async def create_orchestrator_agent() -> OrchestratorAgent:
    """Factory para criar OrchestratorAgent"""
    
    agent = OrchestratorAgent()
    await agent.initialize_agents()
    return agent
