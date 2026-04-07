"""
Teste de Fábrica Diária - Simula 3 dias de execução automática
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator_agent import create_orchestrator_agent
from schedule_manager import ScheduleEntry, time


class DailyFactorySimulation:
    """Simula 3 dias de operação da fábrica"""
    
    def __init__(self):
        self.orchestrator = None
        self.simulation_log = []
        self.total_videos = 0
        self.total_errors = 0
        self.themes_executed = {}
    
    async def initialize(self):
        """Inicializa simulação"""
        
        print("🏭 Inicializando simulação da fábrica...")
        self.orchestrator = await create_orchestrator_agent()
        print("✅ Orchestrator pronto")
    
    async def simulate_daily_cycle(
        self,
        day_number: int,
        dry_run: bool = True
    ):
        """Simula ciclo diário completo"""
        
        print("\n" + "=" * 70)
        print(f"📅 DIA {day_number} - Ciclo Diário")
        print("=" * 70)
        
        day_log = {
            "day": day_number,
            "date": (datetime.now() + timedelta(days=day_number-1)).isoformat(),
            "executions": [],
            "successful": 0,
            "failed": 0
        }
        
        # Executar 3 vídeos por dia (9h, 14h, 20h)
        for exec_number, schedule_entry in enumerate(
            self.orchestrator.schedule_manager.schedule_entries,
            1
        ):
            if not schedule_entry.enabled:
                continue
            
            print(f"\n[{exec_number}/3] {schedule_entry.description}")
            print(f"      Tema: {schedule_entry.theme}")
            
            execution_log = {
                "time": schedule_entry.time_of_day.isoformat(),
                "theme": schedule_entry.theme,
                "status": "pending",
                "duration": 0
            }
            
            # Simular execução
            if dry_run:
                # Apenas simular, sem executar realmente
                print(f"      [DRY RUN] Executando ciclo...")
                
                # Atualizar tema executado
                if schedule_entry.theme not in self.themes_executed:
                    self.themes_executed[schedule_entry.theme] = 0
                self.themes_executed[schedule_entry.theme] += 1
                
                execution_log["status"] = "success_simulated"
                execution_log["duration"] = 420  # ~7 minutos simulados
                
                print(f"      ✅ Vídeo gerado (simulado)")
                
                day_log["successful"] += 1
                self.total_videos += 1
            
            else:
                # Executar realmente (CUIDADO!)
                print(f"      ⚠️  EXECUTANDO REALMENTE...")
                
                result = await self.orchestrator.execute({
                    "action": "run_once",
                    "theme": schedule_entry.theme,
                    "publish": False  # Não publicar
                })
                
                if result["success"]:
                    execution_log["status"] = "success"
                    execution_log["duration"] = result["data"].get("duration_seconds", 0)
                    
                    print(f"      ✅ Vídeo gerado")
                    
                    day_log["successful"] += 1
                    self.total_videos += 1
                
                else:
                    execution_log["status"] = "failed"
                    execution_log["error"] = result["error"]
                    
                    print(f"      ❌ Erro: {result['error']}")
                    
                    day_log["failed"] += 1
                    self.total_errors += 1
            
            day_log["executions"].append(execution_log)
        
        self.simulation_log.append(day_log)
        
        # Resumo do dia
        print(f"\n📊 Resumo do Dia {day_number}:")
        print(f"   ✅ Sucesso: {day_log['successful']}")
        print(f"   ❌ Erro: {day_log['failed']}")
        print(f"   Total acumulado: {self.total_videos} vídeos gerados")
    
    async def simulate_three_days_dry_run(self):
        """Simula 3 dias em modo seco (recomendado)"""
        
        print("\n" + "=" * 70)
        print("🏭 SIMULAÇÃO DE 3 DIAS (DRY RUN)")
        print("=" * 70)
        print("\nEsta simulação NÃO gera vídeos realmente")
        print("Apenas testa a lógica de agendamento e rotação")
        
        for day in range(1, 4):
            await self.simulate_daily_cycle(day, dry_run=True)
            
            # Simular passar para o próximo dia
            print(f"\n⏳ Aguardando próximo dia...")
            await asyncio.sleep(1)
        
        await self.print_summary()
    
    async def simulate_three_days_real(self):
        """Simula 3 dias com execução REAL (cuidado!)"""
        
        print("\n" + "=" * 70)
        print("⚠️  SIMULAÇÃO DE 3 DIAS (EXECUÇÃO REAL)")
        print("=" * 70)
        print("\n🚨 ATENÇÃO:")
        print("   • Irá GERAR VÍDEOS REALMENTE")
        print("   • Irá criar MUITOS arquivos")
        print("   • Irá consumir quotas de API")
        print("   • Pode levar VÁRIAS HORAS")
        
        response = input("\nTem certeza que deseja continuar? (sim/não): ").lower()
        if response not in ["sim", "yes"]:
            print("❌ Simulação cancelada")
            return
        
        for day in range(1, 4):
            await self.simulate_daily_cycle(day, dry_run=False)
            
            if day < 3:
                print(f"\n⏳ Aguardando próximo dia...")
                # Em produção, seria 24 horas. Para teste, 5s
                await asyncio.sleep(5)
        
        await self.print_summary()
    
    async def test_theme_rotation(self):
        """Testa rotação de temas"""
        
        print("\n" + "=" * 70)
        print("🔄 TESTE: Rotação de Temas")
        print("=" * 70)
        
        themes_sequence = []
        
        # Simular 30 execuções (10 dias de 3 vídeos)
        orchestrator = self.orchestrator
        
        for i in range(30):
            theme = orchestrator._select_next_theme()
            themes_sequence.append(theme)
            orchestrator.last_themes_executed.append(theme)
            
            # Verificar que não há repetição consecutiva
            if i > 0:
                if themes_sequence[i] == themes_sequence[i-1]:
                    print(f"⚠️  Repetição consecutiva detectada: {theme} em sequência")
        
        print(f"\n✅ Sequência de 30 temas gerada:")
        print(f"   {' → '.join(themes_sequence)}")
        
        # Estatísticas
        print(f"\n📊 Distribuição de temas:")
        for theme in orchestrator.schedule_manager.THEMES:
            count = themes_sequence.count(theme)
            print(f"   • {theme}: {count}x")
    
    async def test_health_monitoring(self):
        """Testa monitoramento de saúde durante simulação"""
        
        print("\n" + "=" * 70)
        print("🏥 TESTE: Monitoramento de Saúde")
        print("=" * 70)
        
        for day in range(1, 4):
            print(f"\n📅 Dia {day}:")
            
            health = self.orchestrator.health_monitor.check_system_health()
            
            print(f"   Saúde: {'✅ SAUDÁVEL' if health.healthy else '⚠️ PROBLEMAS'}")
            print(f"   CPU: {health.components['cpu']['percent']:.1f}%")
            print(f"   Memória: {health.components['memory']['percent']:.1f}%")
            
            disk = health.components['disk']
            print(f"   Disco: {disk['free_gb']:.1f}GB livres")
            
            if health.alerts:
                for alert in health.alerts:
                    print(f"   🚨 {alert}")
            
            await asyncio.sleep(1)
    
    async def print_summary(self):
        """Imprime resumo da simulação"""
        
        print("\n" + "=" * 70)
        print("📊 RESUMO DA SIMULAÇÃO")
        print("=" * 70)
        
        print(f"\n✅ Total de vídeos gerados: {self.total_videos}")
        print(f"❌ Total de erros: {self.total_errors}")
        print(f"📊 Taxa de sucesso: {(self.total_videos / (self.total_videos + self.total_errors) * 100) if (self.total_videos + self.total_errors) > 0 else 0:.1f}%")
        
        print(f"\n🔄 Distribuição de temas:")
        for theme, count in sorted(self.themes_executed.items()):
            print(f"   • {theme}: {count}x")
        
        print(f"\n📅 Dias simulados: {len(self.simulation_log)}")
        for day_log in self.simulation_log:
            print(f"   Dia {day_log['day']}: {day_log['date']} - {day_log['successful']} sucesso, {day_log['failed']} erro")
        
        # Salvar log
        import json
        log_file = Path("data") / "simulation_log.json"
        log_file.parent.mkdir(exist_ok=True)
        
        with open(log_file, "w") as f:
            json.dump(self.simulation_log, f, indent=2)
        
        print(f"\n💾 Log salvo em: {log_file}")


async def main():
    """Executa simulação interativa"""
    
    print("\n" + "=" * 70)
    print("🏭 SIMULADOR DE FÁBRICA DIÁRIA")
    print("=" * 70)
    
    simulator = DailyFactorySimulation()
    await simulator.initialize()
    
    print("\nEscolha uma opção:")
    print("1. Simulação 3 dias [DRY RUN] - Recomendado ✅")
    print("2. Simulação 3 dias [REAL] - Gera vídeos realmente ⚠️")
    print("3. Teste de rotação de temas")
    print("4. Teste de monitoramento de saúde")
    print("5. Sair")
    
    while True:
        choice = input("\nOpção (1-5): ").strip()
        
        if choice == "1":
            await simulator.simulate_three_days_dry_run()
            break
        
        elif choice == "2":
            await simulator.simulate_three_days_real()
            break
        
        elif choice == "3":
            await simulator.test_theme_rotation()
            break
        
        elif choice == "4":
            await simulator.test_health_monitoring()
            break
        
        elif choice == "5":
            print("👋 Até logo!")
            break
        
        else:
            print("❌ Opção inválida")


if __name__ == "__main__":
    asyncio.run(main())
