"""
Testes para Orchestrator Agent
"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator_agent import create_orchestrator_agent


async def test_orchestrator_initialization():
    """Testa inicialização do orchestrator"""
    
    print("\n" + "=" * 70)
    print("TEST 1: Inicialização do Orchestrator")
    print("=" * 70)
    
    orchestrator = await create_orchestrator_agent()
    
    assert orchestrator is not None, "Orchestrator não foi criado"
    assert orchestrator.content_agent is not None, "Content agent não inicializado"
    assert orchestrator.audio_agent is not None, "Audio agent não inicializado"
    assert orchestrator.visual_agent is not None, "Visual agent não inicializado"
    assert orchestrator.editor_agent is not None, "Editor agent não inicializado"
    assert orchestrator.publisher_agent is not None, "Publisher agent não inicializado"
    
    print("✅ Todos os agentes foram inicializados com sucesso")
    print(f"   • ContentAgent: {orchestrator.content_agent}")
    print(f"   • AudioAgent: {orchestrator.audio_agent}")
    print(f"   • VisualAgent: {orchestrator.visual_agent}")
    print(f"   • EditorAgent: {orchestrator.editor_agent}")
    print(f"   • PublisherAgent: {orchestrator.publisher_agent}")


async def test_schedule_manager():
    """Testa Schedule Manager"""
    
    print("\n" + "=" * 70)
    print("TEST 2: Schedule Manager")
    print("=" * 70)
    
    orchestrator = await create_orchestrator_agent()
    
    # Verificar agendamento padrão
    schedules = orchestrator.schedule_manager.get_all_schedules()
    print(f"\n✅ Agendamentos configurados: {len(schedules)}")
    
    for sched in schedules:
        print(f"   • {sched['time']} - {sched['theme']} ({sched['description']})")
    
    # Próxima execução
    next_exec = orchestrator.schedule_manager.get_next_execution()
    if next_exec:
        time, theme, desc = next_exec
        print(f"\n✅ Próxima execução: {time} ({theme})")
    
    # Segundos até próxima execução
    seconds = orchestrator.schedule_manager.seconds_until_next_execution()
    if seconds:
        print(f"   Tempo até execução: {seconds}s (~{seconds//60}min)")
    
    print(orchestrator.get_schedule_info())


async def test_health_monitor():
    """Testa Health Monitor"""
    
    print("\n" + "=" * 70)
    print("TEST 3: Health Monitor")
    print("=" * 70)
    
    orchestrator = await create_orchestrator_agent()
    
    # Verificação de saúde
    health = orchestrator.health_monitor.check_system_health()
    print(f"\n✅ Saúde do sistema: {'SAUDÁVEL ✅' if health.healthy else 'PROBLEMAS ⚠️'}")
    
    print(f"   Componentes: {health.components}")
    
    if health.messages:
        print(f"\n   Mensagens:")
        for msg in health.messages:
            print(f"   • {msg}")
    
    if health.alerts:
        print(f"\n   ⚠️ Alertas:")
        for alert in health.alerts:
            print(f"   • {alert}")
    
    # Quotas de API
    quotas = orchestrator.health_monitor.check_api_quotas()
    print(f"\n✅ Quotas de API:")
    for service, quota in quotas.items():
        print(f"   • {service.upper()}: {quota['used']}/{quota['limit']} ({quota['percent']:.0f}%)")
    
    print(orchestrator.get_health_report())


async def test_theme_selection():
    """Testa seleção de temas"""
    
    print("\n" + "=" * 70)
    print("TEST 4: Seleção de Temas")
    print("=" * 70)
    
    orchestrator = await create_orchestrator_agent()
    
    themes = orchestrator.schedule_manager.THEMES
    print(f"\n✅ Temas disponíveis: {len(themes)}")
    for i, theme in enumerate(themes, 1):
        print(f"   {i}. {theme}")
    
    # Simular seleção
    selected = orchestrator._select_next_theme()
    print(f"\n✅ Próximo tema selecionado: {selected}")
    
    # Simular execução de vários temas (teste de rotação)
    print(f"\n✅ Simulando rotação de temas:")
    for i in range(8):
        theme = orchestrator._select_next_theme()
        orchestrator.last_themes_executed.append(theme)
        print(f"   {i+1}. {theme}")


async def test_execution_stats():
    """Testa estatísticas de execução"""
    
    print("\n" + "=" * 70)
    print("TEST 5: Estatísticas de Execução")
    print("=" * 70)
    
    orchestrator = await create_orchestrator_agent()
    
    # Simular execuções
    themes = ["estoicismo", "cristianismo", "filosofia"]
    for theme in themes:
        orchestrator.execution_count += 1
        orchestrator.last_themes_executed.append(theme)
    
    orchestrator._save_execution_stats()
    
    # Recuperar estatísticas
    result = await orchestrator._get_execution_stats({})
    
    assert result["success"], "Falha ao recuperar estatísticas"
    
    stats = result["data"]
    print(f"\n✅ Estatísticas de Execução:")
    print(f"   Total de execuções: {stats['execution_count']}")
    print(f"   Últimos temas: {stats['last_themes']}")
    print(f"   Dados: {stats['statistics']}")


async def test_orchestrator_dry_run():
    """Testa ciclo de produção em modo seco (sem publicação)"""
    
    print("\n" + "=" * 70)
    print("TEST 6: Ciclo de Produção Seco (Dry Run)")
    print("=" * 70)
    print("\n⚠️  ATENÇÃO: Este teste executará o pipeline completo!")
    print("   Irá gerar conteúdo, áudio, imagens, vídeo...")
    print("   NÃO publicará no YouTube")
    
    response = input("\nDeseja continuar? (s/n): ").lower()
    if response != "s":
        print("❌ Teste cancelado")
        return
    
    orchestrator = await create_orchestrator_agent()
    
    result = await orchestrator.execute({
        "action": "run_once",
        "theme": "estoicismo",
        "publish": False  # Sem publicação
    })
    
    if result["success"]:
        print(f"\n✅ Ciclo completado com sucesso!")
        cycle = result["data"].get("cycle_data", {})
        print(f"   Tema: {cycle.get('theme')}")
        print(f"   Duração: {result['data'].get('duration_seconds', 0):.0f}s")
        print(f"   Estágios completados: {len(cycle.get('stages', {}))}")
    else:
        print(f"\n❌ Ciclo falhou: {result['error']}")


async def test_get_stats():
    """Testa recuperação de estatísticas"""
    
    print("\n" + "=" * 70)
    print("TEST 7: Recuperação de Estatísticas")
    print("=" * 70)
    
    orchestrator = await create_orchestrator_agent()
    
    result = await orchestrator.execute({
        "action": "get_stats"
    })
    
    assert result["success"], "Falha ao obter estatísticas"
    
    print(f"✅ Estatísticas obtidas:")
    print(f"   {result['data']}")


async def main():
    """Executa todos os testes"""
    
    print("\n" + "=" * 70)
    print("🏭 TESTES DO ORCHESTRATOR AGENT")
    print("=" * 70)
    
    try:
        await test_orchestrator_initialization()
        await test_schedule_manager()
        await test_health_monitor()
        await test_theme_selection()
        await test_execution_stats()
        await test_get_stats()
        
        # Teste interativo
        print("\n" + "=" * 70)
        print("TESTE 6: Ciclo de Produção (Opcional)")
        print("=" * 70)
        response = input("\nDeseja executar ciclo de produção completo? (s/n): ").lower()
        if response == "s":
            await test_orchestrator_dry_run()
        
        print("\n" + "=" * 70)
        print("✅ TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
        print("=" * 70)
    
    except Exception as e:
        print(f"\n❌ ERRO NOS TESTES: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
