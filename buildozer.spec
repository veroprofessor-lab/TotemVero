[app]
source.dir = .
version = 1.0
title = Totem Midia
package.name = totemmidia
package.domain = org.amendoim

# (list) Application requirements
# ⚠️ CRUCIAL: Adicionar ffpyplayer e os componentes sdl2 necessários para vídeo
requirements = python3, kivy==2.3.1, ffpyplayer, sdl2, sdl2_image, sdl2_mixer, sdl2_ttf
# (str) Supported orientations (landscape é o padrão de TVs)
orientation = landscape
p4a.branch = release-2024.01.21
# (bool) Use fullscreen or not
fullscreen = 1

# (list) Permissions
# ⚠️ CRUCIAL: Permite que o app leia a pasta pública "TotemVideos" da TV-Box
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE

# (int) Target Android API (33 ou 34 atende a grande maioria das TV-Boxes atuais)
android.api = 34
# (str) Android NDK version to use
android.ndk = 26b

# (bool) If True, then skip trying to update the Android sdk
# Useful if you are packaging offline or wish to skip standard updates
android.skip_update = False

# (bool) If True, then automatically accept SDK licenses
android.accept_sdk_license = True
