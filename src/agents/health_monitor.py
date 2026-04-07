"""
Health Monitor - Monitor de saúde da fábrica de vídeos
Responsável por: Verificação de sistema, quotas de API, espaço em disco
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import psutil
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.logger import get_logger

logger = get_logger(__name__)


@dataclass
class HealthStatus:
    """Status de saúde do sistema"""
    healthy: bool
    timestamp: str
    components: Dict[str, Any]
    messages: list
    alerts: list


class HealthMonitor:
    """Monitor de saúde da fábrica"""
    
    # Thresholds
    DISK_SPACE_WARNING_GB = 5       # Aviso com < 5GB
    DISK_SPACE_CRITICAL_GB = 2     # Crítico com < 2GB
    CPU_WARNING_PERCENT = 80       # Aviso com > 80% CPU
    CPU_CRITICAL_PERCENT = 95      # Crítico com > 95% CPU
    MEMORY_WARNING_PERCENT = 80    # Aviso com > 80% RAM
    MEMORY_CRITICAL_PERCENT = 90   # Crítico com > 90% RAM
    
    # Quotas de API (exemplo)
    GEMINI_QUOTA_DAILY = 50        # Requisições Gemini/dia (limite)
    THUMBNAIL_QUOTA_DAILY = 50     # Gerações de imagem/dia
    
    def __init__(self, output_dir: Path = None):
        self.logger = logger
        self.output_dir = output_dir or Path("data")
        self.output_dir.mkdir(exist_ok=True)
        self.health_history_file = self.output_dir / "health_history.json"
        self.api_usage_file = self.output_dir / "api_usage.json"
    
    def check_system_health(self) -> HealthStatus:
        """Verifica saúde geral do sistema"""
        
        components = {}
        messages = []
        alerts = []
        
        # Verificar CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        components["cpu"] = {
            "percent": cpu_percent,
            "status": self._status_from_percent(
                cpu_percent,
                self.CPU_WARNING_PERCENT,
                self.CPU_CRITICAL_PERCENT
            )
        }
        
        if cpu_percent > self.CPU_CRITICAL_PERCENT:
            alerts.append(f"⚠️ CPU CRÍTICA: {cpu_percent}%")
        elif cpu_percent > self.CPU_WARNING_PERCENT:
            messages.append(f"📊 CPU elevada: {cpu_percent}%")
        
        # Verificar Memória
        memory = psutil.virtual_memory()
        components["memory"] = {
            "percent": memory.percent,
            "available_gb": memory.available / (1024**3),
            "status": self._status_from_percent(
                memory.percent,
                self.MEMORY_WARNING_PERCENT,
                self.MEMORY_CRITICAL_PERCENT
            )
        }
        
        if memory.percent > self.MEMORY_CRITICAL_PERCENT:
            alerts.append(f"⚠️ MEMÓRIA CRÍTICA: {memory.percent}%")
        elif memory.percent > self.MEMORY_WARNING_PERCENT:
            messages.append(f"📊 Memória elevada: {memory.percent}%")
        
        # Verificar Disco
        disk = psutil.disk_usage("/")
        disk_free_gb = disk.free / (1024**3)
        components["disk"] = {
            "percent_used": disk.percent,
            "free_gb": disk_free_gb,
            "total_gb": disk.total / (1024**3),
            "status": self._status_from_disk_gb(disk_free_gb)
        }
        
        if disk_free_gb < self.DISK_SPACE_CRITICAL_GB:
            alerts.append(f"⚠️ DISCO CRÍTICO: {disk_free_gb:.1f}GB livre")
        elif disk_free_gb < self.DISK_SPACE_WARNING_GB:
            messages.append(f"📊 Espaço em disco baixo: {disk_free_gb:.1f}GB")
        
        # Verificar diretórios de saída
        output_sizes = self._check_output_directories()
        components["output_sizes"] = output_sizes
        
        # Determinar saúde geral
        healthy = len(alerts) == 0
        
        status = HealthStatus(
            healthy=healthy,
            timestamp=datetime.now().isoformat(),
            components=components,
            messages=messages,
            alerts=alerts
        )
        
        return status
    
    def check_api_quotas(self) -> Dict[str, Any]:
        """Verifica quotas de API"""
        
        usage = self._load_api_usage()
        today = datetime.now().date().isoformat()
        
        if today not in usage:
            usage[today] = {
                "gemini_requests": 0,
                "image_generations": 0,
                "youtube_uploads": 0
            }
        
        today_usage = usage[today]
        
        quotas = {
            "gemini": {
                "used": today_usage["gemini_requests"],
                "limit": self.GEMINI_QUOTA_DAILY,
                "percent": (today_usage["gemini_requests"] / self.GEMINI_QUOTA_DAILY) * 100,
                "available": max(0, self.GEMINI_QUOTA_DAILY - today_usage["gemini_requests"])
            },
            "images": {
                "used": today_usage["image_generations"],
                "limit": self.THUMBNAIL_QUOTA_DAILY,
                "percent": (today_usage["image_generations"] / self.THUMBNAIL_QUOTA_DAILY) * 100,
                "available": max(0, self.THUMBNAIL_QUOTA_DAILY - today_usage["image_generations"])
            },
            "youtube": {
                "used": today_usage["youtube_uploads"],
                "limit": 50,  # YouTube permite ~50 uploads/dia
                "percent": (today_usage["youtube_uploads"] / 50) * 100,
                "available": max(0, 50 - today_usage["youtube_uploads"])
            }
        }
        
        return quotas
    
    def record_api_usage(
        self,
        service: str,  # "gemini", "images", "youtube"
        count: int = 1
    ):
        """Registra uso de API"""
        
        usage = self._load_api_usage()
        today = datetime.now().date().isoformat()
        
        if today not in usage:
            usage[today] = {
                "gemini_requests": 0,
                "image_generations": 0,
                "youtube_uploads": 0
            }
        
        if service == "gemini":
            usage[today]["gemini_requests"] += count
        elif service == "images":
            usage[today]["image_generations"] += count
        elif service == "youtube":
            usage[today]["youtube_uploads"] += count
        
        self._save_api_usage(usage)
        logger.debug(f"Uso de API registrado: {service} +{count}")
    
    def _check_output_directories(self) -> Dict[str, float]:
        """Verifica tamanho dos diretórios de saída"""
        
        sizes = {}
        
        dirs_to_check = ["output", "data", "cache"]
        
        for dir_name in dirs_to_check:
            dir_path = Path(dir_name)
            if dir_path.exists():
                size_mb = self._get_directory_size(dir_path) / (1024**2)
                sizes[dir_name] = round(size_mb, 2)
        
        return sizes
    
    def _get_directory_size(self, path: Path) -> int:
        """Calcula tamanho total de um diretório"""
        
        total = 0
        try:
            for entry in path.rglob("*"):
                if entry.is_file():
                    total += entry.stat().st_size
        except Exception as e:
            logger.warning(f"Erro ao calcular tamanho de {path}: {e}")
        
        return total
    
    def _status_from_percent(
        self,
        percent: float,
        warning: float,
        critical: float
    ) -> str:
        """Mapeia porcentagem para status"""
        
        if percent >= critical:
            return "critical"
        elif percent >= warning:
            return "warning"
        else:
            return "healthy"
    
    def _status_from_disk_gb(self, free_gb: float) -> str:
        """Mapeia espaço livre em disco para status"""
        
        if free_gb < self.DISK_SPACE_CRITICAL_GB:
            return "critical"
        elif free_gb < self.DISK_SPACE_WARNING_GB:
            return "warning"
        else:
            return "healthy"
    
    def _load_api_usage(self) -> Dict[str, Dict[str, int]]:
        """Carrega histórico de uso de API"""
        
        if self.api_usage_file.exists():
            try:
                with open(self.api_usage_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Erro ao carregar uso de API: {e}")
        
        return {}
    
    def _save_api_usage(self, usage: Dict[str, Dict[str, int]]):
        """Salva histórico de uso de API"""
        
        try:
            with open(self.api_usage_file, "w") as f:
                json.dump(usage, f, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar uso de API: {e}")
    
    def save_health_report(self, status: HealthStatus):
        """Salva relatório de saúde"""
        
        try:
            history = []
            if self.health_history_file.exists():
                with open(self.health_history_file, "r") as f:
                    history = json.load(f)
            
            report = {
                "timestamp": status.timestamp,
                "healthy": status.healthy,
                "components": status.components,
                "messages": status.messages,
                "alerts": status.alerts
            }
            
            history.append(report)
            
            # Manter últimas 100 leituras
            history = history[-100:]
            
            with open(self.health_history_file, "w") as f:
                json.dump(history, f, indent=2)
            
            logger.debug("Relatório de saúde salvo")
        
        except Exception as e:
            logger.error(f"Erro ao salvar relatório: {e}")
    
    def format_health_report(self, status: HealthStatus) -> str:
        """Formata relatório de saúde para exibição"""
        
        health_icon = "✅" if status.healthy else "⚠️"
        
        output = f"\n{health_icon} SAÚDE DO SISTEMA ({status.timestamp})\n"
        output += "─" * 60 + "\n"
        
        cpu = status.components["cpu"]
        output += f"CPU:      {cpu['percent']:>6.1f}% [{self._status_bar(cpu['percent'])}]\n"
        
        mem = status.components["memory"]
        output += f"Memória:  {mem['percent']:>6.1f}% [{self._status_bar(mem['percent'])}]\n"
        
        disk = status.components["disk"]
        output += f"Disco:    {disk['percent_used']:>6.1f}% ({disk['free_gb']:>6.1f}GB livres) [{self._status_bar(disk['percent_used'])}]\n"
        
        if status.messages:
            output += "\n📋 Mensagens:\n"
            for msg in status.messages:
                output += f"  • {msg}\n"
        
        if status.alerts:
            output += "\n🚨 Alertas:\n"
            for alert in status.alerts:
                output += f"  • {alert}\n"
        
        output += "─" * 60
        
        return output
    
    def _status_bar(self, percent: float, width: int = 20) -> str:
        """Cria barra de status visual"""
        
        filled = int(percent / 100 * width)
        bar = "█" * filled + "░" * (width - filled)
        return bar
