#!/bin/bash

# AppDev-Bench 应用切换脚本
# 使用方法: ./switch_app_config.sh <应用名>

if [ $# -eq 0 ]; then
    echo "可用的应用:"
    echo "=== 原有应用 (11个) ==="
    echo "1. MedTimer"
    echo "2. ShareX"
    echo "3. SimpleTextEditor"
    echo "4. Vanilla_Music"
    echo "5. Vector_Pinball"
    echo "6. openWorkout"
    echo "7. audiorecorder"
    echo "8. createpdf"
    echo "9. henri_dialer"
    echo "10. newpass"
    echo "11. periodical"
    echo ""
    echo "=== 新增应用 (9个) ==="
    echo "12. SlideshowWallpaper"
    echo "13. NextcloudServices"
    echo "14. PianOli"
    echo "15. SshDaemon"
    echo "16. SMS_to_URL_Forwarder"
    echo "17. Intra"
    echo "18. Semitone"
    echo "19. RandomixDecisionMaker"
    echo "20. SmartEggTimer"
    echo ""
    echo "=== 最新应用 (10个) ==="
    echo "21. DNS_Hero"
    echo "22. Transdroid_Torrent_Search"
    echo "23. Bluetooth_Viewer"
    echo "24. CityZen"
    echo "25. SetEdit"
    echo "26. AnLinux"
    echo "27. Echo"
    echo "28. BusyBox_Installer"
    echo "29. Pendulums"
    echo "30. Wave_Lines_Live_Wallpaper"
    echo ""
    echo "=== 最新添加应用 (15个) ==="
    echo "31. Skewy"
    echo "32. TimeLapseCam"
    echo "33. ToGoZip"
    echo "34. Equate"
    echo "35. Morse"
    echo "36. Get_id"
    echo "37. Location_Share"
    echo "38. Little_Music_Player"
    echo "39. heartbeat"
    echo "40. Syncthing-Fork"
    echo "41. Arcticons"
    echo "42. SocksTun"
    echo "43. Network_Tools_Library"
    echo "44. GPS_Cockpit"
    echo "45. Signal_Generator"
    echo ""
    echo "=== 新增应用 (11个) ==="
    echo "46. Plant_it"
    echo "47. Currency"
    echo "48. Oscilloscope"
    echo "49. FakeStandby"
    echo "50. Daedalus"
    echo "51. Feudal_Tactics"
    echo "52. Wi_Fi_Privacy_Police"
    echo "53. Autostarts"
    echo "54. Karma_Firewall"
    echo "55. PrivacyBreacher"
    echo "56. ulogger"
    echo ""
    echo "=== 最新新增应用 (7个) ==="
    echo "57. DNS66"
    echo "58. Whisper"
    echo "59. DiskUsage"
    echo "60. JustPlayer"
    echo "61. LRCEditor"
    echo "62. AFWeatherWidget"
    echo "63. AnotherMonitor"
    echo ""
    echo "=== 第三批新增应用 (7个) ==="
    echo "64. De_Bloater"
    echo "65. Enchanted_Fortress"
    echo "66. tinywheels"
    echo "67. Food_Tracker"
    echo "68. Meme_Creator"
    echo "69. Tempo"
    echo "70. Giggity"
    echo ""
    echo "=== 第四批新增应用 (8个) ==="
    echo "71. QuickWeather"
    echo "72. MyOwnNotes"
    echo "73. DiaguardDiabetesDiary"
    echo "74. droidVNC_NG"
    echo "75. Notes"
    echo "76. SecScanQR"
    echo "77. DiscreetLauncher"
    echo "78. DailyDozen"
    echo ""
    echo "总计: 78个应用"
    echo "使用方法: $0 <应用名>"
    exit 1
fi

APP_NAME=$1

# 检查应用是否存在
if [ ! -d "tasks/$APP_NAME" ]; then
    echo "错误: 应用 '$APP_NAME' 不存在"
    echo "请使用 '$0' 查看可用应用列表"
    exit 1
fi

# 根据应用名设置APK路径
case $APP_NAME in
    # 原有应用
    "MedTimer") APK_PATH="apk/MedTimer.apk" ;;
    "ShareX") APK_PATH="apk/ShareX.apk" ;;
    "SimpleTextEditor") APK_PATH="apk/SimpleTextEditor.apk" ;;
    "Vanilla_Music") APK_PATH="apk/Vanilla_Music.apk" ;;
    "Vector_Pinball") APK_PATH="apk/Vector_Pinball.apk" ;;
    "openWorkout") APK_PATH="apk/openWorkout.apk" ;;
    "audiorecorder") APK_PATH="apk/audiorecorder.apk" ;;
    "createpdf") APK_PATH="apk/createpdf.apk" ;;
    "henri_dialer") APK_PATH="apk/henri_dialer.apk" ;;
    "newpass") APK_PATH="apk/newpass.apk" ;;
    "periodical") APK_PATH="apk/periodical.apk" ;;
    # 新增应用
    "SlideshowWallpaper") APK_PATH="apk/SlideshowWallpaper.apk" ;;
    "NextcloudServices") APK_PATH="apk/NextcloudServices.apk" ;;
    "PianOli") APK_PATH="apk/PianOli.apk" ;;
    "SshDaemon") APK_PATH="apk/SshDaemon.apk" ;;
    "SMS_to_URL_Forwarder") APK_PATH="apk/SMS_to_URL_Forwarder.apk" ;;
    "Intra") APK_PATH="apk/Intra.apk" ;;
    "Semitone") APK_PATH="apk/Semitone.apk" ;;
    "RandomixDecisionMaker") APK_PATH="apk/RandomixDecisionMaker.apk" ;;
    "SmartEggTimer") APK_PATH="apk/SmartEggTimer.apk" ;;
    # 最新应用
    "DNS_Hero") APK_PATH="apk/DNS_Hero.apk" ;;
    "Transdroid_Torrent_Search") APK_PATH="apk/Transdroid_Torrent_Search.apk" ;;
    "Bluetooth_Viewer") APK_PATH="apk/Bluetooth_Viewer.apk" ;;
    "CityZen") APK_PATH="apk/CityZen.apk" ;;
    "SetEdit") APK_PATH="apk/SetEdit.apk" ;;
    "AnLinux") APK_PATH="apk/AnLinux.apk" ;;
    "Echo") APK_PATH="apk/Echo.apk" ;;
    "BusyBox_Installer") APK_PATH="apk/BusyBox_Installer.apk" ;;
    "Pendulums") APK_PATH="apk/Pendulums.apk" ;;
    "Wave_Lines_Live_Wallpaper") APK_PATH="apk/Wave_Lines_Live_Wallpaper.apk" ;;
    # 最新添加应用
    "Skewy") APK_PATH="apk/Skewy.apk" ;;
    "TimeLapseCam") APK_PATH="apk/TimeLapseCam.apk" ;;
    "ToGoZip") APK_PATH="apk/ToGoZip.apk" ;;
    "Equate") APK_PATH="apk/Equate.apk" ;;
    "Morse") APK_PATH="apk/Morse.apk" ;;
    "Get_id") APK_PATH="apk/Get_id.apk" ;;
    "Location_Share") APK_PATH="apk/Location_Share.apk" ;;
    "Little_Music_Player") APK_PATH="apk/Little_Music_Player.apk" ;;
    "heartbeat") APK_PATH="apk/heartbeat.apk" ;;
    "Syncthing-Fork") APK_PATH="apk/Syncthing-Fork.apk" ;;
    "Arcticons") APK_PATH="apk/Arcticons.apk" ;;
    "SocksTun") APK_PATH="apk/SocksTun.apk" ;;
    "Network_Tools_Library") APK_PATH="apk/Network Tools Library.apk" ;;
    "GPS_Cockpit") APK_PATH="apk/GPS Cockpit.apk" ;;
    "Signal_Generator") APK_PATH="apk/Signal Generator.apk" ;;
    # 新增应用
    "Plant_it") APK_PATH="apk/Plant-it.apk" ;;
    "Currency") APK_PATH="apk/Currency.apk" ;;
    "Oscilloscope") APK_PATH="apk/Oscilloscope.apk" ;;
    "FakeStandby") APK_PATH="apk/FakeStandby.apk" ;;
    "Daedalus") APK_PATH="apk/Daedalus.apk" ;;
    "Feudal_Tactics") APK_PATH="apk/Feudal Tactics.apk" ;;
    "Wi_Fi_Privacy_Police") APK_PATH="apk/Wi-Fi Privacy Police.apk" ;;
    "Autostarts") APK_PATH="apk/Autostarts - Block apps from starting automaticall.apk" ;;
    "Karma_Firewall") APK_PATH="apk/Karma_Firewall.apk" ;;
    "PrivacyBreacher") APK_PATH="apk/PrivacyBreacher.apk" ;;
    "ulogger") APK_PATH="apk/ulogger.apk" ;;
    # 最新新增应用
    "DNS66") APK_PATH="apk/DNS66.apk" ;;
    "Whisper") APK_PATH="apk/Whisper.apk" ;;
    "DiskUsage") APK_PATH="apk/DiskUsage.apk" ;;
    "JustPlayer") APK_PATH="apk/JustPlayer.apk" ;;
    "LRCEditor") APK_PATH="apk/LRCEditor.apk" ;;
    "AFWeatherWidget") APK_PATH="apk/AFWeatherWidget.apk" ;;
    "AnotherMonitor") APK_PATH="apk/AnotherMonitor.apk" ;;
    # 第三批新增应用
    "De_Bloater") APK_PATH="apk/De-Bloater.apk" ;;
    "Enchanted_Fortress") APK_PATH="apk/Enchanted Fortress.apk" ;;
    "tinywheels") APK_PATH="apk/tinywheels.apk" ;;
    "Food_Tracker") APK_PATH="apk/Food-Tracker.apk" ;;
    "Meme_Creator") APK_PATH="apk/Meme Creator.apk" ;;
    "Tempo") APK_PATH="apk/Tempo.apk" ;;
    "Giggity") APK_PATH="apk/Giggity.apk" ;;
    # 第四批新增应用
    "QuickWeather") APK_PATH="apk/QuickWeather.apk" ;;
    "MyOwnNotes") APK_PATH="apk/MyOwnNotes.apk" ;;
    "DiaguardDiabetesDiary") APK_PATH="apk/DiaguardDiabetesDiary.apk" ;;
    "droidVNC_NG") APK_PATH="apk/droidVNC-NG.apk" ;;
    "Notes") APK_PATH="apk/Notes.apk" ;;
    "SecScanQR") APK_PATH="apk/SecScanQR.apk" ;;
    "DiscreetLauncher") APK_PATH="apk/DiscreetLauncher.apk" ;;
    "DailyDozen") APK_PATH="apk/DailyDozen.apk" ;;
    *)
        echo "错误: 未知应用 '$APP_NAME'"
        exit 1
        ;;
esac

# 更新 collect_config.json
cat > collect_config.json << CONFIGEOF
{
    "port": "emulator-5554",
    "task_name": "$APP_NAME",
    "apk_path": "$APK_PATH"
}
CONFIGEOF

echo "✅ 已切换到应用: $APP_NAME"
echo "📱 APK路径: $APK_PATH"
echo "🚀 现在可以运行: python collect_tool.py"
