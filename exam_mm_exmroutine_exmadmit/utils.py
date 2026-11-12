import re
import unicodedata

# বিষয়ের নাম দেখে ধর্ম চেনার শব্দ (বানান ভুল/ভিন্ন বানান ধরার জন্য একাধিক রূপ)
RELIGION_KEYWORDS = {
    'islam': ['islam', 'ইসলাম', 'ইসলামিক'],
    'hindu': ['hindu', 'হিন্দু', 'হিন্দ'],
    'christian': ['christ', 'খ্রিস্ট', 'খ্রিষ্ট', 'খ্রীষ্ট', 'খ্রীস্ট', 'খ্রিশ্চান', 'খৃষ্ট', 'খৃস্ট'],
    'buddhism': ['buddh', 'bouddh', 'বৌদ্ধ', 'বুদ্ধ', 'বৌদ্ব'],
}

# এগুলো থাকলে ধর্ম বিষয় ধরা হবে না (যেমন "ইসলামের ইতিহাস")
RELIGION_EXCLUDE = ['history', 'ইতিহাস', 'সংস্কৃতি', 'culture', 'civilization', 'সভ্যতা']

# ঐচ্ছিক (৪র্থ) বিষয় চেনার শব্দ
OPTIONAL_KEYWORDS = [
    'highermath', 'highermathematics', 'highmath', 'hmath',
    'উচ্চতরগণিত', 'উচ্চগণিত', 'উচ্চতরগনিত', 'উচ্চতরগণীত',
    'agricultur', 'agriculter', 'agri',
    'কৃষি',
]


def _norm(text):
    """ছোট হাতের, ফাঁকা/চিহ্ন/জোড়া-না-জোড়া অক্ষর বাদ, যাতে বানান ফাঁক-ফোঁকর কম পড়ে।"""
    text = unicodedata.normalize('NFC', (text or '').lower())
    text = text.replace('\u200c', '').replace('\u200d', '')
    return re.sub(r'[\s\.\-_,()/&]+', '', text)


def subject_religion(subject):
    """বিষয়ের নাম দেখে ধর্ম: 'islam' / 'hindu' / 'christian' / 'buddhism', নাহলে ''।"""
    name = _norm(getattr(subject, 'name', ''))
    if not name or any(_norm(w) in name for w in RELIGION_EXCLUDE):
        return ''
    for religion, words in RELIGION_KEYWORDS.items():
        if any(_norm(w) in name for w in words):
            return religion
    return ''


def subject_is_optional(subject):
    name = _norm(getattr(subject, 'name', ''))
    return bool(name) and any(_norm(w) in name for w in OPTIONAL_KEYWORDS)


def student_takes_subject(student, subject):
    """
    ছাত্র এই বিষয় পড়ে কিনা (admit/result দুই জায়গায় একই নিয়ম)।
    - ধর্ম বিষয় হলে: ছাত্রের প্রোফাইলের ধর্ম মিলতে হবে।
    - অন্য সব বিষয়: হ্যাঁ।
    """
    religion = subject_religion(subject)
    if religion:
        return (student.religion or '') == religion
    return True