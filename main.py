import os
from kivy.config import Config

# Força o Kivy a usar apenas os backends de renderização direta mais leves
os.environ['KIVY_IMAGE'] = 'sdl2'
os.environ['KIVY_VIDEO'] = 'ffpyplayer'

Config.set('graphics', 'fullscreen', 'auto')
Config.set('graphics', 'show_cursor', '0')

from kivy.app import App
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics import Color, Line
from kivy.utils import platform
from ffpyplayer.player import MediaPlayer


class TotemVideoPlayer(Image):
    def __init__(self, **kwargs):
        kwargs.setdefault('allow_stretch', True)
        kwargs.setdefault('keep_ratio', True)
        super(TotemVideoPlayer, self).__init__(**kwargs)

        # 📂 GERENCIAMENTO DE PASTAS MULTIPLATAFORMA
        if platform == 'android':
            # Na TV-Box, cria/usa a pasta "TotemVideos" na raiz do armazenamento interno público
            from android.storage import primary_external_storage_path
            storage = primary_external_storage_path()
            self.video_dir = os.path.join(storage, "TotemVideos")
        else:
            # No Windows, mantém a pasta local para os seus testes
            self.video_dir = os.path.join(os.path.dirname(__file__), "videos")

        if not os.path.exists(self.video_dir):
            try:
                os.makedirs(self.video_dir)
            except Exception as e:
                print(f"❌ Erro ao criar diretório: {e}")

        self.video_files = []
        self.current_index = 0
        self.video_duration = 15  # Tempo rigoroso de exibição por vídeo
        
        self.player = None
        self.last_pts = -1  # Evita reprocessar o mesmo frame repetidamente

        # Desenha a moldura discreta do totem
        with self.canvas.before:
            Color(0.12, 0.12, 0.12, 1)
            self.border = Line(rectangle=(self.x, self.y, self.width, self.height), width=1.5)
        self.bind(size=self._update_border, pos=self._update_border)

        self._reload_playlist()
        if self.video_files:
            Clock.schedule_once(self.start_playback, 1.0)
        else:
            # Se a pasta estiver vazia no Android, checa de 5 em 5 segundos até o cliente colocar os vídeos
            Clock.schedule_interval(self._check_empty_playlist, 5.0)

    def _reload_playlist(self):
        """Lê os arquivos de vídeo da pasta (máximo 20)"""
        supported = ('.mp4', '.mkv', '.avi')
        if os.path.exists(self.video_dir):
            files = [os.path.join(self.video_dir, f) for f in os.listdir(self.video_dir) if f.lower().endswith(supported)]
            self.video_files = sorted(files)[:20]

    def _check_empty_playlist(self, dt):
        """Tenta iniciar o player caso os vídeos tenham sido adicionados depois"""
        self._reload_playlist()
        if self.video_files:
            self.start_playback(0)
            return False # Cancela este timer específico
        return True

    def start_playback(self, dt):
        """Dispara o carrossel e o atualizador visual cravado no padrão de TV (30 FPS)"""
        self.play_video_index(self.current_index)
        Clock.schedule_interval(self.next_video_timer, self.video_duration)
        Clock.schedule_interval(self.update_video_frame, 1 / 30.0)

    def play_video_index(self, index):
        """Fecha o reprodutor anterior e reseta a tela para o próximo vídeo"""
        if not self.video_files:
            return

        if self.player:
            self.player.close_player()
            self.player = None

        self.texture = None  # Limpa o último frame imediatamente (mata fantasmas e misturas)
        self.last_pts = -1   # Reseta o rastreador de quadros

        video_path = self.video_files[index]
        print(f"🎬 [Totem Ativo] Reproduzindo: {os.path.basename(video_path)}")

        # Configurações otimizadas para decodificação em TV-Box (ignora clock de áudio físico)
        ff_opts = {'paused': False, 'out_fmt': 'rgba', 'sn': True, 'an': True}
        try:
            self.player = MediaPlayer(video_path, ff_opts=ff_opts)
        except Exception as e:
            print(f"❌ Erro ao abrir vídeo: {e}")

    def update_video_frame(self, dt):
        """Consome o frame disponível no ritmo controlado do Kivy"""
        if not self.player:
            return

        frame, val = self.player.get_frame()
        
        if val == 'eof':
            self.player.seek(0, relative=False)
            return

        if frame is None:
            return

        img, pts = frame
        
        # Filtro de repetição para manter os 30 FPS estáveis
        if pts == self.last_pts:
            return
        
        self.last_pts = pts

        size = img.get_size()
        try:
            data = b''.join(img.to_bytearray())
            
            from kivy.graphics.texture import Texture
            texture = Texture.create(size=size, colorfmt='rgba')
            texture.blit_buffer(data, colorfmt='rgba', bufferfmt='ubyte')
            texture.flip_vertical()
            
            self.texture = texture
        except Exception as e:
            pass

    def next_video_timer(self, dt):
        """Avança o carrossel infinito limpando a memória"""
        self._reload_playlist()
        if not self.video_files:
            return

        self.current_index = (self.current_index + 1) % len(self.video_files)
        self.play_video_index(self.current_index)

    def _update_border(self, *args):
        self.border.rectangle = (self.x + 4, self.y + 4, self.width - 8, self.height - 8)


class TotemApp(App):
    def build(self):
        return TotemVideoPlayer()


if __name__ == '__main__':
    TotemApp().run()