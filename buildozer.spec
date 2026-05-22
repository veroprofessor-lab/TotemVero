[app]
source.dir = .
version = 1.0
title = Totem Midia
package.name = totemmidia
package.domain = org.amendoim

# (list) Application requirements
# ⚠️ CRUCIAL: Adicionar ffpyplayer e os componentes sdl2 necessários para vídeo
# (list) Application requirements
# (list) Application requirements
requirements = python3, kivy, ffmpeg, ffpyplayer, sdl2, sdl2_image, sdl2_mixer, sdl2_ttf, android
# (str) Supported orientations (landscape é o padrão de TVs)
orientation = landscape
p4a.branch = release-2024.01.21
# (bool) Use fullscreen or not
fullscreen = 1
# (int) Target Android Python version
android.python_version = 3.11

# (list) Permissions
# ⚠️ CRUCIAL: Permite que o app leia a pasta pública "TotemVideos" da TV-Box
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# (str) python-for-android branch to use

# (int) Target Android API (33 ou 34 atende a grande maioria das TV-Boxes atuais)
android.api = 29
# (str) Android NDK version to use
android.ndk = 25c
# (list) The Android architectures to build for
android.archs = armeabi-v7a, arm64-v8a
# (int) Log level (0 = error only, 1 = info, 2 = debug and big outputs)
log_level = 2

# (bool) If True, then skip trying to update the Android sdk
# Useful if you are packaging offline or wish to skip standard updates
android.skip_update = False

# (bool) If True, then automatically accept SDK licenses
android.accept_sdk_license = True
