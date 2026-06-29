from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

try:
    from .analytics import ReviewLogEntry
except ImportError:
    from analytics import ReviewLogEntry


DEMO_DECK_NAME = "Insights Demo::Cardiology"
CONTROL_DECK_NAME = "Insights Demo::Mostly Stable"


@dataclass(frozen=True)
class DemoExpectedImprovement:
    insight: str
    action: str


@dataclass(frozen=True)
class DemoExpectedInsight:
    key: str
    positives: tuple[str, ...]
    improvements: tuple[DemoExpectedImprovement, ...]


@dataclass(frozen=True)
class DemoCard:
    label: str
    tag: str
    text: str
    pattern: str


DEMO_EXPECTED_INSIGHTS = (
    DemoExpectedInsight(
        key="cardio_hemodynamics",
        positives=(
            "Most reviewed cardiology cards stayed outside the missed-card set in this window.",
        ),
        improvements=(
            DemoExpectedImprovement(
                "Pressure-volume loops, preload/afterload changes, and murmur maneuvers form the main physiology cluster.",
                "Search for murmur and pressure-volume cards, then review those before drug cards.",
            ),
            DemoExpectedImprovement(
                "Left-sided heart finding cards are close enough to blur when mixed together.",
                "Put handgrip maneuvers first, then loading-condition cards.",
            ),
        ),
    ),
    DemoExpectedInsight(
        key="cardio_drugs",
        positives=(
            "Medication misses form a narrower cluster than the full cardiology deck.",
        ),
        improvements=(
            DemoExpectedImprovement(
                "Medication safety misses center on contraindications and adverse effects.",
                "Search for drug safety cards and sort them into contraindication versus toxicity piles.",
            ),
            DemoExpectedImprovement(
                "Repeated drug misses may be coming from cards with several facts at once.",
                "Open the repeated drug card and split it if it asks for multiple toxicities.",
            ),
        ),
    ),
    DemoExpectedInsight(
        key="cardio_arrhythmias",
        positives=(
            "Rhythm misses appear mainly in the longer window, not only the newest reviews.",
        ),
        improvements=(
            DemoExpectedImprovement(
                "Rhythm strip and first-line management cards appear mainly in the longer window.",
                "Search rhythm cards separately after finishing the newer physiology cluster.",
            ),
            DemoExpectedImprovement(
                "Arrhythmia cards mix recognition and management details.",
                "Review rhythm identification cards first, then treatment-choice cards.",
            ),
        ),
    ),
)


_HEMODYNAMIC_CARDS = (
    (
        "Aortic stenosis murmur with handgrip",
        "In aortic stenosis, handgrip increases afterload and usually makes the systolic crescendo-decrescendo murmur softer.",
    ),
    (
        "Mitral regurgitation murmur with handgrip",
        "In mitral regurgitation, handgrip increases afterload and makes the holosystolic murmur louder.",
    ),
    (
        "Hypertrophic cardiomyopathy with Valsalva",
        "Valsalva decreases preload and makes hypertrophic cardiomyopathy louder because the outflow tract narrows.",
    ),
    (
        "Aortic stenosis with Valsalva",
        "Valsalva decreases preload and usually makes the aortic stenosis murmur softer.",
    ),
    (
        "Mitral valve prolapse with standing",
        "Standing decreases preload, so mitral valve prolapse clicks earlier in systole.",
    ),
    (
        "Mitral valve prolapse with squatting",
        "Squatting increases preload, so the mitral valve prolapse click moves later in systole.",
    ),
    (
        "S3 in systolic heart failure",
        "An S3 after S2 suggests volume overload and is classically heard in systolic heart failure.",
    ),
    (
        "S4 in stiff ventricle",
        "An S4 before S1 suggests atrial contraction into a stiff ventricle, such as long-standing hypertension.",
    ),
    (
        "Pressure-volume loop in systolic failure",
        "Systolic heart failure lowers contractility, increasing end-systolic volume and reducing ejection fraction.",
    ),
    (
        "Pressure-volume loop with increased afterload",
        "Increased afterload raises end-systolic volume and reduces stroke volume on the pressure-volume loop.",
    ),
    (
        "Pressure-volume loop with increased preload",
        "Increased preload raises end-diastolic volume and increases stroke volume if contractility is unchanged.",
    ),
    (
        "Aortic regurgitation pulse pressure",
        "Aortic regurgitation causes wide pulse pressure because diastolic pressure falls while stroke volume rises.",
    ),
    (
        "Pulsus paradoxus in tamponade",
        "Cardiac tamponade can cause pulsus paradoxus from exaggerated inspiratory drop in systolic pressure.",
    ),
    (
        "JVP in right heart failure",
        "Right-sided heart failure often raises jugular venous pressure because systemic venous pressure backs up.",
    ),
    (
        "Pulmonary edema in left heart failure",
        "Left-sided heart failure raises pulmonary venous pressure and can cause pulmonary edema.",
    ),
    (
        "ACE inhibitors and afterload",
        "ACE inhibitors reduce afterload, which can improve forward flow in systolic heart failure.",
    ),
)

_DRUG_CARDS = (
    (
        "Nitroglycerin with sildenafil",
        "Nitroglycerin is contraindicated with sildenafil because both increase cGMP and can cause severe hypotension.",
    ),
    (
        "Beta blocker in acute decompensated heart failure",
        "Beta blockers are avoided during acute decompensated heart failure because negative inotropy can worsen symptoms.",
    ),
    (
        "Verapamil adverse effect",
        "Verapamil can cause constipation and AV nodal blockade.",
    ),
    (
        "Dihydropyridine calcium channel blocker edema",
        "Amlodipine can cause peripheral edema from preferential arteriolar dilation.",
    ),
    (
        "Digoxin toxicity rhythm",
        "Digoxin toxicity can cause nausea, visual changes, and arrhythmias including AV block.",
    ),
    (
        "Amiodarone toxicities",
        "Amiodarone can cause pulmonary fibrosis, thyroid dysfunction, liver injury, and corneal deposits.",
    ),
    (
        "Hydralazine lupus-like syndrome",
        "Hydralazine can cause drug-induced lupus with antihistone antibodies.",
    ),
    (
        "ACE inhibitor cough",
        "ACE inhibitors can cause cough and angioedema from increased bradykinin.",
    ),
    (
        "Loop diuretic toxicity",
        "Loop diuretics can cause hypokalemia, ototoxicity, and sulfa allergy reactions.",
    ),
    (
        "Spironolactone endocrine effects",
        "Spironolactone can cause hyperkalemia and gynecomastia from antiandrogen effects.",
    ),
)

_ARRHYTHMIA_CARDS = (
    (
        "WPW with atrial fibrillation",
        "Avoid AV nodal blockers in atrial fibrillation with WPW because conduction may favor the accessory pathway.",
    ),
    (
        "Adenosine for AVNRT",
        "Adenosine transiently blocks the AV node and can terminate AV nodal reentrant tachycardia.",
    ),
    (
        "Torsades treatment",
        "Torsades de pointes is treated with IV magnesium and correction of prolonged QT contributors.",
    ),
    (
        "Atrial fibrillation irregularly irregular",
        "Atrial fibrillation has an irregularly irregular rhythm without consistent P waves.",
    ),
    (
        "Mobitz I Wenckebach",
        "Mobitz I has progressive PR prolongation followed by a dropped beat.",
    ),
    (
        "Mobitz II heart block",
        "Mobitz II has dropped beats without progressive PR prolongation and often needs pacing.",
    ),
    (
        "Ventricular tachycardia wide complex",
        "Stable monomorphic ventricular tachycardia is a wide-complex tachycardia that may require antiarrhythmic therapy.",
    ),
    (
        "Long QT medication risk",
        "Macrolides, fluoroquinolones, antipsychotics, and antiarrhythmics can prolong QT and increase torsades risk.",
    ),
)

_STABLE_CARDS = (
    (
        "Aspirin mechanism",
        "Aspirin irreversibly inhibits cyclooxygenase and reduces thromboxane A2 in platelets.",
    ),
    (
        "Statin mechanism",
        "Statins inhibit HMG-CoA reductase and upregulate LDL receptors.",
    ),
    (
        "Warfarin monitoring",
        "Warfarin is monitored with PT/INR because it affects vitamin K-dependent clotting factors.",
    ),
    (
        "Heparin monitoring",
        "Unfractionated heparin is commonly monitored with PTT.",
    ),
    (
        "Clopidogrel target",
        "Clopidogrel blocks the ADP P2Y12 receptor on platelets.",
    ),
    (
        "Furosemide nephron site",
        "Furosemide acts on the Na-K-2Cl cotransporter in the thick ascending limb.",
    ),
    (
        "Ezetimibe mechanism",
        "Ezetimibe blocks intestinal cholesterol absorption at NPC1L1.",
    ),
    (
        "Milrinone mechanism",
        "Milrinone inhibits phosphodiesterase 3 and increases cAMP in cardiac muscle.",
    ),
)

_BACKGROUND_CARDS = (
    ("ST elevation MI artery", "Inferior STEMI often involves the right coronary artery."),
    ("Lateral STEMI artery", "Lateral STEMI often involves the left circumflex artery or diagonal branches."),
    ("Anterior STEMI artery", "Anterior STEMI often involves the left anterior descending artery."),
    ("Right ventricular infarct clue", "Right ventricular infarct can present with clear lungs, hypotension, and elevated JVP."),
    ("Dressler syndrome timing", "Dressler syndrome is autoimmune pericarditis weeks after myocardial infarction."),
    ("Acute rheumatic fever valve", "Rheumatic heart disease most commonly affects the mitral valve."),
    ("Infective endocarditis organism", "Staphylococcus aureus is a common cause of acute infective endocarditis."),
    ("Viridans endocarditis risk", "Viridans streptococci can cause endocarditis after dental procedures."),
    ("Janeway lesions", "Janeway lesions are painless palm or sole lesions in infective endocarditis."),
    ("Osler nodes", "Osler nodes are painful finger or toe nodules in infective endocarditis."),
    ("Atrial myxoma finding", "Atrial myxoma can cause a diastolic plop and positional symptoms."),
    ("Coarctation rib notching", "Aortic coarctation can cause rib notching from collateral intercostal arteries."),
    ("Patent ductus arteriosus murmur", "Patent ductus arteriosus classically causes a continuous machine-like murmur."),
    ("Tetralogy of Fallot features", "Tetralogy of Fallot includes VSD, overriding aorta, pulmonary stenosis, and right ventricular hypertrophy."),
    ("Transposition treatment bridge", "Prostaglandin E1 can keep the ductus arteriosus open before repair in duct-dependent lesions."),
    ("Kawasaki coronary risk", "Kawasaki disease can cause coronary artery aneurysms."),
    ("Takayasu patient clue", "Takayasu arteritis classically affects young women and can reduce upper-extremity pulses."),
    ("Temporal arteritis treatment", "Suspected giant cell arteritis is treated promptly with corticosteroids to prevent vision loss."),
    ("Buerger disease association", "Thromboangiitis obliterans is strongly associated with smoking."),
    ("Raynaud phenomenon", "Raynaud phenomenon causes episodic digital color change triggered by cold or stress."),
    ("Aortic dissection pain", "Aortic dissection classically causes sudden tearing chest pain radiating to the back."),
    ("Marfan aortic risk", "Marfan syndrome increases risk of aortic root dilation and dissection."),
    ("Homocystinuria vascular risk", "Homocystinuria can cause thrombosis and lens subluxation downward."),
    ("Peripheral artery disease ABI", "An ankle-brachial index below 0.9 supports peripheral artery disease."),
)


def build_demo_review_entries(now: datetime) -> list[ReviewLogEntry]:
    cards = _demo_cards()
    entries: list[ReviewLogEntry] = []
    for offset, card in enumerate(cards):
        entries.extend(_reviews_for_card(card, card_id=900_000 + offset, note_id=800_000 + offset, now=now, offset=offset))
    return entries


def _demo_cards() -> tuple[DemoCard, ...]:
    cards: list[DemoCard] = []
    cards.extend(_cards_for_group(_HEMODYNAMIC_CARDS, tag="cardio_hemodynamics", pattern="recent_cluster"))
    cards.extend(_cards_for_group(_DRUG_CARDS, tag="cardio_drugs", pattern="thirty_day_cluster"))
    cards.extend(_cards_for_group(_ARRHYTHMIA_CARDS, tag="cardio_arrhythmias", pattern="ninety_day_cluster"))
    cards.extend(_cards_for_group(_BACKGROUND_CARDS, tag="cardio_background", pattern="cardio_background"))
    cards.extend(_cards_for_group(_STABLE_CARDS, tag="cardio_stable", pattern="mostly_passed"))
    return tuple(cards)


def _cards_for_group(raw_cards: tuple[tuple[str, str], ...], *, tag: str, pattern: str) -> tuple[DemoCard, ...]:
    return tuple(
        DemoCard(
            label=label,
            tag=tag,
            text=f"Front: {label}. Back: {answer}",
            pattern=pattern,
        )
        for label, answer in raw_cards
    )


def _reviews_for_card(card: DemoCard, *, card_id: int, note_id: int, now: datetime, offset: int) -> list[ReviewLogEntry]:
    if card.pattern == "recent_cluster":
        return [
            _entry(card, card_id, note_id, now - timedelta(days=48 + offset % 20), 3, reps=7, lapses=1),
            _entry(card, card_id, note_id, now - timedelta(days=18 + offset % 9), 1, reps=8, lapses=2),
            _entry(card, card_id, note_id, now - timedelta(days=2 + offset % 4, hours=1), 1, reps=9, lapses=3),
            _entry(card, card_id, note_id, now - timedelta(days=1 + offset % 4, hours=10), 1, reps=10, lapses=4),
        ]
    if card.pattern == "thirty_day_cluster":
        return [
            _entry(card, card_id, note_id, now - timedelta(days=58 + offset % 20), 3, reps=6, lapses=0),
            _entry(card, card_id, note_id, now - timedelta(days=23 + offset % 6), 1, reps=7, lapses=1),
            _entry(card, card_id, note_id, now - timedelta(days=10 + offset % 8), 1, reps=8, lapses=2),
            _entry(card, card_id, note_id, now - timedelta(days=3 + offset % 5), 3, reps=9, lapses=2),
        ]
    if card.pattern == "ninety_day_cluster":
        return [
            _entry(card, card_id, note_id, now - timedelta(days=82 + offset % 6), 1, reps=4, lapses=1),
            _entry(card, card_id, note_id, now - timedelta(days=64 + offset % 8), 1, reps=5, lapses=2),
            _entry(card, card_id, note_id, now - timedelta(days=32 + offset % 7), 3, reps=6, lapses=2),
            _entry(card, card_id, note_id, now - timedelta(days=12 + offset % 5), 3, reps=7, lapses=2),
        ]
    if card.pattern == "cardio_background":
        return [
            _entry(card, card_id, note_id, now - timedelta(days=70 + offset % 12), 3, reps=5, lapses=0),
            _entry(card, card_id, note_id, now - timedelta(days=28 + offset % 10), 3, reps=6, lapses=0),
            _entry(card, card_id, note_id, now - timedelta(days=4 + offset % 6), 3, reps=7, lapses=0),
        ]
    return [
        _entry(card, card_id, note_id, now - timedelta(days=50 + offset % 10), 3, reps=4, lapses=0, deck=CONTROL_DECK_NAME),
        _entry(card, card_id, note_id, now - timedelta(days=20 + offset % 10), 3, reps=5, lapses=0, deck=CONTROL_DECK_NAME),
        _entry(card, card_id, note_id, now - timedelta(days=3 + offset % 5), 3, reps=6, lapses=0, deck=CONTROL_DECK_NAME),
    ]


def _entry(
    card: DemoCard,
    card_id: int,
    note_id: int,
    reviewed_at: datetime,
    ease: int,
    *,
    reps: int,
    lapses: int,
    deck: str = DEMO_DECK_NAME,
) -> ReviewLogEntry:
    return ReviewLogEntry(
        card_id=card_id,
        ease=ease,
        reviewed_at=reviewed_at,
        deck_name=deck,
        card_label=card.label,
        note_id=note_id,
        note_card_count=1,
        tags=(card.tag,),
        source_text=card.text,
        duration_ms=20_000 if ease == 1 else 9_000,
        review_type=2,
        card_reps=reps,
        card_lapses=lapses,
        card_type=2,
        card_queue=2,
    )
