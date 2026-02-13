import requests
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
BATCH_NUMBER = 3

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

def generate_description_from_all_sources(data, title):
    """Generate description from ALL available sources in XML - SAFE VERSION"""
    desc_parts = []
    
    # 1. Try Content
    content = clean_text(safe_get_text(data, 'Content'))
    if content:
        return content
    
    # 2. Try Excerpt
    excerpt = clean_text(safe_get_text(data, 'Excerpt'))
    if excerpt:
        return excerpt
    
    # 3. Try PurchaseNote
    purchase_note = clean_text(safe_get_text(data, 'PurchaseNote'))
    if purchase_note:
        desc_parts.append(purchase_note)
    
    # 4. Build from attributes - SAFE
    tech_specs = safe_get_text(data, 'AttributeValuepa_technika_charaktiristika')
    if tech_specs:
        desc_parts.append(f"<strong>Τεχνικές Προδιαγραφές:</strong> {tech_specs}")
    
    dims = safe_get_text(data, 'AttributeValuepa_diastaseis')
    if dims:
        desc_parts.append(f"<strong>Διαστάσεις:</strong> {dims}")
    
    material = safe_get_text(data, 'AttributeValuepa_yliko_kataskevis')
    if material:
        desc_parts.append(f"<strong>Υλικό:</strong> {material}")
    
    color = safe_get_text(data, 'AttributeValuepa_chroma')
    if color:
        desc_parts.append(f"<strong>Χρώμα:</strong> {color}")
    
    # 5. If still empty, use title as description
    if not desc_parts:
        return f"<p>{title}</p>"
    
    return '<br><br>'.join(desc_parts)
def get_higher_quality_url(image_url):
    """
    Get FULL SIZE image instead of thumbnails
    WordPress stores: product-300x300.jpg, product-768x768.jpg, product.jpg
    We want: product.jpg (the biggest)
    """
    if not image_url:
        return image_url
    
    # Remove WordPress thumbnail sizes like -300x300, -150x150, etc
    patterns = [
        r'-\d+x\d+\.(jpg|jpeg|png|webp|gif)',  # -300x300.jpg
        r'_\d+x\d+\.(jpg|jpeg|png|webp|gif)',  # _300x300.jpg
    ]
    
    for pattern in patterns:
        # Replace "-300x300.jpg" with ".jpg"
        image_url = re.sub(pattern, r'.\1', image_url, flags=re.IGNORECASE)
    
    return image_url


def extract_all_images_from_xml(data):
    """
    Extract ALL images from XML product data + GET HIGH QUALITY VERSIONS
    Handles: ImageURL, ImageFeatured, ProductImageGallery, AttachmentURL
    """
    all_images = []
    seen_urls = set()
    
    # 1. Featured Image (highest priority)
    featured_img = safe_get_text(data, 'ImageFeatured')
    if featured_img and featured_img.startswith('http'):
        # Get full size version
        high_quality = get_higher_quality_url(featured_img)
        if high_quality not in seen_urls:
            all_images.append(high_quality)
            seen_urls.add(high_quality)
    
    # 2. ImageURL (may contain multiple images separated by |)
    image_urls = safe_get_text(data, 'ImageURL')
    if image_urls:
        for img in re.split(r'[|,;]', image_urls):
            img = img.strip()
            if img and img.startswith('http'):
                # Get full size version
                high_quality = get_higher_quality_url(img)
                if high_quality not in seen_urls:
                    all_images.append(high_quality)
                    seen_urls.add(high_quality)
    
    # 3. ProductImageGallery (contains image IDs)
    image_titles = safe_get_text(data, 'ImageTitle')
    if image_titles and '|' in image_titles:
        filenames = image_titles.split('|')
        base_url = "https://arlight.gr/wp-content/uploads/"
        
        # Try to extract year/month from existing URLs
        if all_images:
            first_url = all_images[0]
            match = re.search(r'uploads/(\d{4}/\d{2})/', first_url)
            if match:
                date_path = match.group(1)
                for filename in filenames:
                    filename = filename.strip()
                    if filename and filename not in [f.split('/')[-1] for f in all_images]:
                        constructed_url = f"{base_url}{date_path}/{filename}"
                        # Get full size version
                        high_quality = get_higher_quality_url(constructed_url)
                        if high_quality not in seen_urls:
                            all_images.append(high_quality)
                            seen_urls.add(high_quality)
    
    # 4. AttachmentURL (additional attachments)
    attachment_url = safe_get_text(data, 'AttachmentURL')
    if attachment_url and attachment_url.startswith('http'):
        # Get full size version
        high_quality = get_higher_quality_url(attachment_url)
        if high_quality not in seen_urls:
            all_images.append(high_quality)
            seen_urls.add(high_quality)

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
        return None
    
    first_cat = category_text.split('>')[0].strip().lower()
    full_text = (first_cat + ' ' + title.lower()).lower()
    
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
    """Extract subcollections with 'Other' fallback for unmatched products"""
    if not main_collection:
        return []
    
    text_to_check = (category_text + ' ' + title).lower()
    subcollections = []
    
    # PRIMARY subcollections
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
    
    # CROSS-CATEGORY tags
    is_children_light = any(keyword in text_to_check for keyword in [
        'παιδικο φωτιστικο', 'παιδικό φωτιστικό',
        'φωτιστικο παιδικο', 'φωτιστικό παιδικό',
        'kids light', 'children lamp', 'child light'
    ])
    
    if is_children_light:
        if main_collection == 'lighting-fixtures':
            if 'children-lights' not in subcollections:
                subcollections.append('children-lights')
        
        if main_collection == 'children':
            if 'children-lighting' not in subcollections:
                subcollections.append('children-lighting')
        
        if main_collection not in ['lighting-fixtures', 'children']:
            if 'children-lights' not in subcollections:
                subcollections.append('children-lights')
            if 'children-lighting' not in subcollections:
                subcollections.append('children-lighting')
    
    is_children_bed = any(keyword in text_to_check for keyword in [
        'παιδικο κρεβατι', 'παιδικό κρεβάτι',
        'κρεβατι παιδικο', 'κρεβάτι παιδικό',
        'kids bed', 'children bed', 'child bed'
    ])
    
    if is_children_bed:
        if 'beds' not in subcollections:
            subcollections.append('beds')
        if 'children-beds' not in subcollections:
            subcollections.append('children-beds')
    
    is_children_furniture = any(keyword in text_to_check for keyword in [
        'παιδικο επιπλο', 'παιδικό έπιπλο',
        'επιπλο παιδικο', 'έπιπλο παιδικό',
        'kids furniture', 'children furniture',
        'παιδικη καρεκλα', 'children chair'
    ]) and not is_children_bed and not is_children_light
    
    if is_children_furniture:
        if 'children-furniture' not in subcollections:
            subcollections.append('children-furniture')
    
    is_outdoor_keywords = any(keyword in text_to_check for keyword in [
        'εξωτερικου χωρου', 'εξωτερικου χώρου',
        'εξωτερικου', 'εξωτερικού',
        'κηπου', 'κήπου',
        'outdoor', 'garden', 'exterior',
        'κολονακι', 'κολονάκι',
        'χελωνα', 'χελώνα'
    ])
    
    is_lighting_keywords = any(keyword in text_to_check for keyword in [
        'φωτιστικο', 'φωτιστικό', 'φωτισμος', 'φωτισμός',
        'light', 'lighting', 'lamp', 'λαμπα', 'λάμπα'
    ])
    
    if is_outdoor_keywords and is_lighting_keywords:
        if 'outdoor-lights' not in subcollections:
            subcollections.append('outdoor-lights')
    
    is_furniture_keywords = any(keyword in text_to_check for keyword in [
        'επιπλο', 'έπιπλο', 'furniture',
        'καρεκλα', 'καρέκλα', 'chair',
        'τραπεζι', 'τραπέζι', 'table',
        'τραπεζακι', 'τραπεζάκι',
        'καναπες', 'καναπές', 'sofa',
        'σκαμπω', 'σκαμπώ', 'stool',
        'πολυθρονα', 'armchair',
        'catering', 'συνεδριου',
        'διπλωτη', 'folding'
    ])
    
    if is_outdoor_keywords and is_furniture_keywords:
        if 'outdoor-furniture' not in subcollections:
            subcollections.append('outdoor-furniture')
    
    is_hanger = any(keyword in text_to_check for keyword in [
        'κρεμαστρα', 'κρεμάστρα',
        'καλογερος', 'καλόγερος',
        'coat rack', 'coat hanger', 'hanger'
    ])
    
    if is_hanger:
        if main_collection == 'furniture' and 'hangers' not in subcollections:
            subcollections.append('hangers')
        elif main_collection == 'decoratives' and 'key-holders' not in subcollections:
            subcollections.append('key-holders')
    
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

def extract_special_tags(category_text, title, price, compare_price, product_date, attributes):
    """Extract special tags (offers, new arrivals) - ENHANCED & SAFE"""
    tags = []
    text_to_check = (category_text + ' ' + title).lower()
    
    # OFFERS - Check multiple sources
    # 1. Check category/title text
    for keyword in SPECIAL_TAGS['offers']:
        if keyword in text_to_check:
            tags.append('offers')
            break
    
    # 2. Check pa_se_prosfora attribute - SAFE VERSION
    if 'offers' not in tags:
        offer_attr = safe_get_text(attributes, 'pa_se_prosfora').upper()
        if offer_attr == 'OFFER':
            tags.append('offers')
    
    # 3. Check price discount
    if 'offers' not in tags:
        try:
            if compare_price and price:
                if float(compare_price) > float(price):
                    tags.append('offers')
        except:
            pass
    
    # NEW ARRIVALS - Check date
    if is_new_arrival(product_date):
        tags.append('new-arrivals')
    
    return tags

def build_final_tags(main_collection, subcollections, special_tags):
    """Build final tag list - ENGLISH ONLY"""
    tags = []
    
    if main_collection:
        tags.append(main_collection)
    
    tags.extend(subcollections)
    tags.extend(special_tags)
    
    return list(set(tags))

# ============================================
# PARSERS
# ============================================

def parse_arlight(url):
    print("📄 Fetching Arlight...")
    
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
        
        for post in root.findall('post'):
            data = {child.tag: child.text for child in post}
            
            # Skip hidden products
            if data.get('ProductVisibility') == 'hidden':
                continue
            
            title = clean_text(safe_get_text(data, 'Title'))
            if not title:
                continue
            
            category = clean_text(safe_get_text(data, 'Κατηγορίεςπροϊόντων'))
            
            # ENHANCED DESCRIPTION - Try ALL sources - SAFE VERSION
            description = generate_description_from_all_sources(data, title)
            if 'Technical Specifications' in description or description == f"<p>{title}</p>":
                auto_description_count += 1
            
            # ENHANCED PRICE LOGIC - SAFE
            price = clean_text(safe_get_text(data, 'Price', '0'))
            retail_price_vat = clean_text(safe_get_text(data, 'retail-price-with-vat'))
            regular_price = clean_text(safe_get_text(data, 'RegularPrice'))
            
            compare_price = ''
            try:
                if retail_price_vat and float(retail_price_vat) > float(price):
                    compare_price = retail_price_vat
                elif regular_price and float(regular_price) > float(price):
                    compare_price = regular_price
            except:
                pass
            
            # EXTRACT ALL IMAGES
            all_images = extract_all_images_from_xml(data)
            
            if not all_images and USE_PLACEHOLDER_FOR_MISSING_IMAGES:
                all_images = [PLACEHOLDER_IMAGE_URL]
                no_image_count += 1
            
            if len(all_images) > 1:
                multi_image_count += 1
            
            total_images += len(all_images)
            
            # Attributes for special tags - SAFE
            attributes = {
                'pa_se_prosfora': safe_get_text(data, 'AttributeValuepa_se_prosfora'),
            }
            
            # Extract tags
            main_collection = extract_main_collection(category, title)
            subcollections = extract_subcollections(category, title, main_collection)
            
            product_date = safe_get_text(data, 'Date')
            special_tags = extract_special_tags(category, title, price, compare_price, product_date, attributes)
            
            final_tags = build_final_tags(main_collection, subcollections, special_tags)
            
            if not main_collection:
                continue
            
            if 'offers' in special_tags:
                offer_count += 1
            if 'new-arrivals' in special_tags:
                new_count += 1
            
            # Weight - SAFE
            weight = safe_get_text(data, 'Weight', '0')
            try:
                weight_grams = int(float(weight) * 1000) if weight else 0
            except:
                weight_grams = 0
            
            product = {
                'source': 'arlight',
                'id': safe_get_text(data, 'ID'),
                'sku': clean_text(safe_get_text(data, 'Sku')),
                'title': title,
                'description': description,
                'price': price,
                'compare_price': compare_price,
                'main_collection': main_collection,
                'subcollections': ', '.join(subcollections),
                'tags': ', '.join(final_tags),
                'main_image': all_images[0] if all_images else '',
                'additional_images': '|'.join(all_images[1:]) if len(all_images) > 1 else '',
                'total_images': len(all_images),
                'stock': clean_text(safe_get_text(data, 'Stock', '0')),
                'category_full': category,
                'weight_grams': weight_grams,
                'vendor': 'Arlight',
            }
            
            products.append(product)
        
        print(f"✅ Arlight: {len(products)} products")
        print(f"🖼️  Total images found: {total_images}")
        print(f"📸 Products with multiple images: {multi_image_count}")
        print(f"📝 Auto-generated descriptions: {auto_description_count}")
        print(f"🏷️  Products with OFFERS tag: {offer_count}")
        print(f"🆕 Products with NEW tag: {new_count}")
        if no_image_count > 0:
            print(f"📷 Products with placeholder: {no_image_count}")
        
        return products
        
    except Exception as e:
        print(f"❌ Arlight Error: {e}")
        import traceback
        traceback.print_exc()
        return []

def parse_pakoworld(url):
    print("📄 Fetching Pakoworld...")
    
    try:
        response = requests.get(url, timeout=60)
        response.encoding = 'utf-8'
        root = ET.fromstring(response.content)
        
        products = []
        items = root.findall('.//product')
        
        no_image_count = 0
        multi_image_count = 0
        
        for item in items:
            data = {}
            
            for child in item:
                tag_name = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                
                if tag_name.lower() == 'images':
                    continue
                
                data[tag_name.lower()] = clean_text(child.text if child.text else '')
            
            title = data.get('name', '')
            if not title:
                continue
            
            category = data.get('category', '')
            description = data.get('description', '')
            price = data.get('weboffer_price_with_vat', '') or data.get('retail_price_with_vat', '')
            compare_price = ''
            
            # Images
            all_images = []
            
            main_img = data.get('main_image', '')
            if main_img and main_img.startswith('http'):
                all_images.append(main_img)
            
            images_element = item.find('images')
            if images_element is not None:
                for img_child in images_element.findall('image'):
                    img_url = clean_text(img_child.text if img_child.text else '')
                    if img_url and img_url.startswith('http') and img_url not in all_images:
                        all_images.append(img_url)
            
            if not all_images and USE_PLACEHOLDER_FOR_MISSING_IMAGES:
                all_images = [PLACEHOLDER_IMAGE_URL]
                no_image_count += 1
            
            if len(all_images) > 1:
                multi_image_count += 1
            
            # Extract tags
            main_collection = extract_main_collection(category, title)
            subcollections = extract_subcollections(category, title, main_collection)
            special_tags = extract_special_tags(category, title, price, compare_price, '', {})
            final_tags = build_final_tags(main_collection, subcollections, special_tags)
            
            if not main_collection:
                continue
            
            # Weight
            weight = data.get('weight', '0')
            try:
                weight_grams = int(float(weight) * 1000) if weight else 0
            except:
                weight_grams = 0
            
            product = {
                'source': 'pakoworld',
                'id': data.get('id', '') or data.get('model', ''),
                'sku': data.get('ean', ''),
                'title': title,
                'description': description,
                'price': price,
                'compare_price': compare_price,
                'main_collection': main_collection,
                'subcollections': ', '.join(subcollections),
                'tags': ', '.join(final_tags),
                'main_image': all_images[0] if all_images else '',
                'additional_images': '|'.join(all_images[1:]) if len(all_images) > 1 else '',
                'total_images': len(all_images),
                'stock': data.get('quantity', ''),
                'category_full': category,
                'weight_grams': weight_grams,
                'vendor': 'Pakoworld',
            }
            
            products.append(product)
        
        print(f"✅ Pakoworld: {len(products)} products")
        print(f"🖼️  Products with multiple images: {multi_image_count}")
        if no_image_count > 0:
            print(f"📷 Products with placeholder: {no_image_count}")
        
        return products
        
    except Exception as e:
        print(f"❌ Pakoworld Error: {e}")
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
            f.write(f"BATCH #{batch_number} PREVIEW - COMPLETE VERSION\n")
        else:
            f.write("ALL BATCHES PREVIEW - COMPLETE VERSION\n")
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
                    f.write(f"       Price: €{p['price']} {f'(was €{p['compare_price']})' if p['compare_price'] else ''}\n")
                    f.write(f"       Tags: {p['tags']}\n")
                    f.write(f"       Images: {p['total_images']}\n")
                    f.write(f"       Description: {'✅' if p['description'] else '❌'}\n\n")
                
                if len(prods) > 5:
                    f.write(f"    ... +{len(prods)-5} more\n\n")
    
    print(f"✅ Preview: {filename}")

def track_uploaded_batches(batch_number, products):
    """Track all uploaded batches in a cumulative file"""
    
    tracking_file = 'preview_all_batches.txt'
    
    existing_content = ""
    if os.path.exists(tracking_file):
        with open(tracking_file, 'r', encoding='utf-8') as f:
            existing_content = f.read()
    
    with open(tracking_file, 'a', encoding='utf-8') as f:
        if not existing_content:
            f.write("="*80 + "\n")
            f.write("ALL UPLOADED BATCHES TRACKING\n")
            f.write("="*80 + "\n\n")
        
        f.write(f"\n{'='*80}\n")
        f.write(f"BATCH #{batch_number} - {len(products)} PRODUCTS\n")
        f.write(f"{'='*80}\n")
        
        by_main = defaultdict(list)
        for p in products:
            by_main[p['main_collection']].append(p)
        
        for main in sorted(by_main.keys()):
            prods = by_main[main]
            f.write(f"\n  {main}: {len(prods)} products\n")
            
            for i, p in enumerate(prods[:3], 1):
                f.write(f"    - {p['title'][:70]}\n")
            
            if len(prods) > 3:
                f.write(f"    ... +{len(prods)-3} more\n")
        
        f.write("\n")
    
    print(f"✅ Batch tracking updated: {tracking_file}")

def update_descriptions_only(products, filename='update_descriptions.csv'):
    """Update ONLY descriptions without touching other data - SAFE METHOD"""
    if not products:
        print("❌ No products!")
        return
    
    print(f"\n💾 Preparing description updates for {len(products)} products...")
    
    headers = ['Handle', 'Body (HTML)']
    
    rows = []
    for p in products:
        handle = p['sku'] or p['id'] or p['title']
        handle = re.sub(r'[^a-z0-9-]', '-', handle.lower())[:100]
        handle = re.sub(r'-+', '-', handle).strip('-')
        
        description = p['description'][:5000] if p['description'] else ''
        
        rows.append({
            'Handle': handle,
            'Body (HTML)': description
        })
    
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"✅ Update file created: {filename}")
    print(f"📝 {len(rows)} descriptions ready to update")

def export_csv(products, filename='shopify_products.csv'):
    """Export products to Shopify CSV format with ALL images"""
    if not products:
        print("❌ No products!")
        return
    
    print(f"\n💾 Exporting {len(products)}...")
    
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
    products_with_multiple_images = 0
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
        
        if len(all_product_images) > 1:
            products_with_multiple_images += 1
        
        # Count tags
        if 'offers' in p['tags']:
            products_with_offers += 1
        if 'new-arrivals' in p['tags']:
            products_with_new += 1
    
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
    print(f"📸 Total images exported: {total_images_exported}")
    print(f"🖼  Products with multiple images: {products_with_multiple_images}/{len(products)}")
    print(f"🏷  Products with OFFERS tag: {products_with_offers}")
    print(f"🆕 Products with NEW tag: {products_with_new}")
    
    # Stats
    print("\n" + "="*60)
    print("📊 STATS")
    print("="*60)
    
    main_counts = defaultdict(int)
    sub_counts = defaultdict(int)
    image_stats = defaultdict(int)
    
    for p in products:
        main_counts[p['main_collection']] += 1
        if p['subcollections']:
            for sub in p['subcollections'].split(', '):
                sub_counts[sub] += 1
                
        img_count = p['total_images']
        if img_count == 0:
            image_stats['No Images'] += 1
        elif img_count == 1:
            image_stats['1 Image'] += 1
        elif img_count <= 3:
            image_stats['2-3 Images'] += 1
        elif img_count <= 5:
            image_stats['4-5 Images'] += 1
        else:
            image_stats['6+ Images'] += 1
    
    print(f"\n📦 Total Products: {len(products)}")
    print(f"📸 Total Image Rows in CSV: {len(rows)}")
    print(f"🖼  Average images per product: {total_images_exported/len(products):.1f}\n")
    
    print("Main Collections:")
    for m, c in sorted(main_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {m:.<30} {c:>5}")
    
    print("\nTop 20 Subcollections:")
    for s, c in sorted(sub_counts.items(), key=lambda x: x[1], reverse=True)[:20]:
        print(f"  {s:.<30} {c:>5}")
    
    print("\n📸 Image Statistics:")
    for stat, count in sorted(image_stats.items()):
        print(f"  {stat:.<30} {count:>5}")
    
    if image_stats.get('No Images', 0) > 0:
        print(f"\n📷 Note: {image_stats['No Images']} products using placeholder images")
    
    print("\n" + "="*60)

# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎯 SHOPIFY IMPORTER - COMPLETE VERSION WITH ALL TAGS")
    print("="*60)
    print(f"\n📦 Batch Size: {BATCH_SIZE} products per batch")
    print(f"🔢 Current Batch: #{BATCH_NUMBER}")
    print(f"🆕 NEW tag for products added in last {NEW_ARRIVAL_DAYS} days")
    print(f"\n✅ ALL XML data will be imported")
    print(f"✅ ALL images will be extracted")
    print(f"✅ ALL tags & collections properly mapped")
    print(f"✅ Descriptions fallback to title if empty")
    print(f"✅ Safe for OVERRIDE operations")
    
    arlight_url = "https://arlight.gr/wp-load.php?security_key=e5a0faf3ffa1aabd&export_id=1&action=get_data"
    pakoworld_url = "https://www.pakoworld.com/?route=extension/feed/csxml_feed&token=MTYyNzVMUDI0MQ==&lang=el"
    
    all_products = []
    
    print("\n🔍 SOURCE 1: ARLIGHT")
    all_products.extend(parse_arlight(arlight_url))
    
    print("\n🔍 SOURCE 2: PAKOWORLD")
    all_products.extend(parse_pakoworld(pakoworld_url))
    
    print("\n🔍 Removing duplicates...")
    all_products = remove_duplicates(all_products)
    
    if all_products:
        print(f"\n📊 Total products fetched: {len(all_products)}")
        
        # Calculate batch range
        start_idx = (BATCH_NUMBER - 1) * BATCH_SIZE
        end_idx = min(start_idx + BATCH_SIZE, len(all_products))
        
        # Check if batch number is valid
        if start_idx >= len(all_products):
            print(f"\n❌ ERROR: Batch #{BATCH_NUMBER} doesn't exist!")
            print(f"   Total products: {len(all_products)}")
            print(f"   Max batches: {(len(all_products) + BATCH_SIZE - 1) // BATCH_SIZE}")
            print(f"\n💡 Set BATCH_NUMBER to a value between 1 and {(len(all_products) + BATCH_SIZE - 1) // BATCH_SIZE}")
        else:
            # Extract current batch
            current_batch = all_products[start_idx:end_idx]
            
            print(f"\n" + "="*60)
            print(f"📦 BATCH #{BATCH_NUMBER}")
            print("="*60)
            print(f"Range: Products {start_idx + 1} to {end_idx}")
            print(f"Count: {len(current_batch)} products")
            print(f"Total Batches: {(len(all_products) + BATCH_SIZE - 1) // BATCH_SIZE}")
            print(f"Progress: {end_idx}/{len(all_products)} ({end_idx*100//len(all_products)}%)")
            
            # Generate files for this batch
            preview_file = f'preview_batch_{BATCH_NUMBER}.txt'
            csv_file = f'shopify_batch_{BATCH_NUMBER}.csv'
            update_file = f'update_descriptions_batch_{BATCH_NUMBER}.csv'
            
            # 1. Preview for CURRENT batch only
            generate_preview(current_batch, preview_file, batch_number=BATCH_NUMBER)
            
            # 2. Track in ALL batches file
            track_uploaded_batches(BATCH_NUMBER, current_batch)
            
            # 3. Export FULL CSV 
            export_csv(current_batch, csv_file)
            
            # 4. Export UPDATE CSV 
            update_descriptions_only(current_batch, update_file)
            
            print("\n" + "="*60)
            print("✅ BATCH COMPLETE - FULL VERSION WITH ALL TAGS!")
            print("="*60)
            print(f"\n📁 Files Generated:")
            print(f"  1. {csv_file} (FULL import for NEW products)")
            print(f"  2. {update_file} (SAFE update for EXISTING products)")
            print(f"  3. {preview_file} (Current batch preview)")
            print(f"  4. preview_all_batches.txt (All batches tracking)")
            
            print(f"\n✨ FEATURES IN THIS VERSION:")
            print(f"  ✅ Complete tag mappings (10 main + 66 subcollections)")
            print(f"  ✅ Auto-generated descriptions from attributes")
            print(f"  ✅ OFFER detection (category/attribute/price)")
            print(f"  ✅ NEW arrivals (last {NEW_ARRIVAL_DAYS} days)")
            print(f"  ✅ Enhanced image extraction")
            print(f"  ✅ Correct compare price logic")
            print(f"  ✅ Safe for override operations")
            
            print(f"\n📖 NEXT STEPS:")
            print(f"  1️⃣  Check preview file: {preview_file}")
            print(f"  2️⃣  For OVERRIDE (update existing):")
            print(f"      → Upload {csv_file} to Shopify")
            print(f"      → Shopify will update existing products by Handle (SKU)")
            print(f"  3️⃣  For NEW products only:")
            print(f"      → Same file: {csv_file}")
            print(f"  4️⃣  For descriptions only update:")
            print(f"      → Upload {update_file}")
            print(f"  5️⃣  Next batch: Set BATCH_NUMBER = {BATCH_NUMBER + 1}")
            
            print(f"\n⏳ Remaining: {len(all_products) - end_idx} products in {((len(all_products) - end_idx) + BATCH_SIZE - 1) // BATCH_SIZE} batches")
            
            print(f"\n⚠️  OVERRIDE SAFETY:")
            print(f"  ✅ Shopify matches products by Handle (SKU)")
            print(f"  ✅ Existing products will be UPDATED, not duplicated")
            print(f"  ✅ New products will be ADDED")
            print(f"  ✅ All data (images, descriptions, tags) will be refreshed")
            
    else:
        print("\n❌ No products!")