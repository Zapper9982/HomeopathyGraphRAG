"""
Expanded Homeopathic Knowledge Graph — based on classical repertory sources.

Contains ~150 symptoms, ~50 remedies, ~30 rubrics across major chapters,
plus extensive contradiction/correlation edges and historical case data.

Sources modeled after: Kent's Repertory, Boericke's Materia Medica,
Clarke's Dictionary, Phatak's Repertory (structure, not verbatim text).
"""

# ══════════════════════════════════════════════════════════
#  SYMPTOMS — organized by category
# ══════════════════════════════════════════════════════════

SYMPTOMS = [
    # ── Mind ────────────────────────────────────────────
    {"id": "SYM_MIND_001", "name": "Anxiety about health", "category": "mental"},
    {"id": "SYM_MIND_002", "name": "Restlessness", "category": "mental"},
    {"id": "SYM_MIND_003", "name": "Fear of death", "category": "mental"},
    {"id": "SYM_MIND_004", "name": "Irritability", "category": "mental"},
    {"id": "SYM_MIND_005", "name": "Weeping tendency", "category": "mental"},
    {"id": "SYM_MIND_006", "name": "Emotional numbness", "category": "mental"},
    {"id": "SYM_MIND_007", "name": "Grief suppressed", "category": "mental"},
    {"id": "SYM_MIND_008", "name": "Anticipatory anxiety", "category": "mental"},
    {"id": "SYM_MIND_009", "name": "Sadness without cause", "category": "mental"},
    {"id": "SYM_MIND_010", "name": "Concentration difficulty", "category": "mental"},
    {"id": "SYM_MIND_011", "name": "Jealousy", "category": "mental"},
    {"id": "SYM_MIND_012", "name": "Suspicious nature", "category": "mental"},
    {"id": "SYM_MIND_013", "name": "Fear of being alone", "category": "mental"},
    {"id": "SYM_MIND_014", "name": "Desire for company", "category": "mental"},
    {"id": "SYM_MIND_015", "name": "Aversion to company", "category": "mental"},
    {"id": "SYM_MIND_016", "name": "Anger with trembling", "category": "mental"},
    {"id": "SYM_MIND_017", "name": "Ailments from fright", "category": "mental"},
    {"id": "SYM_MIND_018", "name": "Fastidious about order", "category": "mental"},
    {"id": "SYM_MIND_019", "name": "Delusion of being watched", "category": "mental"},
    {"id": "SYM_MIND_020", "name": "Mental exhaustion", "category": "mental"},
    {"id": "SYM_MIND_021", "name": "Forgetfulness", "category": "mental"},
    {"id": "SYM_MIND_022", "name": "Desire to break things", "category": "mental"},
    {"id": "SYM_MIND_023", "name": "Indifference to loved ones", "category": "mental"},
    {"id": "SYM_MIND_024", "name": "Ailments from grief", "category": "mental"},
    {"id": "SYM_MIND_025", "name": "Hurried feeling", "category": "mental"},

    # ── Head ────────────────────────────────────────────
    {"id": "SYM_HEAD_001", "name": "Throbbing headache", "category": "head"},
    {"id": "SYM_HEAD_002", "name": "Bursting headache", "category": "head"},
    {"id": "SYM_HEAD_003", "name": "Pressing headache forehead", "category": "head"},
    {"id": "SYM_HEAD_004", "name": "One-sided headache", "category": "head"},
    {"id": "SYM_HEAD_005", "name": "Headache from sun exposure", "category": "head"},
    {"id": "SYM_HEAD_006", "name": "Headache with nausea", "category": "head"},
    {"id": "SYM_HEAD_007", "name": "Headache better by pressure", "category": "head"},
    {"id": "SYM_HEAD_008", "name": "Congestive headache", "category": "head"},
    {"id": "SYM_HEAD_009", "name": "Occipital headache", "category": "head"},
    {"id": "SYM_HEAD_010", "name": "Headache worse morning", "category": "head"},

    # ── Eye ─────────────────────────────────────────────
    {"id": "SYM_EYE_001", "name": "Dilated pupils", "category": "eye"},
    {"id": "SYM_EYE_002", "name": "Burning in eyes", "category": "eye"},
    {"id": "SYM_EYE_003", "name": "Photophobia", "category": "eye"},
    {"id": "SYM_EYE_004", "name": "Lachrymation in open air", "category": "eye"},
    {"id": "SYM_EYE_005", "name": "Styes recurring", "category": "eye"},

    # ── Face ────────────────────────────────────────────
    {"id": "SYM_FACE_001", "name": "Red flushed face", "category": "face"},
    {"id": "SYM_FACE_002", "name": "Pale face", "category": "face"},
    {"id": "SYM_FACE_003", "name": "Swollen face", "category": "face"},
    {"id": "SYM_FACE_004", "name": "Acne on face", "category": "face"},
    {"id": "SYM_FACE_005", "name": "Facial neuralgia", "category": "face"},

    # ── Throat ──────────────────────────────────────────
    {"id": "SYM_THROAT_001", "name": "Burning in throat", "category": "throat"},
    {"id": "SYM_THROAT_002", "name": "Throat pain swallowing", "category": "throat"},
    {"id": "SYM_THROAT_003", "name": "Throat dry and raw", "category": "throat"},
    {"id": "SYM_THROAT_004", "name": "Sensation of lump in throat", "category": "throat"},
    {"id": "SYM_THROAT_005", "name": "Throat better warm drinks", "category": "throat"},
    {"id": "SYM_THROAT_006", "name": "Throat worse warm drinks", "category": "throat"},

    # ── Stomach ─────────────────────────────────────────
    {"id": "SYM_STOM_001", "name": "Nausea", "category": "stomach"},
    {"id": "SYM_STOM_002", "name": "Vomiting", "category": "stomach"},
    {"id": "SYM_STOM_003", "name": "Thirstlessness", "category": "stomach"},
    {"id": "SYM_STOM_004", "name": "Extreme thirst for cold water", "category": "stomach"},
    {"id": "SYM_STOM_005", "name": "Thirst for small sips", "category": "stomach"},
    {"id": "SYM_STOM_006", "name": "Desire for sour food", "category": "stomach"},
    {"id": "SYM_STOM_007", "name": "Desire for sweets", "category": "stomach"},
    {"id": "SYM_STOM_008", "name": "Aversion to fatty food", "category": "stomach"},
    {"id": "SYM_STOM_009", "name": "Desire for salt", "category": "stomach"},
    {"id": "SYM_STOM_010", "name": "Bloating after eating", "category": "stomach"},
    {"id": "SYM_STOM_011", "name": "Heartburn", "category": "stomach"},
    {"id": "SYM_STOM_012", "name": "Appetite increased", "category": "stomach"},
    {"id": "SYM_STOM_013", "name": "Appetite lost", "category": "stomach"},

    # ── Abdomen ─────────────────────────────────────────
    {"id": "SYM_ABD_001", "name": "Abdominal distension", "category": "abdomen"},
    {"id": "SYM_ABD_002", "name": "Cutting abdominal pain", "category": "abdomen"},
    {"id": "SYM_ABD_003", "name": "Rumbling in abdomen", "category": "abdomen"},
    {"id": "SYM_ABD_004", "name": "Pain right hypochondrium", "category": "abdomen"},
    {"id": "SYM_ABD_005", "name": "Pain better bending double", "category": "abdomen"},

    # ── Respiratory ─────────────────────────────────────
    {"id": "SYM_RESP_001", "name": "Dry cough", "category": "respiratory"},
    {"id": "SYM_RESP_002", "name": "Cough worse at night", "category": "respiratory"},
    {"id": "SYM_RESP_003", "name": "Cough worse lying down", "category": "respiratory"},
    {"id": "SYM_RESP_004", "name": "Dyspnea on exertion", "category": "respiratory"},
    {"id": "SYM_RESP_005", "name": "Wheezing", "category": "respiratory"},
    {"id": "SYM_RESP_006", "name": "Rattling cough", "category": "respiratory"},

    # ── Extremities ─────────────────────────────────────
    {"id": "SYM_EXT_001", "name": "Joint stiffness", "category": "extremity"},
    {"id": "SYM_EXT_002", "name": "Wandering pains", "category": "extremity"},
    {"id": "SYM_EXT_003", "name": "Numbness in extremities", "category": "extremity"},
    {"id": "SYM_EXT_004", "name": "Cramps in calves", "category": "extremity"},
    {"id": "SYM_EXT_005", "name": "Cold extremities", "category": "extremity"},
    {"id": "SYM_EXT_006", "name": "Hot palms and soles", "category": "extremity"},
    {"id": "SYM_EXT_007", "name": "Restless legs", "category": "extremity"},
    {"id": "SYM_EXT_008", "name": "Swollen joints", "category": "extremity"},

    # ── Skin ────────────────────────────────────────────
    {"id": "SYM_SKIN_001", "name": "Itching worse warmth", "category": "skin"},
    {"id": "SYM_SKIN_002", "name": "Dry rough skin", "category": "skin"},
    {"id": "SYM_SKIN_003", "name": "Eruptions with burning", "category": "skin"},
    {"id": "SYM_SKIN_004", "name": "Urticaria", "category": "skin"},
    {"id": "SYM_SKIN_005", "name": "Eczema of folds", "category": "skin"},
    {"id": "SYM_SKIN_006", "name": "Psoriasis patches", "category": "skin"},

    # ── Sleep ───────────────────────────────────────────
    {"id": "SYM_SLEEP_001", "name": "Insomnia from anxiety", "category": "sleep"},
    {"id": "SYM_SLEEP_002", "name": "Sleeps on left side", "category": "sleep"},
    {"id": "SYM_SLEEP_003", "name": "Unrefreshing sleep", "category": "sleep"},
    {"id": "SYM_SLEEP_004", "name": "Night terrors", "category": "sleep"},
    {"id": "SYM_SLEEP_005", "name": "Wakes at 3 AM", "category": "sleep"},

    # ── Fever / Thermal ─────────────────────────────────
    {"id": "SYM_THER_001", "name": "Chilly patient", "category": "thermal"},
    {"id": "SYM_THER_002", "name": "Hot patient", "category": "thermal"},
    {"id": "SYM_THER_003", "name": "Desire for open air", "category": "thermal"},
    {"id": "SYM_THER_004", "name": "Aversion to open air", "category": "thermal"},
    {"id": "SYM_THER_005", "name": "Fever with shivering", "category": "thermal"},
    {"id": "SYM_THER_006", "name": "Night sweats", "category": "thermal"},

    # ── Modalities ──────────────────────────────────────
    {"id": "SYM_MOD_001", "name": "Worse by heat", "category": "modality"},
    {"id": "SYM_MOD_002", "name": "Desire for warmth", "category": "modality"},
    {"id": "SYM_MOD_003", "name": "Worse at night", "category": "modality"},
    {"id": "SYM_MOD_004", "name": "Better by pressure", "category": "modality"},
    {"id": "SYM_MOD_005", "name": "Worse by motion", "category": "modality"},
    {"id": "SYM_MOD_006", "name": "Better by motion", "category": "modality"},
    {"id": "SYM_MOD_007", "name": "Worse by cold", "category": "modality"},
    {"id": "SYM_MOD_008", "name": "Better by cold application", "category": "modality"},
    {"id": "SYM_MOD_009", "name": "Worse by touch", "category": "modality"},
    {"id": "SYM_MOD_010", "name": "Worse in morning", "category": "modality"},
    {"id": "SYM_MOD_011", "name": "Better by eating", "category": "modality"},
    {"id": "SYM_MOD_012", "name": "Worse after eating", "category": "modality"},
    {"id": "SYM_MOD_013", "name": "Worse in damp weather", "category": "modality"},
    {"id": "SYM_MOD_014", "name": "Better in dry weather", "category": "modality"},
    {"id": "SYM_MOD_015", "name": "Worse by exertion", "category": "modality"},
    {"id": "SYM_MOD_016", "name": "Better by rest", "category": "modality"},
    {"id": "SYM_MOD_017", "name": "Sun aggravation", "category": "modality"},
    {"id": "SYM_MOD_018", "name": "Periodicity in symptoms", "category": "modality"},
    {"id": "SYM_MOD_019", "name": "Worse in autumn", "category": "modality"},
    {"id": "SYM_MOD_020", "name": "Worse by suppressed eruptions", "category": "modality"},
    {"id": "SYM_MOD_021", "name": "Weeping ameliorates", "category": "modality"},

    # ── Onset ───────────────────────────────────────────
    {"id": "SYM_ONSET_001", "name": "Sudden onset", "category": "onset"},
    {"id": "SYM_ONSET_002", "name": "Gradual onset", "category": "onset"},

    # ── Sensation ───────────────────────────────────────
    {"id": "SYM_SENS_001", "name": "Burning pains", "category": "sensation"},
    {"id": "SYM_SENS_002", "name": "Stitching pains", "category": "sensation"},
    {"id": "SYM_SENS_003", "name": "Soreness bruised feeling", "category": "sensation"},
    {"id": "SYM_SENS_004", "name": "Heaviness sensation", "category": "sensation"},
    {"id": "SYM_SENS_005", "name": "Constriction band-like", "category": "sensation"},

    # ── Sexual / Hormonal ───────────────────────────────
    {"id": "SYM_SEX_001", "name": "Menses scanty", "category": "sexual"},
    {"id": "SYM_SEX_002", "name": "Menses profuse", "category": "sexual"},
    {"id": "SYM_SEX_003", "name": "Premenstrual irritability", "category": "sexual"},
    {"id": "SYM_SEX_004", "name": "Leucorrhea acrid", "category": "sexual"},
    {"id": "SYM_SEX_005", "name": "Menopausal flushes", "category": "sexual"},
]

# ══════════════════════════════════════════════════════════
#  RUBRICS — repertory chapter headings
# ══════════════════════════════════════════════════════════

RUBRICS = [
    # Mind
    {"id": "RUB_MIND_01", "chapter": "Mind", "text": "Mind; anxiety; health about"},
    {"id": "RUB_MIND_02", "chapter": "Mind", "text": "Mind; restlessness; anxious"},
    {"id": "RUB_MIND_03", "chapter": "Mind", "text": "Mind; fear; death of"},
    {"id": "RUB_MIND_04", "chapter": "Mind", "text": "Mind; irritability"},
    {"id": "RUB_MIND_05", "chapter": "Mind", "text": "Mind; weeping; tendency"},
    {"id": "RUB_MIND_06", "chapter": "Mind", "text": "Mind; emotional; numbness"},
    {"id": "RUB_MIND_07", "chapter": "Mind", "text": "Mind; grief; ailments from"},
    {"id": "RUB_MIND_08", "chapter": "Mind", "text": "Mind; anticipation; anxiety from"},
    {"id": "RUB_MIND_09", "chapter": "Mind", "text": "Mind; sadness; causeless"},
    {"id": "RUB_MIND_10", "chapter": "Mind", "text": "Mind; concentration; difficult"},
    {"id": "RUB_MIND_11", "chapter": "Mind", "text": "Mind; jealousy"},
    {"id": "RUB_MIND_12", "chapter": "Mind", "text": "Mind; suspicious"},
    {"id": "RUB_MIND_13", "chapter": "Mind", "text": "Mind; company; desire for"},
    {"id": "RUB_MIND_14", "chapter": "Mind", "text": "Mind; company; aversion to"},
    {"id": "RUB_MIND_15", "chapter": "Mind", "text": "Mind; anger; trembling with"},
    {"id": "RUB_MIND_16", "chapter": "Mind", "text": "Mind; fright; ailments from"},
    {"id": "RUB_MIND_17", "chapter": "Mind", "text": "Mind; fastidious"},
    {"id": "RUB_MIND_18", "chapter": "Mind", "text": "Mind; indifference; loved ones to"},
    {"id": "RUB_MIND_19", "chapter": "Mind", "text": "Mind; hurried"},

    # Head
    {"id": "RUB_HEAD_01", "chapter": "Head", "text": "Head; pain; throbbing"},
    {"id": "RUB_HEAD_02", "chapter": "Head", "text": "Head; pain; bursting"},
    {"id": "RUB_HEAD_03", "chapter": "Head", "text": "Head; pain; pressing; forehead"},
    {"id": "RUB_HEAD_04", "chapter": "Head", "text": "Head; pain; one-sided"},
    {"id": "RUB_HEAD_05", "chapter": "Head", "text": "Head; pain; sun from"},
    {"id": "RUB_HEAD_06", "chapter": "Head", "text": "Head; pain; nausea with"},
    {"id": "RUB_HEAD_07", "chapter": "Head", "text": "Head; congestion"},

    # Eye
    {"id": "RUB_EYE_01", "chapter": "Eye", "text": "Eye; pupils; dilated"},
    {"id": "RUB_EYE_02", "chapter": "Eye", "text": "Eye; burning"},
    {"id": "RUB_EYE_03", "chapter": "Eye", "text": "Eye; photophobia"},

    # Face
    {"id": "RUB_FACE_01", "chapter": "Face", "text": "Face; red"},
    {"id": "RUB_FACE_02", "chapter": "Face", "text": "Face; pale"},
    {"id": "RUB_FACE_03", "chapter": "Face", "text": "Face; swelling"},

    # Throat
    {"id": "RUB_THR_01", "chapter": "Throat", "text": "Throat; pain; burning"},
    {"id": "RUB_THR_02", "chapter": "Throat", "text": "Throat; pain; swallowing on"},
    {"id": "RUB_THR_03", "chapter": "Throat", "text": "Throat; dryness"},
    {"id": "RUB_THR_04", "chapter": "Throat", "text": "Throat; lump sensation"},

    # Stomach
    {"id": "RUB_STOM_01", "chapter": "Stomach", "text": "Stomach; nausea"},
    {"id": "RUB_STOM_02", "chapter": "Stomach", "text": "Stomach; vomiting"},
    {"id": "RUB_STOM_03", "chapter": "Stomach", "text": "Stomach; thirstless"},
    {"id": "RUB_STOM_04", "chapter": "Stomach", "text": "Stomach; thirst; large quantities"},
    {"id": "RUB_STOM_05", "chapter": "Stomach", "text": "Stomach; thirst; small sips"},
    {"id": "RUB_STOM_06", "chapter": "Stomach", "text": "Stomach; desires; sour"},
    {"id": "RUB_STOM_07", "chapter": "Stomach", "text": "Stomach; desires; salt"},
    {"id": "RUB_STOM_08", "chapter": "Stomach", "text": "Stomach; bloating; eating after"},

    # Respiratory
    {"id": "RUB_RESP_01", "chapter": "Respiratory", "text": "Cough; dry"},
    {"id": "RUB_RESP_02", "chapter": "Respiratory", "text": "Cough; night; agg"},
    {"id": "RUB_RESP_03", "chapter": "Respiratory", "text": "Respiration; difficult; exertion on"},

    # Generalities
    {"id": "RUB_GEN_01", "chapter": "Generalities", "text": "Generalities; heat; agg"},
    {"id": "RUB_GEN_02", "chapter": "Generalities", "text": "Generalities; warmth; desire"},
    {"id": "RUB_GEN_03", "chapter": "Generalities", "text": "Generalities; cold; agg"},
    {"id": "RUB_GEN_04", "chapter": "Generalities", "text": "Generalities; motion; agg"},
    {"id": "RUB_GEN_05", "chapter": "Generalities", "text": "Generalities; motion; amel"},
    {"id": "RUB_GEN_06", "chapter": "Generalities", "text": "Generalities; night; agg"},
    {"id": "RUB_GEN_07", "chapter": "Generalities", "text": "Generalities; sun; agg"},
    {"id": "RUB_GEN_08", "chapter": "Generalities", "text": "Generalities; sudden onset"},
    {"id": "RUB_GEN_09", "chapter": "Generalities", "text": "Generalities; pressure; amel"},
    {"id": "RUB_GEN_10", "chapter": "Generalities", "text": "Generalities; touch; agg"},
    {"id": "RUB_GEN_11", "chapter": "Generalities", "text": "Generalities; damp weather; agg"},
    {"id": "RUB_GEN_12", "chapter": "Generalities", "text": "Generalities; periodicity"},
    {"id": "RUB_GEN_13", "chapter": "Generalities", "text": "Generalities; burning pains"},

    # Skin
    {"id": "RUB_SKIN_01", "chapter": "Skin", "text": "Skin; itching; warmth agg"},
    {"id": "RUB_SKIN_02", "chapter": "Skin", "text": "Skin; eruptions; burning"},
    {"id": "RUB_SKIN_03", "chapter": "Skin", "text": "Skin; dry"},
    {"id": "RUB_SKIN_04", "chapter": "Skin", "text": "Skin; urticaria"},

    # Sleep
    {"id": "RUB_SLEEP_01", "chapter": "Sleep", "text": "Sleep; insomnia; anxiety from"},
    {"id": "RUB_SLEEP_02", "chapter": "Sleep", "text": "Sleep; unrefreshing"},
    {"id": "RUB_SLEEP_03", "chapter": "Sleep", "text": "Sleep; waking; 3 AM"},

    # Female
    {"id": "RUB_FEM_01", "chapter": "Female", "text": "Female; menses; scanty"},
    {"id": "RUB_FEM_02", "chapter": "Female", "text": "Female; menses; profuse"},
]


# ══════════════════════════════════════════════════════════
#  REMEDIES — 50 key polychrests + smaller remedies
# ══════════════════════════════════════════════════════════

REMEDIES = [
    {"name": "Aconitum Napellus",   "abbrev": "Acon",    "miasm": "acute"},
    {"name": "Apis Mellifica",      "abbrev": "Apis",    "miasm": "sycotic"},
    {"name": "Argentum Nitricum",   "abbrev": "Arg-n",   "miasm": "sycotic"},
    {"name": "Arnica Montana",      "abbrev": "Arn",     "miasm": "psoric"},
    {"name": "Arsenicum Album",     "abbrev": "Ars",     "miasm": "psoric"},
    {"name": "Belladonna",          "abbrev": "Bell",    "miasm": "acute"},
    {"name": "Bryonia Alba",        "abbrev": "Bry",     "miasm": "psoric"},
    {"name": "Calcarea Carbonica",  "abbrev": "Calc",    "miasm": "psoric"},
    {"name": "Carbo Vegetabilis",   "abbrev": "Carb-v",  "miasm": "psoric"},
    {"name": "Chamomilla",          "abbrev": "Cham",    "miasm": "psoric"},
    {"name": "China Officinalis",   "abbrev": "Chin",    "miasm": "psoric"},
    {"name": "Colocynthis",         "abbrev": "Coloc",   "miasm": "psoric"},
    {"name": "Dulcamara",           "abbrev": "Dulc",    "miasm": "sycotic"},
    {"name": "Gelsemium",           "abbrev": "Gels",    "miasm": "psoric"},
    {"name": "Graphites",           "abbrev": "Graph",   "miasm": "psoric"},
    {"name": "Hepar Sulphuris",     "abbrev": "Hep",     "miasm": "psoric"},
    {"name": "Ignatia Amara",       "abbrev": "Ign",     "miasm": "psoric"},
    {"name": "Ipecacuanha",         "abbrev": "Ip",      "miasm": "psoric"},
    {"name": "Kali Carbonicum",     "abbrev": "Kali-c",  "miasm": "psoric"},
    {"name": "Lachesis",            "abbrev": "Lach",    "miasm": "syphilitic"},
    {"name": "Lycopodium",          "abbrev": "Lyc",     "miasm": "sycotic"},
    {"name": "Mercurius Solubilis", "abbrev": "Merc",    "miasm": "syphilitic"},
    {"name": "Natrum Carbonicum",   "abbrev": "Nat-c",   "miasm": "psoric"},
    {"name": "Natrum Muriaticum",   "abbrev": "Nat-m",   "miasm": "psoric"},
    {"name": "Nitric Acid",         "abbrev": "Nit-ac",  "miasm": "syphilitic"},
    {"name": "Nux Moschata",        "abbrev": "Nux-m",   "miasm": "psoric"},
    {"name": "Nux Vomica",          "abbrev": "Nux-v",   "miasm": "psoric"},
    {"name": "Opium",               "abbrev": "Op",      "miasm": "psoric"},
    {"name": "Phosphoric Acid",     "abbrev": "Ph-ac",   "miasm": "psoric"},
    {"name": "Phosphorus",          "abbrev": "Phos",    "miasm": "psoric"},
    {"name": "Pulsatilla",          "abbrev": "Puls",    "miasm": "psoric"},
    {"name": "Rhus Toxicodendron",  "abbrev": "Rhus-t",  "miasm": "psoric"},
    {"name": "Sepia",               "abbrev": "Sep",     "miasm": "psoric"},
    {"name": "Silicea",             "abbrev": "Sil",     "miasm": "psoric"},
    {"name": "Staphysagria",        "abbrev": "Staph",   "miasm": "sycotic"},
    {"name": "Sulphur",             "abbrev": "Sulph",   "miasm": "psoric"},
    {"name": "Thuja Occidentalis",  "abbrev": "Thuj",    "miasm": "sycotic"},
    {"name": "Tuberculinum",        "abbrev": "Tub",     "miasm": "tubercular"},
    {"name": "Veratrum Album",      "abbrev": "Verat",   "miasm": "psoric"},
    {"name": "Zincum Metallicum",   "abbrev": "Zinc",    "miasm": "psoric"},
    {"name": "Medorrhinum",         "abbrev": "Med",     "miasm": "sycotic"},
    {"name": "Baryta Carbonica",    "abbrev": "Bar-c",   "miasm": "psoric"},
    {"name": "Causticum",           "abbrev": "Caust",   "miasm": "sycotic"},
    {"name": "Conium Maculatum",    "abbrev": "Con",     "miasm": "sycotic"},
    {"name": "Aurum Metallicum",    "abbrev": "Aur",     "miasm": "syphilitic"},
    {"name": "Platina",             "abbrev": "Plat",    "miasm": "syphilitic"},
    {"name": "Stramonium",          "abbrev": "Stram",   "miasm": "acute"},
    {"name": "Antimonium Tartaricum", "abbrev": "Ant-t", "miasm": "psoric"},
    {"name": "Podophyllum",         "abbrev": "Podo",    "miasm": "psoric"},
    {"name": "Cantharis",           "abbrev": "Canth",   "miasm": "sycotic"},
]


# ══════════════════════════════════════════════════════════
#  SYMPTOM → RUBRIC MAPPINGS
# ══════════════════════════════════════════════════════════

SYMPTOM_RUBRIC_LINKS = [
    # Mind
    ("SYM_MIND_001", "RUB_MIND_01"),
    ("SYM_MIND_002", "RUB_MIND_02"),
    ("SYM_MIND_003", "RUB_MIND_03"),
    ("SYM_MIND_004", "RUB_MIND_04"),
    ("SYM_MIND_005", "RUB_MIND_05"),
    ("SYM_MIND_006", "RUB_MIND_06"),
    ("SYM_MIND_007", "RUB_MIND_07"),
    ("SYM_MIND_024", "RUB_MIND_07"),
    ("SYM_MIND_008", "RUB_MIND_08"),
    ("SYM_MIND_009", "RUB_MIND_09"),
    ("SYM_MIND_010", "RUB_MIND_10"),
    ("SYM_MIND_011", "RUB_MIND_11"),
    ("SYM_MIND_012", "RUB_MIND_12"),
    ("SYM_MIND_014", "RUB_MIND_13"),
    ("SYM_MIND_015", "RUB_MIND_14"),
    ("SYM_MIND_016", "RUB_MIND_15"),
    ("SYM_MIND_017", "RUB_MIND_16"),
    ("SYM_MIND_018", "RUB_MIND_17"),
    ("SYM_MIND_023", "RUB_MIND_18"),
    ("SYM_MIND_025", "RUB_MIND_19"),
    # Head
    ("SYM_HEAD_001", "RUB_HEAD_01"),
    ("SYM_HEAD_002", "RUB_HEAD_02"),
    ("SYM_HEAD_003", "RUB_HEAD_03"),
    ("SYM_HEAD_004", "RUB_HEAD_04"),
    ("SYM_HEAD_005", "RUB_HEAD_05"),
    ("SYM_HEAD_006", "RUB_HEAD_06"),
    ("SYM_HEAD_008", "RUB_HEAD_07"),
    # Eye
    ("SYM_EYE_001", "RUB_EYE_01"),
    ("SYM_EYE_002", "RUB_EYE_02"),
    ("SYM_EYE_003", "RUB_EYE_03"),
    # Face
    ("SYM_FACE_001", "RUB_FACE_01"),
    ("SYM_FACE_002", "RUB_FACE_02"),
    ("SYM_FACE_003", "RUB_FACE_03"),
    # Throat
    ("SYM_THROAT_001", "RUB_THR_01"),
    ("SYM_THROAT_002", "RUB_THR_02"),
    ("SYM_THROAT_003", "RUB_THR_03"),
    ("SYM_THROAT_004", "RUB_THR_04"),
    # Stomach
    ("SYM_STOM_001", "RUB_STOM_01"),
    ("SYM_STOM_002", "RUB_STOM_02"),
    ("SYM_STOM_003", "RUB_STOM_03"),
    ("SYM_STOM_004", "RUB_STOM_04"),
    ("SYM_STOM_005", "RUB_STOM_05"),
    ("SYM_STOM_006", "RUB_STOM_06"),
    ("SYM_STOM_009", "RUB_STOM_07"),
    ("SYM_STOM_010", "RUB_STOM_08"),
    # Respiratory
    ("SYM_RESP_001", "RUB_RESP_01"),
    ("SYM_RESP_002", "RUB_RESP_02"),
    ("SYM_RESP_004", "RUB_RESP_03"),
    # Generalities / Modalities
    ("SYM_MOD_001", "RUB_GEN_01"),
    ("SYM_THER_002", "RUB_GEN_01"),
    ("SYM_MOD_002", "RUB_GEN_02"),
    ("SYM_THER_001", "RUB_GEN_03"),
    ("SYM_MOD_007", "RUB_GEN_03"),
    ("SYM_MOD_005", "RUB_GEN_04"),
    ("SYM_MOD_006", "RUB_GEN_05"),
    ("SYM_MOD_003", "RUB_GEN_06"),
    ("SYM_MOD_017", "RUB_GEN_07"),
    ("SYM_ONSET_001", "RUB_GEN_08"),
    ("SYM_MOD_004", "RUB_GEN_09"),
    ("SYM_MOD_009", "RUB_GEN_10"),
    ("SYM_MOD_013", "RUB_GEN_11"),
    ("SYM_MOD_018", "RUB_GEN_12"),
    ("SYM_SENS_001", "RUB_GEN_13"),
    # Skin
    ("SYM_SKIN_001", "RUB_SKIN_01"),
    ("SYM_SKIN_003", "RUB_SKIN_02"),
    ("SYM_SKIN_002", "RUB_SKIN_03"),
    ("SYM_SKIN_004", "RUB_SKIN_04"),
    # Sleep
    ("SYM_SLEEP_001", "RUB_SLEEP_01"),
    ("SYM_SLEEP_003", "RUB_SLEEP_02"),
    ("SYM_SLEEP_005", "RUB_SLEEP_03"),
    # Female
    ("SYM_SEX_001", "RUB_FEM_01"),
    ("SYM_SEX_002", "RUB_FEM_02"),
]


# ══════════════════════════════════════════════════════════
#  RUBRIC → REMEDY INDICATIONS  (rubric_id, remedy_name, grade 1-3)
#
#  Grade 3 = bold/strongly confirmed
#  Grade 2 = italic/confirmed
#  Grade 1 = plain/mentioned
# ══════════════════════════════════════════════════════════

RUBRIC_REMEDY_INDICATIONS = [
    # ── Mind rubrics ─────────────────────────────────────
    # Anxiety about health
    ("RUB_MIND_01", "Arsenicum Album", 3),
    ("RUB_MIND_01", "Phosphorus", 2),
    ("RUB_MIND_01", "Nitric Acid", 2),
    ("RUB_MIND_01", "Kali Carbonicum", 1),
    ("RUB_MIND_01", "Calcarea Carbonica", 2),

    # Restlessness
    ("RUB_MIND_02", "Arsenicum Album", 3),
    ("RUB_MIND_02", "Rhus Toxicodendron", 3),
    ("RUB_MIND_02", "Aconitum Napellus", 2),
    ("RUB_MIND_02", "Chamomilla", 2),
    ("RUB_MIND_02", "Zincum Metallicum", 2),
    ("RUB_MIND_02", "Tuberculinum", 1),

    # Fear of death
    ("RUB_MIND_03", "Aconitum Napellus", 3),
    ("RUB_MIND_03", "Arsenicum Album", 3),
    ("RUB_MIND_03", "Phosphorus", 1),
    ("RUB_MIND_03", "Platina", 1),

    # Irritability
    ("RUB_MIND_04", "Nux Vomica", 3),
    ("RUB_MIND_04", "Chamomilla", 3),
    ("RUB_MIND_04", "Bryonia Alba", 2),
    ("RUB_MIND_04", "Kali Carbonicum", 2),
    ("RUB_MIND_04", "Hepar Sulphuris", 2),
    ("RUB_MIND_04", "Staphysagria", 2),
    ("RUB_MIND_04", "Lycopodium", 2),
    ("RUB_MIND_04", "Sepia", 2),
    ("RUB_MIND_04", "Sulphur", 1),

    # Weeping tendency
    ("RUB_MIND_05", "Pulsatilla", 3),
    ("RUB_MIND_05", "Ignatia Amara", 3),
    ("RUB_MIND_05", "Natrum Muriaticum", 2),
    ("RUB_MIND_05", "Sepia", 2),
    ("RUB_MIND_05", "Calcarea Carbonica", 1),

    # Emotional numbness
    ("RUB_MIND_06", "Natrum Muriaticum", 3),
    ("RUB_MIND_06", "Phosphoric Acid", 3),
    ("RUB_MIND_06", "Opium", 2),
    ("RUB_MIND_06", "Sepia", 2),
    ("RUB_MIND_06", "Conium Maculatum", 1),

    # Grief ailments
    ("RUB_MIND_07", "Ignatia Amara", 3),
    ("RUB_MIND_07", "Natrum Muriaticum", 3),
    ("RUB_MIND_07", "Phosphoric Acid", 2),
    ("RUB_MIND_07", "Staphysagria", 2),
    ("RUB_MIND_07", "Aurum Metallicum", 2),

    # Anticipatory anxiety
    ("RUB_MIND_08", "Argentum Nitricum", 3),
    ("RUB_MIND_08", "Gelsemium", 3),
    ("RUB_MIND_08", "Lycopodium", 2),
    ("RUB_MIND_08", "Silicea", 2),

    # Sadness causeless
    ("RUB_MIND_09", "Natrum Muriaticum", 3),
    ("RUB_MIND_09", "Aurum Metallicum", 3),
    ("RUB_MIND_09", "Sepia", 2),
    ("RUB_MIND_09", "Ignatia Amara", 2),
    ("RUB_MIND_09", "Phosphoric Acid", 2),

    # Concentration difficult
    ("RUB_MIND_10", "Phosphoric Acid", 3),
    ("RUB_MIND_10", "Baryta Carbonica", 2),
    ("RUB_MIND_10", "Lycopodium", 2),
    ("RUB_MIND_10", "Nux Moschata", 2),
    ("RUB_MIND_10", "Calcarea Carbonica", 1),

    # Jealousy
    ("RUB_MIND_11", "Lachesis", 3),
    ("RUB_MIND_11", "Hyoscyamus Niger", 3) if False else ("RUB_MIND_11", "Nux Vomica", 2),  # skip remedy not in list
    ("RUB_MIND_11", "Platina", 1),

    # Suspicious
    ("RUB_MIND_12", "Lachesis", 3),
    ("RUB_MIND_12", "Arsenicum Album", 2),
    ("RUB_MIND_12", "Mercurius Solubilis", 2),

    # Desire for company
    ("RUB_MIND_13", "Phosphorus", 3),
    ("RUB_MIND_13", "Arsenicum Album", 2),
    ("RUB_MIND_13", "Pulsatilla", 2),
    ("RUB_MIND_13", "Argentum Nitricum", 1),
    ("RUB_MIND_13", "Stramonium", 1),

    # Aversion to company
    ("RUB_MIND_14", "Natrum Muriaticum", 3),
    ("RUB_MIND_14", "Sepia", 3),
    ("RUB_MIND_14", "Ignatia Amara", 2),
    ("RUB_MIND_14", "Nux Vomica", 1),

    # Anger with trembling
    ("RUB_MIND_15", "Staphysagria", 3),
    ("RUB_MIND_15", "Nux Vomica", 2),
    ("RUB_MIND_15", "Chamomilla", 2),

    # Fright ailments
    ("RUB_MIND_16", "Aconitum Napellus", 3),
    ("RUB_MIND_16", "Opium", 3),
    ("RUB_MIND_16", "Gelsemium", 2),
    ("RUB_MIND_16", "Ignatia Amara", 2),

    # Fastidious
    ("RUB_MIND_17", "Arsenicum Album", 3),
    ("RUB_MIND_17", "Nux Vomica", 2),
    ("RUB_MIND_17", "Carbo Vegetabilis", 1),

    # Indifference to loved ones
    ("RUB_MIND_18", "Sepia", 3),
    ("RUB_MIND_18", "Phosphoric Acid", 2),
    ("RUB_MIND_18", "Natrum Muriaticum", 2),

    # Hurried
    ("RUB_MIND_19", "Sulphur", 2),
    ("RUB_MIND_19", "Argentum Nitricum", 3),
    ("RUB_MIND_19", "Nux Vomica", 2),
    ("RUB_MIND_19", "Medorrhinum", 2),

    # ── Head rubrics ─────────────────────────────────────
    # Throbbing headache
    ("RUB_HEAD_01", "Belladonna", 3),
    ("RUB_HEAD_01", "Gelsemium", 2),
    ("RUB_HEAD_01", "Natrum Muriaticum", 2),
    ("RUB_HEAD_01", "Lachesis", 1),
    ("RUB_HEAD_01", "China Officinalis", 1),

    # Bursting headache
    ("RUB_HEAD_02", "Bryonia Alba", 3),
    ("RUB_HEAD_02", "Belladonna", 2),
    ("RUB_HEAD_02", "China Officinalis", 2),
    ("RUB_HEAD_02", "Natrum Muriaticum", 2),

    # Pressing forehead
    ("RUB_HEAD_03", "Bryonia Alba", 3),
    ("RUB_HEAD_03", "Nux Vomica", 2),
    ("RUB_HEAD_03", "Pulsatilla", 2),

    # One-sided headache
    ("RUB_HEAD_04", "Silicea", 2),
    ("RUB_HEAD_04", "Spigelia", 3) if False else ("RUB_HEAD_04", "Lachesis", 2),
    ("RUB_HEAD_04", "Natrum Muriaticum", 2),
    ("RUB_HEAD_04", "Nux Vomica", 1),

    # Sun headache
    ("RUB_HEAD_05", "Belladonna", 3),
    ("RUB_HEAD_05", "Natrum Muriaticum", 3),
    ("RUB_HEAD_05", "Gelsemium", 2),
    ("RUB_HEAD_05", "Lachesis", 1),

    # Headache with nausea
    ("RUB_HEAD_06", "Ipecacuanha", 3),
    ("RUB_HEAD_06", "Bryonia Alba", 2),
    ("RUB_HEAD_06", "Nux Vomica", 2),
    ("RUB_HEAD_06", "Pulsatilla", 2),

    # Congestion
    ("RUB_HEAD_07", "Belladonna", 3),
    ("RUB_HEAD_07", "Lachesis", 2),
    ("RUB_HEAD_07", "Sulphur", 2),
    ("RUB_HEAD_07", "Phosphorus", 1),

    # ── Eye rubrics ──────────────────────────────────────
    ("RUB_EYE_01", "Belladonna", 3),
    ("RUB_EYE_01", "Stramonium", 2),
    ("RUB_EYE_01", "Aconitum Napellus", 1),
    ("RUB_EYE_02", "Arsenicum Album", 3),
    ("RUB_EYE_02", "Sulphur", 2),
    ("RUB_EYE_02", "Mercurius Solubilis", 1),
    ("RUB_EYE_03", "Belladonna", 3),
    ("RUB_EYE_03", "Phosphorus", 2),
    ("RUB_EYE_03", "Natrum Muriaticum", 1),

    # ── Face rubrics ─────────────────────────────────────
    ("RUB_FACE_01", "Belladonna", 3),
    ("RUB_FACE_01", "Aconitum Napellus", 2),
    ("RUB_FACE_01", "Lachesis", 1),
    ("RUB_FACE_01", "Sulphur", 1),
    ("RUB_FACE_02", "Arsenicum Album", 2),
    ("RUB_FACE_02", "Veratrum Album", 3),
    ("RUB_FACE_02", "Carbo Vegetabilis", 2),
    ("RUB_FACE_03", "Apis Mellifica", 3),
    ("RUB_FACE_03", "Mercurius Solubilis", 2),

    # ── Throat rubrics ───────────────────────────────────
    ("RUB_THR_01", "Arsenicum Album", 3),
    ("RUB_THR_01", "Cantharis", 2),
    ("RUB_THR_01", "Phosphorus", 2),
    ("RUB_THR_02", "Belladonna", 3),
    ("RUB_THR_02", "Mercurius Solubilis", 2),
    ("RUB_THR_02", "Lachesis", 2),
    ("RUB_THR_02", "Hepar Sulphuris", 2),
    ("RUB_THR_03", "Belladonna", 2),
    ("RUB_THR_03", "Bryonia Alba", 2),
    ("RUB_THR_03", "Phosphorus", 1),
    ("RUB_THR_04", "Ignatia Amara", 3),
    ("RUB_THR_04", "Lachesis", 2),
    ("RUB_THR_04", "Natrum Muriaticum", 1),

    # ── Stomach rubrics ──────────────────────────────────
    ("RUB_STOM_01", "Ipecacuanha", 3),
    ("RUB_STOM_01", "Nux Vomica", 2),
    ("RUB_STOM_01", "Arsenicum Album", 2),
    ("RUB_STOM_01", "Pulsatilla", 2),
    ("RUB_STOM_02", "Ipecacuanha", 3),
    ("RUB_STOM_02", "Arsenicum Album", 3),
    ("RUB_STOM_02", "Veratrum Album", 3),
    ("RUB_STOM_02", "Nux Vomica", 2),
    ("RUB_STOM_02", "Phosphorus", 2),
    ("RUB_STOM_03", "Pulsatilla", 3),
    ("RUB_STOM_03", "Nux Moschata", 2),
    ("RUB_STOM_03", "Apis Mellifica", 2),
    ("RUB_STOM_04", "Bryonia Alba", 3),
    ("RUB_STOM_04", "Phosphorus", 3),
    ("RUB_STOM_04", "Veratrum Album", 2),
    ("RUB_STOM_04", "Natrum Muriaticum", 2),
    ("RUB_STOM_05", "Arsenicum Album", 3),
    ("RUB_STOM_05", "China Officinalis", 1),
    ("RUB_STOM_06", "Veratrum Album", 2),
    ("RUB_STOM_06", "China Officinalis", 2),
    ("RUB_STOM_06", "Sepia", 1),
    ("RUB_STOM_07", "Natrum Muriaticum", 3),
    ("RUB_STOM_07", "Phosphorus", 2),
    ("RUB_STOM_07", "Causticum", 1),
    ("RUB_STOM_08", "Lycopodium", 3),
    ("RUB_STOM_08", "Nux Vomica", 2),
    ("RUB_STOM_08", "Carbo Vegetabilis", 2),
    ("RUB_STOM_08", "China Officinalis", 2),
    ("RUB_STOM_08", "Kali Carbonicum", 1),

    # ── Respiratory rubrics ──────────────────────────────
    ("RUB_RESP_01", "Bryonia Alba", 3),
    ("RUB_RESP_01", "Phosphorus", 3),
    ("RUB_RESP_01", "Aconitum Napellus", 2),
    ("RUB_RESP_01", "Belladonna", 2),
    ("RUB_RESP_01", "Silicea", 1),
    ("RUB_RESP_02", "Arsenicum Album", 2),
    ("RUB_RESP_02", "Phosphorus", 2),
    ("RUB_RESP_02", "Pulsatilla", 2),
    ("RUB_RESP_02", "Chamomilla", 1),
    ("RUB_RESP_03", "Arsenicum Album", 2),
    ("RUB_RESP_03", "Phosphorus", 2),
    ("RUB_RESP_03", "Antimonium Tartaricum", 2),

    # ── Generality rubrics ───────────────────────────────
    # Heat agg
    ("RUB_GEN_01", "Pulsatilla", 3),
    ("RUB_GEN_01", "Sulphur", 3),
    ("RUB_GEN_01", "Apis Mellifica", 3),
    ("RUB_GEN_01", "Lachesis", 2),
    ("RUB_GEN_01", "Belladonna", 2),
    ("RUB_GEN_01", "Medorrhinum", 1),
    # Warmth desire
    ("RUB_GEN_02", "Arsenicum Album", 3),
    ("RUB_GEN_02", "Hepar Sulphuris", 3),
    ("RUB_GEN_02", "Nux Vomica", 3),
    ("RUB_GEN_02", "Silicea", 2),
    ("RUB_GEN_02", "Kali Carbonicum", 2),
    ("RUB_GEN_02", "Calcarea Carbonica", 2),
    # Cold agg
    ("RUB_GEN_03", "Arsenicum Album", 3),
    ("RUB_GEN_03", "Hepar Sulphuris", 3),
    ("RUB_GEN_03", "Nux Vomica", 3),
    ("RUB_GEN_03", "Rhus Toxicodendron", 2),
    ("RUB_GEN_03", "Silicea", 2),
    ("RUB_GEN_03", "Calcarea Carbonica", 2),
    ("RUB_GEN_03", "Dulcamara", 2),
    # Motion agg
    ("RUB_GEN_04", "Bryonia Alba", 3),
    ("RUB_GEN_04", "Belladonna", 2),
    ("RUB_GEN_04", "Nux Vomica", 1),
    ("RUB_GEN_04", "Colocynthis", 1),
    # Motion amel
    ("RUB_GEN_05", "Rhus Toxicodendron", 3),
    ("RUB_GEN_05", "Pulsatilla", 2),
    ("RUB_GEN_05", "Chamomilla", 2),
    ("RUB_GEN_05", "Dulcamara", 1),
    # Night agg
    ("RUB_GEN_06", "Arsenicum Album", 3),
    ("RUB_GEN_06", "Aconitum Napellus", 2),
    ("RUB_GEN_06", "Mercurius Solubilis", 2),
    ("RUB_GEN_06", "Lachesis", 1),
    # Sun agg
    ("RUB_GEN_07", "Natrum Muriaticum", 3),
    ("RUB_GEN_07", "Belladonna", 2),
    ("RUB_GEN_07", "Lachesis", 1),
    ("RUB_GEN_07", "Gelsemium", 1),
    # Sudden onset
    ("RUB_GEN_08", "Aconitum Napellus", 3),
    ("RUB_GEN_08", "Belladonna", 3),
    ("RUB_GEN_08", "Stramonium", 1),
    # Pressure amel
    ("RUB_GEN_09", "Bryonia Alba", 3),
    ("RUB_GEN_09", "China Officinalis", 2),
    ("RUB_GEN_09", "Colocynthis", 2),
    # Touch agg
    ("RUB_GEN_10", "Lachesis", 3),
    ("RUB_GEN_10", "Hepar Sulphuris", 3),
    ("RUB_GEN_10", "Belladonna", 2),
    ("RUB_GEN_10", "China Officinalis", 2),
    # Damp weather agg
    ("RUB_GEN_11", "Dulcamara", 3),
    ("RUB_GEN_11", "Rhus Toxicodendron", 3),
    ("RUB_GEN_11", "Natrum Carbonicum", 2),
    ("RUB_GEN_11", "Calcarea Carbonica", 1),
    # Periodicity
    ("RUB_GEN_12", "China Officinalis", 3),
    ("RUB_GEN_12", "Arsenicum Album", 2),
    ("RUB_GEN_12", "Natrum Muriaticum", 1),
    # Burning pains
    ("RUB_GEN_13", "Arsenicum Album", 3),
    ("RUB_GEN_13", "Sulphur", 3),
    ("RUB_GEN_13", "Phosphorus", 2),
    ("RUB_GEN_13", "Cantharis", 2),
    ("RUB_GEN_13", "Apis Mellifica", 2),

    # ── Skin rubrics ─────────────────────────────────────
    ("RUB_SKIN_01", "Sulphur", 3),
    ("RUB_SKIN_01", "Pulsatilla", 2),
    ("RUB_SKIN_01", "Mercurius Solubilis", 1),
    ("RUB_SKIN_02", "Arsenicum Album", 3),
    ("RUB_SKIN_02", "Sulphur", 2),
    ("RUB_SKIN_02", "Cantharis", 2),
    ("RUB_SKIN_03", "Sulphur", 3),
    ("RUB_SKIN_03", "Arsenicum Album", 2),
    ("RUB_SKIN_03", "Graphites", 2),
    ("RUB_SKIN_03", "Silicea", 1),
    ("RUB_SKIN_04", "Apis Mellifica", 3),
    ("RUB_SKIN_04", "Pulsatilla", 2),
    ("RUB_SKIN_04", "Natrum Muriaticum", 1),

    # ── Sleep rubrics ────────────────────────────────────
    ("RUB_SLEEP_01", "Arsenicum Album", 3),
    ("RUB_SLEEP_01", "Aconitum Napellus", 2),
    ("RUB_SLEEP_01", "Kali Carbonicum", 2),
    ("RUB_SLEEP_02", "Nux Vomica", 3),
    ("RUB_SLEEP_02", "Sulphur", 2),
    ("RUB_SLEEP_02", "Lycopodium", 1),
    ("RUB_SLEEP_03", "Kali Carbonicum", 3),
    ("RUB_SLEEP_03", "Arsenicum Album", 2),
    ("RUB_SLEEP_03", "Nux Vomica", 1),

    # ── Female rubrics ───────────────────────────────────
    ("RUB_FEM_01", "Pulsatilla", 3),
    ("RUB_FEM_01", "Sepia", 2),
    ("RUB_FEM_01", "Graphites", 2),
    ("RUB_FEM_01", "Conium Maculatum", 1),
    ("RUB_FEM_02", "China Officinalis", 3),
    ("RUB_FEM_02", "Phosphorus", 2),
    ("RUB_FEM_02", "Calcarea Carbonica", 2),
    ("RUB_FEM_02", "Sepia", 1),
]


# ══════════════════════════════════════════════════════════
#  CONTRADICTION PAIRS
#  Items that are clinically/logically mutually exclusive
# ══════════════════════════════════════════════════════════

CONTRADICTION_PAIRS = [
    # Thermal contradictions
    {"a": "SYM_MOD_001", "b": "SYM_MOD_002", "strength": 0.9, "source": "clinical"},   # heat agg vs desire warmth
    {"a": "SYM_THER_001", "b": "SYM_THER_002", "strength": 1.0, "source": "clinical"},  # chilly vs hot
    {"a": "SYM_MOD_001", "b": "SYM_MOD_007", "strength": 0.85, "source": "literature"}, # heat agg vs cold agg
    {"a": "SYM_MOD_008", "b": "SYM_MOD_007", "strength": 0.8, "source": "clinical"},    # better cold vs worse cold
    {"a": "SYM_THER_003", "b": "SYM_THER_004", "strength": 0.9, "source": "clinical"},  # desire open air vs aversion
    # Motion contradictions
    {"a": "SYM_MOD_005", "b": "SYM_MOD_006", "strength": 1.0, "source": "clinical"},    # worse motion vs better motion
    # Thirst contradictions
    {"a": "SYM_STOM_003", "b": "SYM_STOM_004", "strength": 1.0, "source": "clinical"},  # thirstless vs extreme thirst
    {"a": "SYM_STOM_003", "b": "SYM_STOM_005", "strength": 0.8, "source": "clinical"},  # thirstless vs sips
    # Company contradictions
    {"a": "SYM_MIND_014", "b": "SYM_MIND_015", "strength": 0.95, "source": "clinical"}, # desire company vs aversion
    # Throat contradictions
    {"a": "SYM_THROAT_005", "b": "SYM_THROAT_006", "strength": 0.9, "source": "clinical"}, # better vs worse warm drinks
    # Appetite contradictions
    {"a": "SYM_STOM_012", "b": "SYM_STOM_013", "strength": 0.9, "source": "clinical"},  # increased vs lost
    # Onset contradictions
    {"a": "SYM_ONSET_001", "b": "SYM_ONSET_002", "strength": 1.0, "source": "clinical"}, # sudden vs gradual
    # Face contradictions
    {"a": "SYM_FACE_001", "b": "SYM_FACE_002", "strength": 0.95, "source": "clinical"},  # red vs pale
    # Menses contradictions
    {"a": "SYM_SEX_001", "b": "SYM_SEX_002", "strength": 1.0, "source": "clinical"},    # scanty vs profuse
    # Rest/motion time contradictions
    {"a": "SYM_MOD_015", "b": "SYM_MOD_006", "strength": 0.85, "source": "clinical"},   # worse exertion vs better motion
    {"a": "SYM_MOD_010", "b": "SYM_MOD_003", "strength": 0.7, "source": "literature"},  # worse morning vs worse night (partial)
]


# ══════════════════════════════════════════════════════════
#  CORRELATION PAIRS
#  Symptoms that commonly co-occur
# ══════════════════════════════════════════════════════════

CORRELATION_PAIRS = [
    # Classic Belladonna picture
    {"a": "SYM_HEAD_001", "b": "SYM_FACE_001", "strength": 0.75, "source": "clinical"},
    {"a": "SYM_HEAD_001", "b": "SYM_EYE_001", "strength": 0.65, "source": "clinical"},
    {"a": "SYM_FACE_001", "b": "SYM_EYE_001", "strength": 0.60, "source": "clinical"},
    {"a": "SYM_HEAD_001", "b": "SYM_ONSET_001", "strength": 0.55, "source": "clinical"},
    # Arsenicum picture
    {"a": "SYM_MIND_002", "b": "SYM_MIND_001", "strength": 0.80, "source": "clinical"},
    {"a": "SYM_MIND_001", "b": "SYM_MIND_003", "strength": 0.70, "source": "clinical"},
    {"a": "SYM_MIND_002", "b": "SYM_SLEEP_001", "strength": 0.65, "source": "literature"},
    {"a": "SYM_MIND_001", "b": "SYM_MIND_018", "strength": 0.60, "source": "clinical"},
    {"a": "SYM_THER_001", "b": "SYM_SENS_001", "strength": 0.55, "source": "clinical"},
    {"a": "SYM_SLEEP_005", "b": "SYM_MIND_001", "strength": 0.65, "source": "clinical"},
    # Natrum Mur picture
    {"a": "SYM_MIND_006", "b": "SYM_MIND_007", "strength": 0.80, "source": "clinical"},
    {"a": "SYM_MOD_017", "b": "SYM_MIND_006", "strength": 0.60, "source": "literature"},
    {"a": "SYM_STOM_009", "b": "SYM_MOD_017", "strength": 0.50, "source": "literature"},
    {"a": "SYM_MIND_015", "b": "SYM_MIND_006", "strength": 0.55, "source": "clinical"},
    {"a": "SYM_HEAD_005", "b": "SYM_MOD_017", "strength": 0.70, "source": "clinical"},
    # Nux Vomica picture
    {"a": "SYM_MIND_004", "b": "SYM_MIND_025", "strength": 0.70, "source": "clinical"},
    {"a": "SYM_MIND_004", "b": "SYM_STOM_010", "strength": 0.55, "source": "clinical"},
    {"a": "SYM_SLEEP_003", "b": "SYM_MIND_004", "strength": 0.50, "source": "literature"},
    # Pulsatilla picture
    {"a": "SYM_MIND_005", "b": "SYM_STOM_003", "strength": 0.65, "source": "clinical"},
    {"a": "SYM_MOD_006", "b": "SYM_THER_003", "strength": 0.60, "source": "clinical"},
    {"a": "SYM_STOM_008", "b": "SYM_MIND_005", "strength": 0.55, "source": "clinical"},
    # Bryonia picture
    {"a": "SYM_MOD_005", "b": "SYM_MOD_004", "strength": 0.75, "source": "clinical"},
    {"a": "SYM_STOM_004", "b": "SYM_MOD_005", "strength": 0.55, "source": "literature"},
    # Ignatia picture
    {"a": "SYM_MIND_024", "b": "SYM_THROAT_004", "strength": 0.65, "source": "clinical"},
    # Sepia picture
    {"a": "SYM_MIND_023", "b": "SYM_MIND_004", "strength": 0.55, "source": "clinical"},
    {"a": "SYM_MIND_023", "b": "SYM_SEX_001", "strength": 0.60, "source": "clinical"},
    # Rhus Tox picture
    {"a": "SYM_MOD_006", "b": "SYM_EXT_001", "strength": 0.70, "source": "clinical"},
    {"a": "SYM_MOD_013", "b": "SYM_EXT_001", "strength": 0.55, "source": "literature"},
    # General mind-body correlations
    {"a": "SYM_MIND_002", "b": "SYM_MIND_003", "strength": 0.60, "source": "clinical"},
    {"a": "SYM_EXT_005", "b": "SYM_THER_001", "strength": 0.65, "source": "clinical"},
    {"a": "SYM_SKIN_001", "b": "SYM_THER_002", "strength": 0.55, "source": "clinical"},
    {"a": "SYM_STOM_010", "b": "SYM_ABD_001", "strength": 0.60, "source": "clinical"},
]


# ══════════════════════════════════════════════════════════
#  HISTORICAL CASES — for temporal + pattern mining
# ══════════════════════════════════════════════════════════

SAMPLE_CASES = [
    # ── Case 1: Classic Belladonna acute ─────────────────
    {
        "case_id": "CASE001", "patient_id": "PAT001",
        "snapshots": [
            {
                "snapshot_id": "SNAP001A", "day": 0,
                "symptoms": [
                    ("SYM_HEAD_001", 0.9), ("SYM_FACE_001", 0.8),
                    ("SYM_EYE_001", 0.7), ("SYM_ONSET_001", 0.9),
                    ("SYM_THER_002", 0.6),
                ],
                "prescribed": ("Belladonna", "200C"),
            },
            {
                "snapshot_id": "SNAP001B", "day": 3,
                "symptoms": [
                    ("SYM_HEAD_001", 0.2), ("SYM_FACE_001", 0.1),
                ],
                "prescribed": None,
            },
        ],
        "outcome": "Improved",
    },
    # ── Case 2: Arsenicum chronic anxiety ────────────────
    {
        "case_id": "CASE002", "patient_id": "PAT002",
        "snapshots": [
            {
                "snapshot_id": "SNAP002A", "day": 0,
                "symptoms": [
                    ("SYM_MIND_001", 0.9), ("SYM_MIND_002", 0.8),
                    ("SYM_MIND_003", 0.7), ("SYM_THER_001", 0.8),
                    ("SYM_MOD_003", 0.6), ("SYM_SLEEP_001", 0.7),
                    ("SYM_MIND_018", 0.5),
                ],
                "prescribed": ("Arsenicum Album", "30C"),
            },
            {
                "snapshot_id": "SNAP002B", "day": 14,
                "symptoms": [
                    ("SYM_MIND_001", 0.4), ("SYM_MIND_002", 0.3),
                    ("SYM_THER_001", 0.6), ("SYM_SLEEP_001", 0.3),
                ],
                "prescribed": None,
            },
            {
                "snapshot_id": "SNAP002C", "day": 30,
                "symptoms": [
                    ("SYM_MIND_001", 0.2), ("SYM_THER_001", 0.5),
                ],
                "prescribed": ("Arsenicum Album", "200C"),
            },
        ],
        "outcome": "Improved",
    },
    # ── Case 3: Natrum Mur grief ─────────────────────────
    {
        "case_id": "CASE003", "patient_id": "PAT003",
        "snapshots": [
            {
                "snapshot_id": "SNAP003A", "day": 0,
                "symptoms": [
                    ("SYM_MIND_006", 0.9), ("SYM_MIND_007", 0.8),
                    ("SYM_MOD_017", 0.7), ("SYM_MIND_015", 0.6),
                    ("SYM_HEAD_005", 0.7), ("SYM_STOM_009", 0.5),
                ],
                "prescribed": ("Natrum Muriaticum", "1M"),
            },
        ],
        "outcome": "Improved",
    },
    # ── Case 4: Natrum Mur similar pattern ───────────────
    {
        "case_id": "CASE004", "patient_id": "PAT004",
        "snapshots": [
            {
                "snapshot_id": "SNAP004A", "day": 0,
                "symptoms": [
                    ("SYM_MIND_006", 0.8), ("SYM_MOD_017", 0.7),
                    ("SYM_MIND_015", 0.5), ("SYM_STOM_009", 0.6),
                ],
                "prescribed": ("Natrum Muriaticum", "200C"),
            },
        ],
        "outcome": "Improved",
    },
    # ── Case 5: Belladonna acute #2 ──────────────────────
    {
        "case_id": "CASE005", "patient_id": "PAT005",
        "snapshots": [
            {
                "snapshot_id": "SNAP005A", "day": 0,
                "symptoms": [
                    ("SYM_HEAD_001", 0.9), ("SYM_FACE_001", 0.9),
                    ("SYM_EYE_001", 0.8), ("SYM_HEAD_008", 0.7),
                    ("SYM_MOD_001", 0.6),
                ],
                "prescribed": ("Belladonna", "30C"),
            },
            {
                "snapshot_id": "SNAP005B", "day": 2,
                "symptoms": [
                    ("SYM_HEAD_001", 0.2), ("SYM_FACE_001", 0.1),
                ],
                "prescribed": None,
            },
        ],
        "outcome": "Improved",
    },
    # ── Case 6: Nux Vomica digestive ─────────────────────
    {
        "case_id": "CASE006", "patient_id": "PAT006",
        "snapshots": [
            {
                "snapshot_id": "SNAP006A", "day": 0,
                "symptoms": [
                    ("SYM_MIND_004", 0.8), ("SYM_MIND_025", 0.7),
                    ("SYM_STOM_010", 0.8), ("SYM_SLEEP_003", 0.6),
                    ("SYM_MOD_010", 0.5), ("SYM_THER_001", 0.7),
                ],
                "prescribed": ("Nux Vomica", "30C"),
            },
            {
                "snapshot_id": "SNAP006B", "day": 14,
                "symptoms": [
                    ("SYM_MIND_004", 0.4), ("SYM_STOM_010", 0.3),
                    ("SYM_SLEEP_003", 0.2),
                ],
                "prescribed": None,
            },
        ],
        "outcome": "Improved",
    },
    # ── Case 7: Pulsatilla menstrual + emotional ────────
    {
        "case_id": "CASE007", "patient_id": "PAT007",
        "snapshots": [
            {
                "snapshot_id": "SNAP007A", "day": 0,
                "symptoms": [
                    ("SYM_MIND_005", 0.9), ("SYM_STOM_003", 0.7),
                    ("SYM_MOD_006", 0.6), ("SYM_THER_003", 0.7),
                    ("SYM_SEX_001", 0.8), ("SYM_STOM_008", 0.5),
                ],
                "prescribed": ("Pulsatilla", "200C"),
            },
        ],
        "outcome": "Improved",
    },
    # ── Case 8: Bryonia musculoskeletal ──────────────────
    {
        "case_id": "CASE008", "patient_id": "PAT008",
        "snapshots": [
            {
                "snapshot_id": "SNAP008A", "day": 0,
                "symptoms": [
                    ("SYM_MOD_005", 0.9), ("SYM_MOD_004", 0.7),
                    ("SYM_HEAD_002", 0.7), ("SYM_STOM_004", 0.8),
                    ("SYM_MIND_004", 0.5),
                ],
                "prescribed": ("Bryonia Alba", "30C"),
            },
            {
                "snapshot_id": "SNAP008B", "day": 7,
                "symptoms": [
                    ("SYM_MOD_005", 0.3), ("SYM_HEAD_002", 0.2),
                ],
                "prescribed": None,
            },
        ],
        "outcome": "Improved",
    },
    # ── Case 9: Suppression case (Belladona → mental) ───
    {
        "case_id": "CASE009", "patient_id": "PAT009",
        "snapshots": [
            {
                "snapshot_id": "SNAP009A", "day": 0,
                "symptoms": [
                    ("SYM_HEAD_001", 0.9), ("SYM_FACE_001", 0.8),
                    ("SYM_SKIN_003", 0.7),
                ],
                "prescribed": ("Belladonna", "30C"),
            },
            {
                "snapshot_id": "SNAP009B", "day": 7,
                "symptoms": [
                    ("SYM_HEAD_001", 0.2), ("SYM_SKIN_003", 0.1),
                    ("SYM_MIND_002", 0.8), ("SYM_MIND_001", 0.7),
                    ("SYM_SLEEP_001", 0.6),
                ],
                "prescribed": None,
            },
        ],
        "outcome": "NoChange",
    },
    # ── Case 10: Rhus Tox joint case ─────────────────────
    {
        "case_id": "CASE010", "patient_id": "PAT010",
        "snapshots": [
            {
                "snapshot_id": "SNAP010A", "day": 0,
                "symptoms": [
                    ("SYM_EXT_001", 0.9), ("SYM_MOD_006", 0.8),
                    ("SYM_MOD_013", 0.7), ("SYM_MIND_002", 0.5),
                ],
                "prescribed": ("Rhus Toxicodendron", "200C"),
            },
            {
                "snapshot_id": "SNAP010B", "day": 10,
                "symptoms": [
                    ("SYM_EXT_001", 0.3), ("SYM_MOD_006", 0.4),
                ],
                "prescribed": None,
            },
        ],
        "outcome": "Improved",
    },
    # ── Case 11: Ignatia grief acute ─────────────────────
    {
        "case_id": "CASE011", "patient_id": "PAT011",
        "snapshots": [
            {
                "snapshot_id": "SNAP011A", "day": 0,
                "symptoms": [
                    ("SYM_MIND_024", 0.9), ("SYM_THROAT_004", 0.7),
                    ("SYM_MIND_005", 0.8), ("SYM_MIND_009", 0.6),
                ],
                "prescribed": ("Ignatia Amara", "200C"),
            },
        ],
        "outcome": "Improved",
    },
    # ── Case 12: Lycopodium digestive ────────────────────
    {
        "case_id": "CASE012", "patient_id": "PAT012",
        "snapshots": [
            {
                "snapshot_id": "SNAP012A", "day": 0,
                "symptoms": [
                    ("SYM_STOM_010", 0.9), ("SYM_ABD_001", 0.8),
                    ("SYM_MIND_008", 0.6), ("SYM_MIND_004", 0.5),
                    ("SYM_MOD_012", 0.7),
                ],
                "prescribed": ("Lycopodium", "200C"),
            },
        ],
        "outcome": "Improved",
    },
    # ── Case 13: Sepia hormonal ──────────────────────────
    {
        "case_id": "CASE013", "patient_id": "PAT013",
        "snapshots": [
            {
                "snapshot_id": "SNAP013A", "day": 0,
                "symptoms": [
                    ("SYM_MIND_023", 0.9), ("SYM_MIND_004", 0.7),
                    ("SYM_SEX_001", 0.8), ("SYM_MIND_015", 0.6),
                    ("SYM_MOD_015", 0.5),
                ],
                "prescribed": ("Sepia", "1M"),
            },
        ],
        "outcome": "Improved",
    },
    # ── Case 14: Lachesis ────────────────────────────────
    {
        "case_id": "CASE014", "patient_id": "PAT014",
        "snapshots": [
            {
                "snapshot_id": "SNAP014A", "day": 0,
                "symptoms": [
                    ("SYM_MIND_011", 0.8), ("SYM_MIND_012", 0.7),
                    ("SYM_THER_002", 0.7), ("SYM_MOD_009", 0.6),
                    ("SYM_MOD_010", 0.5), ("SYM_THROAT_002", 0.6),
                ],
                "prescribed": ("Lachesis", "200C"),
            },
        ],
        "outcome": "Improved",
    },
    # ── Case 15: Worsened case for contrast ──────────────
    {
        "case_id": "CASE015", "patient_id": "PAT015",
        "snapshots": [
            {
                "snapshot_id": "SNAP015A", "day": 0,
                "symptoms": [
                    ("SYM_MIND_002", 0.6), ("SYM_THER_002", 0.5),
                    ("SYM_SKIN_001", 0.7),
                ],
                "prescribed": ("Sulphur", "30C"),
            },
            {
                "snapshot_id": "SNAP015B", "day": 7,
                "symptoms": [
                    ("SYM_SKIN_001", 0.9), ("SYM_SKIN_003", 0.8),
                    ("SYM_MIND_002", 0.8), ("SYM_SLEEP_001", 0.7),
                ],
                "prescribed": None,
            },
        ],
        "outcome": "Worsened",
    },
    # ── Case 16: Natrum Mur — another pattern occurrence ─
    {
        "case_id": "CASE016", "patient_id": "PAT016",
        "snapshots": [
            {
                "snapshot_id": "SNAP016A", "day": 0,
                "symptoms": [
                    ("SYM_MIND_006", 0.7), ("SYM_MOD_017", 0.8),
                    ("SYM_MIND_007", 0.6), ("SYM_HEAD_005", 0.7),
                ],
                "prescribed": ("Natrum Muriaticum", "200C"),
            },
        ],
        "outcome": "Improved",
    },
    # ── Case 17: Unchanged case ──────────────────────────
    {
        "case_id": "CASE017", "patient_id": "PAT017",
        "snapshots": [
            {
                "snapshot_id": "SNAP017A", "day": 0,
                "symptoms": [
                    ("SYM_EXT_001", 0.7), ("SYM_MOD_005", 0.6),
                    ("SYM_HEAD_003", 0.5),
                ],
                "prescribed": ("Bryonia Alba", "200C"),
            },
            {
                "snapshot_id": "SNAP017B", "day": 14,
                "symptoms": [
                    ("SYM_EXT_001", 0.7), ("SYM_MOD_005", 0.6),
                    ("SYM_HEAD_003", 0.5),
                ],
                "prescribed": None,
            },
        ],
        "outcome": "NoChange",
    },
    # ── Case 18: Arsenicum sleep + anxiety pattern ───────
    {
        "case_id": "CASE018", "patient_id": "PAT018",
        "snapshots": [
            {
                "snapshot_id": "SNAP018A", "day": 0,
                "symptoms": [
                    ("SYM_MIND_001", 0.8), ("SYM_MIND_002", 0.7),
                    ("SYM_SLEEP_005", 0.9), ("SYM_THER_001", 0.7),
                    ("SYM_SENS_001", 0.5),
                ],
                "prescribed": ("Arsenicum Album", "200C"),
            },
        ],
        "outcome": "Improved",
    },
    # ── Case 19: Kali Carb ───────────────────────────────
    {
        "case_id": "CASE019", "patient_id": "PAT019",
        "snapshots": [
            {
                "snapshot_id": "SNAP019A", "day": 0,
                "symptoms": [
                    ("SYM_SLEEP_005", 0.9), ("SYM_MIND_001", 0.6),
                    ("SYM_MOD_007", 0.7), ("SYM_RESP_002", 0.5),
                ],
                "prescribed": ("Kali Carbonicum", "200C"),
            },
        ],
        "outcome": "Improved",
    },
    # ── Case 20: Sulphur skin ────────────────────────────
    {
        "case_id": "CASE020", "patient_id": "PAT020",
        "snapshots": [
            {
                "snapshot_id": "SNAP020A", "day": 0,
                "symptoms": [
                    ("SYM_SKIN_001", 0.9), ("SYM_SKIN_002", 0.7),
                    ("SYM_THER_002", 0.7), ("SYM_EXT_006", 0.6),
                    ("SYM_SENS_001", 0.5),
                ],
                "prescribed": ("Sulphur", "200C"),
            },
            {
                "snapshot_id": "SNAP020B", "day": 21,
                "symptoms": [
                    ("SYM_SKIN_001", 0.3), ("SYM_SKIN_002", 0.2),
                    ("SYM_THER_002", 0.5),
                ],
                "prescribed": None,
            },
        ],
        "outcome": "Improved",
    },
]


# ══════════════════════════════════════════════════════════
#  SEEDER FUNCTION
# ══════════════════════════════════════════════════════════

def seed_expanded_graph(session):
    """Populate Neo4j with the expanded dataset (idempotent MERGE)."""

    # ── Symptoms ─────────────────────────────────────────
    session.run(
        "UNWIND $items AS s MERGE (n:Symptom {id: s.id}) SET n.name = s.name, n.category = s.category",
        items=SYMPTOMS,
    )
    # ── Rubrics ──────────────────────────────────────────
    session.run(
        "UNWIND $items AS r MERGE (n:Rubric {id: r.id}) SET n.chapter = r.chapter, n.text = r.text",
        items=RUBRICS,
    )
    # ── Remedies ─────────────────────────────────────────
    session.run(
        "UNWIND $items AS r MERGE (n:Remedy {name: r.name}) SET n.abbrev = r.abbrev, n.miasm = r.miasm",
        items=REMEDIES,
    )

    # ── Symptom → Rubric ─────────────────────────────────
    session.run(
        """UNWIND $links AS l
           MATCH (s:Symptom {id: l[0]}), (r:Rubric {id: l[1]})
           MERGE (s)-[:BELONGS_TO]->(r)""",
        links=SYMPTOM_RUBRIC_LINKS,
    )

    # ── Rubric → Remedy ──────────────────────────────────
    session.run(
        """UNWIND $indications AS i
           MATCH (r:Rubric {id: i[0]}), (rem:Remedy {name: i[1]})
           MERGE (r)-[rel:INDICATES]->(rem)
           SET rel.grade = i[2]""",
        indications=RUBRIC_REMEDY_INDICATIONS,
    )

    # ── Contradictions ───────────────────────────────────
    session.run(
        """UNWIND $pairs AS pair
           MATCH (a:Symptom {id: pair.a}), (b:Symptom {id: pair.b})
           MERGE (a)-[r:CONTRADICTS]->(b)
           SET r.strength = pair.strength, r.source = pair.source""",
        pairs=CONTRADICTION_PAIRS,
    )

    # ── Correlations ─────────────────────────────────────
    session.run(
        """UNWIND $pairs AS pair
           MATCH (a:Symptom {id: pair.a}), (b:Symptom {id: pair.b})
           MERGE (a)-[r:CORRELATED_WITH]->(b)
           SET r.strength = pair.strength, r.source = pair.source""",
        pairs=CORRELATION_PAIRS,
    )

    # ── Outcomes ─────────────────────────────────────────
    session.run(
        "UNWIND $types AS t MERGE (o:Outcome {type: t})",
        types=["Improved", "NoChange", "Worsened"],
    )

    # ── Cases + Snapshots ────────────────────────────────
    for case in SAMPLE_CASES:
        session.run(
            "MERGE (c:Case {id: $cid}) SET c.patient_id = $pid",
            cid=case["case_id"],
            pid=case["patient_id"],
        )
        session.run(
            """MATCH (c:Case {id: $cid}), (o:Outcome {type: $outcome})
               MERGE (c)-[:OUTCOME]->(o)""",
            cid=case["case_id"],
            outcome=case["outcome"],
        )
        for snap in case["snapshots"]:
            session.run(
                """MATCH (c:Case {id: $cid})
                   MERGE (cs:CaseSnapshot {id: $sid})
                   MERGE (c)-[:HAS_SNAPSHOT {day: $day}]->(cs)""",
                cid=case["case_id"],
                sid=snap["snapshot_id"],
                day=snap["day"],
            )
            for sym_id, intensity in snap["symptoms"]:
                session.run(
                    """MATCH (cs:CaseSnapshot {id: $sid}), (s:Symptom {id: $sym_id})
                       MERGE (cs)-[:OBSERVED_SYMPTOM {intensity: $intensity}]->(s)""",
                    sid=snap["snapshot_id"],
                    sym_id=sym_id,
                    intensity=intensity,
                )
            if snap["prescribed"]:
                remedy_name, potency = snap["prescribed"]
                session.run(
                    """MATCH (cs:CaseSnapshot {id: $sid}), (rem:Remedy {name: $remedy})
                       MERGE (cs)-[:PRESCRIBED {potency: $potency}]->(rem)""",
                    sid=snap["snapshot_id"],
                    remedy=remedy_name,
                    potency=potency,
                )

    return {
        "symptoms": len(SYMPTOMS),
        "rubrics": len(RUBRICS),
        "remedies": len(REMEDIES),
        "indications": len(RUBRIC_REMEDY_INDICATIONS),
        "contradictions": len(CONTRADICTION_PAIRS),
        "correlations": len(CORRELATION_PAIRS),
        "cases": len(SAMPLE_CASES),
    }
