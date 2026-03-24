#!/usr/bin/env python3
"""
vault_migrator.py — Migração segura e controlada de frontmatter YAML
para o Vault Obsidian CACD 2025.

Uso:
    python3 vault_migrator.py --dry-run     # Gera relatórios, não altera nada
    python3 vault_migrator.py --write       # Aplica mudanças (faz backup Git antes)

Relatórios gerados em: /tmp/vault_migration/
"""

import os
import re
import sys
import subprocess
import datetime
import yaml
from collections import Counter, defaultdict

# ═══════════════════════════════════════════════════════════════
# CONFIGURAÇÃO
# ═══════════════════════════════════════════════════════════════

VAULT_PATH = "/home/cal/Documents/CACD_Vault_2025"
EDITAL_PATH = os.path.join(VAULT_PATH, "00 - GESTÃO & METADADOS",
                           "01 - Edital e Documentos Oficiais",
                           "_Edital e Documentos Oficiais.md")
REPORT_DIR = "/tmp/vault_migration"
TODAY = datetime.date.today().strftime("%d/%m/%Y")

SKIP_DIRS = {".obsidian", ".git", ".scripts", ".Quarentena"}

# Tipos possíveis de nota
TIPOS = [
    "nota-tema", "indice", "prova", "material-bruto",
    "resumo-agregador", "utilitario", "dashboard", "nao-classificado"
]

# ═══════════════════════════════════════════════════════════════
# FUNÇÕES AUXILIARES
# ═══════════════════════════════════════════════════════════════

def should_skip(path):
    """Retorna True se o caminho contém um diretório que deve ser ignorado."""
    parts = path.split(os.sep)
    return any(p in SKIP_DIRS for p in parts)


def scan_vault(vault_path):
    """Lista todos os .md do vault, excluindo diretórios ignorados."""
    notes = []
    for root, dirs, files in os.walk(vault_path):
        # Poda de diretórios ignorados
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f.endswith(".md"):
                full = os.path.join(root, f)
                rel = os.path.relpath(full, vault_path)
                notes.append({"path": full, "rel": rel, "filename": f})
    return notes


def extract_frontmatter(content):
    """
    Extrai o frontmatter YAML e o corpo da nota.
    Retorna (parsed_dict | None, body_str, raw_yaml_str).
    Nunca corrompe o conteúdo fora do YAML.
    """
    if not content.startswith("---"):
        return None, content, ""

    # Encontrar o segundo '---'
    end_match = re.search(r'\n---\s*\n', content[3:])
    if not end_match:
        # YAML aberto / malformado: tratar como sem frontmatter
        return None, content, ""

    end_pos = 3 + end_match.end()
    raw_yaml = content[3:3 + end_match.start()]
    body = content[end_pos:]

    try:
        parsed = yaml.safe_load(raw_yaml)
        if not isinstance(parsed, dict):
            parsed = {}
    except yaml.YAMLError:
        parsed = {}

    return parsed, body, raw_yaml


def render_frontmatter(data):
    """Serializa um dicionário como bloco YAML frontmatter."""
    # Ordem desejada dos campos
    key_order = [
        "tema", "area", "subarea", "topico_edital", "data",
        "tags", "aliases", "conexoes", "tipo", "status"
    ]
    ordered = {}
    for k in key_order:
        if k in data:
            ordered[k] = data[k]
    # Campos extras não previstos
    for k in data:
        if k not in ordered:
            ordered[k] = data[k]

    result = yaml.dump(
        ordered,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
        width=120
    )
    return f"---\n{result}---\n"


# ═══════════════════════════════════════════════════════════════
# CLASSIFICAÇÃO DE NOTAS
# ═══════════════════════════════════════════════════════════════

def classify_note(note, content, parsed_yaml):
    """
    Classifica uma nota em um dos tipos definidos.
    Retorna (tipo, confianca: float, razao: str).
    """
    rel = note["rel"]
    fname = note["filename"]
    parts = rel.split(os.sep)

    # --- Utilitários conhecidos ---
    util_names = {"BEM-VINDO", "RELATORIO", "SETUP", "_análise",
                  "arquivos_md", "com_tags", "sem_yaml", "links_internos",
                  "sem_yaml_correto", "_Indice_Geral_Tags"}
    basename = fname.replace(".md", "")
    if basename in util_names:
        return "utilitario", 0.95, f"Nome reconhecido como utilitário: {basename}"

    # Arquivos .txt.md / logs na raiz
    if len(parts) == 1 and not fname.startswith("_"):
        return "utilitario", 0.8, "Arquivo na raiz do vault sem prefixo de índice"

    # --- Provas ---
    prova_patterns = ["Provas Anteriores", "SIMULADOS & EXERCÍCIOS", "10 - SIMULADOS"]
    if any(p in rel for p in prova_patterns):
        return "prova", 0.9, f"Localizado em pasta de provas/simulados"

    # Detecção por conteúdo de prova
    if re.search(r'###\s*Item\s+\d+', content) or re.search(r'Gabarito', content, re.IGNORECASE):
        if any(p in rel for p in prova_patterns):
            return "prova", 0.95, "Contém 'Item N' e 'Gabarito' em pasta de provas"

    # --- Índice / MOC ---
    if fname.startswith("_"):
        # Contar wikilinks vs. texto corrido
        wikilinks = len(re.findall(r'\[\[.*?\]\]', content))
        text_lines = [l for l in content.split('\n')
                      if l.strip() and not l.strip().startswith('#')
                      and '[[' not in l and not l.strip().startswith('---')
                      and not l.strip().startswith('>')]
        text_ratio = len(text_lines)
        if wikilinks > 5 and text_ratio < wikilinks:
            return "indice", 0.9, f"Prefixo '_', {wikilinks} wikilinks, pouco texto corrido"
        # Mesmo com texto, se começa com _ é provavelmente índice ou nota-tema
        if wikilinks > 3:
            return "indice", 0.75, f"Prefixo '_', {wikilinks} wikilinks"
        # Se tem conteúdo real, tratar como nota-tema
        if len(content.strip()) > 500:
            return "nota-tema", 0.7, "Prefixo '_' mas com conteúdo substancial"
        return "indice", 0.7, "Prefixo '_' sem muitas wikilinks mas é um arquivo índice"

    # --- Material Bruto ---
    bruto_dirs = ["HTML import", "Estudos"]
    if any(parts[0].startswith(d) for d in bruto_dirs):
        if parsed_yaml and len(content.strip()) > 1000:
            return "material-bruto", 0.7, "Dentro de pasta de material bruto mas com conteúdo"
        return "material-bruto", 0.85, f"Dentro de pasta de material bruto: {parts[0]}"

    # --- Flashcards / Recursos ---
    if "FLASHCARDS" in rel or "MAPAS MENTAIS" in rel:
        return "utilitario", 0.85, "Pasta de flashcards/mapas mentais"
    if "RECURSOS ADICIONAIS" in rel:
        return "material-bruto", 0.75, "Dentro de Recursos Adicionais"

    # --- Nota-tema (default para pastas de disciplina 01-09) ---
    disciplina_prefixes = [f"{i:02d}" for i in range(1, 10)]
    if parts and any(parts[0].startswith(p) for p in disciplina_prefixes):
        if len(content.strip()) > 200:
            return "nota-tema", 0.85, "Pasta de disciplina com conteúdo substancial"
        if len(content.strip()) > 0:
            return "nota-tema", 0.6, "Pasta de disciplina com pouco conteúdo"
        return "nao-classificado", 0.5, "Pasta de disciplina mas arquivo vazio/mínimo"

    # --- Fallback ---
    return "nao-classificado", 0.5, "Nenhum critério com confiança alta"


# ═══════════════════════════════════════════════════════════════
# NORMALIZAÇÃO E MERGE
# ═══════════════════════════════════════════════════════════════

def _to_list(val):
    """Converte valor escalar ou None em lista."""
    if val is None:
        return []
    if isinstance(val, str):
        return [val] if val.strip() else []
    if isinstance(val, list):
        return [str(v) for v in val if v is not None and str(v).strip()]
    return []


def merge_tags(existing, ensure_cacd=True):
    """Funde tags preservando ordem, sem duplicatas, garantindo 'cacd' no topo."""
    tags = _to_list(existing)
    # Deduplicar preservando ordem
    seen = set()
    deduped = []
    for t in tags:
        t_clean = t.strip()
        if t_clean and t_clean not in seen:
            seen.add(t_clean)
            deduped.append(t_clean)
    if ensure_cacd:
        if "cacd" not in seen:
            deduped.insert(0, "cacd")
        elif deduped[0] != "cacd":
            deduped.remove("cacd")
            deduped.insert(0, "cacd")
    return deduped


def merge_aliases(existing, new_aliases=None):
    """Funde aliases sem duplicatas."""
    result = _to_list(existing)
    if new_aliases:
        for a in _to_list(new_aliases):
            if a and a not in result:
                result.append(a)
    return result


def normalize_metadata(parsed, note, note_type):
    """
    Normaliza campos antigos para o novo schema.
    Retorna (novo_dict, lista_de_inferencias).
    """
    if parsed is None:
        parsed = {}

    new = {}
    inferences = []

    # --- tema ---
    tema = parsed.get("tema") or parsed.get("title") or parsed.get("titulo")
    if tema:
        source = "existente" if parsed.get("tema") else "campo antigo (title/titulo)"
        new["tema"] = str(tema)
        if source != "existente":
            inferences.append(f"tema ← {source}: '{tema}'")
    else:
        # Inferir do nome do arquivo
        basename = note["filename"].replace(".md", "").lstrip("_")
        new["tema"] = basename
        inferences.append(f"tema ← [INFERIDO do nome do arquivo]: '{basename}'")

    # --- area ---
    area = parsed.get("area") or parsed.get("área")
    if area:
        new["area"] = str(area)
        if parsed.get("área") and not parsed.get("area"):
            inferences.append(f"area ← normalização de 'área'")
    else:
        new["area"] = ""
        inferences.append("area: vazio (sem dados)")

    # --- subarea ---
    subarea = parsed.get("subarea") or parsed.get("subárea")
    if subarea:
        new["subarea"] = str(subarea)
        if parsed.get("subárea") and not parsed.get("subarea"):
            inferences.append(f"subarea ← normalização de 'subárea'")
    else:
        new["subarea"] = ""

    # --- topico_edital ---
    new["topico_edital"] = parsed.get("topico_edital", "")

    # --- data ---
    new["data"] = parsed.get("data", TODAY)

    # --- tags ---
    new["tags"] = merge_tags(parsed.get("tags"))

    # --- aliases ---
    new["aliases"] = merge_aliases(parsed.get("aliases"))

    # --- conexoes ---
    conexoes = parsed.get("conexoes") or parsed.get("connections")
    if conexoes:
        new["conexoes"] = _to_list(conexoes)
        if parsed.get("connections") and not parsed.get("conexoes"):
            inferences.append("conexoes ← normalização de 'connections'")
    else:
        new["conexoes"] = ['[[]]']

    # --- tipo ---
    existing_tipo = parsed.get("tipo")
    if existing_tipo and existing_tipo in TIPOS:
        new["tipo"] = existing_tipo
    else:
        new["tipo"] = note_type

    # --- status ---
    existing_status = parsed.get("status")
    if existing_status:
        new["status"] = str(existing_status)
    else:
        new["status"] = "rascunho"

    # Remover campos antigos que não devem migrar
    # (materia, title, titulo, área, subárea, connections já foram absorvidos)

    return new, inferences


def build_new_frontmatter(parsed, note, note_type):
    """
    Constrói o novo frontmatter completo conforme o tipo da nota.
    Retorna (novo_dict, inferences).
    """
    if note_type == "nota-tema":
        return normalize_metadata(parsed, note, note_type)

    elif note_type == "indice":
        new, infs = normalize_metadata(parsed, note, note_type)
        # Template enxuto: manter só campos relevantes
        slim = {
            "tema": new.get("tema", ""),
            "tipo": "indice",
            "data": new.get("data", TODAY),
            "tags": merge_tags(new.get("tags"), ensure_cacd=True),
            "aliases": new.get("aliases", []),
            "status": new.get("status", "ativo"),
        }
        # Preservar area/subarea se existirem
        if new.get("area"):
            slim["area"] = new["area"]
        if new.get("subarea"):
            slim["subarea"] = new["subarea"]
        return slim, infs

    elif note_type == "prova":
        new, infs = normalize_metadata(parsed, note, note_type)
        slim = {
            "tipo": "prova",
            "data": new.get("data", TODAY),
            "tags": merge_tags(new.get("tags"), ensure_cacd=True),
        }
        if new.get("tema"):
            slim["tema"] = new["tema"]
        return slim, infs

    elif note_type in ("material-bruto", "utilitario", "resumo-agregador", "dashboard"):
        new, infs = normalize_metadata(parsed, note, note_type)
        slim = {
            "tipo": note_type,
            "data": new.get("data", TODAY),
            "tags": merge_tags(new.get("tags"), ensure_cacd=True),
        }
        if new.get("tema"):
            slim["tema"] = new["tema"]
        if new.get("aliases"):
            slim["aliases"] = new["aliases"]
        return slim, infs

    else:
        # nao-classificado: não gerar frontmatter novo
        return None, [f"Tipo '{note_type}': sem transformação aplicada"]


# ═══════════════════════════════════════════════════════════════
# AUDITORIA DE CAMPOS
# ═══════════════════════════════════════════════════════════════

def audit_fields(notes_data):
    """
    Mapeia todos os campos YAML encontrados, suas frequências e variações.
    """
    field_counter = Counter()
    field_examples = defaultdict(list)

    for nd in notes_data:
        if nd["parsed"]:
            for key in nd["parsed"]:
                field_counter[key] += 1
                if len(field_examples[key]) < 3:
                    field_examples[key].append(nd["note"]["rel"])

    return field_counter, field_examples


# ═══════════════════════════════════════════════════════════════
# RELATÓRIOS
# ═══════════════════════════════════════════════════════════════

def generate_reports(notes_data, report_dir):
    """Gera os 4 relatórios obrigatórios."""
    os.makedirs(report_dir, exist_ok=True)

    # Contadores
    total = len(notes_data)
    with_yaml = sum(1 for n in notes_data if n["parsed"] is not None)
    without_yaml = total - with_yaml
    by_type = Counter(n["type"] for n in notes_data)
    by_folder = Counter(n["note"]["rel"].split(os.sep)[0] for n in notes_data)
    with_tags = sum(1 for n in notes_data
                    if n["parsed"] and _to_list(n["parsed"].get("tags")))
    with_aliases = sum(1 for n in notes_data
                       if n["parsed"] and _to_list(n["parsed"].get("aliases")))
    ambiguous = [n for n in notes_data if n["confidence"] < 0.7]
    would_change = [n for n in notes_data if n["new_fm"] is not None]

    # ── Relatório 1: Classificação ──
    with open(os.path.join(report_dir, "relatorio_classificacao.md"), "w", encoding="utf-8") as f:
        f.write("# Relatório de Classificação do Vault\n\n")
        f.write(f"**Data:** {TODAY}\n\n")
        f.write("## Resumo Geral\n\n")
        f.write(f"| Métrica | Valor |\n|---|---|\n")
        f.write(f"| Total de arquivos `.md` | {total} |\n")
        f.write(f"| Com YAML | {with_yaml} |\n")
        f.write(f"| Sem YAML | {without_yaml} |\n")
        f.write(f"| Com tags | {with_tags} |\n")
        f.write(f"| Com aliases | {with_aliases} |\n")
        f.write(f"| Ambíguos (confiança < 0.7) | {len(ambiguous)} |\n")
        f.write(f"| Seriam alterados | {len(would_change)} |\n\n")

        f.write("## Por Tipo\n\n")
        f.write("| Tipo | Quantidade |\n|---|---|\n")
        for t in TIPOS:
            f.write(f"| `{t}` | {by_type.get(t, 0)} |\n")

        f.write("\n## Por Pasta\n\n")
        f.write("| Pasta | Quantidade |\n|---|---|\n")
        for folder, count in sorted(by_folder.items()):
            f.write(f"| `{folder}` | {count} |\n")

        f.write("\n## Lista Completa\n\n")
        for nd in notes_data:
            conf_str = f"{nd['confidence']:.0%}"
            f.write(f"- `{nd['note']['rel']}` → **{nd['type']}** ({conf_str}) — {nd['reason']}\n")

    # ── Relatório 2: Migração ──
    field_counter, field_examples = audit_fields(notes_data)
    with open(os.path.join(report_dir, "relatorio_migracao.md"), "w", encoding="utf-8") as f:
        f.write("# Relatório de Migração\n\n")
        f.write(f"**Data:** {TODAY}\n\n")

        f.write("## Auditoria de Campos YAML Existentes\n\n")
        f.write("| Campo | Frequência | Exemplos |\n|---|---|---|\n")
        for field, count in field_counter.most_common():
            exs = ", ".join(f"`{e}`" for e in field_examples[field][:3])
            f.write(f"| `{field}` | {count} | {exs} |\n")

        f.write("\n## Regras de Transformação Aplicadas\n\n")
        f.write("| Campo antigo | Campo novo | Regra |\n|---|---|---|\n")
        f.write("| `title` / `titulo` | `tema` | Copiar se `tema` ausente |\n")
        f.write("| `área` | `area` | Normalizar grafia |\n")
        f.write("| `subárea` | `subarea` | Normalizar grafia |\n")
        f.write("| `materia` | *(removido)* | Não migrar |\n")
        f.write("| `connections` | `conexoes` | Converter, preservar valores |\n")
        f.write("| `tags` | `tags` | Preservar, deduplicar, prefixar `cacd` |\n")
        f.write("| `aliases` | `aliases` | Preservar e fundir |\n")

        f.write("\n## Inferências Realizadas\n\n")
        for nd in notes_data:
            if nd["inferences"]:
                f.write(f"### `{nd['note']['rel']}`\n")
                for inf in nd["inferences"]:
                    f.write(f"- {inf}\n")
                f.write("\n")

    # ── Relatório 3: Ambiguidades ──
    with open(os.path.join(report_dir, "ambiguidade_para_revisao.md"), "w", encoding="utf-8") as f:
        f.write("# Ambiguidades para Revisão Manual\n\n")
        f.write(f"**Data:** {TODAY}\n\n")
        f.write(f"Total de casos ambíguos: **{len(ambiguous)}**\n\n")
        if not ambiguous:
            f.write("*Nenhum caso ambíguo encontrado. Todos os arquivos foram classificados com confiança ≥ 0.7.*\n")
        for nd in ambiguous:
            f.write(f"### `{nd['note']['rel']}`\n")
            f.write(f"- **Tipo sugerido:** `{nd['type']}`\n")
            f.write(f"- **Confiança:** {nd['confidence']:.0%}\n")
            f.write(f"- **Razão:** {nd['reason']}\n")
            if nd["inferences"]:
                f.write(f"- **Inferências:**\n")
                for inf in nd["inferences"]:
                    f.write(f"  - {inf}\n")
            f.write("\n")

    # ── Relatório 4: Amostras Antes/Depois ──
    with open(os.path.join(report_dir, "amostras_antes_depois.md"), "w", encoding="utf-8") as f:
        f.write("# Amostras de Antes/Depois\n\n")
        f.write(f"**Data:** {TODAY}\n\n")

        # Selecionar até 3 exemplos por tipo
        shown = defaultdict(int)
        for nd in notes_data:
            if nd["new_fm"] is not None and shown[nd["type"]] < 3:
                shown[nd["type"]] += 1
                f.write(f"## `{nd['note']['rel']}` — Tipo: `{nd['type']}`\n\n")

                f.write("### ANTES\n")
                f.write("```yaml\n")
                if nd["parsed"]:
                    f.write(yaml.dump(nd["parsed"], allow_unicode=True,
                                      sort_keys=False, default_flow_style=False))
                else:
                    f.write("(sem frontmatter)\n")
                f.write("```\n\n")

                f.write("### DEPOIS\n")
                f.write("```yaml\n")
                f.write(yaml.dump(nd["new_fm"], allow_unicode=True,
                                  sort_keys=False, default_flow_style=False))
                f.write("```\n\n")
                if nd["inferences"]:
                    f.write("**Inferências:**\n")
                    for inf in nd["inferences"]:
                        f.write(f"- {inf}\n")
                f.write("\n---\n\n")


# ═══════════════════════════════════════════════════════════════
# BACKUP
# ═══════════════════════════════════════════════════════════════

def backup_vault(vault_path):
    """Cria um commit Git dedicado como ponto de restauração."""
    try:
        subprocess.run(["git", "add", "-A"], cwd=vault_path, check=True,
                        capture_output=True)
        msg = f"BACKUP PRE-MIGRAÇÃO — {TODAY}"
        subprocess.run(["git", "commit", "-m", msg], cwd=vault_path,
                        check=True, capture_output=True)
        print(f"  ✅ Backup Git criado: '{msg}'")
        print(f"     Para reverter: git reset --hard HEAD~1")
        return True
    except subprocess.CalledProcessError as e:
        # Pode não haver mudanças para commitar
        print(f"  ⚠️  Git commit: {e.stderr.decode().strip()}")
        print(f"     (Isso é normal se não houver mudanças pendentes)")
        return True


# ═══════════════════════════════════════════════════════════════
# ESCRITA
# ═══════════════════════════════════════════════════════════════

def write_changes(notes_data, vault_path):
    """
    Aplica as mudanças de frontmatter nos arquivos.
    Só altera notas com confiança >= 0.7 e new_fm definido.
    """
    written = 0
    skipped = 0

    for nd in notes_data:
        if nd["new_fm"] is None:
            skipped += 1
            continue
        if nd["confidence"] < 0.7:
            skipped += 1
            continue

        new_yaml_str = render_frontmatter(nd["new_fm"])
        new_content = new_yaml_str + nd["body"]

        with open(nd["note"]["path"], "w", encoding="utf-8") as f:
            f.write(new_content)
        written += 1

    return written, skipped


# ═══════════════════════════════════════════════════════════════
# ORQUESTRADOR PRINCIPAL
# ═══════════════════════════════════════════════════════════════

def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("--dry-run", "--write"):
        print("Uso:")
        print("  python3 vault_migrator.py --dry-run   # Gera relatórios, não altera nada")
        print("  python3 vault_migrator.py --write     # Aplica mudanças com backup Git")
        sys.exit(1)

    mode = sys.argv[1]
    print(f"\n{'='*60}")
    print(f"  VAULT MIGRATOR — Modo: {mode}")
    print(f"  Vault: {VAULT_PATH}")
    print(f"  Data: {TODAY}")
    print(f"{'='*60}\n")

    # ETAPA 1: Scan
    print("📂 Etapa 1: Escaneando vault...")
    notes = scan_vault(VAULT_PATH)
    print(f"   Encontrados: {len(notes)} arquivos .md\n")

    # ETAPA 2: Extrair frontmatter e classificar
    print("🔍 Etapa 2: Extraindo frontmatter e classificando...")
    notes_data = []
    for note in notes:
        with open(note["path"], "r", encoding="utf-8") as f:
            content = f.read()

        parsed, body, raw_yaml = extract_frontmatter(content)
        note_type, confidence, reason = classify_note(note, content, parsed)
        new_fm, inferences = build_new_frontmatter(parsed, note, note_type)

        notes_data.append({
            "note": note,
            "content": content,
            "parsed": parsed,
            "body": body,
            "raw_yaml": raw_yaml,
            "type": note_type,
            "confidence": confidence,
            "reason": reason,
            "new_fm": new_fm,
            "inferences": inferences,
        })

    by_type = Counter(n["type"] for n in notes_data)
    for t in TIPOS:
        if by_type.get(t, 0) > 0:
            print(f"   {t}: {by_type[t]}")
    ambig = sum(1 for n in notes_data if n["confidence"] < 0.7)
    print(f"   ⚠️  Ambíguos (confiança < 70%): {ambig}\n")

    # ETAPA 3: Gerar relatórios
    print(f"📝 Etapa 3: Gerando relatórios em {REPORT_DIR}/...")
    generate_reports(notes_data, REPORT_DIR)
    print(f"   ✅ relatorio_classificacao.md")
    print(f"   ✅ relatorio_migracao.md")
    print(f"   ✅ ambiguidade_para_revisao.md")
    print(f"   ✅ amostras_antes_depois.md\n")

    if mode == "--dry-run":
        would = sum(1 for n in notes_data
                    if n["new_fm"] is not None and n["confidence"] >= 0.7)
        skip = len(notes_data) - would
        print(f"📊 Resultado do Dry Run:")
        print(f"   Seriam alterados: {would}")
        print(f"   Seriam pulados: {skip}")
        print(f"\n   👉 Revise os relatórios em: {REPORT_DIR}/")
        print(f"   👉 Se aprovado, execute: python3 vault_migrator.py --write\n")

    elif mode == "--write":
        print("💾 Etapa 4: Criando backup Git...")
        backup_vault(VAULT_PATH)

        print("\n✍️  Etapa 5: Escrevendo mudanças...")
        written, skipped = write_changes(notes_data, VAULT_PATH)
        print(f"   ✅ Escritos: {written}")
        print(f"   ⏭️  Pulados: {skipped}")
        print(f"\n   Para REVERTER tudo: cd {VAULT_PATH} && git reset --hard HEAD~1\n")


if __name__ == "__main__":
    main()
