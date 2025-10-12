#!/bin/bash


declare -A apps=(
    ["SlideshowWallpaper.apk"]="wallpaper|slide"
    ["NextcloudServices.apk"]="nextcloud"
    ["PianOli.apk"]="piano|pian"
    ["SshDaemon.apk"]="ssh"
    ["SMS_to_URL_Forwarder.apk"]="sms|url"
    ["Intra.apk"]="intra"
    ["Semitone.apk"]="semitone|semi"
    ["RandomixDecisionMaker.apk"]="random|decision"
    ["SmartEggTimer.apk"]="egg|timer"
    ["DNS_Hero.apk"]="dns|hero"
    ["Transdroid_Torrent_Search.apk"]="transdroid|torrent"
    ["Bluetooth_Viewer.apk"]="bluetooth|viewer"
    ["CityZen.apk"]="cityzen|city"
    ["SetEdit.apk"]="setedit|set"
    ["AnLinux.apk"]="anlinux|linux"
    ["Echo.apk"]="echo"
    ["BusyBox_Installer.apk"]="busybox|installer"
    ["Pendulums.apk"]="pendulum"
    ["Wave_Lines_Live_Wallpaper.apk"]="wave|lines|wallpaper"
)

for apk in "${!apps[@]}"; do
    echo "Processing $apk..."
    adb install "apk/$apk"
    echo "Package name for $apk:"
    adb shell pm list packages | grep -E "${apps[$apk]}"
    echo "---"
done
