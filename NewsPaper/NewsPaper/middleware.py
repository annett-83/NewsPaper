from django.conf import settings

class MobileTemplatesMiddleware:
    def __init__(self, get_response): # Scheinbar braucht die middleware IMMER einen Konstruktor
        self.get_response = get_response

    def __call__(self, request):
        # wenn ein request kommt, wird geguckt welchen "geschmack" er hat
        # kommt er von einem Mobilgerät, oder nicht
        # je nachdem wird die Variable umgebogen, die sagt, welche Templates genommen werden sollen
        # settings.TEMPLATE_DIRS <-- da steckt der Pfad drin
        # settings.MOBILE_TEMPLATE_DIRS  <-- Pfad zu den Mobil-templates
        # settings.DESKTOP_TEMPLATE_DIRS  <-- Pfad zu den Desktop-templates
        user_agent = request.META['HTTP_USER_AGENT'] # In der Variable Request gibt es einen Eintrag zu dem Browser, der die Seite aufgerufen hat.
        #Die gängigsten Desktop-Browser
        if user_agent=='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.39':
            # kommt NICHT von einem Mobilgerät
            settings.TEMPLATE_DIRS = settings.DESKTOP_TEMPLATE_DIRS
        else:
            # kommt von einem Mobilgerät
            settings.TEMPLATE_DIRS = settings.MOBILE_TEMPLATE_DIRS

        response = self.get_response(request)

        # код, выполняемый после формирования запроса (или нижнего слоя)

        return response

