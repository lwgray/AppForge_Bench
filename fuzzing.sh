#!/bin/bash

PACKAGE_NAME="$1"
export ANDROID_SERIAL="$2"

TOTAL_DURATION=600
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_DIR="fuzz_logs/$TIMESTAMP"
MAIN_LOG="$LOG_DIR/fuzz_main.log"
CRASH_LOG="$LOG_DIR/crashes.log"
LOGCAT_LOG="$LOG_DIR/logcat_full.log"

# 创建日志目录
mkdir -p $LOG_DIR

echo "Starting fuzzing with comprehensive crash monitoring..." | tee $MAIN_LOG
echo "Logs will be saved in: $LOG_DIR"

# 清理旧的logcat并开始新的logcat监控
adb logcat -c
adb logcat -v time > $LOGCAT_LOG &
LOGCAT_PID=$!

# Crash统计变量
TOTAL_CRASHES=0
JAVA_CRASHES=0
NATIVE_CRASHES=0
ANR_COUNT=0

# 创建crash日志文件头
echo "=== CRASH MONITORING LOG ===" > $CRASH_LOG
echo "Package: $PACKAGE_NAME" >> $CRASH_LOG
echo "Start Time: $(date)" >> $CRASH_LOG
echo "==============================" >> $CRASH_LOG
echo "" >> $CRASH_LOG



# 监控crash的函数
monitor_crashes() {
    local monitor_duration=$1
    local start_time=$(date +%s)
    local end_time=$((start_time + monitor_duration))
    
    while [ $(date +%s) -lt $end_time ]; do
        # 检查Java crashes
        if adb logcat -d -s AndroidRuntime:E | grep -q "FATAL EXCEPTION.*$PACKAGE_NAME"; then
            echo "$(date): Java crash detected!" | tee -a $MAIN_LOG
            echo "=== JAVA CRASH at $(date) ===" >> $CRASH_LOG
            adb logcat -d -s AndroidRuntime:E | tail -20 >> $CRASH_LOG
            echo "" >> $CRASH_LOG
            JAVA_CRASHES=$((JAVA_CRASHES + 1))
            TOTAL_CRASHES=$((TOTAL_CRASHES + 1))
        fi
        
        # 检查Native crashes
        if adb logcat -d | grep -q "SIGSEGV\|SIGABRT\|SIGFPE.*$PACKAGE_NAME"; then
            echo "$(date): Native crash detected!" | tee -a $MAIN_LOG
            echo "=== NATIVE CRASH at $(date) ===" >> $CRASH_LOG
            adb logcat -d | grep -A 10 -B 5 "SIGSEGV\|SIGABRT\|SIGFPE.*$PACKAGE_NAME" >> $CRASH_LOG
            echo "" >> $CRASH_LOG
            NATIVE_CRASHES=$((NATIVE_CRASHES + 1))
            TOTAL_CRASHES=$((TOTAL_CRASHES + 1))
        fi
        
        # 检查ANR
        if adb logcat -d | grep -q "ANR.*$PACKAGE_NAME"; then
            echo "$(date): ANR detected!" | tee -a $MAIN_LOG
            echo "=== ANR at $(date) ===" >> $CRASH_LOG
            adb logcat -d | grep -A 15 -B 5 "ANR.*$PACKAGE_NAME" >> $CRASH_LOG
            echo "" >> $CRASH_LOG
            ANR_COUNT=$((ANR_COUNT + 1))
        fi
        
        sleep 2
    done
}

# 主fuzzing循环
END_TIME=$(($(date +%s) + TOTAL_DURATION))
CYCLE_COUNT=0

while [ $(date +%s) -lt $END_TIME ]; do
    REMAINING_TIME=$((END_TIME - $(date +%s)))
    if [ $REMAINING_TIME -le 0 ]; then
        break
    fi
    
    CYCLE_COUNT=$((CYCLE_COUNT + 1))
    CYCLE_DURATION=$((REMAINING_TIME < 60 ? REMAINING_TIME : 60))
    
    echo "$(date): Cycle $CYCLE_COUNT - Duration: ${CYCLE_DURATION}s, Remaining: ${REMAINING_TIME}s" | tee -a $MAIN_LOG
    
    # 清理logcat缓冲区
    adb logcat -c
    
    # 强制停止并重启应用
    adb shell am force-stop $PACKAGE_NAME
    sleep 2
    
    echo "$(date): Starting app..." | tee -a $MAIN_LOG
    adb shell am start -n $PACKAGE_NAME/.MainActivity
    sleep 3
    
    # 检查应用是否成功启动
    if ! adb shell pidof $PACKAGE_NAME > /dev/null; then
        echo "$(date): Failed to start app, skipping cycle" | tee -a $MAIN_LOG
        continue
    fi
    
    # 开始crash监控（后台进程）
    monitor_crashes $CYCLE_DURATION &
    MONITOR_PID=$!
    
    # 计算事件数量
    EVENT_COUNT=$((CYCLE_DURATION * 2))  # 每秒2个事件
    
    echo "$(date): Starting monkey with $EVENT_COUNT events..." | tee -a $MAIN_LOG
    
    # 运行monkey
    adb shell monkey -p $PACKAGE_NAME \
        --pct-touch 30 \
        --pct-motion 20 \
        --pct-trackball 10 \
        --pct-nav 10 \
        --pct-majornav 10 \
        --pct-syskeys 10 \
        --pct-appswitch 10 \
        --throttle 500 \
        --ignore-crashes \
        --ignore-timeouts \
        --ignore-security-exceptions \
        -v 500 \
        $EVENT_COUNT >> $MAIN_LOG 2>&1
    
    # 等待crash监控完成
    wait $MONITOR_PID 2>/dev/null
    
    # 收集额外的crash信息
    if [ -f /data/tombstones ]; then
        echo "$(date): Checking tombstones..." | tee -a $MAIN_LOG
        adb shell "ls -la /data/tombstones/ | tail -5" >> $CRASH_LOG 2>/dev/null
    fi
    
    echo "$(date): Cycle $CYCLE_COUNT completed. Total crashes so far: $TOTAL_CRASHES" | tee -a $MAIN_LOG
done

# 停止logcat监控
kill $LOGCAT_PID 2>/dev/null
wait $LOGCAT_PID 2>/dev/null

# 生成最终报告
REPORT_FILE="$LOG_DIR/crash_report.txt"
echo "=== FUZZING CRASH REPORT ===" > $REPORT_FILE
echo "Package: $PACKAGE_NAME" >> $REPORT_FILE
echo "Duration: $TOTAL_DURATION seconds" >> $REPORT_FILE
echo "Cycles: $CYCLE_COUNT" >> $REPORT_FILE
echo "Start Time: $(date -d @$(($(date +%s) - TOTAL_DURATION)))" >> $REPORT_FILE
echo "End Time: $(date)" >> $REPORT_FILE
echo "" >> $REPORT_FILE
echo "=== CRASH STATISTICS ===" >> $REPORT_FILE
echo "Total Crashes: $TOTAL_CRASHES" >> $REPORT_FILE
echo "Java Crashes: $JAVA_CRASHES" >> $REPORT_FILE
echo "Native Crashes: $NATIVE_CRASHES" >> $REPORT_FILE
echo "ANRs: $ANR_COUNT" >> $REPORT_FILE
echo "Crash Rate: $(echo "scale=2; $TOTAL_CRASHES / $CYCLE_COUNT" | bc 2>/dev/null || echo "N/A") crashes per cycle" >> $REPORT_FILE

# 清理应用
adb shell am force-stop $PACKAGE_NAME

echo "" | tee -a $MAIN_LOG
echo "=== FUZZING COMPLETED ===" | tee -a $MAIN_LOG
echo "Total Duration: $TOTAL_DURATION seconds" | tee -a $MAIN_LOG
echo "Total Cycles: $CYCLE_COUNT" | tee -a $MAIN_LOG
echo "Total Crashes: $TOTAL_CRASHES" | tee -a $MAIN_LOG
echo "  - Java Crashes: $JAVA_CRASHES" | tee -a $MAIN_LOG
echo "  - Native Crashes: $NATIVE_CRASHES" | tee -a $MAIN_LOG
echo "  - ANRs: $ANR_COUNT" | tee -a $MAIN_LOG
echo "" | tee -a $MAIN_LOG
echo "All logs saved in: $LOG_DIR" | tee -a $MAIN_LOG
echo "  - Main log: $MAIN_LOG"
echo "  - Crash log: $CRASH_LOG"
echo "  - Full logcat: $LOGCAT_LOG"
echo "  - Summary report: $REPORT_FILE"