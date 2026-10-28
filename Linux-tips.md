---
layout: post
title: "Linux Tips"
date: 2024-10-04
description: collection of linux tools, tips and tricks
tags: [ "post" ]
---
`/bin/sh`, one line, handling directory names with spaces:

```sh
dirs=$(find /media -mindepth 1 -maxdepth 1 -type d -exec printf '%s\n' '{}' \;); printf '%s\n' "$dirs" | while IFS= read -r dir; do printf '%s\n' "$dir"; done
```
* * *
[python: how to check if a line is an empty line - Stack Overflow](https://stackoverflow.com/questions/7896495/python-how-to-check-if-a-line-is-an-empty-line)

If you want to ignore lines with only whitespace:

```python
if line.strip():
    ... do something
```

The empty string is a False value.

Or if you really want only empty lines:

```python
if line in ['\n', '\r\n']:
    ... do  something
```
* * *
[Search for executable files using find command](https://stackoverflow.com/questions/4458120/search-for-executable-files-using-find-command)

> answered by [GreenGiant - Stack Overflow](https://stackoverflow.com/users/539048/greengiant)

On GNU versions of find you can use `-executable`:

```sh
find . -type f -executable -print
```

For BSD (and MacOS) versions of find, you can use `-perm` with `+` and an octal mask:

```sh
find . -type f -perm +111 -print
```

In this context "+" means "any of these bits are set" and 111 is the execute bits. Note that this is not identical to the `-executable` predicate in GNU find. In particular, `-executable` tests that the file can be executed by the current user, while `-perm +111` just tests if any execute permissions are set.

* * * 
use a subshell to collect files into a tar archive, without switching to the folder
(cd /usr/share/fonts/TTF && tar czf ~/tmp/ttf-fira-code-nerd.tgz Fira*Nerd*.ttf)

* * *
TODO, explain setting up wlan0 bridge to use with cockpit guest VM

add a shared directory to the VM in guest add to fstab or mount using

`mount -t virtiofs share /share`

* * *
sudo journalctl -n 99 -kf --grep=UFW

* * *
Build site once: npx @11ty/eleventy
Serve locally with live reload: npx @11ty/eleventy --serve
Watch for file changes: npx @11ty/eleventy --watch

* * *
[SSH keys - ArchWiki](https://wiki.archlinux.org/title/SSH_keys#SSH_agents)
systemctl status ssh-agent --user

* * *
`yes | sudo pacman -Scc --noconfirm`

* * *
Create a new user who is a member of the same groups as the current user.

```sh
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

```sh
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
