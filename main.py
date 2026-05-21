import os
import sys
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import Color, Line
from kivy.utils import platform

# Força o Kivy a usar o ffpyplayer como player de vídeo padrão
os.environ['KIVY_VIDEO'] = 'ffpyplayer'

class TotemPlayerWidget(Widget):
    def __init__(self, **kwargs):
        super(TotemPlayerWidget, self).__init__(**kwargs)
        
        # 📂 GERENCIAMENTO DE PASTAS SEGURO (RAIZ PÚBLICA DO ANDROID)
        if platform == 'android':
            from android.storage import primary_external_storage_path
            # Pega o caminho real da memória interna (ex: /sdcard ou /storage/emulated/0)
            storage = primary_external_storage_path()
            
            # Rota 1: Tenta usar a pasta "Movies/TotemVideos" (Pasta padrão de vídeos do Android)
            self.video_dir = os.path.join(storage, "Movies", "TotemVideos")
            
            # Se não conseguir criar ou acessar, usa a pasta Download como Plano B definitivo
            if not os.path.exists(self.video_dir):
                try:
                    os.makedirs(self.video_dir, exist_ok=True)
                except:
                    self.video_dir = os.path.join(storage, "Download")
            
            print(f"📱 Pasta ativa no Android: {self.video_dir}")
        else:
            # No Windows, mantém a pasta local para os seus testes no VS Code
            self.video_dir = os.path.join(os.path.dirname(__file__), "videos")
            if not os.path.exists(self.video_dir):
                os.makedirs(self.video_dir, exist_ok=True)
            print(f"💻 Ambiente Windows detectado. Pasta de testes: {self.video_dir}")

        # Configurações do Carrossel de Vídeo
        self.video_files = []
        self.current_index = 0
        self.video_duration = 15  # Tempo rigoroso de exibição por vídeo (15 segundos)
        
        self.player = None
        self.last_pts = -1  # Evita reprocessar o mesmo frame repetidamente

        # Desenha a moldura discreta do totem (Layout)
        with self.canvas.before:
            Color(0.12, 0.12, 0.12, 1)
            self.border = Line(rectangle=(self.x, self.y, self.width, self.height), width=1.5)
        self.bind(size=self._update_border, pos=self._update_border)

        # Inicializa a Playlist
        self._reload_playlist()
        if self.video_files:
            Clock.schedule_once(self.start_playback, 1.0)
        else:
            # Se a pasta estiver vazia, checa de 5 em 5 segundos automaticamente
            Clock.schedule_interval(self._check_empty_playlist, 5.0)

    def _update_border(self, instance, value):
        self.border.rectangle = (self.x, self.y, self.width, self.height)

    def _reload_playlist(self):
        """Lê os arquivos de vídeo da pasta (máximo 20 arquivos .mp4)"""
        supported = ('.mp4', '.mkv', '.avi')
        if os.path.exists(self.video_dir):
            try:
                files = [os.path.join(self.video_dir, f) for f in os.listdir(self.video_dir) if f.lower().endswith(supported)]
                self.video_files = sorted(files)[:20]
                print(f"🎶 Playlist carregada: {len(self.video_files)} vídeos.")
            except Exception as e:
                print(f"❌ Erro ao ler arquivos da pasta: {e}")
                self.video_files = []

    def _check_empty_playlist(self, dt):
        """Tenta iniciar o player assim que os vídeos forem detectados"""
        self._reload_playlist()
        if self.video_files:
            self.start_playback(0)
            return False  # Cancela este timer de checagem interna
        return True

    def start_playback(self, dt):
        self.play_video_index(self.current_index)
        Clock.schedule_interval(self.next_video_timer, self.video_duration)
        Clock.schedule_interval(self.update_video_frame, 1 / 30.0)

    def play_video_index(self, index):
        if not self.video_files:
            return

        if self.player:
            try:
                self.player.close_player()
            except:
                pass
            self.player = None

        self.texture = None  
        self.last_pts = -1   

        if index >= len(self.video_files):
            self.current_index = 0
            index = 0

        video_path = self.video_files[index]
        
        from ffpyplayer.player import MediaPlayer
        ff_opts = {'paused': False, 'out_fmt': 'rgba', 'sn': True, 'an': False}
        self.player = MediaPlayer(video_path, ff_opts=ff_opts)

    def next_video_timer(self, dt):
        if not self.video_files:
            return
        self.current_index = (self.current_index + 1) % len(self.video_files)
        self.play_video_index(self.current_index)

    def update_video_frame(self, dt):
        if not self.player:
            return

        frame, val = self.player.get_frame()
        if val == 'eof':
            self.player.seek(0, relative=False)
            return

        if frame is None:
            return

        img, pts = frame
        if pts == self.last_pts:
            return
        
        self.last_pts = pts
        size = img.get_size()
        
        from kivy.graphics.texture import Texture
        texture = Texture.create(size=size, colorfmt='rgba')
        texture.blit_buffer(img.to_bytearray()[0], colorfmt='rgba', bufferfmt='ubyte')
        texture.flip_vertical()
        self.texture = texture

class TotemMidiaApp(App):
    def build(self):
        return TotemPlayerWidget()

if __name__ == '__main__':
    TotemMidiaApp().run()

