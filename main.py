import os
from kivy.app import App
from kivy.uix.videoplayer import VideoPlayer
from kivy.clock import Clock
from kivy.utils import platform

class TotemApp(App):
    def build(self):
        # 🔗 PLAYLIST DE VÍDEOS NA INTERNET
        # Substitua os links abaixo pelos links dos seus vídeos!
        # Dica: Se usar o Dropbox, mude o final do link de 'dl=0' para 'raw=1'
        self.playlist = [
            "https://libs.html5video.org/video/mp4/movies/transcode/360p/big_buck_bunny.mp4",
            "https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
            "https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4"
        ]
        
        self.current_index = 0
        
        # Cria o player de vídeo do Kivy ocupando a tela inteira
        self.player = VideoPlayer(
            source=self.playlist[self.current_index],
            state='play',
            options={'allow_stretch': True, 'eos': 'loop'}
        )
        
        # Oculta os botões de controle do player (pausa, barra de tempo) para ficar estético no totem
        self.player.allow_fullscreen = True
        
        # Configura o carrossel: muda de vídeo a cada 15 segundos de forma perpétua
        Clock.schedule_interval(self.next_video, 15.0)
        
        return self.player

    def next_video(self, dt):
        if not self.playlist:
            return
            
        # Avança para o próximo link da lista
        self.current_index = (self.current_index + 1) % len(self.playlist)
        
        # Atualiza a fonte do player e força a reprodução imediata
        self.player.source = self.playlist[self.current_index]
        self.player.state = 'play'
        print(f"🌐 Reproduzindo vídeo da web: {self.player.source}")

if __name__ == '__main__':
    TotemApp().run()

