[app]
title = BetonCalc
package.name = betoncalc
package.domain = org.betoncalc
source.dir = .
source.include_exts = py,png
version = 0.1

# КЛЮЧЕВАЯ СТРОКА: python3 и hostpython3 ОДНОЙ версии
requirements = python3==3.11.9,hostpython3==3.11.9,kivy

orientation = portrait
fullscreen = 0

android.accept_sdk_license = True

icon.filename = ./icon.png
android.adaptive_icon_background = ./icon_background.png
android.adaptive_icon_foreground = ./icon_foreground.png

[buildozer]
log_level = 2
warn_on_root = 0
