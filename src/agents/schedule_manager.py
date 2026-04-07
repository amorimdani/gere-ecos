"""
Schedule Manager - Gerenciador de agendamentos da fábrica
Responsável por: Timing, rotação de temas, execução agendada
"""

import sys
from pathlib import Path
from typing import List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, time, timedelta
import schedule
import asyncio

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ScheduleEntry:
    """Entrada de agendamento"""
    time_of_day: time          # Hora para executar (HH:MM:SS)
    theme: str                 # Tema para este horário
    description: str           # Descrição
    enabled: bool = True       # Agendamento ativo?


class ScheduleManager:
    """Gerenciador de agendamentos para fábrica de vídeos"""
    
    # Temas disponíveis (rotação)
    THEMES = ["estoicismo", "cristianismo", "filosofia", "licoes_de_vida"]
    
    def __init__(self):
        self.logger = logger
        self.schedule_entries: List[ScheduleEntry] = []
        self.last_execution = {}
        self._build_default_schedule()
    
    def _build_default_schedule(self):
        """Constrói agendamento padrão: 3 vídeos/dia (9h, 14h, 20h)"""
        
        self.schedule_entries = [
            ScheduleEntry(
                time_of_day=time(9, 0, 0),
                theme="estoicismo",
                description="Manhã - Estoicismo",
                enabled=True
            ),
            ScheduleEntry(
                time_of_day=time(14, 0, 0),
                theme="cristianismo",
                description="Tarde - Cristianismo",
                enabled=True
            ),
            ScheduleEntry(
                time_of_day=time(20, 0, 0),
                theme="filosofia",
                description="Noite - Filosofia",
                enabled=True
            )
        ]
        
        logger.info("Agendamento padrão criado: 3 vídeos/dia")
        for entry in self.schedule_entries:
            logger.info(
                f"  • {entry.time_of_day} - {entry.theme} "
                f"({'ativo' if entry.enabled else 'inativo'})"
            )
    
    def set_custom_schedule(self, entries: List[ScheduleEntry]):
        """Define agendamento customizado"""
        
        self.schedule_entries = entries
        logger.info(f"Agendamento customizado: {len(entries)} entrada(s)")
    
    def get_next_execution(self) -> Optional[tuple]:
        """
        Retorna próxima execução agendada
        
        Returns:
            (time_of_day: time, theme: str, description: str) ou None
        """
        
        now = datetime.now().time()
        
        # Procura próxima execução hoje
        for entry in self.schedule_entries:
            if entry.enabled and entry.time_of_day > now:
                return (entry.time_of_day, entry.theme, entry.description)
        
        # Se nenhuma hoje, primeira do próximo dia
        if self.schedule_entries:
            first = next(
                (e for e in self.schedule_entries if e.enabled),
                None
            )
            if first:
                tomorrow = datetime.now() + timedelta(days=1)
                return (first.time_of_day, first.theme, first.description)
        
        return None
    
    def get_all_schedules(self) -> List[dict]:
        """Retorna todas as execuções agendadas"""
        
        return [
            {
                "time": entry.time_of_day.isoformat(),
                "theme": entry.theme,
                "description": entry.description,
                "enabled": entry.enabled
            }
            for entry in self.schedule_entries
        ]
    
    def seconds_until_next_execution(self) -> Optional[int]:
        """Calcula segundos até próxima execução"""
        
        next_exec = self.get_next_execution()
        
        if not next_exec:
            return None
        
        scheduled_time = next_exec[0]
        now = datetime.now().time()
        
        scheduled_dt = datetime.combine(datetime.now().date(), scheduled_time)
        now_dt = datetime.combine(datetime.now().date(), now)
        
        if scheduled_dt <= now_dt:
            # Próxima execução é amanhã
            scheduled_dt = datetime.combine(
                datetime.now().date() + timedelta(days=1),
                scheduled_time
            )
        
        delta = (scheduled_dt - datetime.now()).total_seconds()
        return max(0, int(delta))
    
    def should_execute_now(self, threshold_seconds: int = 60) -> Optional[tuple]:
        """
        Verifica se deve executar agora (dentro do threshold)
        
        Args:
            threshold_seconds: Margem de tempo (padrão: 60s)
        
        Returns:
            (time_of_day, theme, description) se deve executar, None caso contrário
        """
        
        now = datetime.now().time()
        
        for entry in self.schedule_entries:
            if not entry.enabled:
                continue
            
            # Calcula diferença com margem
            entry_dt = datetime.combine(datetime.now().date(), entry.time_of_day)
            now_dt = datetime.combine(datetime.now().date(), now)
            
            diff = abs((entry_dt - now_dt).total_seconds())
            
            # Se dentro do threshold e não foi executado hoje
            if diff <= threshold_seconds:
                key = f"{entry.time_of_day}_{datetime.now().date()}"
                
                if key not in self.last_execution:
                    self.last_execution[key] = True
                    logger.info(f"Hora de executar: {entry.description}")
                    return (entry.time_of_day, entry.theme, entry.description)
        
        return None
    
    def format_schedule_for_display(self) -> str:
        """Formata agendamento para exibição"""
        
        output = "\n📅 AGENDAMENTO DA FÁBRICA:\n"
        output += "─" * 60 + "\n"
        
        for entry in self.schedule_entries:
            status = "✅" if entry.enabled else "❌"
            output += f"{status} {entry.time_of_day} → {entry.theme:15} ({entry.description})\n"
        
        output += "─" * 60
        
        return output


class Scheduler:
    """Wrapper para library schedule (agendamento em polling)"""
    
    def __init__(self, schedule_manager: ScheduleManager):
        self.schedule_manager = schedule_manager
        self.jobs = {}
    
    async def add_job(
        self,
        task_func: Callable,
        entry: ScheduleEntry
    ):
        """Adiciona job de execução"""
        
        hour = entry.time_of_day.hour
        minute = entry.time_of_day.minute
        
        job = schedule.at(f"{hour:02d}:{minute:02d}").do(task_func)
        
        key = f"{entry.time_of_day}_{entry.theme}"
        self.jobs[key] = job
        
        logger.info(
            f"Job agendado: {entry.time_of_day} - {entry.theme}"
        )
    
    async def run_pending(self):
        """Executa jobs pendentes"""
        schedule.run_pending()
    
    async def clear_jobs(self):
        """Remove todos os jobs"""
        schedule.clear()
        self.jobs.clear()
        logger.info("Todos os jobs foram removidos")
    
    def get_jobs_info(self) -> list:
        """Retorna informações dos jobs"""
        
        return [
            {
                "schedule": str(job),
                "next_run": job.next_run.isoformat() if job.next_run else None
            }
            for job in schedule.get_jobs()
        ]
