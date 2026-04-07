# Skill: Video Pipeline Orchestration

**Description**: Master the complete video generation pipeline orchestration (Content → Audio → Visual → Editor → Publisher). Use this skill when working with the OrchestratorAgent, coordinating multiple agents, troubleshooting pipeline failures, optimizing execution flow, scheduling video generation runs, monitoring health/stats, or debugging end-to-end video creation workflows.

**Triggers**:

- "How do I orchestrate the video pipeline?"
- "Why is my video generation failing?"
- "How do I schedule 3 videos per day?"
- "How do I monitor pipeline execution?"
- "Pipeline coordination", "agent orchestration", "video workflow"
- "Fix pipeline errors", "debug orchestrator", "optimize execution"

## Key Concepts

### Pipeline Architecture

```
ContentAgent → AudioAgent → VisualAgent → EditorAgent → PublisherAgent
     ↓            ↓            ↓             ↓             ↓
Roteiros      Narração      Imagens      Edição        YouTube
```

### OrchestratorAgent Structure

- **ScheduleManager**: Agendamento automático de execuções (3x/dia)
- **HealthMonitor**: Monitoramento de saúde e estatísticas
- **Pipeline Execution**: Execução sequencial/paralela de agentes
- **Error Recovery**: Try/catch e fallbacks em cada etapa

### Key Files

- `src/agents/orchestrator_agent.py` - Orquestrador principal
- `src/agents/base_agent.py` - Classe base para todos os agentes
- `src/agents/schedule_manager.py` - Agendamento de execuções
- `src/agents/health_monitor.py` - Monitoramento da saúde

## Common Tasks

### Debugging Pipeline Failures

1. **Check Health Monitor**: Revise `health_monitor.py` para entender logs
2. **Identify Failing Agent**: Cada agente retorna status (success/error)
3. **Review Error Logs**: Verifica arquivos em `logs/`
4. **Test Individual Agent**: Execute o agente isoladamente primeiro
5. **Check Data Continuity**: Verifica se outputs de um agente alimentam o próximo

### Optimizing Execution

- **Parallelização**: Alguns agentes como VisualAgent podem rodar em paralelo
- **Caching**: Reutiliza imagens/áudio já gerado quando possível
- **Batch Processing**: Processa múltiplos vídeos na mesma execução
- **Resource Management**: Monitora CPU/memória entre execuções

### Scheduling Configuration

- **Schedule Entry**: Define times para execução automática
- **Retry Logic**: Configure tentativas em caso de falha
- **Max Retries**: Limite máximo de tentativas (default: 3)
- **Timeout Values**: Tempo máximo de execução por agente

## Best Practices

✅ **Always check health_monitor output** before debugging failures  
✅ **Use logging levels** appropriately (DEBUG/INFO/ERROR)  
✅ **Test agents individually** antes de testar pipeline completo  
✅ **Monitor resource usage** durante execução (FFmpeg consome muita RAM)  
✅ **Keep execution history** em `data/orchestrator_stats.json`  
✅ **Implement exponential backoff** para retries automáticos

## Common Issues & Solutions

| Problema              | Causa                     | Solução                                     |
| --------------------- | ------------------------- | ------------------------------------------- |
| Pipeline trava        | FFmpeg ou OutOfMemory     | Reduz resolução ou limita batch size        |
| Agente falha          | API key expirada/inválida | Valida credentials.json e env vars          |
| Videos não publicam   | YouTube quota exceeded    | Aguarda reset diário (00:00 UTC)            |
| Áudio quebrado        | TTS API indisponível      | Ativa fallback para pyttsx3 local           |
| Agendador não executa | Cron job não configurado  | Roda `run_orchestrator_once.py` manualmente |

## Working with the Code

### Running Full Pipeline

```python
from src.agents.orchestrator_agent import OrchestratorAgent

orchestrator = OrchestratorAgent()
result = orchestrator.execute_pipeline()
```

### Monitoring Execution

```python
health_data = orchestrator.health_monitor.get_stats()
print(f"Videos generated: {health_data['total_videos']}")
print(f"Success rate: {health_data['success_rate']}")
```

### Scheduling Configuration

```python
schedule_entry = ScheduleEntry(
    time="08:00",
    interval="daily",
    max_retries=3
)
orchestrator.schedule_manager.add(schedule_entry)
```

## Related Agents/Skills

- **video-agents-architecture** - Individual agent implementation
- **video-audio-synthesis** - Audio/TTS processing
- **video-content-generation** - Content creation
- **video-editing-effects** - Editing and effects
- **youtube-api-publishing** - YouTube publishing
