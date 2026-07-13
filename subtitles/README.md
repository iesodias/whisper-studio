# 🎬 Geração de Legendas (Subtítulos)

Gera legendas sincronizadas (VTT) para vídeos usando Whisper AI.

## 🎯 Funcionalidade

Este módulo processa **todos os vídeos** da pasta `videos/` e gera legendas automaticamente.

### Dois scripts disponíveis:

1. **`generate_en.py`** - Legendas em Inglês (PT → EN)
2. **`generate_es.py`** - Legendas em Espanhol (PT → ES)

## 📦 Uso

### 1. Preparar Vídeos

Coloque seus vídeos na pasta `videos/`:
```bash
videos/
├── aula-01.mp4
├── aula-02.mp4
└── tutorial.mov
```

### 2. Gerar Legendas

#### Legendas em Inglês
```bash
python subtitles/generate_en.py
```

**Funcionamento:**
- Processa todos os vídeos em `videos/`
- Whisper traduz PT → EN automaticamente
- Gera `.vtt` em `subtitles/outputs/`

**Output:**
```
subtitles/outputs/
├── aula-01.vtt
├── aula-02.vtt
└── tutorial.vtt
```

#### Legendas em Espanhol
```bash
python subtitles/generate_es.py
```

**Funcionamento:**
- Transcreve vídeos em português
- Traduz cada segmento PT → ES via GoogleTranslator
- Gera `.vtt` com sufixo `_es` em `subtitles/outputs/`

**Output:**
```
subtitles/outputs/
├── aula-01_es.vtt
├── aula-02_es.vtt
└── tutorial_es.vtt
```

## 📂 Estrutura de Output

```
subtitles/outputs/
├── video1.vtt         # Legenda em inglês
├── video1_es.vtt      # Legenda em espanhol
├── video2.vtt
└── video2_es.vtt
```

## 🔄 Diferenças entre os Scripts

| Característica | generate_en.py | generate_es.py |
|---------------|----------------|----------------|
| **Idioma alvo** | Inglês | Espanhol |
| **Método** | Whisper `task="translate"` | Whisper + GoogleTranslator |
| **Velocidade** | ⚡ Rápido | 🐌 Mais lento |
| **Dependência externa** | Não | Sim (internet) |
| **Sufixo no arquivo** | Nenhum | `_es` |
| **Qualidade** | Alta (nativo Whisper) | Boa (tradução automática) |

## 📝 Formato VTT

Os arquivos gerados seguem o padrão WebVTT:

```vtt
WEBVTT

00:00:00.000 --> 00:00:05.120
Hello, today we will learn about cloud infrastructure.

00:00:05.120 --> 00:00:10.340
First, let's understand what Terraform is.
```

### Compatibilidade

✅ YouTube  
✅ Vimeo  
✅ HTML5 Video  
✅ VLC Player  
✅ Editores de vídeo (Premiere, Final Cut, etc.)

## ⚙️ Configuração

### Alterar Modelo Whisper

Edite o script e modifique:
```python
from shared.config import DEFAULT_MODEL

# Ou diretamente no código:
model = whisper.load_model("small")  # tiny, base, small, medium, large, turbo
```

### Personalizar Prompt

Edite `shared/config.py`:
```python
TECH_PROMPT = """
    Seus termos técnicos personalizados aqui...
"""
```

### Alterar Idioma de Origem (generate_es.py)

Se seus vídeos não estão em português:
```python
result = model.transcribe(
    str(file_path),
    task="transcribe",
    language="en",  # Altere aqui: en, es, fr, etc.
    # ...
)
```

## 📊 Performance

### Tempo Estimado (modelo medium)

| Vídeo | generate_en.py | generate_es.py |
|-------|----------------|----------------|
| 10 min | ~1-2 min | ~3-5 min |
| 1 hora | ~6-12 min | ~20-30 min |

*Com GPU. CPU é 10-50x mais lento.*

**generate_es.py é mais lento** porque:
1. Transcreve em PT
2. Traduz cada segmento individualmente para ES
3. Depende de chamadas de API externa

## 🎨 Exemplos de Uso

### Processar apenas um vídeo

Modifique temporariamente o script:
```python
# No início do script
arquivos = [Path("videos/meu_video.mp4")]
```

### Processar apenas .mp4
```python
arquivos = [f for f in input_dir.iterdir() if f.suffix.lower() == '.mp4']
```

### Adicionar mais idiomas

Crie um novo script `generate_fr.py` (francês):
```python
result = model.transcribe(
    str(file_path),
    task="translate",  # Se Whisper suporta tradução para FR
    target_language="fr",
    # ...
)
```

## ⚠️ Troubleshooting

### Erro: "No files found in videos/"
Certifique-se de que:
1. A pasta `videos/` existe
2. Há arquivos com extensões válidas

### Erro: "deep_translator not found" (generate_es.py)
```bash
pip install deep-translator
```

### Legendas fora de sincronia
1. Verifique a qualidade do áudio original
2. Use modelo maior: `model = whisper.load_model("large")`
3. Áudios com muito ruído podem afetar a sincronização

### Tradução ruim (generate_es.py)
1. Tradutor online pode ter limitações
2. Considere usar uma API de tradução premium
3. Ou gere em inglês e traduza manualmente depois

### Script muito lento
1. **Use GPU**: Verifique se CUDA/MPS está disponível
2. **Modelo menor**: Use `small` ou `base`
3. **generate_en.py**: Mais rápido que generate_es.py

### Sem conexão à internet (generate_es.py)
`generate_es.py` requer internet para GoogleTranslator.  
Use `generate_en.py` que funciona offline.

## 🔗 Formatos Suportados

### Entrada (vídeos/)
`.mp4`, `.mp3`, `.wav`, `.m4a`, `.mov`, `.avi`, `.mkv`, `.webm`, `.flv`, `.ogg`, `.aac`, `.wma`, `.opus`

### Saída (subtitles/outputs/)
`.vtt` (WebVTT)

## 💡 Dicas

### 1. Processamento em Lote
Os scripts processam **automaticamente** todos os vídeos da pasta:
```bash
python subtitles/generate_en.py  # Processa tudo de uma vez
```

### 2. Monitoramento
Use `tqdm` para ver o progresso:
```
Processando vídeos: 2/5 [████████          ] 40%
```

### 3. Organização
Mantenha vídeos originais em `videos/` e legendas em `subtitles/outputs/`

### 4. Backup
Faça backup das legendas geradas antes de reprocessar.

## 📖 Exemplos de Workflow

### Workflow completo
```bash
# 1. Adicionar vídeos
cp ~/Downloads/*.mp4 videos/

# 2. Gerar legendas em inglês
python subtitles/generate_en.py

# 3. Gerar legendas em espanhol
python subtitles/generate_es.py

# 4. Verificar outputs
ls -lh subtitles/outputs/
```

### Integração com YouTube
1. Gere legendas: `python subtitles/generate_en.py`
2. Faça upload do vídeo no YouTube
3. Adicione o arquivo `.vtt` nas configurações de legendas

## 🔗 Links Úteis

- [Documentação principal](../README.md)
- [Transcrição de vídeo](../transcription/README.md)
- [Configurações compartilhadas](../shared/config.py)
- [Especificação WebVTT](https://www.w3.org/TR/webvtt1/)

---

💡 **Dica**: Para máxima qualidade em inglês, use `generate_en.py` pois a tradução do Whisper é superior à tradução automática.
