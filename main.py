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
        
        # 📂 GERENCIAMENTO DE PASTAS MULTIPLATAFORMA (LEITURA DIRETA DO PENDRIVE)
        if platform == 'android':
            base_storage = "/storage"
            self.video_dir = None
            
            # Detetive de Pendrive: Varre a pasta /storage procurando o USB
            if os.path.exists(base_storage):
                for item in os.listdir(base_storage):
                    # Ignora a memória interna padrão do Android
                    if item not in ['emulated', 'self', 'enc_emulated']:
                        usb_path = os.path.join(base_storage, item, "TotemVideos")
                        # Se encontrar a pasta "TotemVideos" dentro do pendrive, usa ela!
                        if os.path.exists(usb_path):
                            self.video_dir = usb_path
                            print(f"💾 Pendrive Detectado com Sucesso em: {self.video_dir}")
                            break
            
            # Se não achou nenhum pendrive conectado, usa a memória interna como Plano B
            if not self.video_dir:
                from android.storage import primary_external_storage_path
                storage = primary_external_storage_path()
                self.video_dir = os.path.join(storage, "TotemVideos")
                if not os.path.exists(self.video_dir):
                    os.makedirs(self.video_dir, exist_ok=True)
                print(f"📱 Pendrive não encontrado. Usando memória interna: {self.video_dir}")
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
            # Se o pendrive estiver desplugado ou sem vídeos, checa de 5 em 5 segundos automaticamente
            Clock.schedule_interval(self._check_empty_playlist, 5.0)

    def _update_border(self, instance, value):
        """Atualiza a moldura caso o tamanho da tela mude"""
        self.border.rectangle = (self.x, self.y, self.width, self.height)

    def _reload_playlist(self):
        """Lê os arquivos de vídeo da pasta (máximo 20 arquivos .mp4)"""
        supported = ('.mp4', '.mkv', '.avi')
        if os.path.exists(self.video_dir):
            try:
                files = [os.path.join(self.video_dir, f) for f in os.listdir(self.video_dir) if f.lower().endswith(supported)]
                self.video_files = sorted(files)[:20]
                print(f"🎶 Playlist carregada: {len(self.video_files)} vídeos encontrados.")
            except Exception as e:
                print(f"❌ Erro ao ler arquivos da pasta: {e}")
                self.video_files = []

    def _check_empty_playlist(self, dt):
        """Tenta iniciar o player caso o pendrive seja plugado tardiamente"""
        self._reload_playlist()
        if self.video_files:
            self.start_playback(0)
            return False  # Cancela este timer de checagem interna
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
            try:
                self.player.close_player()
            except:
                pass
            self.player = None

        self.texture = None  # Limpa o último frame imediatamente (mata fantasmas de imagem)
        self.last_pts = -1   # Reseta o rastreador de quadros

        # Garante que o índice não estoure a lista
        if index >= len(self.video_files):
            self.current_index = 0
            index = 0

        video_path = self.video_files[index]
        print(f"🎬 [Totem Ativo] Reproduzindo: {os.path.basename(video_path)}")
        
        # Inicializa o ffpyplayer nativo para o vídeo atual
        from ffpyplayer.player import MediaPlayer
        ff_opts = {'paused': False, 'out_fmt': 'rgba', 'sn': True, 'an': False} # sn=Sinal de vídeo ativo, an=Sem áudio para totens comerciais
        self.player = MediaPlayer(video_path, ff_opts=ff_opts)

    def next_video_timer(self, dt):
        """Avança de forma perpétua para o próximo vídeo após os 15 segundos"""
        if not self.video_files:
            return
        
        self.current_index = (self.current_index + 1) % len(self.video_files)
        self.play_video_index(self.current_index)

    def update_video_frame(self, dt):
        """Atualiza a textura da tela frame a frame a 30 FPS puxando do ffpyplayer"""
        if not self.player:
            return

        # Puxa o frame atual do decodificador
        frame, val = self.player.get_frame()
        
        if val == 'eof':
            # Se o vídeo acabar antes dos 15 segundos, força o looping do mesmo arquivo imediatamente
            self.player.seek(0, relative=False)
            return

        if frame is None:
            return

        # Extrai os dados de imagem e atualiza a textura do widget na tela
        img, pts = frame
        if pts == self.last_pts:
            return
        
        self.last_pts = pts
        size = img.get_size()
        
        # Cria a textura em tempo real na tela do Android/Windows
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
