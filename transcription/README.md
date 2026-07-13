# 📝 Transcrição de Áudio/Vídeo

Converte arquivos de áudio e vídeo em texto usando Whisper AI.

## 🎯 Funcionalidade

O script `transcribe.py` processa arquivos de áudio/vídeo e gera documentos DOCX com a transcrição completa.

### Características

- ✅ Suporta vídeo e áudio
- ✅ Detecção automática de GPU (CUDA/MPS/CPU)
- ✅ Múltiplos idiomas (PT, EN, ES)
- ✅ CLI interativo com argumentos
- ✅ Output em DOCX formatado
- ✅ Extração automática de áudio
- ✅ Otimizado para performance

## 📦 Uso

### Comando Básico

```bash
python transcription/transcribe.py --input video.mp4
```

### Opções Disponíveis

```bash
python transcription/transcribe.py \
    --input video.mp4 \           # Arquivo de entrada (obrigatório)
    --output resultado.docx \      # Arquivo de saída (opcional)
    --lang pt \                    # Idioma: pt, en (opcional, padrão: pt)
    --model medium                 # Modelo Whisper (opcional, padrão: medium)
```

### Exemplos

#### Transcrição em Português
```bash
python transcription/transcribe.py --input video.mp4
# Output: transcription/outputs/transcricao_pt.docx
```

#### Transcrição em Inglês
```bash
python transcription/transcribe.py --input video.mp4 --lang en
# Output: transcription/outputs/transcricao_en.docx
```

#### Com modelo mais rápido
```bash
python transcription/transcribe.py --input audio.mp3 --model small
```

#### Output personalizado
```bash
python transcription/transcribe.py \
    --input video.mp4 \
    --output minha_transcricao.docx \
    --lang pt \
    --model medium
```

## 📂 Estrutura de Output

Os arquivos são salvos em:
```
transcription/outputs/
├── transcricao_pt.docx    # Transcrições em português
├── transcricao_en.docx    # Transcrições em inglês
└── [custom].docx          # Outputs personalizados
```

## ⚙️ Parâmetros

### `--input` / `-i` (obrigatório)
Caminho para o arquivo de vídeo ou áudio.

**Formatos suportados:**
- **Vídeo**: `.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`, `.flv`, `.wmv`, `.m4v`
- **Áudio**: `.mp3`, `.wav`, `.m4a`, `.flac`, `.ogg`, `.aac`, `.wma`, `.opus`

### `--output` / `-o` (opcional)
Caminho personalizado para o arquivo DOCX de saída.

**Padrão**: `transcription/outputs/transcricao_<lang>.docx`

### `--lang` / `-l` (opcional)
Idioma da transcrição.

**Opções**: `pt`, `en`  
**Padrão**: `pt`

### `--model` / `-m` (opcional)
Tamanho do modelo Whisper.

**Opções**: `tiny`, `base`, `small`, `medium`, `large`, `turbo`  
**Padrão**: `medium`

**Tabela de modelos:**

| Modelo | Velocidade | Qualidade | RAM Necessária |
|--------|------------|-----------|----------------|
| tiny   | ⚡⚡⚡⚡     | ⭐⭐       | ~1 GB          |
| base   | ⚡⚡⚡      | ⭐⭐⭐     | ~1 GB          |
| small  | ⚡⚡       | ⭐⭐⭐⭐   | ~2 GB          |
| medium | ⚡         | ⭐⭐⭐⭐⭐ | ~5 GB          |
| large  | 🐌         | ⭐⭐⭐⭐⭐⭐ | ~10 GB        |
| turbo  | ⚡⚡       | ⭐⭐⭐⭐⭐ | ~6 GB          |

## 🔧 Configuração Avançada

Para alterar prompts e configurações, edite `shared/config.py`:

```python
PROMPTS = {
    "pt": "Seu prompt personalizado para português...",
    "en": "Your custom prompt for English...",
}
```

## 💻 Detecção de Device

O script detecta automaticamente o melhor device disponível:

1. **CUDA** (NVIDIA GPU) - mais rápido
2. **MPS** (Apple Silicon) - rápido
3. **CPU** - mais lento

A mensagem inicial mostra qual device está sendo usado:
```
🔊  Iniciando transcrição...
    Device   : cuda  # ou mps ou cpu
```

## 📊 Performance

### Tempo estimado (modelo medium):

| Device | Vídeo de 10 min | Vídeo de 1 hora |
|--------|-----------------|-----------------|
| CUDA   | ~30 segundos    | ~3 minutos      |
| MPS    | ~1 minuto       | ~6 minutos      |
| CPU    | ~10 minutos     | ~60 minutos     |

*Valores aproximados, variam conforme hardware*

## ⚠️ Troubleshooting

### Erro: "Device cuda/mps not available"
GPU não disponível. O script usará CPU automaticamente (mais lento).

### Erro: "File not found"
Verifique se o caminho do arquivo está correto e se o arquivo existe.

### Transcrição incorreta
1. Use um modelo maior: `--model large`
2. Verifique a qualidade do áudio
3. Ajuste o prompt em `shared/config.py` para seu contexto específico

### Memória insuficiente
Use um modelo menor:
```bash
python transcription/transcribe.py --input video.mp4 --model small
```

## 📖 Exemplos de Workflow

### Transcrever múltiplos arquivos
```bash
# Script bash
for file in videos/*.mp4; do
    python transcription/transcribe.py --input "$file"
done
```

### Processar e renomear
```bash
python transcription/transcribe.py \
    --input aula-01.mp4 \
    --output anotacoes/aula-01-transcricao.docx \
    --lang pt \
    --model medium
```

## 🔗 Links Úteis

- [Documentação principal](../README.md)
- [Geração de legendas](../subtitles/README.md)
- [Configurações compartilhadas](../shared/config.py)

---

💡 **Dica**: Para vídeos longos, use `--model turbo` para um bom equilíbrio entre velocidade e qualidade.
