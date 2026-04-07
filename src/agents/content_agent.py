"""
Content Agent - Responsável por brainstorming e geração de roteiros
Cria conteúdo magnético com ganchos de retenção
"""

import sys
import json
import random
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.base_agent import BaseAgent
from agents.llm_manager import LLMManager
from config.logger import get_logger

logger = get_logger(__name__)


class ContentAgent(BaseAgent):
    """
    Agente responsável por:
    1. Escolher tema de forma autônoma
    2. Gerar roteiro de 10 minutos com ganchos de retenção
    3. Criar título magnético/clickbait
    4. Gerar tags otimizadas para SEO
    5. Dividir em cenas e criar prompts de imagem
    """
    
    # Temas disponíveis
    THEMES = {
        "estoicismo": {
            "name": "Estoicismo",
            "keywords": ["Marco Aurélio", "Epicteto", "Zenão", "Controle", "Razão"],
            "tone": "Contemplativo, profundo, motivacional"
        },
        "cristianismo": {
            "name": "Cristianismo",
            "keywords": ["Fé", "Graça", "Jesus", "Perdão", "Salvação"],
            "tone": "Inspirador, esperançoso, espiritual"
        },
        "filosofia": {
            "name": "Filosofia",
            "keywords": ["Sócrates", "Platão", "Aristóteles", "Sabedoria", "Verdade"],
            "tone": "Pensativo, questionador, reflexivo"
        },
        "licoes_de_vida": {
            "name": "Lições de Vida",
            "keywords": ["Crescimento", "Xito", "Relacionamentos", "Saúde", "Propósito"],
            "tone": "Prático, motivador, transformador"
        }
    }
    
    def __init__(self):
        super().__init__(agent_name="ContentAgent", max_retries=3)
        self.llm_manager = LLMManager(self.config)
    
    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa o pipeline de geração de conteúdo.
        
        Args:
            payload: {"theme": "estoicismo"} ou {} para tema aleatório
            
        Returns:
            dict: Conteúdo completo (roteiro, título, tags, cenas)
        """
        
        self.log_info("Iniciando geração de conteúdo...")
        
        # 1. Escolher tema
        theme_key = payload.get("theme") or random.choice(list(self.THEMES.keys()))
        theme = self.THEMES[theme_key]
        self.log_info(f"Tema selecionado: {theme['name']}")
        
        # 2. Gerar roteiro com ganchos
        script_result = await self._generate_script(theme)
        if not script_result["success"]:
            raise Exception(f"Falha ao gerar roteiro: {script_result.get('error')}")
        
        script = script_result["script"]
        self.log_info(f"Roteiro gerado ({len(script.split())} palavras)")
        
        # 3. Gerar título e tags
        title_result = await self._generate_title_and_tags(theme, script)
        if not title_result["success"]:
            raise Exception(f"Falha ao gerar título: {title_result.get('error')}")
        
        # 4. Dividir em cenas e gerar prompts visuais
        scenes_result = await self._generate_scenes_and_prompts(script, theme)
        if not scenes_result["success"]:
            raise Exception(f"Falha ao gerar cenas: {scenes_result.get('error')}")
        
        # 5. Compilar resultado final
        content = {
            "theme": theme["name"],
            "theme_key": theme_key,
            "script": script,
            "title": title_result["title"],
            "description": title_result["description"],
            "tags": title_result["tags"],
            "scenes": scenes_result["scenes"],
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "llm_provider": script_result.get("provider"),
                "word_count": len(script.split()),
                "estimated_duration_minutes": len(script.split()) / 130,  # ~130 palavras/min
                "scene_count": len(scenes_result["scenes"])
            }
        }
        
        self.log_info("Conteúdo gerado com sucesso!")
        return content
    
    async def _generate_script(self, theme: Dict[str, Any]) -> Dict[str, Any]:
        """Gera roteiro de 10 minutos com ganchos de retenção"""
        
        prompt = f"""
        Você é um roteirista especializado em criar vídeos envolventes para o YouTube.
        
        TEMA: {theme['name']}
        TOM: {theme['tone']}
        PALAVRAS-CHAVE: {', '.join(theme['keywords'])}
        
        TAREFA: Criar um roteiro de vídeo de EXATAMENTE 10 minutos (~1300 palavras)
        
        REQUISITOS OBRIGATÓRIOS:
        1. Abrir com uma PERGUNTA que prenda atenção (HOOK)
        2. Adicionar ganchos de retenção A CADA MINUTO:
           - Frases como: "E aqui está o que a maioria não sabe..."
           - "Mas espera, tem mais..."
           - "Isso vai mudar sua perspectiva..."
        3. Conter 3 histórias/exemplos práticos
        4. Incluir um "plot twist" no meio
        5. Terminar com CTA (Call To Action): "O que você acha? Comente abaixo!"
        6. Usar linguagem conversacional e dinâmica
        7. Marcar em [CENA X] sempre que houver mudança visual
        
        Formato de resposta:
        [HOOK] - Começe aqui
        [CENA 1] - Introdução
        [CONTEÚDO PRINCIPAL]
        [PLOT TWIST] - Reviravolta
        [CENA FINAL] - Conclusão com CTA
        
        COMECE AGORA:
        """
        
        result = await self.llm_manager.generate(prompt, max_tokens=2000)
        
        if result["success"] and result.get("text"):
            return {
                "success": True,
                "script": result["text"],
                "provider": result.get("provider")
            }

        # Fallback offline se nenhum LLM estiver disponível
        self.log_warning("LLM indisponível para roteiro; usando conteúdo padrão offline.")
        keywords = ", ".join(theme.get("keywords", []))
        base_paragraph = (
            f"Vivemos em um mundo acelerado, e poucas pessoas param para refletir sobre o verdadeiro significado de {theme['name']}. "
            f"Ao longo deste vídeo vamos explorar, de forma simples e prática, como aplicar esses princípios no dia a dia. "
            "Enquanto você assiste, pense em como pequenas mudanças de atitude podem gerar transformações profundas na sua vida. "
        )
        script = f"""[HOOK] Já se perguntou como {theme['name'].lower()} pode mudar completamente a forma como você enxerga a sua própria vida?\n\n""" \
            f"""[CENA 1] Origens e fundamentos\n{base_paragraph}\n""" \
            f"""[CENA 2] Aplicação prática no dia a dia\n{base_paragraph}\n""" \
            f"""[PLOT TWIST] O que quase ninguém fala sobre {theme['name'].lower()}\n{base_paragraph}\n""" \
            f"""[CENA FINAL] Conclusão e chamada para ação\n""" \
            f"""Essas ideias não são apenas conceitos abstratos: elas se tornam reais quando você decide agir. "
            f"Ao terminar este vídeo, escolha uma pequena atitude inspirada em {theme['name'].lower()} e coloque em prática ainda hoje. "
            f"Quais dessas reflexões mais tocaram você? Compartilhe nos comentários para continuarmos essa conversa. Palavras-chave: {keywords}."""

        return {
            "success": True,
            "script": script,
            "provider": "offline-fallback"
        }
    
    async def _generate_title_and_tags(self, theme: Dict[str, Any], 
                                       script: str) -> Dict[str, Any]:
        """Gera título magnético, descrição e tags SEO"""
        
        # Extrai primeira sentença do script para context
        first_sentence = script.split('\n')[0][:100]
        
        prompt = f"""
        Você é um especialista em SEO e títulos virais para YouTube.
        
        TEMA: {theme['name']}
        EXCERTO DO ROTEIRO: {first_sentence}...
        
        TAREFA: Criar:
        1. Um TÍTULO MAGNÉTICO (60-70 caracteres) que seja clickbait mas honesto
        2. Uma DESCRIÇÃO (150-200 palavras) otimizada para SEO
        3. 15 TAGS relevantes (separadas por vírgula)
        
        DICAS PARA TÍTULO:
        - Use números quando possível: "3 Lições de...", "5 Razões..."
        - Use palavras poderosas: "Surpreendente", "Revelado", "Finalmente", "Secreto"
        - Inclua emoção: !, ?
        - Maksimo 70 caracteres
        
        RESPONDA EM FORMATO JSON:
        {{
            "title": "Seu título aqui",
            "description": "Descrição de 150-200 palavras aqui",
            "tags": ["tag1", "tag2", "tag3", ...]
        }}
        """
        
        result = await self.llm_manager.generate(prompt, max_tokens=1000)
        
        if result["success"]:
            try:
                # Extrai JSON da resposta
                response_text = result["text"]
                # Tenta encontrar JSON no texto
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                json_str = response_text[start:end]
                data = json.loads(json_str)
                
                return {
                    "success": True,
                    "title": data.get("title", ""),
                    "description": data.get("description", ""),
                    "tags": data.get("tags", [])
                }
            except (json.JSONDecodeError, ValueError, IndexError):
                # Fallback para parsing manual
                lines = result["text"].split('\n')
                return {
                    "success": True,
                    "title": lines[0][:70] if lines else "Novo vídeo incrivelmente revelador!",
                    "description": '\n'.join(lines[1:]),
                    "tags": theme["keywords"]
                }

        # Fallback offline para título, descrição e tags
        self.log_warning("LLM indisponível para título/tags; usando conteúdo padrão offline.")
        title = f"{theme['name']}: 3 lições para transformar sua vida"
        description = (
            f"Neste vídeo vamos explorar de forma simples e direta como os princípios de {theme['name']} "
            "podem ser aplicados no seu dia a dia. A ideia é trazer exemplos práticos, reflexões profundas "
            "e pequenas atitudes que você pode começar a colocar em prática ainda hoje. Assista até o final "
            "para descobrir um insight especial que a maioria das pessoas ignora quando fala sobre esse tema."
        )
        tags = list(theme.get("keywords", [])) + [theme["name"], "desenvolvimento pessoal", "reflexão"]
        return {
            "success": True,
            "title": title,
            "description": description,
            "tags": tags
        }
    
    async def _generate_scenes_and_prompts(self, script: str, 
                                          theme: Dict[str, Any]) -> Dict[str, Any]:
        """Divide script em cenas e gera prompts de geração de imagem"""
        
        # Extrai cenas do script (marcadas com [CENA X])
        scenes = []
        lines = script.split('\n')
        current_scene = None
        current_text = []
        
        for line in lines:
            if '[CENA' in line or '[HOOK]' in line or '[PLOT TWIST]' in line:
                if current_scene and current_text:
                    scenes.append({
                        "title": current_scene,
                        "script": ' '.join(current_text),
                        "duration_seconds": 0  # Será calculado depois
                    })
                current_scene = line.strip()
                current_text = []
            else:
                current_text.append(line.strip())
        
        # Adiciona última cena
        if current_scene and current_text:
            scenes.append({
                "title": current_scene,
                "script": ' '.join(current_text),
                "duration_seconds": 0
            })
        
        # Se não encontrou cenas marcadas, cria 5 cenas padrão
        if not scenes or len(scenes) < 2:
            scenes = self._create_default_scenes(script, theme)
        
        # Gera prompts de imagem para cada cena
        prompt = f"""
        Você é um especialista em criar prompts para geração de imagens com AI.
        
        TEMA: {theme['name']}
        PALAVRAS-CHAVE VISUAIS: {', '.join(theme['keywords'])}
        
        Para cada cena abaixo, crie um prompt descritivo para Stable Diffusion/Pollinations.
        
        CENAS PARA PROCESSAR:
        """
        
        for i, scene in enumerate(scenes, 1):
            prompt += f"\nCENA {i}: {scene['script'][:150]}..."
        
        prompt += """
        
        RESPONDA EM FORMATO JSON ASSIM:
        {{
            "scenes": [
                {{
                    "scene_number": 1,
                    "visual_prompt": "prompt descritivo para AI gerar imagem",
                    "style": "cinematic, 4K, professional"
                }},
                ...
            ]
        }}
        """
        
        result = await self.llm_manager.generate(prompt, max_tokens=1500)
        
        if result["success"]:
            try:
                response_text = result["text"]
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                json_str = response_text[start:end]
                data = json.loads(json_str)
                
                # Merge com scenes originais
                for i, scene_data in enumerate(data.get("scenes", [])):
                    if i < len(scenes):
                        scenes[i]["visual_prompt"] = scene_data.get("visual_prompt", "")
                        scenes[i]["style"] = scene_data.get("style", "cinematic, 4K")
                
                return {
                    "success": True,
                    "scenes": scenes
                }
            except (json.JSONDecodeError, ValueError):
                # Fallback: gera prompts genéricos
                for i, scene in enumerate(scenes, 1):
                    scene["visual_prompt"] = f"{theme['name']} tema, {scene['script'][:50]}"
                    scene["style"] = "cinematic, 4K, professional, dramatic lighting"
                
                return {
                    "success": True,
                    "scenes": scenes
                }

        # Fallback offline: gera prompts genéricos para cada cena
        self.log_warning("LLM indisponível para cenas; gerando prompts visuais padrão offline.")
        for i, scene in enumerate(scenes, 1):
            scene["visual_prompt"] = f"Cena {i} sobre {theme['name']} com foco em {scene['script'][:60]}"
            scene["style"] = "cinematic, 4K, professional, dramatic lighting"
        return {
            "success": True,
            "scenes": scenes
        }
    
    def _create_default_scenes(self, script: str, theme: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Cria estrutura padrão de 5 cenas se não conseguir extrair do script"""
        
        words = script.split()
        chunk_size = len(words) // 5
        
        # Visuais distintos para cada cena
        visual_concepts = [
            ("pessoa pensativa em contemplação", "porcelana, minimalismo, introspection"),
            ("natureza selvagem e empoderada", "floresta densa, poder, liberdade"),
            ("conhecimento antigo e sabedoria", "biblioteca antiga, pergaminhos, ouro e azul"),
            ("transformação e mudança radical", "metamorfose, borboleta, energia quântica"),
            ("horizonte esperançoso e futuro brilhante", "amanhecer, montanhas, luz dourada")
        ]
        
        scenes = []
        scene_titles = [
            "[HOOK] - Abertura Impactante",
            "[CENA 1] - Desenvolvimento Conceitual",
            "[CENA 2] - Aprofundamento Prático",
            "[PLOT TWIST] - Reviravolta Inesperada",
            "[FINAL] - Conclusão Transformadora"
        ]
        
        for i, (title, (concept, style_mods)) in enumerate(zip(scene_titles, visual_concepts)):
            scene_num = i + 1
            scene_text = ' '.join(words[i*chunk_size:(i+1)*chunk_size])
            
            # Prompts ALTAMENTE DISTINTOS por cena
            if i == 0:  # HOOK
                visual_prompt = (
                    f"Abertura dramática e impactante sobre {theme['name']}, "
                    f"{concept}, com tipografia moderna, 4K ultra HD, "
                    f"iluminação cinematográfica, estilo Hollywood blockbuster"
                )
            elif i == 1:  # CENA 1
                visual_prompt = (
                    f"Conceito visual educacional de {theme['name']} - {concept}, "
                    f"tons profissionais, infográficos, diagramas conceituais, "
                    f"design moderno, TED talk aesthetic, 4K, bem iluminado"
                )
            elif i == 2:  # CENA 2
                visual_prompt = (
                    f"Aplicação prática de {theme['name']} no cotidiano - {concept}, "
                    f"pessoas reais, ambientes domésticos realistas, "
                    f"fotografia documental de qualidade, natural, environmental storytelling"
                )
            elif i == 3:  # PLOT TWIST
                visual_prompt = (
                    f"Reviravolta surpreendente em {theme['name']} - {concept}, "
                    f"efeitos visuais paradoxais, perspectivas impossíveis, "
                    f"M.C. Escher-inspired, surrealismo conceitual, cores vibrantes"
                )
            else:  # FINAL
                visual_prompt = (
                    f"Conclusão épica e inspiradora sobre {theme['name']} - {concept}, "
                    f"vista panorâmica, esperança e vitória, cores quentes, "
                    f"cinematografia de Hollywood épica, John Williams-like, transcendent"
                )
            
            scenes.append({
                "title": title,
                "script": scene_text,
                "visual_prompt": visual_prompt,
                "style": f"cinematic, 4K, professional, {style_mods}, hyper-detailed"
            })
        
        return scenes


def create_content_agent() -> ContentAgent:
    """Factory function para criar o agente de conteúdo"""
    return ContentAgent()
