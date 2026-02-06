---
layout: post
title: "Linux Tips"
date: 2024-10-04
description: collection of linux tools, tips and tricks (WORK IN PROGRESS)
tags: [ "post" ]
---

Create a new user who is a member of the same groups as the current user.

``` shell
$ groups
users lp wheel dialout video audio render docker autologin

$ printf "%s\n" $(groups) | sort
audio
autologin
dialout
docker
lp
render
users
video
wheel
```

`tr '\n' ','`  translates the newlines into commas, converting the list of groups into a comma-separated string

`sed 's/.$//'` uses sed (stream editor) to remove the last character (which will be the trailing comma from the previous step)

``` shell
$ printf "%s\n" $(groups) | sort | tr '\n' ',' | sed 's/.$//'
audio,autologin,dialout,docker,lp,render,video,wheel

$ my_groups=$(printf "%s\n" $(groups) | sort | tr '\n' ',' | sed 's/.$//')
$ sudo useradd \
    --comment "Hullo" \
    --gid sudo \
    --groups $my_groups \
    --create-home \
    --no-user-group \
    newuser

# using short options
$ sudo useradd -g users -G $groups -m -N newuser
```
