import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import platform
from kivy.clock import Clock

class TotemWebWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(TotemWebWidget, self).__init__(**kwargs)
        
        # Link do vídeo ou da página do seu totem que vai rodar em loop
        # Para testar agora, usei um link de vídeo direto de alta velocidade
        self.video_url = "https://static.videezy.com/system/resources/previews/000/045/486/original/water-01.mp4"
        
        if platform == 'android':
            # Chama o navegador nativo do Android para rodar o vídeo dentro do app
            from android.runnable import run_on_ui_thread
            Clock.schedule_once(self.init_android_webview, 1.0)
        else:
            print(f"💻 Ambiente de testes no Windows. Abrindo link: {self.video_url}")

    @run_on_ui_thread
    def init_android_webview(self, dt):
        """Inicializa o WebView do Android usando o motor do Chrome nativo da TV Box"""
        try:
            from jnius import autoclass
            
            # Puxa as ferramentas nativas do sistema Android
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            WebView = autoclass('android.webkit.WebView')
            WebViewClient = autoclass('android.webkit.WebViewClient')
            WebSettings = autoclass('android.webkit.WebSettings')
            
            activity = PythonActivity.mActivity
            webview = WebView(activity)
            
            # Configura o navegador interno para rodar vídeos em tela cheia e dar autoplay
            settings = webview.getSettings()
            settings.setJavaScriptEnabled(True)
            settings.setMediaPlaybackRequiresUserGesture(False) # Permite dar Play automático!
            settings.setDomStorageEnabled(True)
            
            webview.setWebViewClient(WebViewClient())
            
            # Adiciona o navegador ocupando a tela inteira da TV Box
            activity.setContentView(webview)
            
            # Carrega o vídeo direto
            webview.loadUrl(self.video_url)
            print("🚀 WebView Nativo iniciado com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao iniciar o WebView: {e}")

class TotemMidiaApp(App):
    def build(self):
        return TotemWebWidget()

if __name__ == '__main__':
    TotemMidiaApp().run()

