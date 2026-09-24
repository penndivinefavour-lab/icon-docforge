package com.iconstudios.docforge

import android.os.Bundle
import android.view.View
import android.widget.Toast
import capacitor.android.CapacitorActivity
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.FileProvider
import java.io.File

class MainActivity : CapacitorActivity() {
    
    companion object {
        const val TAG = "IconDocForge"
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Enable WebView debugging in debug builds
        if (BuildConfig.DEBUG) {
            android.webkit.WebView.setWebContentsDebuggingEnabled(true)
        }
        
        // Initialize Capacitor
        init(savedInstanceState, StarterPlugin())
        
        // Load the web app
        load()
    }
    
    /**
     * Get content URI for sharing files
     */
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
    
    /**
     * Share a file via Android share sheet
     */
    fun shareFile(filePath: String, mimeType: String) {
        val uri = getFileUri(filePath) ?: return
        
        val intent = android.content.Intent(android.content.Intent.ACTION_SEND).apply {
            type = mimeType
            putExtra(android.content.Intent.EXTRA_STREAM, uri)
            addFlags(android.content.Intent.FLAG_GRANT_READ_URI_PERMISSION)
        }
        
        startActivity(android.content.Intent.createChooser(intent, "Share via"))
    }
    
    /**
     * Open a file with appropriate app
     */
    fun openFile(filePath: String, mimeType: String) {
        val uri = getFileUri(filePath) ?: return
        
        val intent = android.content.Intent(android.content.Intent.ACTION_VIEW).apply {
            setDataAndType(uri, mimeType)
            addFlags(android.content.Intent.FLAG_GRANT_READ_URI_PERMISSION)
            addFlags(android.content.Intent.FLAG_ACTIVITY_NEW_TASK)
        }
        
        try {
            startActivity(intent)
        } catch (e: Exception) {
            Toast.makeText(this, "No app found to open this file type", Toast.LENGTH_LONG).show()
        }
    }
    
    /**
     * Show error toast
     */
    fun showError(message: String) {
        runOnUiThread {
            Toast.makeText(this, message, Toast.LENGTH_LONG).show()
        }
    }
    
    /**
     * Show success toast
     */
    fun showSuccess(message: String) {
        runOnUiThread {
            Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
        }
    }
}

/**
 * StarterPlugin - Capacitor plugin registration
 */
class StarterPlugin : org.apache.cordova.CordovaPlugin() {
    override fun execute(action: String, args: org.json.JSONArray, callbackContext: org.apache.cordova.CallbackContext): Boolean {
        when (action) {
            "clearTemp" -> {
                val tempDir = File(activity?.cacheDir, "temp")
                if (tempDir.exists()) {
                    tempDir.deleteRecursively()
                    tempDir.mkdirs()
                }
                callbackContext.success()
                return true
            }
            else -> {
                return false
            }
        }
    }
}
