from .models import SiteInfo

def site_info(request):
    """Добавляет информацию о сайте во все шаблоны"""
    try:
        site_info = SiteInfo.objects.first()
        if not site_info:
            site_info = SiteInfo.objects.create()
    except:
        site_info = None
    
    return {
        'site_info': site_info
    } 