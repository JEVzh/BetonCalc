[app]
version = 0.1
title = BetonCalc
package.name = betoncalc
package.domain = org.betoncalc
source.dir = .
source.include_exts = py,png

requirements = python3,kivy
orientation = portrait
fullscreen = 0

icon.filename = ./icon.png
android.adaptive_icon_background = ./icon_background.png
android.adaptive_icon_foreground = ./icon_foreground.png

[buildozer]
log_level = 2
warn_on_root = 1