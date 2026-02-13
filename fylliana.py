import requests
import xml.etree.ElementTree as ET
import csv
import re
from collections import defaultdict
from datetime import datetime, timedelta

# ============================================
# CONFIGURATION
# ============================================

BATCH_SIZE = 2000
BATCH_NUMBER = 3

# FYLLIANA XML URL
FYLLIANA_URL = "https://www.fylliana.gr/datafeed/133629/5wJRcoVlEQnbZNiPJR8s3yECEx0QbDyj"

# IMAGE SETTINGS
USE_PLACEHOLDER_FOR_MISSING_IMAGES = True
PLACEHOLDER_IMAGE_URL = "https://via.placeholder.com/600x600.png?text=No+Image+Available"

# NEW ARRIVALS SETTING
NEW_ARRIVAL_DAYS = 30

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
# LIGHTING FIXTURES Subcollections (11/11) ✅
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
# DECORATIVES Subcollections (20/20) ✅ COMPLETE
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
        'general decorative', 'misc decorative'
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
# FURNITURE Subcollections (21/21) ✅ COMPLETE
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
# WHITE GOODS Subcollections (4/4) ✅ (TEXTILES)
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
# CHILDREN Subcollections (3/3) ✅
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
# HOUSEHOLD Subcollections (3/3) ✅
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
# SEASONAL Subcollections (4/4) ✅
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
# BAPTISM Subcollections (2/2) ✅
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
    """Safely get text value from data dict"""
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

def generate_description_fylliana(data, title):
    """Generate description from available sources"""
    # 1. Try existing description
    desc = clean_text(safe_get_text(data, 'description'))
    if desc and len(desc) > 10:
        return desc
    
    # 2. Try short description
    short_desc = clean_text(safe_get_text(data, 'description_short'))
    if short_desc and len(short_desc) > 10:
        return short_desc
    
    # 3. Build from Filters (Χρώμα, Υλικό, etc.)
    desc_parts = []
    
    # Extract color and material from Filters
    filters = data.get('filters', [])
    colors = []
    materials = []
    
    for f in filters:
        group = f.get('group', '').lower()
        value = f.get('value', '')
        
        if 'χρώμα' in group or 'color' in group:
            if value:
                colors.append(value)
        elif 'υλικό' in group or 'material' in group or 'υλικο' in group:
            if value:
                materials.append(value)
    
    if colors:
        desc_parts.append(f"<strong>Χρώμα:</strong> {', '.join(colors)}")
    
    if materials:
        desc_parts.append(f"<strong>Υλικό:</strong> {', '.join(materials)}")
    
    # Dimensions
    dimensions = safe_get_text(data, 'dimensions')
    if dimensions:
        desc_parts.append(f"<strong>Διαστάσεις:</strong> {dimensions}")
    
    if desc_parts:
        return '<br><br>'.join(desc_parts)
    
    # 4. Last resort: use title
    return f"<p>{title}</p>"

def extract_all_images_fylliana(data):
    """Extract ALL images from Fylliana XML"""
    all_images = []
    seen_urls = set()
    
    # 1. Main image
    main_img = safe_get_text(data, 'image')
    if main_img and main_img.startswith('http'):
        if main_img not in seen_urls:
            all_images.append(main_img)
            seen_urls.add(main_img)
    
    # 2. Additional images
    additional_imgs = data.get('additional_images', [])
    for img in additional_imgs:
        img = img.strip()
        if img and img.startswith('http'):
            if img not in seen_urls:
                all_images.append(img)
                seen_urls.add(img)
    
    return all_images

def is_new_arrival(date_str):
    """Check if product is NEW (added in last X days)"""
    if not date_str:
        return False
    
    try:
        product_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        cutoff_date = datetime.now() - timedelta(days=NEW_ARRIVAL_DAYS)
        return product_date >= cutoff_date
    except:
        return False

def extract_main_collection(category_text, title):
    """Extract main collection from category/title"""
    if not category_text:
        return 'household'  # Default fallback
    
    # Use MAIN_COLLECTIONS
    MAIN_COLLECTIONS = {
        'φωτιστικα': 'lighting-fixtures', 'φωτιστικά': 'lighting-fixtures',
        'φωτισμος': 'lighting-fixtures', 'φωτισμός': 'lighting-fixtures',
        'lighting': 'lighting-fixtures', 'light': 'lighting-fixtures',
        'διακοσμητικα': 'decoratives', 'διακοσμητικά': 'decoratives',
        'διακοσμηση': 'decoratives', 'διακόσμηση': 'decoratives',
        'decoratives': 'decoratives', 'decorative': 'decoratives', 'decor': 'decoratives',
        'επιπλα': 'furniture', 'έπιπλα': 'furniture', 'επιπλο': 'furniture', 'furniture': 'furniture',
        'οικιακα': 'household', 'οικιακά': 'household', 'household': 'household',
        'εποχιακα': 'seasonal', 'εποχιακά': 'seasonal', 'seasonal': 'seasonal',
        'λευκα ειδη': 'white-goods', 'λευκά είδη': 'white-goods', 'white goods': 'white-goods', 'textiles': 'white-goods',
        'παιδικα': 'children', 'παιδικά': 'children', 'παιδικο': 'children', 'children': 'children', 'kids': 'children',
        'βαπτιση': 'baptism', 'βάπτιση': 'baptism', 'baptism': 'baptism',
    }
    
    full_text = f"{category_text} {title}".lower()
    
    matches = []
    for keyword, tag in MAIN_COLLECTIONS.items():
        if keyword in full_text:
            matches.append((tag, len(keyword)))
    
    if matches:
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches[0][0]
    
    # FALLBACK: If no collection found, use household as default
    return 'household'
def find_best_subcollection(text_to_check, subcollection_dict):
    """Find BEST matching subcollection"""
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
    """Extract subcollections"""
    if not main_collection:
        return []
    
    text_to_check = f"{category_text} {title}".lower()
    subcollections = []
    
    # ✅ استخدم الـ Global Dictionaries الكاملة
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
    
    # ✅ "OTHER" FALLBACK - لو مالقاش subcollection
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

def extract_special_tags(category_text, title, price_ind, price_special, created_at):
    """Extract special tags (offers, new arrivals)"""
    tags = []
    
    # OFFERS - Check if price_special < price_ind
    try:
        if price_ind and price_special:
            if float(price_special) < float(price_ind):
                tags.append('offers')
    except:
        pass
    
    # NEW ARRIVALS - Check date OR title/category
    text_to_check = f"{category_text} {title}".lower()
    
    # Check for "new" in text
    if any(keyword in text_to_check for keyword in ['νεο', 'νέο', 'new']):
        tags.append('new-arrivals')
    
    # Check date (last 30 days)
    if is_new_arrival(created_at):
        if 'new-arrivals' not in tags:
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
# MAIN PARSER FOR FYLLIANA
# ============================================

def parse_fylliana(url):
    """Parse Fylliana XML"""
    print("📄 Fetching Fylliana...")
    
    try:
        response = requests.get(url, timeout=60)
        response.encoding = 'utf-8'
        root = ET.fromstring(response.content)
        
        products = []
        no_image_count = 0
        multi_image_count = 0
        auto_description_count = 0
        offer_count = 0
        new_count = 0
        total_images = 0
        
        total_products_found = 0
        skipped_no_title = 0
        skipped_no_collection = 0
        
        for product in root.findall('.//product'):
            total_products_found += 1
            data = {}
            
            # Extract basic fields
            for child in product:
                tag_name = child.tag
                if tag_name == 'additional_image':
                    if 'additional_images' not in data:
                        data['additional_images'] = []
                    if child.text:
                        data['additional_images'].append(child.text)
                elif tag_name == 'Filters':
                    data['filters'] = []
                    for filter_elem in child.findall('filter'):
                        filter_data = {}
                        group_elem = filter_elem.find('group')
                        value_elem = filter_elem.find('value')
                        if group_elem is not None:
                            filter_data['group'] = group_elem.text or ''
                        if value_elem is not None:
                            filter_data['value'] = value_elem.text or ''
                        data['filters'].append(filter_data)
                else:
                    data[tag_name] = child.text if child.text else ''
            
            # Required fields
            title = clean_text(safe_get_text(data, 'name'))
            if not title:
                skipped_no_title += 1
                continue
            
            product_id = safe_get_text(data, 'id')
            sku = safe_get_text(data, 'sku') or product_id
            
            # Category
            category_name = safe_get_text(data, 'category_name')
            category_path = safe_get_text(data, 'category_path')
            category_full = f"{category_path} > {category_name}" if category_path else category_name
            
            # Description
            description = generate_description_fylliana(data, title)
            if 'Χρώμα:' in description or 'Υλικό:' in description or description == f"<p>{title}</p>":
                auto_description_count += 1
            
            # Prices
            price_ind = safe_get_text(data, 'price_ind', '0')
            price_special = safe_get_text(data, 'price_ind_special', '0')
            
            price = price_special if price_special else price_ind
            compare_price = ''
            
            # If price_special < price_ind → OFFER
            try:
                if float(price_special) < float(price_ind):
                    compare_price = price_ind
            except:
                pass
            
            # Images
            all_images = extract_all_images_fylliana(data)
            
            if not all_images and USE_PLACEHOLDER_FOR_MISSING_IMAGES:
                all_images = [PLACEHOLDER_IMAGE_URL]
                no_image_count += 1
            
            if len(all_images) > 1:
                multi_image_count += 1
            
            total_images += len(all_images)
            
            # Stock
            stock_qty = safe_get_text(data, 'stock_qty', '0')
            
            # Created date
            created_at = safe_get_text(data, 'created_at')
            
            # Extract tags
            main_collection = extract_main_collection(category_full, title)
            if not main_collection:
                # DEBUG: Print first 5 products without collection
                if skipped_no_collection < 5:
                    print(f"\n⚠️  Skipped (no collection): {title[:50]}")
                    print(f"    Category: {category_full}")
                skipped_no_collection += 1
                continue
            
            subcollections = extract_subcollections(category_full, title, main_collection)
            special_tags = extract_special_tags(category_full, title, price_ind, price_special, created_at)
            final_tags = build_final_tags(main_collection, subcollections, special_tags)
            
            if 'offers' in special_tags:
                offer_count += 1
            if 'new-arrivals' in special_tags:
                new_count += 1
            
            # Weight
            weight = safe_get_text(data, 'weight', '0')
            try:
                weight_grams = int(float(weight) * 1000) if weight else 0
            except:
                weight_grams = 0
            
            product_dict = {
                'source': 'fylliana',
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
                'additional_images': '|'.join(all_images[1:]) if len(all_images) > 1 else '',
                'total_images': len(all_images),
                'stock': stock_qty,
                'category_full': category_full,
                'weight_grams': weight_grams,
                'vendor': 'Fylliana',
            }
            
            products.append(product_dict)
        
        print(f"✅ Fylliana: {len(products)} products")
        print(f"📦 Total products in XML: {total_products_found}")
        print(f"⏭️  Skipped (no title): {skipped_no_title}")
        print(f"⏭️  Skipped (no collection): {skipped_no_collection}")
        print(f"🖼️  Total images: {total_images}")
        print(f"📸 Multi-image products: {multi_image_count}")
        print(f"📝 Auto-generated descriptions: {auto_description_count}")
        print(f"🏷️  Products with OFFERS: {offer_count}")
        print(f"🆕 Products with NEW tag: {new_count}")
        if no_image_count > 0:
            print(f"📷 Placeholder images: {no_image_count}")
        
        return products
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return []

def remove_duplicates(products):
    """Remove duplicates by SKU or Title"""
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

def generate_preview(products, filename='preview_fylliana.txt', batch_number=None):
    """Generate preview report"""
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
            f.write(f"FYLLIANA - BATCH #{batch_number} PREVIEW\n")
        else:
            f.write("FYLLIANA - COMPLETE PREVIEW\n")
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
                    f.write(f"       Images: {p['total_images']}\n\n")
                
                if len(prods) > 5:
                    f.write(f"    ... +{len(prods)-5} more\n\n")
    
    print(f"✅ Preview: {filename}")

def export_csv(products, filename='shopify_fylliana.csv'):
    """Export to Shopify CSV"""
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
    total_images_exported = 0
    products_with_offers = 0
    products_with_new = 0
    
    for p in products:
        handle = p['sku'] or p['id'] or p['title']
        handle = re.sub(r'[^a-z0-9-]', '-', handle.lower())[:100]
        handle = re.sub(r'-+', '-', handle).strip('-')
        
        all_product_images = []
        
        if p['main_image']:
            all_product_images.append(p['main_image'])
        
        if p['additional_images']:
            for img in p['additional_images'].split('|'):
                img = img.strip()
                if img:
                    all_product_images.append(img)
        
        if not all_product_images:
            all_product_images = [PLACEHOLDER_IMAGE_URL]
        
        if 'offers' in p['tags']:
            products_with_offers += 1
        if 'new-arrivals' in p['tags']:
            products_with_new += 1
        
        # First row with all product data
        first_row = {
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
            'Image Src': all_product_images[0],
            'Image Position': '1',
            'Image Alt Text': p['title'][:100],
            'SEO Title': p['title'][:70],
            'SEO Description': (p['description'][:320] if p['description'] else p['title'][:320]),
            'Status': 'active',
        }
        rows.append(first_row)
        total_images_exported += 1
        
        # Additional image rows
        for img_index in range(1, len(all_product_images)):
            img_row = {k: '' for k in headers}
            img_row['Handle'] = handle
            img_row['Image Src'] = all_product_images[img_index]
            img_row['Image Position'] = str(img_index + 1)
            img_row['Image Alt Text'] = p['title'][:100]
            rows.append(img_row)
            total_images_exported += 1
    
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"✅ CSV: {filename}")
    print(f"📸 Total images: {total_images_exported}")
    print(f"🏷  OFFERS: {products_with_offers}")
    print(f"🆕 NEW: {products_with_new}")
    
    # Stats
    print("\n" + "="*60)
    print("📊 STATISTICS")
    print("="*60)
    
    main_counts = defaultdict(int)
    for p in products:
        main_counts[p['main_collection']] += 1
    
    print(f"\n📦 Total: {len(products)}\n")
    print("Main Collections:")
    for m, c in sorted(main_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {m:.<30} {c:>5}")
    print("\n" + "="*60)
# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎯 FYLLIANA XML TO SHOPIFY IMPORTER")
    print("="*60)
    print(f"\n📦 Batch Size: {BATCH_SIZE}")
    print(f"🔢 Current Batch: #{BATCH_NUMBER}")
    print(f"\n✅ Features:")
    print(f"  ✅ Same tags as Arlight/Pakoworld")
    print(f"  ✅ All images extracted")
    print(f"  ✅ Auto-generate descriptions")
    print(f"  ✅ OFFERS (price_ind_special < price_ind)")
    print(f"  ✅ NEW (last 30 days OR 'new' in text)")
    
    all_products = parse_fylliana(FYLLIANA_URL)
    
    if all_products:
        print(f"\n📊 Total products: {len(all_products)}")
        
        # Remove duplicates
        print("\n🔍 Removing duplicates...")
        all_products = remove_duplicates(all_products)
        
        # Calculate batch
        start_idx = (BATCH_NUMBER - 1) * BATCH_SIZE
        end_idx = min(start_idx + BATCH_SIZE, len(all_products))
        
        if start_idx >= len(all_products):
            total_batches = (len(all_products) + BATCH_SIZE - 1) // BATCH_SIZE
            print(f"\n❌ ERROR: Batch #{BATCH_NUMBER} doesn't exist!")
            print(f"   Max batches: {total_batches}")
        else:
            current_batch = all_products[start_idx:end_idx]
            
            total_batches = (len(all_products) + BATCH_SIZE - 1) // BATCH_SIZE
            
            print(f"\n" + "="*60)
            print(f"📦 BATCH #{BATCH_NUMBER}")
            print("="*60)
            print(f"Range: {start_idx + 1} to {end_idx}")
            print(f"Count: {len(current_batch)}")
            print(f"Total Batches: {total_batches}")
            print(f"Progress: {end_idx}/{len(all_products)} ({end_idx*100//len(all_products)}%)")
            
            # Generate files for this batch
            preview_file = f'fylliana_preview_batch_{BATCH_NUMBER}.txt'
            csv_file = f'fylliana_shopify_batch_{BATCH_NUMBER}.csv'
            
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
            print(f"  ✅ Same tag system as Arlight/Pakoworld")
            print(f"  ✅ All images extracted (main + additional)")
            print(f"  ✅ Auto descriptions from attributes")
            print(f"  ✅ OFFERS (price_ind_special < price_ind)")
            print(f"  ✅ NEW (date OR keyword)")
            print(f"  ✅ SKU-based matching")
            
    else:
        print("\n❌ No products found!")
        print("\n💡 Possible issues:")
        print("  - Check internet connection")
        print("  - Verify XML URL is accessible")
        print("  - Check XML format")