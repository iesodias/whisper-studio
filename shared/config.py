"""
Configurações globais do projeto de transcrição e legendagem.

Este módulo centraliza prompts, formatos suportados e configurações
compartilhadas entre as frentes de transcrição e legendagem.
"""

# ═══════════════════════════════════════════════════════════════════
# PROMPTS POR IDIOMA
# ═══════════════════════════════════════════════════════════════════

PROMPTS = {
    "pt": """
        Transcrição em português europeu cristão. Termos: Javé, factos, óptimo, conceção,
        Reino de Deus, discípulos, Bíblia, versículo, pecado, salvação, batismo, congregação.
        Pronúncia típica de Portugal com sotaque nortenho.
    """,
    "en": """
        Transcription in English. Religious Christian terms: Jehovah, God, Jesus Christ,
        Holy Spirit, Kingdom of God, disciples, Bible, scripture, verse, sin, salvation,
        baptism, congregation, repentance, righteousness, covenant, prophecy, resurrection.
    """,
    "es": """
        Transcripción en español. Términos cristianos: Jehová, Dios, Jesucristo,
        Espíritu Santo, Reino de Dios, discípulos, Biblia, escritura, versículo,
        pecado, salvación, bautismo, congregación.
    """,
}

# Prompt para tecnologias (usado em legendagem)
TECH_PROMPT = """
    Azure, AWS, Terraform, Kubernetes, DevOps, pipeline, GitHub Actions,
    infraestrutura como código, container, cloud, CI/CD, Docker, Helm, Ansible
"""

# ═══════════════════════════════════════════════════════════════════
# FORMATOS SUPORTADOS
# ═══════════════════════════════════════════════════════════════════

AUDIO_FORMATS = ('.mp3', '.wav', '.m4a', '.flac', '.ogg', '.aac', '.wma', '.opus')
VIDEO_FORMATS = ('.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.m4v')

# ═══════════════════════════════════════════════════════════════════
# CONFIGURAÇÕES DO WHISPER
# ═══════════════════════════════════════════════════════════════════

# Modelos disponíveis (do menor ao maior)
WHISPER_MODELS = ["tiny", "base", "small", "medium", "large", "turbo"]

# Modelo padrão
DEFAULT_MODEL = "medium"

# Configurações de transcrição otimizadas
TRANSCRIPTION_CONFIG = {
    "temperature": 0.2,          # Reduz variações na transcrição
    "beam_size": 1,              # Greedy decode - ~2x mais rápido
    "condition_on_previous_text": False,  # Evita repetições em vídeos longos
    "verbose": False,
}

# ═══════════════════════════════════════════════════════════════════
# CAMINHOS PADRÃO
# ═══════════════════════════════════════════════════════════════════

# Diretórios de output
TRANSCRIPTION_OUTPUT_DIR = "transcription/outputs"
SUBTITLES_OUTPUT_DIR = "subtitles/outputs"

# Diretório de entrada de vídeos
VIDEOS_INPUT_DIR = "videos"

# ═══════════════════════════════════════════════════════════════════
# CONFIGURAÇÕES DE ÁUDIO
# ═══════════════════════════════════════════════════════════════════

# Parâmetros de extração de áudio
AUDIO_CODEC = "pcm_s16le"
AUDIO_SAMPLE_RATE = 16000  # Hz
AUDIO_CHANNELS = 1  # Mono
