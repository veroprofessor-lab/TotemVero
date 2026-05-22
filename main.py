import os
import sys
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import Color, Line
from kivy.utils import platform

class TotemPlayerWidget(Widget):
    def __init__(self, **kwargs):
        super(TotemPlayerWidget, self).__init__(**kwargs)
        
        # 📂 DEFINE A PASTA DOWNLOAD COMO PADRÃO
        if platform == 'android':
            from android.storage import primary_external_storage_path
            storage = primary_external_storage_path()
            self.video_dir = os.path.join(storage, "Download")
        else:
            self.video_dir = os.path.join(os.path.dirname(__file__), "videos")
            if not os.path.exists(self.video_dir):
                os.makedirs(self.video_dir, exist_ok=True)

        self.video_files = []
        self.current_index = 0
        self.video_duration = 15  # Cada vídeo assume a tela por 15 segundos

        # Desenha a moldura do app
        with self.canvas.before:
            Color(0.12, 0.12, 0.12, 1)
            self.border = Line(rectangle=(self.x, self.y, self.width, self.height), width=1.5)
        self.bind(size=self._update_border, pos=self._update_border)

        # Inicializa a lista de vídeos
        self._reload_playlist()
        if self.video_files:
            Clock.schedule_once(self.start_playback, 1.0)
        else:
            Clock.schedule_interval(self._check_empty_playlist, 5.0)

    def _update_border(self, instance, value):
        self.border.rectangle = (self.x, self.y, self.width, self.height)

    def _reload_playlist(self):
        supported = ('.mp4', '.mkv', '.avi')
        if os.path.exists(self.video_dir):
            try:
                files = [os.path.join(self.video_dir, f) for f in os.listdir(self.video_dir) if f.lower().endswith(supported)]
                self.video_files = sorted(files)[:20]
            except:
                self.video_files = []

    def _check_empty_playlist(self, dt):
        self._reload_playlist()
        if self.video_files:
            self.start_playback(0)
            return False
        return True

    def start_playback(self, dt):
        self.play_native_video(self.current_index)
        # Aciona o próximo vídeo a cada 15 segundos
        Clock.schedule_interval(self.next_video_timer, self.video_duration)

    def play_native_video(self, index):
        """Força o Android a abrir o vídeo no player nativo que você sabe que funciona!"""
        if not self.video_files:
            return

        if index >= len(self.video_files):
            self.current_index = 0
            index = 0

        video_path = self.video_files[index]
        print(f"🚀 Chamando o player do sistema para: {video_path}")

        if platform == 'android':
            try:
                # Usa o Pyjnius para chamar comandos nativos do Android (Intent)
                from jnius import autoclass
                
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Intent = autoclass('android.content.Intent')
                Uri = autoclass('android.net.Uri')
                File = autoclass('java.io.File')
                
                # Prepara o arquivo e a ação de visualizar (VIEW)
                video_file = File(video_path)
                video_uri = Uri.fromFile(video_file)
                
                intent = Intent(Intent.ACTION_VIEW)
                intent.setDataAndType(video_uri, "video/*")
                
                # Executa a abertura em tela cheia por cima do nosso app
                current_activity = PythonActivity.mActivity
                current_activity.startActivity(intent)
            except Exception as e:
                print(f"❌ Erro ao chamar player nativo: {e}")
        else:
            # No Windows, apenas simula abrindo no player padrão do PC
            if sys.platform == "win32":
                os.startfile(video_path)

    def next_video_timer(self, dt):
        if not self.video_files:
            return
        self.current_index = (self.current_index + 1) % len(self.video_files)
        self.play_native_video(self.current_index)

class TotemMidiaApp(App):
    def build(self):
        return TotemPlayerWidget()

if __name__ == '__main__':
    TotemMidiaApp().run()

