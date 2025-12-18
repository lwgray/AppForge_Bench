# AppForge_Bench Modernization (2024)

This is a modernized fork of [AppForge_Bench](https://github.com/AppForge-Bench/AppForge_Bench) updated for 2024 Android development standards.

## Attribution

**Original Project**: AppForge_Bench by the AppForge team
**Original Repository**: https://github.com/AppForge-Bench/AppForge_Bench
**Fork Maintained By**: Marcus Project (https://github.com/lwgray/marcus)

## Why This Fork?

The original AppForge_Bench uses Android development tooling from 2021:
- Gradle 7.2 (August 2021)
- Android Gradle Plugin 7.1.2
- Java 8
- API Level 31 (Android 12)

Modern code generation systems (like Marcus) produce Android apps using 2024 standards:
- Gradle 8.8
- Android Gradle Plugin 8.7
- Java 17
- API Level 34 (Android 14)
- Kotlin support
- `namespace` in build.gradle instead of `package` in AndroidManifest.xml

This fork updates **only the build toolchain** while keeping all 101 task definitions unchanged, enabling evaluation of modern Android code generation systems.

## Changes from Original

### 1. Gradle Wrapper: 7.2 → 8.8
**File**: `compiler/templates/empty_activity/gradle/wrapper/gradle-wrapper.properties`

```diff
-distributionUrl=https\://mirrors.cloud.tencent.com/gradle/gradle-7.2-bin.zip
+distributionUrl=https\://services.gradle.org/distributions/gradle-8.8-bin.zip
```

### 2. Android Gradle Plugin: 7.1.2 → 8.7.0
**File**: `compiler/templates/empty_activity/build.gradle`

```diff
 plugins {
-    id 'com.android.application' version '7.1.2' apply false
-    id 'com.android.library' version '7.1.2' apply false
+    id 'com.android.application' version '8.7.0' apply false
+    id 'com.android.library' version '8.7.0' apply false
+    id 'org.jetbrains.kotlin.android' version '1.9.22' apply false
 }
```

### 3. Modern App Configuration
**File**: `compiler/templates/empty_activity/app/build.gradle`

```diff
 plugins {
     id 'com.android.application'
+    id 'org.jetbrains.kotlin.android'
 }

 android {
+    namespace 'com.example.template'
-    compileSdk 31
+    compileSdk 34

     defaultConfig {
         applicationId "com.example.template"
-        minSdk 31
-        targetSdk 31
+        minSdk 24
+        targetSdk 34
         versionCode 1
         versionName "1.0"

         testInstrumentationRunner "androidx.test.runner.AndroidJUnitRunner"
     }

     buildTypes {
         release {
             minifyEnabled false
             proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
         }
     }
     compileOptions {
-        sourceCompatibility JavaVersion.VERSION_1_8
-        targetCompatibility JavaVersion.VERSION_1_8
+        sourceCompatibility JavaVersion.VERSION_17
+        targetCompatibility JavaVersion.VERSION_17
     }
+    kotlinOptions {
+        jvmTarget = '17'
+    }
 }

 dependencies {
-    implementation 'androidx.appcompat:appcompat:1.3.0'
-    implementation 'com.google.android.material:material:1.4.0'
-    implementation 'androidx.constraintlayout:constraintlayout:2.0.4'
+    implementation 'androidx.core:core-ktx:1.12.0'
+    implementation 'androidx.appcompat:appcompat:1.6.1'
+    implementation 'com.google.android.material:material:1.11.0'
+    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
     testImplementation 'junit:junit:4.13.2'
-    androidTestImplementation 'androidx.test.ext:junit:1.1.3'
-    androidTestImplementation 'androidx.test.espresso:espresso-core:3.4.0'
+    androidTestImplementation 'androidx.test.ext:junit:1.1.5'
+    androidTestImplementation 'androidx.test.espresso:espresso-core:3.5.1'
 }
```

## What Stays the Same

- ✅ All 101 task definitions (`tasks/tasks.json`)
- ✅ All test scripts
- ✅ Evaluation methodology
- ✅ Scoring system
- ✅ Task descriptions and requirements

**This fork only updates the build environment to match modern Android development practices.**

## System Requirements

- **Java**: OpenJDK 17 (required)
  ```bash
  # macOS (Homebrew)
  brew install openjdk@17

  # Set JAVA_HOME
  export JAVA_HOME=/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home
  ```

- **Android SDK**: API Level 34 (Android 14)
- **Gradle**: 8.8 (auto-downloaded by wrapper)

## Usage

Same as original AppForge_Bench, but with modern toolchain:

```bash
# Clone this fork
git clone https://github.com/lwgray/AppForge_Bench
cd AppForge_Bench

# Run evaluation (example with Marcus)
python compiler/build.py \
  --task-id 63 \
  --impl-dir /path/to/marcus/output
```

## For Marcus Users

If you're using this fork with Marcus, see the Marcus repository for integration details:
https://github.com/lwgray/marcus/tree/main/dev-tools/experiments/benchmarks/appforge

## Compatibility with Original

**Can results be compared?**

Results from this fork are **not directly comparable** to results from the original AppForge_Bench because:
1. Different build toolchain versions
2. Different dependency versions
3. Different compilation behavior

However, task definitions are identical, so the **evaluation methodology** is the same.

## Syncing with Upstream

To stay updated with upstream task definition changes:

```bash
git fetch upstream
git merge upstream/main
```

Note: Merge conflicts may occur in template files (build.gradle, etc.). Keep the modernized versions from this fork.

## License

Same license as original AppForge_Bench project.

## Contributing

Issues and PRs welcome for:
- Build toolchain updates
- Dependency version updates
- Documentation improvements
- Bug fixes

For changes to task definitions or evaluation methodology, please contribute to the [original repository](https://github.com/AppForge-Bench/AppForge_Bench).

## Citation

If you use this fork in research, please cite both:
1. The original AppForge_Bench paper (when published)
2. Mention this modernized fork: `https://github.com/lwgray/AppForge_Bench`

---

**Questions?** Open an issue or see the [Marcus project](https://github.com/lwgray/marcus) for details.
