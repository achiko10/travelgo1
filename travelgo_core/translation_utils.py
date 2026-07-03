def get_language(request):
    """
    ადგენს მოთხოვნილი ენის კოდს (ka ან en)
    """
    if not request:
        return 'ka'
    
    # 1. URL Query Parameter (?lang=en)
    lang = request.query_params.get('lang')
    if lang in ['en', 'ka']:
        return lang
    
    # 2. User preferred language in DB
    if request.user and request.user.is_authenticated:
        preferred = getattr(request.user, 'preferred_language', None)
        if preferred in ['en', 'ka']:
            return preferred

    # 3. Accept-Language Header
    accept_lang = request.headers.get('Accept-Language', '')
    if 'en' in accept_lang.lower():
        return 'en'
        
    return 'ka'


def get_translated(obj, field_name, request):
    """
    აბრუნებს თარგმნილ ველს ობიექტიდან.
    თუ ენა არის 'en', აბრუნებს field_name_en-ს (თუ არსებობს და შევსებულია),
    სხვა შემთხვევაში აბრუნებს პირდაპირ field_name-ს (ქართულს).
    """
    lang = get_language(request)
    
    if lang == 'en':
        en_field = f"{field_name}_en"
        if hasattr(obj, en_field):
            val = getattr(obj, en_field)
            if val: # თუ შევსებულია
                return val
                
    return getattr(obj, field_name, '')
