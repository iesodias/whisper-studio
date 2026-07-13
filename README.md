# Transcrição de Áudio/Vídeo

Sistema para transcrição de áudio/vídeo em texto e geração de legendas usando Whisper AI.

## Estrutura do Projeto

```
whisper-studio/              # ← Raiz do projeto
├── venv/                    # ← Criar ambiente virtual aqui (não commitar)
├── transcription/           # Transcrição (áudio/vídeo → DOCX)
│   ├── transcribe.py
│   ├── outputs/
│   └── README.md
├── subtitles/               # Legendagem (vídeos → VTT)
│   ├── generate_en.py       # PT → EN
│   ├── generate_es.py       # PT → ES
│   ├── outputs/
│   └── README.md
├── shared/                  # Código compartilhado
│   ├── utils/
│   │   └── file_detector.py
│   └── config.py
├── tests/
│   └── test_file_detection.py
├── videos/                  # Vídeos de entrada
├── requirements.txt
└── .gitignore
```

## Instalação

### 1. Clonar o repositório

```bash
git clone https://github.com/iesodias/whisper-studio.git
cd whisper-studio
```

### 2. Criar ambiente virtual (na raiz do projeto)

```bash
# Criar venv na raiz
python -m venv venv

# Ativar o ambiente
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Instalar ffmpeg

**Mac:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install ffmpeg
```

**Windows:**  
Baixar de https://ffmpeg.org/download.html

## Uso

**IMPORTANTE:** Sempre ative o ambiente virtual antes de usar:
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### Transcrição

Converte áudio/vídeo em texto (DOCX):

```bash
# Básico
python transcription/transcribe.py --input video.mp4

# Personalizado
python transcription/transcribe.py --input video.mp4 --lang pt --model medium --output resultado.docx
```

Documentação completa: [transcription/README.md](transcription/README.md)

### Legendagem

Gera legendas sincronizadas (VTT):

```bash
# Inglês (PT → EN)
python subtitles/generate_en.py

# Espanhol (PT → ES)
python subtitles/generate_es.py
```

Documentação completa: [subtitles/README.md](subtitles/README.md)

## Configuração

Edite `shared/config.py` para alterar:
- Prompts por idioma
- Modelo Whisper padrão
- Diretórios de input/output
- Parâmetros de áudio

## Formatos Suportados

**Vídeo:** mp4, mov, avi, mkv, webm, flv, wmv, m4v  
**Áudio:** mp3, wav, m4a, flac, ogg, aac, wma, opus

## Modelos Whisper

| Modelo | Tamanho | Velocidade | Qualidade |
|--------|---------|------------|-----------|
| tiny   | 39 MB   | Muito rápido | Básica |
| base   | 74 MB   | Rápido     | Boa |
| small  | 244 MB  | Médio      | Muito boa |
| medium | 769 MB  | Lento      | Excelente (padrão) |
| large  | 1.5 GB  | Muito lento | Superior |
| turbo  | ~800 MB | Rápido     | Excelente |

## Requisitos

- Python 3.8+
- 8 GB RAM (mínimo), 16 GB (recomendado)
- GPU opcional (CUDA/MPS): 10-100x mais rápido
- ~2 GB de espaço para modelos

## Troubleshooting

**Erro: "No module named 'whisper'"**
```bash
pip install openai-whisper
```

**Erro: "ffmpeg not found"**  
Instale ffmpeg conforme instruções acima.

**Transcrição lenta**
- Verifique se GPU está sendo usada (mensagem inicial mostra device)
- Use modelo menor: `--model small`

**Erro: "deep_translator not found"**
```bash
pip install deep-translator
```

## Testes

```bash
python tests/test_file_detection.py
```

## Referências

- [Whisper AI](https://github.com/openai/whisper)
- [MoviePy](https://zulko.github.io/moviepy/)
- [Python-DOCX](https://python-docx.readthedocs.io/)
