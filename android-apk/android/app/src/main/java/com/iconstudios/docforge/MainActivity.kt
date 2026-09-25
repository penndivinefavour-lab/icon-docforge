package com.iconstudios.docforge

import android.os.Bundle
import android.view.KeyEvent
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.FileProvider
import com.getcapacitor.BridgeActivity
import com.getcapacitor.Bridge
import com.getcapacitor.Capacitor
import org.json.JSONObject
import java.io.File

class MainActivity : BridgeActivity() {

    companion object {
        const val TAG = "IconDocForge"
        const val API_PORT = 8765
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Load capacitor.config.json before super.onCreate() initializes WebView
        loadConfigFromAssets()

        // Set theme from Capacitor's AppTheme.NoActionBar (no white background flash)
        setTheme(com.getcapacitor.android.R.style.AppTheme_NoActionBar)
    }

    // Keep the WebView-based file handling from the original implementation
    fun getFileUri(filePath: String): android.net.Uri? {
        return try {
            val file = File(filePath)
            if (file.exists()) {
                FileProvider.getUriForFile(
                    this,
                    "${packageName}.fileprovider",
                    file
                )
            } else {
                null
            }
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }

    private fun loadConfigFromAssets() {
        try {
            val configJson = loadJsonFromAssets("capacitor.config.json")
            if (configJson != null) {
                Capacitor.configure(configJson)
            }
        } catch (e: Exception) {
            Capacitor.configure(JSONObject())
        }
    }

    private fun loadJsonFromAssets(filename: String): JSONObject? {
        return try {
            val inputStream = assets.open(filename)
            val jsonString = inputStream.bufferedReader().use { it.readText() }
            inputStream.close()
            JSONObject(jsonString)
        } catch (e: Exception) {
            null
        }
    }
}
