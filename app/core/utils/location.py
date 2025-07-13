import re
import unicodedata

def slugify_vietnamese_location(text):
    text = text.strip().lower()

    # Replace Vietnamese abbreviations
    text = re.sub(r'\b(tp\.?|thành phố)\b', 'thanh pho', text)
    text = re.sub(r'\b(q\.?|quận)\b', 'quan', text)
    text = re.sub(r'\b(h\.?|huyện)\b', 'huyen', text)
    text = re.sub(r'\b(t\.?|tỉnh)\b', 'tinh', text)
    text = re.sub(r'\b(p\.?|phường)\b', 'phuong', text)
    text = re.sub(r'\b(x\.?|xã)\b', 'xa', text)

    # Remove accents
    text = ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )

    # Replace non-alphanum with _
    text = re.sub(r'[^a-z0-9]+', '_', text)

    return text.strip('_')
