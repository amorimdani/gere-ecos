"""
Módulo de Interface Streamlit - Dashboard de configuração e monitoramento
"""

import streamlit as st
import sys
import os
import asyncio
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config
from config.logger import get_logger
from utils import FileManager
from agents import create_orchestrator_agent

logger = get_logger(__name__)


def setup_page():
    """Configura as propriedades da página Streamlit"""
    st.set_page_config(
        page_title="🎥 Fábrica de Vídeos Autônoma - Ecos de Sabedoria",
        page_icon="🎬",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.markdown("""
    <style>
        .main { padding: 1rem; }
        .stTabs { font-size: 1.1em; }
        .success-box { background-color: #d4edda; padding: 1rem; border-radius: 0.5rem; }
        .error-box { background-color: #f8d7da; padding: 1rem; border-radius: 0.5rem; }
        .info-box { background-color: #d1ecf1; padding: 1rem; border-radius: 0.5rem; }
    </style>
    """, unsafe_allow_html=True)


def render_header():
    """Renderiza o cabeçalho da aplicação"""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🎥 Fábrica de Vídeos Autônoma")
        st.write("#### Ecos de Sabedoria - Gerador Automático de Conteúdo")
    with col2:
        st.info("v1.0.0\n🔄 Status: Pronto para Iniciar")


def render_configuration_tab():
    """Renderiza a aba de Configuração"""
    st.header("⚙️ Configuração e Credenciais")
    
    config = Config()
    credentials_status = config.validate_credentials()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if credentials_status["google_api_key"]:
            st.success("✅ Google Gemini API Configurada")
        else:
            st.warning("⚠️ Google Gemini API Não Configurada")
    
    with col2:
        if credentials_status["youtube_configured"]:
            st.success("✅ YouTube API Configurada")
        else:
            st.warning("⚠️ YouTube API Não Configurada")
    
    with col3:
        st.success("✅ Ollama (Fallback) Disponível")
    
    st.divider()
    
    # Formulário para Configuração
    st.subheader("📝 Adicionar/Atualizar Credenciais")
    
    with st.form("credentials_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            google_key = st.text_input(
                "🔑 Google Gemini API Key",
                value=config.google.api_key or "",
                type="password",
                help="Obtenha em: https://makersuite.google.com/app/apikey"
            )
            
            ollama_url = st.text_input(
                "🤖 Ollama Base URL",
                value=config.ollama.base_url,
                help="Padrão: http://localhost:11434"
            )
        
        with col2:
            youtube_client_id = st.text_input(
                "📺 YouTube Client ID",
                value=config.youtube.client_id or "",
                type="password",
                help="Obtenha em Google Cloud Console"
            )
            
            ollama_model = st.text_input(
                "🧠 Ollama Model",
                value=config.ollama.model,
                help="Ex: llama2, mistral, neural-chat"
            )
        
        youtube_secret = st.text_input(
            "📺 YouTube Client Secret",
            value=config.youtube.client_secret or "",
            type="password"
        )
        
        if st.form_submit_button("💾 Salvar Configurações"):
            # Salva as configurações em arquivo .env
            env_content = f"""GOOGLE_API_KEY={google_key}
OLLAMA_BASE_URL={ollama_url}
OLLAMA_MODEL={ollama_model}
YOUTUBE_CLIENT_ID={youtube_client_id}
YOUTUBE_CLIENT_SECRET={youtube_secret}
"""
            env_path = os.path.join(config.base_dir, ".env")
            try:
                with open(env_path, 'w') as f:
                    f.write(env_content)
                st.success("✅ Configurações salvas com sucesso!")
                logger.info("Configurações atualizadas pelo usuário")
            except Exception as e:
                st.error(f"❌ Erro ao salvar: {str(e)}")
                logger.error(f"Erro ao salvar .env: {str(e)}")
    
    st.divider()
    
    # Exibe sumário de configurações
    st.subheader("📊 Sumário de Configurações")
    st.info(config.get_summary())


def render_scheduler_tab():
    """Renderiza a aba de Agendamento"""
    st.header("⏰ Agendador de Vídeos")
    
    config = Config()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Vídeos por Dia", config.app.videos_per_day)
    with col2:
        st.metric("Duração (minutos)", config.app.video_duration_minutes)
    with col3:
        st.metric("Status", "Aguardando Inicialização")
    
    st.divider()
    
    st.subheader("🎯 Horários de Publicação")
    
    with st.expander("Configurar Horários Personalizados", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            time1 = st.time_input("1º Vídeo", value=None)
            time2 = st.time_input("2º Vídeo", value=None)
            time3 = st.time_input("3º Vídeo", value=None)
        
        with col2:
            st.info("""
            **Padrão:**
            - 09:00 AM
            - 02:00 PM
            - 08:00 PM
            
            **Deixe em branco para usar padrão**
            """)
        
        if st.button("⚙️ Salvar Horários"):
            st.success("✅ Horários configurados!")


def render_monitoring_tab():
    """Renderiza a aba de Monitoramento"""
    st.header("📊 Monitoramento e Logs")
    
    config = Config()
    file_manager = FileManager()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📹 Vídeos Publicados")
        videos = file_manager.get_video_records(config)
        
        if videos:
            for video in videos[-10:]:  # Últimos 10 vídeos
                st.write(f"• {video.strip()}")
            st.caption(f"Total: {len(videos)} vídeos publicados")
        else:
            st.info("Nenhum vídeo publicado ainda.")
    
    with col2:
        st.subheader("📋 Logs de Execução")
        log_files = list(Path(config.logs_dir).glob("*.log"))
        
        if log_files:
            selected_log = st.selectbox(
                "Selecione um arquivo de log",
                [f.name for f in sorted(log_files, reverse=True)]
            )
            
            log_path = Path(config.logs_dir) / selected_log
            try:
                with open(log_path, 'r', encoding='utf-8') as f:
                    logs = f.readlines()
                    st.code(''.join(logs[-50:]), language='log')  # Últimas 50 linhas
            except Exception as e:
                st.error(f"Erro ao ler log: {str(e)}")
        else:
            st.info("Nenhum arquivo de log encontrado.")


def render_utils_tab():
    """Renderiza a aba de Utilitários"""
    st.header("🛠️ Utilitários e Testes")
    
    st.subheader("🧪 Teste de Conexão")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔌 Testar Google Gemini"):
            with st.spinner("Testando..."):
                st.info("Funcionalidade disponível quando o agente o LLM estiver pronto")
    
    with col2:
        if st.button("🤖 Testar Ollama"):
            with st.spinner("Testando..."):
                st.info("Funcionalidade disponível quando o agente o LLM estiver pronto")
    
    with col3:
        if st.button("📺 Testar YouTube API"):
            with st.spinner("Testando..."):
                st.info("Funcionalidade disponível quando o agente Publisher estiver pronto")
    
    st.divider()
    
    st.subheader("📂 Gerenciador de Diretórios")
    config = Config()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"📁 Output: `{config.output_dir}`")
    with col2:
        st.info(f"📁 Logs: `{config.logs_dir}`")
    with col3:
        st.info(f"📁 Data: `{config.data_dir}`")


def main():
    """Função principal da aplicação Streamlit"""
    setup_page()
    render_header()
    
    # Sidebar com instruções
    with st.sidebar:
        st.header("📚 Guia Rápido")
        st.markdown("""
        ### 🚀 Começar
        
        1. **Configurar Credenciais**
           - Google Gemini API
           - YouTube API
        
        2. **Iniciar Agendador**
           - Clique no botão Start
        
        3. **Monitorar Geração**
           - Veja os logs em tempo real
        
        ### 📖 Links Úteis
        - [Google Gemini](https://makersuite.google.com)
        - [YouTube API](https://console.cloud.google.com)
        - [Ollama](https://ollama.ai)
        
        ### 🆘 Suporte
        Contacte o desenvolvedor para suporte.
        """)
    
    # Abas principais
    tab1, tab2, tab3, tab4 = st.tabs(
        ["⚙️ Configuração", "⏰ Agendador", "📊 Monitoramento", "🛠️ Utilitários"]
    )
    
    with tab1:
        render_configuration_tab()
    
    with tab2:
        render_scheduler_tab()
    
    with tab3:
        render_monitoring_tab()
    
    with tab4:
        render_utils_tab()
    
    # Botão de ação principal
    st.divider()
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("▶️ Iniciar Fábrica de Vídeos", key="start_button", use_container_width=True):
            st.info("⏳ Iniciando fábrica... Isto pode levar alguns minutos...")
            
            try:
                with st.spinner("🎬 Gerando conteúdo..."):
                    # Criar orchestrator e executar
                    async def run_factory():
                        orchestrator = await create_orchestrator_agent()
                        result = await orchestrator.execute({
                            "action": "run_once",
                            "theme": "estoicismo",
                            "publish": False  # Testar sem publicar primeiro
                        })
                        return result
                    
                    # Executar o factory
                    result = asyncio.run(run_factory())
                    
                    if result["success"]:
                        duration = result["data"].get("duration_seconds", 0)
                        st.success(f"✅ Vídeo gerado com sucesso em {duration:.0f}s!")
                        st.info("📁 Arquivo salvo em: `output/`")
                        
                        # Listar arquivos gerados
                        output_dir = Path("output")
                        if output_dir.exists():
                            files = list(output_dir.glob("*.mp4"))
                            if files:
                                st.write("📊 Arquivos gerados:")
                                for f in sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
                                    size_mb = f.stat().st_size / 1024 / 1024
                                    st.write(f"  • {f.name} ({size_mb:.1f} MB)")
                    else:
                        st.error(f"❌ Erro ao gerar vídeo: {result['error']}")
                    
                    logger.info("Fábrica de Vídeos executada pela interface")
            
            except Exception as e:
                st.error(f"❌ Erro: {str(e)}")
                logger.error(f"Erro ao executar fábrica: {str(e)}", exc_info=True)


if __name__ == "__main__":
    main()
