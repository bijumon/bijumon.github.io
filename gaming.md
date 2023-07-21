+++
title = "gaming"
date = "2022-03-01 17:07 IST"
+++

[Disco Elysium](https://en.wikipedia.org/wiki/Disco_Elysium) has stopped working. The game freezes on loading. A solution is to install a custom build of proton, [GloriousEggroll/proton-ge-custom](https://github.com/GloriousEggroll/proton-ge-custom). It has FFmpeg enabled for FAudio, patches from wine-staging and Vulkan for Direct3D (VKD3D). 

Download a [release](https://github.com/GloriousEggroll/proton-ge-custom/releases)

``` shell
mkdir -v ~/.steam/root/compatibilitytools.d/
tar -xf Proton-7.2-GE-2.tar.gz -C ~/.steam/root/compatibilitytools.d/
```
---
[Civilization IV](https://www.civfanatics.com/civ4/info-center/) needs xml dll's to work with steam proton.

```
$ protontricks 8800 vcrun2003 msxml3 corefonts lucida tahoma fontsmooth=rgb
```

![civ4 beyond the sword](/images/civ4_fixed.jpg "civ4 fixed in proton")

