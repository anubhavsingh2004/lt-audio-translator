import json
import os
import re
from datetime import date

OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "resources", "defense_glossary.json")

def slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "term"

def add(entries, seen, term, hi, variants=None, tags=None, priority=7, notes=None):
    t = term.strip().lower()
    if not t or t in seen:
        return
    seen.add(t)
    e = {
        "id": f"dg_{slugify(term)[:80]}",
        "term": term,
        "target_hi": hi,
        "variants": variants or [],
        "priority": int(priority),
        "tags": tags or []
    }
    if notes:
        e["notes"] = notes
    entries.append(e)

def main():
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    entries, seen = [], set()

    # ---- Tier-A: Ambiguous high-impact terms (priority 10/9) ----
    ambiguous = [
        ("nut", "नट (बोल्ट फास्टनर)", ["fastener nut"], ["engineering"], 10, "Fastener sense, not food"),
        ("bolt", "बोल्ट (फास्टनर)", ["bolt fastener"], ["engineering"], 10, None),
        ("battery", "बैटरी (तोपखाना इकाई)", ["artillery battery"], ["artillery"], 9, "Artillery unit sense"),
        ("charge", "विस्फोटक चार्ज", ["explosive charge"], ["eod","demolitions"], 9, None),
        ("arm", "आर्म करना / सशस्त्र करना", ["arm the device"], ["weapons","eod"], 9, None),
        ("fire", "फायर (गोली चलाना)", ["open fire"], ["tactics","weapons"], 9, None),
        ("round", "राउंड (गोला-बारूद)", ["ammo round"], ["ammunition"], 9, None),
        ("shell", "गोला (तोप/मोर्टार)", ["artillery shell","mortar shell"], ["artillery","ammunition"], 9, None),
        ("magazine", "मैगजीन (गोला-बारूद)", ["mag"], ["weapons","ammunition"], 9, "Ammo magazine, not publication"),
        ("bearing", "दिशा कोण (बेयरिंग)", ["bearing angle"], ["navigation"], 8, None),
        ("mine", "बारूदी सुरंग", ["landmine"], ["eod","engineering"], 9, None),
        ("range", "रेंज (दूरी/फायरिंग क्षेत्र)", ["firing range"], ["navigation","weapons"], 8, None),
        ("secure", "सुरक्षित करना / कब्ज़ा करना", ["secure the area"], ["tactics"], 8, None),
        ("clear", "क्लियर करना (क्षेत्र/कमरा)", ["clear the room"], ["cqb","tactics"], 8, None),
        ("breach", "ब्रीच (तोड़कर प्रवेश)", ["breach point"], ["cqb","tactics"], 8, None),
    ]
    for term, hi, variants, tags, pr, notes in ambiguous:
        add(entries, seen, term, hi, variants=variants, tags=tags, priority=pr, notes=notes)

    # ---- Prowords / radio procedure (high value) ----
    prowords = [
        ("roger", "समझ गया", ["roger that"], ["comms","radio"], 9),
        ("wilco", "अवश्य करूंगा", [], ["comms","radio"], 9),
        ("affirmative", "हां", ["affirm"], ["comms","radio"], 8),
        ("negative", "नहीं", ["neg"], ["comms","radio"], 8),
        ("copy", "समझ गया", ["copy that"], ["comms","radio"], 8),
        ("stand by", "प्रतीक्षा करें", ["standby"], ["comms","radio"], 8),
        ("go ahead", "बोलिए", [], ["comms","radio"], 8),
        ("say again", "दोहराएं", [], ["comms","radio"], 8),
        ("break", "ब्रेक / विराम", [], ["comms","radio"], 8),
        ("over", "ओवर (समाप्त)", [], ["comms","radio"], 8),
        ("out", "आउट (संदेश समाप्त)", [], ["comms","radio"], 8),
        ("repeat", "दोहराएं (रिपीट)", [], ["comms","radio"], 7),
        ("loud and clear", "स्पष्ट सुनाई दे रहा है", [], ["comms","radio"], 7),
        ("read back", "रीड बैक करें", [], ["comms","radio"], 7),
    ]
    for term, hi, variants, tags, pr in prowords:
        add(entries, seen, term, hi, variants=variants, tags=tags, priority=pr)

    # ---- Fire control & tactical phrases (multi-word) ----
    phrases = [
        ("rules of engagement", "युद्ध नियम (ROE)", ["ROE"], ["legal","operations"], 10),
        ("cease fire", "गोलीबारी बंद करो", ["ceasefire"], ["comms","tactics"], 9),
        ("check fire", "फायर रोकें", [], ["tactics","comms"], 9),
        ("shift fire", "फायर शिफ्ट करो", [], ["tactics"], 8),
        ("hold fire", "फायर रोककर रखें", [], ["tactics"], 8),
        ("fire mission", "फायर मिशन", [], ["artillery"], 8),
        ("danger close", "खतरे के बहुत करीब", [], ["tactics"], 8),
        ("covering fire", "कवर फायर", [], ["tactics"], 8),
        ("suppressive fire", "दमनकारी फायर", [], ["tactics"], 8),
        ("secure perimeter", "परिधि सुरक्षित करो", [], ["tactics"], 8),
        ("clear the room", "कमरा क्लियर करो", [], ["cqb"], 8),
        ("entry point", "प्रवेश बिंदु", [], ["cqb"], 7),
        ("breach point", "ब्रीच पॉइंट", [], ["cqb"], 8),
        ("rally point", "एकत्रीकरण बिंदु", ["RP"], ["tactics"], 7),
        ("return to base", "आधार पर वापसी (RTB)", ["RTB"], ["aviation","comms"], 8),
        ("situation report", "स्थिति रिपोर्ट (SITREP)", ["SITREP"], ["comms"], 8),
        ("quick reaction force", "त्वरित प्रतिक्रिया बल (QRF)", ["QRF"], ["tactics"], 8),
        ("improvised explosive device", "स्वनिर्मित विस्फोटक (IED)", ["IED"], ["eod"], 10),
    ]
    for term, hi, variants, tags, pr in phrases:
        add(entries, seen, term, hi, variants=variants, tags=tags, priority=pr)

    # ---- Acronyms (only real ones, no filler) ----
    acronyms = [
        ("IED", "स्वनिर्मित विस्फोटक (IED)", ["improvised explosive device"], ["eod","acronym"], 10),
        ("ROE", "युद्ध नियम (ROE)", ["rules of engagement"], ["legal","acronym"], 10),
        ("SITREP", "स्थिति रिपोर्ट (SITREP)", ["situation report"], ["comms","acronym"], 9),
        ("RTB", "आधार पर वापसी (RTB)", ["return to base"], ["comms","acronym"], 9),
        ("QRF", "त्वरित प्रतिक्रिया बल (QRF)", ["quick reaction force"], ["tactics","acronym"], 9),
        ("MEDEVAC", "चिकित्सा स्थानांतरण (MEDEVAC)", [], ["medical","acronym"], 9),
        ("CASEVAC", "चिकित्सा निकासी (CASEVAC)", [], ["medical","acronym"], 9),
        ("KIA", "युद्ध में मारा गया (KIA)", ["killed in action"], ["medical","acronym"], 9),
        ("WIA", "घायल (WIA)", ["wounded in action"], ["medical","acronym"], 9),
        ("MIA", "लापता (MIA)", ["missing in action"], ["operations","acronym"], 9),
        ("LZ", "उतरान क्षेत्र (LZ)", ["landing zone"], ["aviation","acronym"], 8),
        ("DZ", "ड्रॉप ज़ोन (DZ)", ["drop zone"], ["aviation","acronym"], 8),
        ("HVT", "उच्च मूल्य लक्ष्य (HVT)", ["high value target"], ["intel","acronym"], 9),
        ("CAS", "क्लोज़ एयर सपोर्ट (CAS)", ["close air support"], ["aviation","acronym"], 9),
        ("EOD", "विस्फोटक निष्क्रियकरण (EOD)", ["explosive ordnance disposal"], ["eod","acronym"], 9),
        ("C2", "कमांड एंड कंट्रोल (C2)", ["command and control"], ["c2","acronym"], 8),
        ("C4ISR", "C4ISR", [], ["c2","acronym"], 8),
        ("UAV", "मानवरहित हवाई वाहन (UAV)", ["drone"], ["aviation","acronym"], 8),
        ("EW", "इलेक्ट्रॉनिक वारफेयर (EW)", ["electronic warfare"], ["ew","acronym"], 8),
        ("ISR", "इंटेलिजेंस/सर्विलांस/रिकॉन (ISR)", [], ["intel","acronym"], 8),
    ]
    for term, hi, variants, tags, pr in acronyms:
        add(entries, seen, term, hi, variants=variants, tags=tags, priority=pr)

    # ---- Weapons / ammo / kit (real list; extend over time) ----
    kit = [
        ("assault rifle", "असॉल्ट राइफल"), ("sniper rifle", "स्नाइपर राइफल"),
        ("machine gun", "मशीन गन"), ("light machine gun", "लाइट मशीन गन"),
        ("heavy machine gun", "हैवी मशीन गन"), ("grenade launcher", "ग्रेनेड लॉन्चर"),
        ("rocket launcher", "रॉकेट लॉन्चर"), ("hand grenade", "हैंड ग्रेनेड"),
        ("smoke grenade", "स्मोक ग्रेनेड"), ("fragmentation grenade", "विखंडन ग्रेनेड"),
        ("body armor", "बॉडी आर्मर"), ("helmet", "हेलमेट"), ("night vision", "नाइट विज़न"),
        ("thermal imaging", "थर्मल इमेजिंग"), ("suppressor", "सप्रेसर"),
        ("scope", "स्कोप"), ("ammunition", "गोला-बारूद"),
        ("mortar", "मोर्टार"), ("howitzer", "होवित्ज़र"),
        ("artillery", "तोपखाना"), ("rifle", "राइफल"), ("pistol", "पिस्तौल"),
    ]
    for term, hi in kit:
        add(entries, seen, term, hi, tags=["weapons"], priority=7)

    # ---- Navigation / mapping ----
    nav = [
        ("grid reference", "ग्रिड संदर्भ", ["grid ref"], ["navigation"], 7),
        ("azimuth", "एज़िमुथ / दिशा कोण", [], ["navigation"], 7),
        ("compass bearing", "कम्पास बेयरिंग", [], ["navigation"], 7),
        ("waypoint", "वेपॉइंट", [], ["navigation"], 6),
        ("line of sight", "दृष्टि रेखा", ["LOS"], ["navigation"], 6),
    ]
    for term, hi, variants, tags, pr in nav:
        add(entries, seen, term, hi, variants=variants, tags=tags, priority=pr)

    # ---- Ranks (keep real; extend later) ----
    ranks = [
        ("General", "जनरल"), ("Lieutenant General", "लेफ्टिनेंट जनरल"),
        ("Major General", "मेजर जनरल"), ("Brigadier", "ब्रिगेडियर"),
        ("Colonel", "कर्नल"), ("Lieutenant Colonel", "लेफ्टिनेंट कर्नल"),
        ("Major", "मेजर"), ("Captain", "कैप्टन"),
        ("Lieutenant", "लेफ्टिनेंट"), ("Second Lieutenant", "सेकंड लेफ्टिनेंट"),
        ("Subedar", "सूबेदार"), ("Havildar", "हवलदार"),
        ("Naik", "नायक"), ("Lance Naik", "लांस नायक"), ("Sepoy", "सिपाही")
    ]
    for term, hi in ranks:
        add(entries, seen, term, hi, tags=["rank"], priority=7)

    # ---- Expand with more REAL phrases (no numeric filler) ----
    extra_phrases = [
        ("hold position", "स्थिति बनाए रखें"),
        ("take cover", "आड़ लें"),
        ("provide cover", "कवर दें"),
        ("move to cover", "कवर की ओर बढ़ें"),
        ("enemy contact", "शत्रु संपर्क"),
        ("hostile fire", "शत्रु की गोलीबारी"),
        ("friendly forces", "मित्र बल"),
        ("collateral damage", "अनुषंगिक क्षति"),
        ("search and rescue", "खोज और बचाव"),
        ("combat air patrol", "लड़ाकू हवाई गश्त"),
        ("rules of engagement apply", "युद्ध नियम लागू हैं"),
        ("cleared hot", "फायर की अनुमति है"),
        ("abort mission", "मिशन रद्द करो"),
        ("mission complete", "मिशन पूर्ण"),
    ]
    for term, hi in extra_phrases:
        add(entries, seen, term, hi, tags=["operations"], priority=7)

    out = {
        "_metadata": {
            "version": "1.0",
            "description": "Tier-A curated defense glossary (high quality, no filler).",
            "last_updated": str(date.today()),
            "count": len(entries)
        },
        "entries": entries
    }

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"✅ Wrote {len(entries)} curated entries to: {os.path.abspath(OUT_PATH)}")
    print("Tip: Expand lists (ambiguous/prowords/phrases/acronyms/kit/nav/ranks) to grow to 250–400+ entries.")

if __name__ == "__main__":
    main()
