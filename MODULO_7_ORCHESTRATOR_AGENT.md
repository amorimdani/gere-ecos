# MÓDULO 7: ORCHESTRATOR AGENT - Automatização Completa 🏭

## Visão Geral

O Módulo 7 é o **núcleo de automatização** da fábrica de vídeos. Implementa:

- **Agendamento automático**: 3 vídeos/dia em horários fixos (9h, 14h, 20h)
- **Orquestração do pipeline**: Coordena C→A→V→E→P em sequência
- **Monitoramento de saúde**: Verifica CPU, RAM, disco, quotas de API
- **Rotação de temas**: Garante variedade sem repetição consecutiva
- **Persistência de histórico**: Rastreia todas as execuções

## Arquitetura

```
┌─────────────────────────────────────────────────┐
│         ORCHESTRATOR AGENT (módulo 7)           │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌─────────────────┐  ┌──────────────────────┐ │
│  │ScheduleManager  │  │ HealthMonitor        │ │
│  ├─────────────────┤  ├──────────────────────┤ │
│  │• Agendamentos   │  │• CPU/RAM/Disco       │ │
│  │• Rotação temas  │  │• Quotas API          │ │
│  │• Próxima exec.  │  │• Relatórios de saúde │ │
│  └─────────────────┘  └──────────────────────┘ │
│          ▼                       ▼              │
│  ┌──────────────────────────────────────────┐  │
│  │   Agentes do Pipeline (C→A→V→E→P)       │  │
│  ├──────────────────────────────────────────┤  │
│  │ 1. ContentAgent    → Roteiro/Script      │  │
│  │ 2. AudioAgent      → MP3 Síntese         │  │
│  │ 3. VisualAgent     → Imagens             │  │
│  │ 4. EditorAgent     → Vídeo MP4           │  │
│  │ 5. PublisherAgent  → Upload YouTube      │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
└─────────────────────────────────────────────────┘
```

## Componentes Principais

### 1. ScheduleManager

Gerencia agendamentos da fábrica.

#### Classes

```python
@dataclass
class ScheduleEntry:
    time_of_day: time       # HH:MM:SS para executar
    theme: str              # Tema a usar
    description: str        # Descrição amigável
    enabled: bool = True    # Ativo?

class ScheduleManager:
    # Temas disponíveis (rotação)
    THEMES = ["estoicismo", "cristianismo", "filosofia", "licoes_de_vida"]

    def __init__(self)
    def _build_default_schedule(self)           # Padrão: 9h, 14h, 20h
    def set_custom_schedule(entries)            # Customizar agendamento
    def get_next_execution(self)                # Próxima execução
    def get_all_schedules(self)                 # Listar todos
    def seconds_until_next_execution(self)      # Tempo até próxima
    def should_execute_now(threshold_seconds)   # Validar hora?
    def format_schedule_for_display(self)       # Formatado

class Scheduler:  # Wrapper para schedule library
    def __init__(schedule_manager)
    async def add_job(task_func, entry)
    async def run_pending(self)
    async def clear_jobs(self)
    def get_jobs_info(self)
```

#### Exemplo de Uso

```python
from schedule_manager import ScheduleManager

# Usar agendamento padrão (9h, 14h, 20h)
schedule_mgr = ScheduleManager()

# Verificar horário
print(schedule_mgr.format_schedule_for_display())

# Próxima execução
next_exec = schedule_mgr.get_next_execution()
if next_exec:
    time, theme, desc = next_exec
    print(f"Próxima: {time} ({theme})")

# Tempo até próxima (em segundos)
seconds = schedule_mgr.seconds_until_next_execution()
print(f"{seconds}s até próxima execução")

# Verificar se está na hora
should_run = schedule_mgr.should_execute_now(threshold_seconds=60)
if should_run:
    _, theme, desc = should_run
    print(f"Executar agora: {theme}")
```

### 2. HealthMonitor

Monitora saúde do sistema.

#### Classes

```python
@dataclass
class HealthStatus:
    healthy: bool
    timestamp: str
    components: Dict[str, Any]  # CPU, RAM, Disco
    messages: list              # Avisos
    alerts: list                # Problemas críticos

class HealthMonitor:
    # Thresholds
    DISK_SPACE_WARNING_GB = 5       # < 5GB = aviso
    DISK_SPACE_CRITICAL_GB = 2     # < 2GB = crítico
    CPU_WARNING_PERCENT = 80       # > 80% = aviso
    CPU_CRITICAL_PERCENT = 95      # > 95% = crítico
    MEMORY_WARNING_PERCENT = 80
    MEMORY_CRITICAL_PERCENT = 90

    def __init__(output_dir)
    def check_system_health(self)               # CPU, RAM, Disco
    def check_api_quotas(self)                  # Gemini, Imagens, YouTube
    def record_api_usage(service, count)        # Registrar uso
    def save_health_report(status)              # Salvar histórico
    def format_health_report(status)            # Formatado
```

#### Exemplo de Uso

```python
from health_monitor import HealthMonitor

health_monitor = HealthMonitor()

# Verificação de saúde
status = health_monitor.check_system_health()

if status.healthy:
    print("✅ Sistema OK")
else:
    print("⚠️ Problemas detectados:")
    for alert in status.alerts:
        print(f"  • {alert}")

# Quotas de API
quotas = health_monitor.check_api_quotas()

print(f"Gemini: {quotas['gemini']['used']}/{quotas['gemini']['limit']}")
print(f"Imagens: {quotas['images']['used']}/{quotas['images']['limit']}")

# Registrar uso
health_monitor.record_api_usage("gemini", count=1)
health_monitor.record_api_usage("images", count=3)

# Exibir relatório formatado
print(health_monitor.format_health_report(status))
```

### 3. OrchestratorAgent

Orquestra todo o pipeline.

#### Métodos Principais

```python
class OrchestratorAgent(BaseAgent):
    async def initialize_agents(self)
        # Inicializa todos os 5 agentes

    async def execute(params) → Dict
        # Ações: "run_once", "check_schedule", "health_check", "get_stats"

        # "run_once": Executa 1 ciclo completo C→A→V→E→P
        # "check_schedule": Verifica se deve executar agora
        # "health_check": Verifica saúde do sistema
        # "get_stats": Retorna estatísticas

    async def _run_production_cycle(params)
        # 1. Verificar saúde
        # 2. Seleciona tema
        # 3. Executa C→A→V→E→P em sequência
        # 4. Salva histórico

    def _select_next_theme()
        # Rotação de temas (sem repetição consecutiva)

    def get_schedule_info()
        # Horários agendados formatados

    def get_health_report()
        # Saúde formatada
```

#### Exemplo de Uso

```python
from orchestrator_agent import create_orchestrator_agent

# Criar (inicializa-se automaticamente)
orchestrator = await create_orchestrator_agent()

# Ver agendamento
print(orchestrator.get_schedule_info())

# Ver saúde
print(orchestrator.get_health_report())

# Executar 1 ciclo
result = await orchestrator.execute({
    "action": "run_once",
    "theme": "estoicismo",  # Opcional, se não especificado seleciona automaticamente
    "publish": False         # Não publicar (apenas testar)
})

if result["success"]:
    print(f"✅ Vídeo gerado em {result['data']['duration_seconds']}s")
else:
    print(f"❌ Erro: {result['error']}")

# Verificar agendamento e executar se necessário
result = await orchestrator.execute({
    "action": "check_schedule"
})

# Verificar saúde
result = await orchestrator.execute({
    "action": "health_check"
})

print(result["data"]["system"]["components"])

# Obter estatísticas
result = await orchestrator.execute({
    "action": "get_stats"
})
print(f"Total de vídeos: {result['data']['execution_count']}")
```

## Instalação e Configuração

### 1. Dependências

```bash
pip install psutil schedule google-auth-oauthlib google-api-python-client
```

Todas já estão em `requirements.txt`.

### 2. Estrutura de Diretórios

```
src/agents/
├── __init__.py                    # Exports (ATUALIZADO)
├── schedule_manager.py            # ScheduleManager + Scheduler
├── health_monitor.py              # HealthMonitor + HealthStatus
├── orchestrator_agent.py          # OrchestratorAgent
├── test_orchestrator_agent.py     # Testes unitários
├── test_daily_factory.py          # Simulação 3 dias
└── (outros 12 arquivos de módulos 1-6)

data/
├── orchestrator_stats.json        # Estatísticas de execução
├── api_usage.json                 # Histórico de quotas
├── health_history.json            # Histórico de saúde
└── simulation_log.json            # Log da simulação
```

### 3. Primeiro Uso

```bash
cd src/agents

# Ver informações
python test_orchestrator_agent.py

# Selecione opção 1-2 para testes
```

## Casos de Uso

### Caso 1: Executar 1 Ciclo Manualmente

```python
import asyncio
from orchestrator_agent import create_orchestrator_agent

async def main():
    orchestrator = await create_orchestrator_agent()

    # Executar Estoicismo sem publicar
    result = await orchestrator.execute({
        "action": "run_once",
        "theme": "estoicismo",
        "publish": False
    })

    print(f"Sucesso: {result['success']}")
    print(f"Duração: {result['data']['duration_seconds']:.0f}s")

asyncio.run(main())
```

### Caso 2: Agendamento em Tempo Real

```python
import asyncio
import time
from orchestrator_agent import create_orchestrator_agent

async def scheduler_loop():
    orchestrator = await create_orchestrator_agent()

    print(orchestrator.get_schedule_info())

    while True:
        # Verificar a cada minuto
        result = await orchestrator.execute({
            "action": "check_schedule",
            "threshold_seconds": 60
        })

        if result["data"]["executed"]:
            print("✅ Ciclo executado!")

        # Aguardar 1 minuto
        await asyncio.sleep(60)

asyncio.run(scheduler_loop())
```

### Caso 3: Monitoramento Contínuo

```python
import asyncio
from orchestrator_agent import create_orchestrator_agent

async def monitor_loop():
    orchestrator = await create_orchestrator_agent()

    while True:
        # Verificar saúde a cada 5 minutos
        result = await orchestrator.execute({
            "action": "health_check"
        })

        system = result["data"]["system"]

        if not system["healthy"]:
            print("🚨 PROBLEMAS DETECTADOS:")
            for alert in system["alerts"]:
                print(f"  {alert}")
        else:
            print("✅ Sistema saudável")

        # Aguardar 5 minutos
        await asyncio.sleep(300)

asyncio.run(monitor_loop())
```

### Caso 4: Rotação Automática de Temas

```python
import asyncio
from orchestrator_agent import create_orchestrator_agent
from datetime import datetime

async def daily_factory():
    orchestrator = await create_orchestrator_agent()

    # Simular 3 dias
    for day in range(3):
        print(f"\n📅 DIA {day + 1}")

        # 3 vídeos por dia
        for exec_num in range(3):
            theme = orchestrator._select_next_theme()

            result = await orchestrator.execute({
                "action": "run_once",
                "theme": theme,
                "publish": True
            })

            if result["success"]:
                print(f"✅ {theme} ({result['data']['duration_seconds']:.0f}s)")
            else:
                print(f"❌ {theme}: {result['error']}")

            # Próximo vídeo em 2 horas
            await asyncio.sleep(3600)

asyncio.run(daily_factory())
```

## Simulação

O arquivo `test_daily_factory.py` simula operação de 3 dias.

```bash
python test_daily_factory.py

# Opções:
# 1. Simulação 3 dias [DRY RUN] - Recomendado
# 2. Simulação 3 dias [REAL] - Gera vídeos realmente
# 3. Teste de rotação de temas
# 4. Teste de monitoramento de saúde
# 5. Sair
```

### Modo Dry Run

- ✅ Testa lógica sem gerar arquivos
- ✅ Rápido (segundos)
- ✅ Recomendado para validação

### Modo Real

- ⚠️ Gera vídeos REALMENTE
- ⚠️ Consome quotas de API
- ⚠️ Pode levar horas
- ⚠️ Use com cuidado!

## Estrutura de Dados

### orchestrator_stats.json

```json
{
  "total_executions": 42,
  "last_execution": "2024-01-15T14:30:00",
  "themes_executed": [
    "estoicismo",
    "cristianismo",
    "filosofia",
    "licoes_de_vida",
    "estoicismo"
  ],
  "created_at": "2024-01-01T00:00:00"
}
```

### api_usage.json

```json
{
  "2024-01-15": {
    "gemini_requests": 4,
    "image_generations": 12,
    "youtube_uploads": 4
  },
  "2024-01-16": {
    "gemini_requests": 2,
    "image_generations": 8,
    "youtube_uploads": 2
  }
}
```

### health_history.json

```json
[
  {
    "timestamp": "2024-01-15T14:30:00.123456",
    "healthy": true,
    "components": {
      "cpu": { "percent": 45.2, "status": "healthy" },
      "memory": { "percent": 62.5, "available_gb": 8.2, "status": "healthy" },
      "disk": {
        "percent_used": 45.0,
        "free_gb": 125.3,
        "total_gb": 256.0,
        "status": "healthy"
      },
      "output_sizes": {
        "output": 1234.56,
        "data": 45.23,
        "cache": 89.12
      }
    },
    "messages": [],
    "alerts": []
  }
]
```

## Troubleshooting

### Problema: "Módulo 'schedule' não encontrado"

```bash
pip install schedule==1.2.0
```

### Problema: "Memória CRÍTICA"

Se sistema com < 90% RAM, monitore processos:

```bash
# Windows
tasklist /v

# Linux
top
```

### Problema: "Disco CRÍTICO"

Se < 2GB livre, libere espaço:

```bash
# Limpar cache
rm -rf cache/*

# Mover vídeos antigos
mv output/2024-01-* archive/
```

### Problema: "Quotas de API excedidas"

Reduza frequência de execução ou aguarde reset diário:

```python
# Usar agendamento menos frequente
custom_schedule = [
    {"time": time(9, 0, 0), "theme": "estoicismo"},
    # Apenas 1x/dia em vez de 3x
]
orchestrator.set_custom_schedule(custom_schedule)
```

## Próximos Passos

### 1. Integração Streamlit

Conectar OrchestratorAgent ao dashboard:

```python
# No streamlit_app.py
if st.button("🏭 Executar Agora"):
    result = await orchestrator.execute({
        "action": "run_once",
        "publish": st.checkbox("Publicar no YouTube")
    })
    st.success(f"✅ Ciclo concluído em {result['data']['duration_seconds']:.0f}s")
```

### 2. Persistência de Estado

Salvar estado entre reinicializações:

```python
import pickle

# Salvar
with open("state.pkl", "wb") as f:
    pickle.dump(orchestrator.last_themes_executed, f)

# Restaurar
with open("state.pkl", "rb") as f:
    orchestrator.last_themes_executed = pickle.load(f)
```

### 3. Webhook de Notificações

Discord/Slack em cada execução:

```python
import requests

def notify_discord(message: str):
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    requests.post(webhook_url, json={"content": message})

# Usar em ciclo:
notify_discord(f"✅ Vídeo {theme} gerado em {duration}s")
```

## Resumo de Arquivos Module 7

| Arquivo                      | Linhas    | Propósito                             |
| ---------------------------- | --------- | ------------------------------------- |
| `schedule_manager.py`        | 280+      | Agendamento + Rotação de temas        |
| `health_monitor.py`          | 340+      | Monitoramento de sistema + API quotas |
| `orchestrator_agent.py`      | 380+      | Orquestração C→A→V→E→P                |
| `test_orchestrator_agent.py` | 260+      | Testes do orchestrator                |
| `test_daily_factory.py`      | 380+      | Simulação 3 dias                      |
| **TOTAL**                    | **1640+** | **Módulo 7 Completo**                 |

## Status de Implementação ✅

- ✅ ScheduleManager: Agendamento 3x/dia
- ✅ HealthMonitor: CPU, RAM, Disco, API quotas
- ✅ OrchestratorAgent: Coordenação 5 agentes
- ✅ Rotação de temas: Sem repetição consecutiva
- ✅ Persistência: Histórico em JSON
- ✅ Testes: 7 testes unitários + simulação 3 dias
- ✅ Documentação: Este guia completo

## Próxima Fase

**Módulo 8** (futuro): UI Dashboard

- Integração Streamlit com todos os agentes
- Botões para execução manual
- Visualização de agendamentos
- Gráficos de estatísticas

---

**Fábrica de Vídeos Autônoma** 🏭
Módulo 7 Completo ✅
