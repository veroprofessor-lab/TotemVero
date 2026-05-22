import os
from kivy.app import App
from kivy.uix.video import Video
from kivy.clock import Clock
from kivy.utils import platform

class TotemMidiaApp(App):
    def build(self):
        # 🔗 PLAYLIST DE VÍDEOS NA INTERNET ULTRA-RÁPIDA
        # O primeiro link é um exemplo leve e público para testarmos agora.
        self.playlist = [
            "https://static.videezy.com/system/resources/previews/000/045/486/original/water-01.mp4",
            "https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"
        ]
        
        self.current_index = 0
        
        # Usamos o componente 'Video' puro: SEM BOTÕES, SEM LINHA DE TEMPO. Tela 100% limpa!
        self.player = Video(
            source=self.playlist[self.current_index],
            state='play',
            options={'allow_stretch': True, 'eos': 'loop'}
        )
        
        # Força o vídeo a ocupar a TV inteira sem bordas pretas nas laterais
        self.player.allow_stretch = True
        
        # Carrossel de tempo: muda de vídeo a cada 15 segundos de forma perpétua
        Clock.schedule_interval(self.next_video, 15.0)
        
        return self.player

    def next_video(self, dt):
        if not self.playlist:
            return
            
        # Avança para o próximo link da lista de forma infinita
        self.current_index = (self.current_index + 1) % len(self.playlist)
        
        # Troca a fonte e força o play instantâneo
        self.player.unload()  # Limpa o vídeo anterior da memória da TV-Box
        self.player.source = self.playlist[self.current_index]
        self.player.state = 'play'
        print(f"🌐 Totem mudando para o vídeo: {self.player.source}")

if __name__ == '__main__':
    TotemMidiaApp().run()

