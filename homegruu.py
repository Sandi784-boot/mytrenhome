import xml.etree.ElementTree as ET
import csv
import re
from collections import defaultdict
from datetime import datetime, timedelta
import os

# ============================================
# CONFIGURATION
# ============================================

TEST_MODE = False
BATCH_SIZE = 2000
BATCH_NUMBER = 1

# FILE SOURCE - Choose one:
USE_LOCAL_FILE = True  # Set to True to use local XML file
LOCAL_XML_FILE = "homeguru.xml"  # Name of your XML file
GOOGLE_DRIVE_URL = "https://drive.google.com/uc?export=download&id=1mi5Fbm9wfH8F7qsmnkJI0P_vr6lrcGH2&confirm=t"

# IMAGE SETTINGS
USE_PLACEHOLDER_FOR_MISSING_IMAGES = True
PLACEHOLDER_IMAGE_URL = "https://via.placeholder.com/600x600.png?text=No+Image+Available"

# ============================================
# COMPLETE TAG MAPPING - ALL SUBCOLLECTIONS
# ============================================

# Main Collections (10)
MAIN_COLLECTIONS = {
    # Lighting
    'φωτιστικα': 'lighting-fixtures',
    'φωτιστικά': 'lighting-fixtures',
    'φωτισμος': 'lighting-fixtures',
    'φωτισμός': 'lighting-fixtures',
    'lighting': 'lighting-fixtures',
    'light': 'lighting-fixtures',
    
    # Decoratives
    'διακοσμητικα': 'decoratives',
    'διακοσμητικά': 'decoratives',
    'διακοσμηση': 'decoratives',
    'διακόσμηση': 'decoratives',
    'decoratives': 'decoratives',
    'decorative': 'decoratives',
    'decor': 'decoratives',
    'ντεκορ': 'decoratives',
    
    # Furniture
    'επιπλα': 'furniture',
    'έπιπλα': 'furniture',
    'επιπλο': 'furniture',
    'furniture': 'furniture',
    
    # Household
    'οικιακα': 'household',
    'οικιακά': 'household',
    'household': 'household',
    
    # Seasonal
    'εποχιακα': 'seasonal',
    'εποχιακά': 'seasonal',
    'seasonal': 'seasonal',
    
    # White Goods (TEXTILES!)
    'λευκα ειδη': 'white-goods',
    'λευκά είδη': 'white-goods',
    'white goods': 'white-goods',
    'textiles': 'white-goods',
    
    # Children
    'παιδικα': 'children',
    'παιδικά': 'children',
    'παιδικο': 'children',
    'children': 'children',
    'kids': 'children',
    
    # Baptism
    'βαπτιση': 'baptism',
    'βάπτιση': 'baptism',
    'baptism': 'baptism',
}

# ============================================
# LIGHTING FIXTURES Subcollections
# ============================================
LIGHTING_SUBS = {
    'ceiling-lights': [
        'πλαφονιερα', 'πλαφονιέρα',
        'οροφης', 'οροφής',
        'κρεμαστο', 'κρεμαστό',
        'κρεμαστο οροφης', 'οροφης κρεμαστο',
        'μονοφωτο', 'μονόφωτο', 'πολυφωτο', 'πολύφωτο',
        'pendant', 'ceiling pendant', 'pendant ceiling',
        'ceiling light', 'ceiling',
        'single pendant', 'multi pendant'
    ],
    
    'lighting-accessories': [
        'αξεσουαρ φωτιστικου', 'αξεσουάρ φωτιστικου',
        'μερη φωτιστικου', 'μέρη φωτιστικου',
        'ανταλλακτικο', 'ανταλλακτικό',
        'αναρτηση', 'ανάρτηση',
        'συρματινο', 'συρμάτινο', 'καλωδιο', 'καλώδιο',
        'lighting accessories', 'light parts', 'replacement parts',
        'suspension', 'wire', 'cable', 'cord'
    ],
    
    'tabletop': [
        'επιτραπεζιο φωτιστικο', 'επιτραπέζιο φωτιστικό',
        'επιτραπεζιο', 'επιτραπέζιο',
        'πορτατιφ', 'table lamp', 'desk lamp', 'tabletop'
    ],
    
    'floor': [
        'δαπεδου φωτιστικο', 'φωτιστικο δαπεδου',
        'δαπεδου', 'δαπέδου',
        'floor lamp', 'standing lamp', 'floor'
    ],
    
    'office': [
        'γραφειου φωτιστικο', 'φωτιστικο γραφειου',
        'γραφειου', 'γραφείου',
        'office lamp', 'desk office', 'office'
    ],
    
    'sconces': [
        'απλικα', 'απλίκα',
        'wall lamp', 'sconce', 'wall sconce'
    ],
    
    'hats': [
        'καπελο φωτιστικο', 'φωτιστικο καπελο',
        'καπελο', 'καπέλο',
        'αμπαζουρ',
        'hat light', 'lampshade', 'lamp hat', 'shade'
    ],
    
    'spotlights': [
        'σποτ οροφης', 'spot οροφης',
        'σποτ', 'spot',
        'spotlight', 'ceiling spot'
    ],
    
    'outdoor-lights': [
        'εξωτερικου χωρου', 'εξωτερικου χώρου',
        'εξωτερικου', 'εξωτερικού',
        'κηπου', 'κήπου',
        'κολονακι', 'κολονάκι',
        'χελωνα', 'χελώνα',
        'outdoor light', 'garden light', 'exterior light', 'outdoor',
        'garden', 'exterior'
    ],
    
    'lamps': [
        'λαμπα', 'λάμπα', 'λαμπες', 'λάμπες',
        'bulb', 'light bulb', 'lamp bulb', 'lamps'
    ],
    
    'children-lights': [
        'παιδικο φωτιστικο', 'φωτιστικο παιδικο',
        'παιδικό φωτιστικό',
        'kids light', 'children lamp', 'child light'
    ],
}

# ============================================
# DECORATIVES Subcollections
# ============================================
DECORATIVES_SUBS = {
    'mirrors': [
        'καθρεφτης', 'καθρέφτης', 'καθρεφτες',
        'mirror', 'mirrors'
    ],
    
    'vases-bowls': [
        'βαζο', 'βάζο', 'βαζα',
        'μπολ', 'bowl',
        'vase', 'vases'
    ],
    
    'boxes-baskets': [
        'κουτι', 'κουτί', 'κουτια',
        'καλαθι', 'καλάθι', 'καλαθια',
        'box', 'basket', 'storage box'
    ],
    
    'trays-coasters': [
        'δισκος', 'δίσκος', 'δισκοι',
        'σουβερ', 'tray', 'coaster'
    ],
    
    'plates': [
        'πιατο διακοσμητικο', 'διακοσμητικο πιατο',
        'πιατο', 'πιάτο',
        'decorative plate', 'plate'
    ],
    
    'candles': [
        'κερι', 'κερί', 'κερια',
        'αρωματικο', 'αρωματικά',
        'candle', 'scented candle'
    ],
    
    'sculptures': [
        'γλυπτο', 'γλυπτά', 'φιγουρα',
        'sculpture', 'statue', 'figurine'
    ],
    
    'flowers': [
        'λουλουδι τεχνητο', 'τεχνητο λουλουδι',
        'λουλουδι', 'λουλούδι',
        'artificial flower', 'fake flower', 'flower'
    ],
    
    'wine-sets': [
        'καραφα', 'καράφα',
        'σετ κρασιου', 'σετ κρασιού',
        'carafe', 'wine set', 'decanter'
    ],
    
    'wall-decoration': [
        'διακοσμηση τοιχου', 'διακόσμηση τοίχου',
        'τοιχου διακοσμηση', 'τζακιου',
        'πινακας', 'πίνακας', 'πινακες', 'πίνακες',
        'πινακας mdf', 'πινακας καμβας',
        'εκτυπωση', 'εκτύπωση',
        'wall decor', 'wall art', 'wall decoration',
        'painting', 'canvas', 'print'
    ],
    
    'watches': [
        'ρολοι τοιχου', 'ρολόι τοίχου',
        'ρολοι', 'ρολόι',
        'wall clock', 'clock', 'watch'
    ],
    
    'photo-frames': [
        'κορνιζα', 'κορνίζα', 'κορνιζες',
        'αλμπουμ', 'άλμπουμ',
        'frame', 'photo frame', 'picture frame', 'album'
    ],
    
    'pots-jars': [
        'γλαστρα', 'γλάστρα', 'γλαστρες',
        'βαζο φυτου', 'pot', 'planter', 'flower pot'
    ],
    
    'candlesticks': [
        'κηροπηγιο', 'κηροπήγιο',
        'σταχτοδοχειο', 'σταχτοδοχείο',
        'candlestick', 'candle holder', 'ashtray'
    ],
    
    'animals': [
        'ζωο διακοσμητικο', 'διακοσμητικο ζωο',
        'ζωο', 'ζώο',
        'animal figurine', 'animal'
    ],
    
    'key-holders': [
        'κλειδοθηκη', 'κλειδοθήκη',
        'κρεμαστρα', 'κρεμάστρα',
        'καλογερος', 'καλόγερος',
        'key holder', 'key rack', 'hanger', 'coat rack', 'coat hanger', 'hook'
    ],
    
    'general-decorative': [
        'διακοσμητικα γενικα', 'γενικα διακοσμητικα',
        'υλικά', 'υλικα',
        'general decorative', 'misc decorative', 'materials'
    ],
    
    'holders': [
        'εφημεριδοθηκη', 'εφημεριδοθήκη',
        'ομπρελοθηκη', 'ομπρελοθήκη',
        'newspaper holder', 'umbrella stand', 'magazine rack'
    ],
    
    'tables': [
        'τραπεζακι διακοσμητικο', 'διακοσμητικο τραπεζακι',
        'decorative table', 'small table'
    ],
    
    'traffic-lights': [
        'φαναρι τροχαιας', 'φανάρι τροχαίας',
        'traffic light', 'street light'
    ],
}

# ============================================
# FURNITURE Subcollections
# ============================================
FURNITURE_SUBS = {
    'coffee-tables': [
        'τραπεζακι σαλονιου', 'τραπεζάκι σαλονιου',
        'τραπεζι σαλονιου', 'τραπέζι σαλονιου',
        'τραπεζακι', 'τραπεζάκι',
        'βοηθητικο τραπεζι', 'βοηθητικό τραπέζι',
        'τραπεζακι βοηθητικο', 'τραπεζάκι βοηθητικό',
        'βοηθητικα', 'βοηθητικά',
        'coffee table', 'living room table', 'salon table',
        'side table', 'auxiliary table', 'end table'
    ],
    
    'beds': [
        'κρεβατι', 'κρεβάτι', 'κρεβατια',
        'bed', 'bed frame', 'bedframe'
    ],
    
    'sofas-recliners': [
        'καναπες', 'καναπές', 'καναπεδες',
        'ρελαξ', 'sofa', 'couch', 'recliner'
    ],
    
    'chairs': [
        'καρεκλα τραπεζαριας', 'καρέκλα τραπεζαρίας',
        'καρεκλα', 'καρέκλα',
        'dining chair', 'chair'
    ],
    
    'armchairs': [
        'πολυθρονα', 'πολυθρόνα',
        'armchair', 'lounge chair'
    ],
    
    'wardrobes': [
        'ντουλαπα ρουχων', 'ντουλάπα ρούχων',
        'ντουλαπα', 'ντουλάπα',
        'wardrobe', 'closet', 'armoire'
    ],
    
    'chests-drawers': [
        'συρταριερα', 'συρταριέρα',
        'τουαλετα κρεβατοκαμαρας', 'τουαλέτα κρεβατοκάμαρας',
        'κονσολα', 'κονσόλα',
        'κομοδινο', 'κομοδίνο',
        'chest', 'dresser', 'console', 'drawer', 'nightstand'
    ],
    
    'buffets': [
        'μπουφες', 'μπουφές',
        'buffet', 'sideboard', 'credenza'
    ],
    
    'dining-rooms': [
        'τραπεζαρια', 'τραπεζαρία',
        'τραπεζι τραπεζαριας', 'τραπέζι τραπεζαρίας',
        'τραπεζι με καρεκλες', 'τραπέζι με καρέκλες',
        'καρεκλα τραπεζαριας', 'καρέκλα τραπεζαρίας',
        'dining set', 'dining table', 'dining room', 'table with chairs'
    ],
    
    'bookcase': [
        'βιβλιοθηκη', 'βιβλιοθήκη',
        'ραφιερα', 'ραφιέρα', 'ραφιερες',
        'ραφι τοιχου', 'ράφι τοίχου',
        'ραφια', 'ράφια',
        'bookcase', 'bookshelf', 'shelving',
        'shelf', 'shelves', 'wall shelf', 'shelving unit'
    ],
    
    'tv-furniture': [
        'επιπλο τηλεορασης', 'έπιπλο τηλεόρασης',
        'συνθετο', 'σύνθετο',
        'tv unit', 'tv stand', 'tv', 'entertainment'
    ],
    
    'office-chairs': [
        'καρεκλα γραφειου', 'καρέκλα γραφείου',
        'office chair', 'desk chair', 'task chair'
    ],
    
    'stools-poufs': [
        'πουφ μαξιλαρι', 'πουφ υφασματινο',
        'σκαμπω', 'σκαμπώ', 'πουφ',
        'pouf', 'ottoman', 'stool', 'footstool'
    ],
    
    'mattresses': [
        'στρωμα', 'στρώμα', 'στρωματα',
        'mattress', 'bed mattress'
    ],
    
    'shoe-racks': [
        'παπουτσοθηκη', 'παπουτσοθήκη',
        'ντουλαπακι', 'ντουλαπάκι',
        'shoe rack', 'shoe cabinet', 'shoe storage'
    ],
    
    'table-bases': [
        'βαση τραπεζιου', 'βάση τραπεζιου',
        'βασεις τραπεζιου', 'βάσεις τραπεζιου',
        'table base', 'table leg', 'table support'
    ],
    
    'offices-furniture': [
        'γραφειο επιπλο', 'γραφείο έπιπλο',
        'γραφεια', 'γραφεία',
        'office desk', 'desk furniture', 'office'
    ],
    
    'screen': [
        'παραβαν', 'παραβάν',
        'screen', 'room divider', 'partition'
    ],
    
    'monks': [
        'μοναχος', 'μονάχος', 'μοναχοι',
        'καλογερος', 'καλόγερος',
        'monk seat', 'monks', 'coat stand'
    ],
    
    'hangers': [
        'κρεμαστρα', 'κρεμάστρα',
        'καλογερος', 'καλόγερος',
        'hanger', 'coat rack', 'coat hanger', 'hook', 'wall hanger'
    ],
    
    'outdoor-furniture': [
        'εξωτερικου χωρου επιπλο', 'εξωτερικου χώρου έπιπλο',
        'εξωτερικου χωρου', 'εξωτερικου χώρου',
        'κηπου', 'κήπου',
        'catering', 'συνεδριου', 'συνεδρίου',
        'outdoor furniture', 'garden furniture', 'patio',
        'outdoor', 'garden', 'catering', 'folding'
    ],
}

# ============================================
# WHITE GOODS Subcollections (TEXTILES)
# ============================================
WHITE_GOODS_SUBS = {
    'pillows': [
        'μαξιλαρι', 'μαξιλάρι', 'μαξιλαρια',
        'pillow', 'cushion', 'throw pillow'
    ],
    
    'throws-blankets': [
        'ριχταρι', 'ριχτάρι', 'ριχταρια',
        'κουβερτα', 'κουβέρτα', 'κουβερτες',
        'πλεκτο ριχταρι', 'πλεκτό ριχτάρι',
        'throw', 'blanket', 'knitted', 'bedspread'
    ],
    
    'carpets': [
        'χαλι', 'χαλί', 'χαλια',
        'carpet', 'rug', 'mat'
    ],
    
    'towels': [
        'πετσετα', 'πετσέτα', 'πετσετες',
        'towel', 'bath towel', 'hand towel'
    ],
}

# ============================================
# CHILDREN Subcollections
# ============================================
CHILDREN_SUBS = {
    'children-lighting': [
        'παιδικο φωτιστικο', 'παιδικό φωτιστικό',
        'φωτιστικο παιδικο',
        'kids light', 'children lamp'
    ],
    
    'children-beds': [
        'παιδικο κρεβατι', 'παιδικό κρεβάτι',
        'κρεβατι παιδικο',
        'kids bed', 'children bed'
    ],
    
    'children-furniture': [
        'παιδικο επιπλο', 'παιδικό έπιπλο',
        'επιπλο παιδικο', 'αλλα επιπλα',
        'kids furniture', 'children furniture'
    ],
}

# ============================================
# HOUSEHOLD Subcollections
# ============================================
HOUSEHOLD_SUBS = {
    'kitchen': [
        'κουζινα', 'κουζίνα',
        'kitchen'
    ],
    
    'bathroom': [
        'μπανιο', 'μπάνιο',
        'bathroom', 'bath'
    ],
    
    'radiators': [
        'καλοριφερ', 'καλοριφέρ',
        'radiator', 'heater'
    ],
}

# ============================================
# SEASONAL Subcollections
# ============================================
SEASONAL_SUBS = {
    'christmas': [
        'χριστουγεννα', 'χριστούγεννα',
        'χριστουγεννιατικο', 'χριστουγεννιάτικο',
        'christmas', 'xmas', 'festive'
    ],
    
    'easter-spring': [
        'πασχα', 'πάσχα', 'πασχαλινο',
        'ανοιξη', 'άνοιξη', 'ανοιξιατικο',
        'easter', 'spring'
    ],
    
    'suitcases': [
        'βαλιτσα', 'βαλίτσα', 'βαλιτσες',
        'suitcase', 'luggage', 'travel bag'
    ],
    
    'scrunchies': [
        'λαστιχακι', 'λαστιχάκι', 'λαστιχακια',
        'scrunchie', 'hair tie', 'hair elastic'
    ],
}

# ============================================
# BAPTISM Subcollections
# ============================================
BAPTISM_SUBS = {
    'baptism-boy': [
        'σετ βαπτισης αγοριου', 'σετ βάπτισης αγοριου',
        'αγοριου βαπτιση', 'αγοριου βάπτιση', 'αγοριου',
        'boy baptism', 'baptism boy'
    ],
    
    'baptism-girl': [
        'σετ βαπτισης κοριτσιου', 'σετ βάπτισης κοριτσιου',
        'κοριτσιου βαπτιση', 'κοριτσιου βάπτιση', 'κοριτσιου',
        'girl baptism', 'baptism girl'
    ],
}

# Special tags
SPECIAL_TAGS = {
    'offers': [
        'προσφορα', 'προσφορά', 'προσφορες',
        'offer', 'sale', 'hot deal', 'discount', 'έκπτωση'
    ],
    
    'new-arrivals': [
        'νεο', 'νέο', 'νεα', 'νέα',
        'new arrival', 'new product', 'new'
    ],
}

# ============================================
# HELPER FUNCTIONS
# ============================================

def safe_get_text(data, key, default=''):
    """Safely get text value from data dict, handling None values"""
    value = data.get(key)
    if value is None:
        return default
    return str(value).strip()

def clean_text(text):
    """Clean HTML and extra whitespace + preserve paragraphs"""
    if not text:
        return ''
    
    text = str(text)
    text = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</p>', '\n\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<p[^>]*>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r' \n', '\n', text)
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(line for line in lines if line)
    return text.strip()

def get_higher_quality_url(image_url):
    """Get FULL SIZE image instead of thumbnails"""
    if not image_url:
        return image_url
    
    patterns = [
        r'-\d+x\d+\.(jpg|jpeg|png|webp|gif)',
        r'_\d+x\d+\.(jpg|jpeg|png|webp|gif)',
    ]
    
    for pattern in patterns:
        image_url = re.sub(pattern, r'.\1', image_url, flags=re.IGNORECASE)
    
    return image_url

def generate_description_homeguru(data, title):
    """Generate description from ALL available sources"""
    desc_parts = []
    
    # 1. Try existing description
    existing_desc = clean_text(safe_get_text(data, 'description'))
    if existing_desc and len(existing_desc) > 10:
        return existing_desc
    
    # 2. Build from attributes
    color = safe_get_text(data, 'color')
    if color:
        desc_parts.append(f"<strong>Χρώμα:</strong> {color}")
    
    material = safe_get_text(data, 'yliko')
    if material:
        desc_parts.append(f"<strong>Υλικό:</strong> {material}")
    
    # Build dimensions string
    dims = []
    length = safe_get_text(data, 'length')
    width = safe_get_text(data, 'width')
    height = safe_get_text(data, 'height')
    
    if length:
        dims.append(f"Μήκος: {length}")
    if width:
        dims.append(f"Πλάτος: {width}")
    if height:
        dims.append(f"Ύψος: {height}")
    
    if dims:
        desc_parts.append(f"<strong>Διαστάσεις:</strong> {', '.join(dims)}")
    
    # 3. If we have attributes, return them
    if desc_parts:
        return '<br><br>'.join(desc_parts)
    
    # 4. Last resort: use title
    return f"<p>{title}</p>"

def extract_main_collection(category_text, title, season):
    """Extract main collection from category/title/season"""
    full_text = f"{category_text} {title} {season}".lower()
    
    matches = []
    for keyword, tag in MAIN_COLLECTIONS.items():
        if keyword in full_text:
            matches.append((tag, len(keyword)))
    
    if matches:
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches[0][0]
    
    return None

def find_best_subcollection(text_to_check, subcollection_dict):
    """Find BEST matching subcollection (longest/most specific keyword)"""
    text_lower = text_to_check.lower()
    
    matches = []
    for sub_tag, keywords in subcollection_dict.items():
        for keyword in keywords:
            if keyword in text_lower:
                matches.append((sub_tag, len(keyword)))
    
    if matches:
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches[0][0]
    
    return None

def extract_subcollections(category_text, title, main_collection):
    """Extract subcollections with 'Other' fallback"""
    if not main_collection:
        return []
    
    text_to_check = f"{category_text} {title}".lower()
    subcollections = []
    
    # Map main collections to their subcollection dictionaries
    if main_collection == 'lighting-fixtures':
        sub = find_best_subcollection(text_to_check, LIGHTING_SUBS)
        if sub:
            subcollections.append(sub)
    
    elif main_collection == 'decoratives':
        sub = find_best_subcollection(text_to_check, DECORATIVES_SUBS)
        if sub:
            subcollections.append(sub)
    
    elif main_collection == 'furniture':
        sub = find_best_subcollection(text_to_check, FURNITURE_SUBS)
        if sub:
            subcollections.append(sub)
    
    elif main_collection == 'white-goods':
        sub = find_best_subcollection(text_to_check, WHITE_GOODS_SUBS)
        if sub:
            subcollections.append(sub)
    
    elif main_collection == 'household':
        sub = find_best_subcollection(text_to_check, HOUSEHOLD_SUBS)
        if sub:
            subcollections.append(sub)
    
    elif main_collection == 'children':
        sub = find_best_subcollection(text_to_check, CHILDREN_SUBS)
        if sub:
            subcollections.append(sub)
    
    elif main_collection == 'seasonal':
        sub = find_best_subcollection(text_to_check, SEASONAL_SUBS)
        if sub:
            subcollections.append(sub)
    
    elif main_collection == 'baptism':
        sub = find_best_subcollection(text_to_check, BAPTISM_SUBS)
        if sub:
            subcollections.append(sub)
    
    # Cross-category: Children lights
    is_children_light = any(keyword in text_to_check for keyword in [
        'παιδικο φωτιστικο', 'παιδικό φωτιστικό',
        'φωτιστικο παιδικο', 'kids light', 'children lamp'
    ])
    
    if is_children_light:
        if main_collection == 'lighting-fixtures' and 'children-lights' not in subcollections:
            subcollections.append('children-lights')
        if main_collection == 'children' and 'children-lighting' not in subcollections:
            subcollections.append('children-lighting')
    
    # "OTHER" FALLBACK
    if not subcollections:
        OTHER_MAP = {
            'lighting-fixtures': 'other-lighting',
            'decoratives': 'other-decoratives',
            'furniture': 'other-furniture',
            'white-goods': 'other-textiles',
            'household': 'other-household',
            'children': 'other-children',
            'seasonal': 'other-seasonal',
            'baptism': 'other-baptism',
        }
        
        other_tag = OTHER_MAP.get(main_collection)
        if other_tag:
            subcollections.append(other_tag)
    
    return subcollections

def extract_special_tags(discount, is_new):
    """Extract special tags (offers, new arrivals)"""
    tags = []
    
    # Check for discount (OFFERS) - only if discount field has value
    if discount and discount.strip():
        tags.append('offers')
    
    # Check NEW flag
    if is_new and is_new.lower() == 'true':
        tags.append('new-arrivals')
    
    return tags

def build_final_tags(main_collection, subcollections, special_tags):
    """Build final tag list"""
    tags = []
    
    if main_collection:
        tags.append(main_collection)
    
    tags.extend(subcollections)
    tags.extend(special_tags)
    
    return list(set(tags))

# ============================================
# MAIN PARSER FOR HOMEGURU
# ============================================

def parse_homeguru_file(filepath):
    """Parse HomeGuru XML from local file"""
    print(f"📄 Reading local XML file: {filepath}")
    
    if not os.path.exists(filepath):
        print(f"❌ Error: File '{filepath}' not found!")
        print(f"💡 Please make sure the XML file is in the same folder as this script")
        return []
    
    try:
        # Parse XML from file
        tree = ET.parse(filepath)
        root = tree.getroot()
        
        products = []
        no_image_count = 0
        auto_description_count = 0
        offer_count = 0
        new_count = 0
        total_products = 0
        
        # Find all product elements
        for product in root.findall('.//product'):
            total_products += 1
            
            # Extract data from XML
            data = {}
            for child in product:
                tag_name = child.tag
                data[tag_name] = child.text if child.text else ''
            
            # Required fields
            title = clean_text(safe_get_text(data, 'name'))
            if not title:
                continue
            
            product_id = safe_get_text(data, 'id')
            sku = safe_get_text(data, 'product_sku') or product_id
            
            # Category & Season
            category = safe_get_text(data, 'category')
            season = safe_get_text(data, 'season')
            
            # Description (auto-generate if empty)
            description = generate_description_homeguru(data, title)
            if 'Χρώμα:' in description or 'Υλικό:' in description or description == f"<p>{title}</p>":
                auto_description_count += 1
            
# Prices - CORRECT LOGIC
            eshop_retail = safe_get_text(data, 'eshop_retail', '0')  # Main price
            retail_price = safe_get_text(data, 'retailprice')  # Compare price
            discount = safe_get_text(data, 'discount')  # Discount indicator
            
            # Use eshop_retail as main price
            price = eshop_retail if eshop_retail else safe_get_text(data, 'price', '0')
            
            # Use retailprice as compare price ONLY if discount has a value
            compare_price = ''
            if discount and discount.strip():
                compare_price = retail_price if retail_price else ''
            
            # Images
            image_url = safe_get_text(data, 'imageurl')
            all_images = []
            
            if image_url and image_url.startswith('http'):
                high_quality_url = get_higher_quality_url(image_url)
                all_images.append(high_quality_url)
            
            if not all_images and USE_PLACEHOLDER_FOR_MISSING_IMAGES:
                all_images = [PLACEHOLDER_IMAGE_URL]
                no_image_count += 1
            
            # Stock
            availability = safe_get_text(data, 'Availability')
            stock = '100' if availability == 'instock' else '0'
            
            # NEW flag
            is_new = safe_get_text(data, 'new')
            
            # Extract tags
            main_collection = extract_main_collection(category, title, season)
            if not main_collection:
                continue  # Skip products without valid collection
            
            subcollections = extract_subcollections(category, title, main_collection)
            special_tags = extract_special_tags(discount, is_new)
            final_tags = build_final_tags(main_collection, subcollections, special_tags)
            
            # Count special tags
            if 'offers' in special_tags:
                offer_count += 1
            if 'new-arrivals' in special_tags:
                new_count += 1
            
            # Build product dict
            product_dict = {
                'source': 'homeguru',
                'id': product_id,
                'sku': sku,
                'title': title,
                'description': description,
                'price': price.replace(',', '.'),
                'compare_price': compare_price.replace(',', '.') if compare_price else '',
                'main_collection': main_collection,
                'subcollections': ', '.join(subcollections),
                'tags': ', '.join(final_tags),
                'main_image': all_images[0] if all_images else '',
                'additional_images': '',
                'total_images': len(all_images),
                'stock': stock,
                'category_full': f"{season} > {category}",
                'weight_grams': 0,
                'vendor': 'HomeGuru',
            }
            
            products.append(product_dict)
        
        # Print statistics
        print(f"\n✅ HomeGuru: {len(products)} products parsed (from {total_products} total)")
        print(f"📝 Auto-generated descriptions: {auto_description_count}")
        print(f"🏷️  Products with OFFERS tag: {offer_count}")
        print(f"🆕 Products with NEW tag: {new_count}")
        if no_image_count > 0:
            print(f"📷 Products with placeholder: {no_image_count}")
        
        return products
        
    except ET.ParseError as e:
        print(f"❌ XML Parse Error: {e}")
        print(f"💡 Make sure the file is a valid XML file")
        return []
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return []

def remove_duplicates(products):
    """Remove duplicate products by SKU or Title"""
    seen_sku = set()
    seen_title = set()
    unique = []
    dups = 0
    
    for p in products:
        sku = p['sku']
        title = p['title'].lower()
        
        if sku and sku in seen_sku:
            dups += 1
            continue
        
        if not sku and title in seen_title:
            dups += 1
            continue
        
        if sku:
            seen_sku.add(sku)
        seen_title.add(title)
        unique.append(p)
    
    if dups > 0:
        print(f"⚠️  Removed {dups} duplicates")
    
    return unique

def generate_preview(products, filename='preview_report.txt', batch_number=None):
    """Generate preview report grouped by collections"""
    print(f"\n📋 Generating preview...")
    
    by_collection = defaultdict(lambda: defaultdict(list))
    
    for p in products:
        main = p['main_collection']
        subs = p['subcollections'].split(', ') if p['subcollections'] else ['NO_SUBCOLLECTION']
        for sub in subs:
            by_collection[main][sub].append(p)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        if batch_number:
            f.write(f"HOMEGURU - BATCH #{batch_number} PREVIEW\n")
        else:
            f.write("HOMEGURU - COMPLETE PREVIEW\n")
        f.write("="*80 + "\n")
        f.write(f"Total Products: {len(products)}\n")
        f.write("="*80 + "\n\n")
        
        for main in sorted(by_collection.keys()):
            f.write(f"\n{'='*80}\n")
            f.write(f"MAIN: {main.upper()}\n")
            f.write(f"{'='*80}\n")
            
            for sub in sorted(by_collection[main].keys()):
                prods = by_collection[main][sub]
                f.write(f"\n  Sub: {sub}\n")
                f.write(f"  Count: {len(prods)}\n")
                f.write(f"  {'-'*76}\n")
                
                for i, p in enumerate(prods[:5], 1):
                    f.write(f"    {i}. {p['title'][:60]}\n")
                    f.write(f"       Price: €{p['price']}")
                    if p['compare_price']:
                        f.write(f" (was €{p['compare_price']})")
                    f.write(f"\n")
                    f.write(f"       Tags: {p['tags']}\n")
                    f.write(f"       SKU: {p['sku']}\n")
                    f.write(f"       Description: {'✅' if p['description'] else '❌'}\n\n")
                
                if len(prods) > 5:
                    f.write(f"    ... +{len(prods)-5} more\n\n")
    
    print(f"✅ Preview: {filename}")

def export_csv(products, filename='shopify_homeguru.csv'):
    """Export products to Shopify CSV format"""
    if not products:
        print("❌ No products!")
        return
    
    print(f"\n💾 Exporting {len(products)} products...")
    
    headers = [
        'Handle', 'Title', 'Body (HTML)', 'Vendor', 'Type',
        'Tags', 'Published', 'Variant SKU', 'Variant Grams',
        'Variant Inventory Tracker', 'Variant Inventory Qty',
        'Variant Inventory Policy', 'Variant Fulfillment Service',
        'Variant Price', 'Variant Compare At Price',
        'Variant Requires Shipping', 'Variant Taxable',
        'Image Src', 'Image Position', 'Image Alt Text',
        'SEO Title', 'SEO Description', 'Status'
    ]
    
    rows = []
    products_with_offers = 0
    products_with_new = 0
    
    for p in products:
        # Generate handle from SKU
        handle = p['sku'] or p['id'] or p['title']
        handle = re.sub(r'[^a-z0-9-]', '-', handle.lower())[:100]
        handle = re.sub(r'-+', '-', handle).strip('-')
        
        # Count tags
        if 'offers' in p['tags']:
            products_with_offers += 1
        if 'new-arrivals' in p['tags']:
            products_with_new += 1
        
        # Main product row
        row = {
            'Handle': handle,
            'Title': p['title'],
            'Body (HTML)': p['description'],
            'Vendor': p['vendor'],
            'Type': p['main_collection'],
            'Tags': p['tags'],
            'Published': 'TRUE',
            'Variant SKU': p['sku'],
            'Variant Grams': p['weight_grams'],
            'Variant Inventory Tracker': 'shopify',
            'Variant Inventory Qty': p['stock'],
            'Variant Inventory Policy': 'deny',
            'Variant Fulfillment Service': 'manual',
            'Variant Price': p['price'],
            'Variant Compare At Price': p['compare_price'],
            'Variant Requires Shipping': 'TRUE',
            'Variant Taxable': 'TRUE',
            'Image Src': p['main_image'],
            'Image Position': '1',
            'Image Alt Text': p['title'][:100],
            'SEO Title': p['title'][:70],
            'SEO Description': (p['description'][:320] if p['description'] else p['title'][:320]),
            'Status': 'active',
        }
        rows.append(row)
    
    # Write CSV
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"✅ CSV: {filename}")
    print(f"🏷  Products with OFFERS tag: {products_with_offers}")
    print(f"🆕 Products with NEW tag: {products_with_new}")
    
    # Print statistics
    print("\n" + "="*60)
    print("📊 STATISTICS")
    print("="*60)
    
    main_counts = defaultdict(int)
    sub_counts = defaultdict(int)
    
    for p in products:
        main_counts[p['main_collection']] += 1
        if p['subcollections']:
            for sub in p['subcollections'].split(', '):
                sub_counts[sub] += 1
    
    print(f"\n📦 Total Products: {len(products)}\n")
    
    print("Main Collections:")
    for m, c in sorted(main_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {m:.<30} {c:>5}")
    
    print("\nTop 20 Subcollections:")
    for s, c in sorted(sub_counts.items(), key=lambda x: x[1], reverse=True)[:20]:
        print(f"  {s:.<30} {c:>5}")
    
    print("\n" + "="*60)

# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎯 HOMEGURU XML TO SHOPIFY IMPORTER")
    print("="*60)
    print(f"\n📦 Batch Size: {BATCH_SIZE} products per batch")
    print(f"🔢 Current Batch: #{BATCH_NUMBER}")
    print(f"\n✅ Features:")
    print(f"  ✅ Auto-generate descriptions from attributes")
    print(f"  ✅ Smart tag detection (10 main + 66 subcollections)")
    print(f"  ✅ NEW arrivals from <new> flag")
    print(f"  ✅ OFFERS from price comparison")
    print(f"  ✅ High-quality image extraction")
    print(f"  ✅ Greek language support")
    print(f"  ✅ SKU tracking")
    
    all_products = []
    
    print("\n🔍 PARSING HOMEGURU XML...")
    
    if USE_LOCAL_FILE:
        print(f"📂 Using LOCAL file: {LOCAL_XML_FILE}")
        all_products = parse_homeguru_file(LOCAL_XML_FILE)
    else:
        print(f"🌐 Using ONLINE file from Google Drive")
        print("⚠️  Note: Google Drive links may not work directly")
        print("💡 Tip: Set USE_LOCAL_FILE = True to use a local XML file instead")
    
    if all_products:
        print(f"\n📊 Total products fetched: {len(all_products)}")
        
        # Remove duplicates
        print("\n🔍 Removing duplicates...")
        all_products = remove_duplicates(all_products)
        
        # Calculate batch range
        start_idx = (BATCH_NUMBER - 1) * BATCH_SIZE
        end_idx = min(start_idx + BATCH_SIZE, len(all_products))
        
        # Check if batch number is valid
        if start_idx >= len(all_products):
            total_batches = (len(all_products) + BATCH_SIZE - 1) // BATCH_SIZE
            print(f"\n❌ ERROR: Batch #{BATCH_NUMBER} doesn't exist!")
            print(f"   Total products: {len(all_products)}")
            print(f"   Max batches: {total_batches}")
            print(f"\n💡 Set BATCH_NUMBER to a value between 1 and {total_batches}")
        else:
            # Extract current batch
            current_batch = all_products[start_idx:end_idx]
            
            total_batches = (len(all_products) + BATCH_SIZE - 1) // BATCH_SIZE
            
            print(f"\n" + "="*60)
            print(f"📦 BATCH #{BATCH_NUMBER}")
            print("="*60)
            print(f"Range: Products {start_idx + 1} to {end_idx}")
            print(f"Count: {len(current_batch)} products")
            print(f"Total Batches: {total_batches}")
            print(f"Progress: {end_idx}/{len(all_products)} ({end_idx*100//len(all_products)}%)")
            
            # Generate files for this batch
            preview_file = f'homeguru_preview_batch_{BATCH_NUMBER}.txt'
            csv_file = f'homeguru_shopify_batch_{BATCH_NUMBER}.csv'
            
            # Generate preview
            generate_preview(current_batch, preview_file, batch_number=BATCH_NUMBER)
            
            # Export CSV
            export_csv(current_batch, csv_file)
            
            print("\n" + "="*60)
            print("✅ BATCH COMPLETE!")
            print("="*60)
            print(f"\n📁 Files Generated:")
            print(f"  1. {csv_file} (Shopify import file)")
            print(f"  2. {preview_file} (Preview report)")
            
            print(f"\n📖 NEXT STEPS:")
            print(f"  1️⃣  Check preview file: {preview_file}")
            print(f"  2️⃣  Upload {csv_file} to Shopify")
            print(f"  3️⃣  Shopify will match by Handle (SKU)")
            print(f"      → Existing products = UPDATE")
            print(f"      → New products = CREATE")
            
            if end_idx < len(all_products):
                remaining = len(all_products) - end_idx
                remaining_batches = (remaining + BATCH_SIZE - 1) // BATCH_SIZE
                print(f"\n⏳ Remaining: {remaining} products in {remaining_batches} batches")
                print(f"  → Next batch: Set BATCH_NUMBER = {BATCH_NUMBER + 1}")
            else:
                print(f"\n🎉 All products processed!")
            
            print(f"\n✨ KEY FEATURES:")
            print(f"  ✅ Complete tag system (10 main + 66 subs)")
            print(f"  ✅ Auto descriptions from attributes")
            print(f"  ✅ Smart price comparison (offers)")
            print(f"  ✅ NEW flag detection")
            print(f"  ✅ Greek language support")
            print(f"  ✅ SKU-based matching")
            print(f"  ✅ High-quality images")
            
    else:
        print("\n❌ No products found!")
        print("\n💡 Possible issues:")
        print("  - Check that XML file exists in the same folder")
        print("  - Verify XML format is correct")
        print("  - Make sure LOCAL_XML_FILE name matches your file")