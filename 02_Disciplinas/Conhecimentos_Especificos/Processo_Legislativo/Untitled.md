# Create Anki-ready TSV with flashcards based on the user's definitions.
# Columns: Front, Back, Tags (tab-separated, no header).
cards = []

def add(term_pt, def_pt, term_en, tags_extra=""):
    # Portuguese -> definition
    tags = "legislativo;processo_legislativo"
    if tags_extra:
        tags = f"{tags};{tags_extra}"
    back_pt = f"{def_pt}\n\nEN: {term_en}"
    cards.append((term_pt, back_pt, tags))
    # English -> definition (for bilingual recall)
    front_en = f"{term_en} ({term_pt})"
    cards.append((front_en, back_pt, tags))

# Definitions (kept faithful to user's phrasing, with minor formatting)
add(
    "Ação Orçamentária",
    "Operação da qual resulta um produto (bem ou serviço), contribuindo para a solução de um problema. "
    "Pode ser classificada como Projeto, Atividade ou Operação Especial.",
    "Budgetary Action",
    "orcamento"
)

add(
    "Autógrafos",
    "Texto oficial de um projeto aprovado por uma Casa legislativa, assinado por seu Presidente, "
    "e encaminhado à outra Casa para revisão ou ao Presidente da República para sanção.",
    "Engrossed Bill Text"
)

add(
    "Comissão Mista",
    "Comissão composta por Deputados e Senadores, podendo ser permanente (como a CMO, para orçamento) "
    "ou temporária (como para análise de medidas provisórias ou CPMIs).",
    "Mixed Commission",
    "rccn;comissoes"
)

add(
    "Comissão Parlamentar de Inquérito (CPI)",
    "Comissão temporária, com poderes de investigação próprios das autoridades judiciais, criada por requerimento "
    "de um terço dos membros de uma das Casas para apurar fato determinado. Quando conjunta, é CPMI.",
    "Parliamentary Commission of Inquiry",
    "comissoes;controle"
)

add(
    "Créditos Adicionais",
    "Autorizações orçamentárias para despesas não computadas ou insuficientemente dotadas na LOA. "
    "Podem ser suplementares, especiais ou extraordinários.",
    "Additional Credits",
    "orcamento"
)

add(
    "Destaque",
    "Instrumento procedimental usado na votação em Plenário para destacar parte de uma proposição "
    "(artigo, emenda etc.) e submetê-la a voto em separado.",
    "Highlight / Severance",
    "votacao;plenario"
)

add(
    "Emenda Constitucional (EC)",
    "Ato normativo que modifica a Constituição Federal, aprovado por três quintos dos membros, "
    "em dois turnos, na Câmara e no Senado.",
    "Constitutional Amendment",
    "constitucional"
)

add(
    "Estado de Sítio",
    "Medida grave e temporária que pode ser decretada pelo Presidente da República, com autorização do Congresso Nacional, "
    "em casos de comoção grave com repercussão nacional ou agressão estrangeira.",
    "State of Siege",
    "constitucional;defesa"
)

add(
    "Grupo de Natureza da Despesa (GND)",
    "Classificação que agrega elementos de despesa com características semelhantes, como ‘Pessoal e Encargos Sociais’, "
    "‘Investimentos’ ou ‘Outras Despesas Correntes’.",
    "Expenditure Nature Group",
    "orcamento;classificacao"
)

add(
    "Habeas Corpus",
    "Remédio constitucional cabível quando alguém sofre ou se acha ameaçado de sofrer violência ou coação "
    "em sua liberdade de locomoção por ilegalidade ou abuso de poder.",
    "Habeas Corpus",
    "constitucional;judiciario"
)

add(
    "Lei de Diretrizes Orçamentárias (LDO)",
    "Lei anual que fixa metas e prioridades da administração pública federal, incluindo despesas de capital para o exercício seguinte, "
    "e orienta a elaboração da LOA.",
    "Budgetary Directives Law",
    "orcamento;ldo"
)

add(
    "Lei Orçamentária Anual (LOA)",
    "Lei que estima as receitas e fixa as despesas da União para um exercício financeiro.",
    "Annual Budget Law",
    "orcamento;loa"
)

add(
    "Medida Provisória (MP)",
    "Ato com força de lei, editado pelo Presidente da República em casos de relevância e urgência, "
    "devendo ser submetido imediatamente ao Congresso para conversão em lei.",
    "Provisional Measure",
    "mp;processo_legislativo"
)

add(
    "Mesa Diretora",
    "Órgão diretivo de uma Casa legislativa (Câmara ou Senado), responsável pela direção dos trabalhos legislativos "
    "e dos serviços administrativos. Composta por Presidente, Vice-Presidentes e Secretários.",
    "Directing Board",
    "orgaos"
)

add(
    "Parecer",
    "Manifestação formal de comissão sobre proposição, contendo relatório (resumo da matéria) e voto do relator "
    "pela aprovação ou rejeição.",
    "Opinion / Report",
    "comissoes"
)

add(
    "Plano Plurianual (PPA)",
    "Lei que estabelece, de forma regionalizada, diretrizes, objetivos e metas da administração pública federal "
    "para despesas de capital e programas continuados, por quatro anos.",
    "Pluriannual Plan",
    "orcamento;ppa;planejamento"
)

add(
    "Precatório",
    "Ordem judicial de pagamento de quantia certa devida pela Fazenda Pública (União, Estado, Município) "
    "decorrente de sentença transitada em julgado.",
    "Court-Ordered Government Payment (Writ)",
    "judiciario;orcamento"
)

add(
    "Proposição",
    "Qualquer matéria sujeita à deliberação da Câmara dos Deputados, como PEC, PL, emenda, requerimento, moção e parecer.",
    "Proposal (Legislative Item)",
    "processo_legislativo"
)

add(
    "Questão de Ordem",
    "Indagação apresentada por parlamentar, durante a sessão, sobre a interpretação e aplicação da Constituição "
    "ou do Regimento em relação à matéria em discussão.",
    "Point of Order",
    "plenario;interpretacao"
)

add(
    "Redação Final",
    "Texto definitivo de um projeto após concluída a votação, elaborado por comissão competente para consolidar as alterações "
    "aprovadas e assegurar a técnica legislativa antes do envio à outra Casa ou sanção.",
    "Final Wording",
    "tecnica_legislativa"
)

add(
    "Regime de Urgência",
    "Procedimento que, mediante aprovação do Plenário, acelera a apreciação de uma proposição, dispensando etapas e prazos.",
    "Urgency Procedure",
    "tramitação;plenario"
)

add(
    "Sessão Conjunta",
    "Reunião da Câmara dos Deputados e do Senado Federal para deliberar matérias de competência comum, "
    "como veto presidencial e orçamento, ou para inaugurar a sessão legislativa.",
    "Joint Session",
    "rccn;plenario"
)

add(
    "Súmula Vinculante",
    "Enunciado do STF, aprovado por dois terços de seus membros, que consolida entendimento constitucional e torna-se obrigatório "
    "para o Judiciário e a administração pública.",
    "Binding Precedent (STF)",
    "constitucional;stf"
)

add(
    "Veto (Jurídico / Político)",
    "Ato do Presidente da República que recusa sanção, total ou parcial, a um projeto de lei. O veto jurídico funda-se em "
    "inconstitucionalidade; o veto político, em contrariedade ao interesse público.",
    "Veto (Legal / Political)",
    "veto;processo_legislativo"
)

# Write TSV file
path = "/mnt/data/anki_flashcards_legislativo.tsv"
with open(path, "w", encoding="utf-8") as f:
    for front, back, tags in cards:
        # Replace newlines in fields with <br> so Anki shows line breaks
        front_s = front.replace("\n", "<br>")
        back_s = back.replace("\n", "<br>")
        f.write(f"{front_s}\t{back_s}\t{tags}\n")

path
