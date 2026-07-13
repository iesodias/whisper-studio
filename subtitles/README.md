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
- ✅ Processa todos os vídeos em `videos/` ou diretório especificado
- ✅ Whisper traduz PT → EN automaticamente
- ✅ Gera `.vtt` em `subtitles/outputs/`
- ✅ **Tratamento robusto de erros** - continua o lote mesmo se um vídeo falhar
- ✅ **Skip de arquivos existentes** - reprocessa apenas vídeos novos
- ✅ **Log de erros** - registra falhas em `errors.log`
- ✅ **Progress bar com tqdm** - ETA, velocidade média e resumo final
- ✅ **Estatísticas detalhadas** - sucessos, falhas, tempo médio por vídeo

**CLI completo:**
```bash
python subtitles/generate_en.py \
  --input-dir videos \
  --output-dir subtitles/outputs \
  --model medium \
  --pattern "aula-*.mp4" \
  --skip-existing
```

**Opções disponíveis:**
- `--input-dir DIR`: diretório com vídeos de entrada (padrão: `videos/`)
- `--output-dir DIR`: diretório de saída das legendas (padrão: `subtitles/outputs/`)
- `--model MODEL`: modelo Whisper - tiny, base, small, medium, large (padrão: `medium`)
- `--pattern PATTERN`: filtra arquivos por padrão glob, ex: `"aula-*.mp4"` ou `"*.mp4"`
- `--skip-existing`: pula arquivos cujo `.vtt` já exista (recomendado para lotes grandes)
- `--force`: reprocessa todos os arquivos, ignorando `--skip-existing`

**Output gerado:**
```
subtitles/outputs/
├── aula-01.vtt
├── aula-02.vtt
├── tutorial.vtt
└── errors.log        # Log de vídeos que falharam (se houver)
```

#### Legendas em Espanhol
```bash
python subtitles/generate_es.py
```

**Funcionamento:**
- ✅ Transcreve vídeos em português
- ✅ Traduz cada segmento PT → ES via GoogleTranslator
- ✅ Gera `.vtt` com sufixo `_es` em `subtitles/outputs/`
- ✅ **Fallback inteligente** - se tradução falhar, usa texto original
- ✅ **Mesmas opções CLI** do `generate_en.py`
- ✅ **Log de erros** em `errors_es.log`

**CLI disponível:**
```bash
python subtitles/generate_es.py \
  --input-dir videos \
  --output-dir subtitles/outputs \
  --model medium \
  --skip-existing
```

**Output gerado:**
```
subtitles/outputs/
├── aula-01_es.vtt
├── aula-02_es.vtt
├── tutorial_es.vtt
└── errors_es.log     # Log de falhas (se houver)
```

## 📂 Estrutura de Output

```
subtitles/outputs/
├── video1.vtt         # Legenda em inglês
├── video1_es.vtt      # Legenda em espanhol
├── video2.vtt
├── video2_es.vtt
├── errors.log         # Falhas do generate_en.py (se houver)
└── errors_es.log      # Falhas do generate_es.py (se houver)
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

Agora via CLI:
```bash
python subtitles/generate_en.py --model small
```

Ou ajuste o padrão em `shared/config.py`:
```python
DEFAULT_MODEL = "medium"
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

### Processar todos os vídeos (primeira vez)
```bash
python subtitles/generate_en.py
```

### Processar apenas vídeos novos (lote incremental - RECOMENDADO)
```bash
python subtitles/generate_en.py --skip-existing
```

### Processar apenas arquivos específicos
```bash
# Processar apenas arquivos começando com "aula-"
python subtitles/generate_en.py --pattern "aula-*.mp4"

# Processar apenas .mp4
python subtitles/generate_en.py --pattern "*.mp4" --skip-existing
```

### Reprocessar tudo com outro modelo
```bash
python subtitles/generate_en.py --model small --force
```

### Usar diretórios personalizados
```bash
python subtitles/generate_en.py --input-dir meus-videos --output-dir minhas-legendas
```

### Processar 200 vídeos com resumo
```bash
# Modelo mais rápido para lotes grandes
python subtitles/generate_en.py --model small --skip-existing
```

## ⚠️ Troubleshooting

### Erro: "No files found in videos/"
Certifique-se de que:
1. A pasta `videos/` existe
2. Há arquivos com extensões válidas
3. O filtro `--pattern` corresponde aos arquivos esperados

### Legendas fora de sincronia
1. Verifique a qualidade do áudio original
2. Use modelo maior: `python subtitles/generate_en.py --model large`
3. Áudios com muito ruído podem afetar a sincronização

### Script muito lento
1. **Use GPU**: Verifique se CUDA/MPS está disponível
2. **Modelo menor**: Use `small` ou `base`
3. **generate_en.py**: Mais rápido que generate_es.py

### Falhas durante o lote
Ambos os scripts registram erros e continuam processando:
- `generate_en.py` → `subtitles/outputs/errors.log`
- `generate_es.py` → `subtitles/outputs/errors_es.log`

Para ver estatísticas, basta executar novamente - scripts sempre mostram resumo final.

### Sem conexão à internet (generate_es.py)
`generate_es.py` requer internet para GoogleTranslator.  
Use `generate_en.py` que funciona offline.

## 🔗 Formatos Suportados

### Entrada (vídeos/)
`.mp4`, `.mp3`, `.wav`, `.m4a`, `.mov`, `.avi`, `.mkv`, `.webm`, `.flv`, `.ogg`, `.aac`, `.wma`, `.opus`

### Saída (subtitles/outputs/)
`.vtt` (WebVTT)

## 💡 Dicas

### 1. Processamento em Lote de 200+ vídeos
**Sempre use `--skip-existing`** para evitar reprocessamento:
```bash
python subtitles/generate_en.py --skip-existing
```
Se o script for interrompido, basta executar novamente - ele continua de onde parou!

### 2. Monitoramento em Tempo Real
Progress bar com `tqdm` mostra:
- Vídeos processados / total
- ETA (tempo estimado restante)
- Velocidade (vídeos/hora)
- Status de cada vídeo

### 3. Organização
Mantenha vídeos originais em `videos/` e legendas em `subtitles/outputs/`

### 4. Recuperação de Falhas
Se um vídeo falhar:
1. O script continua com os demais
2. Falha é registrada em `errors.log` ou `errors_es.log`
3. Use `--force` para reprocessar apenas os que falharam

### 5. Performance em Lotes Grandes
Para 200 vídeos de 10 min cada:
- **GPU**: 2-4 horas (generate_en.py) | 6-10 horas (generate_es.py)
- **CPU**: 20-40 horas (generate_en.py) | 60-100 horas (generate_es.py)
- **Recomendado**: Use modelo `small` para velocidade ou `medium` para qualidade

## 📖 Exemplos de Workflow

### Workflow completo
```bash
# 1. Adicionar vídeos
cp ~/Downloads/*.mp4 videos/

# 2. Gerar legendas em inglês
python subtitles/generate_en.py --skip-existing

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
