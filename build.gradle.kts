plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}
android {
    namespace = "com.yami.tradesai"
    compileSdk = 35
    defaultConfig {
        applicationId = "com.yami.tradesai"
        minSdk = 23
        targetSdk = 35
        versionCode = 1
        versionName = "1.0"
    }
}
