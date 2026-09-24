package com.iconstudios.docforge

import android.os.Bundle
import android.webkit.WebView
import com.getcapacitor.BridgeActivity
import androidx.core.content.FileProvider
import java.io.File

class MainActivity : BridgeActivity() {
    
    companion object {
        const val TAG = "IconDocForge"
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Enable WebView debugging in debug builds
        if (BuildConfig.DEBUG) {
            WebView.setWebContentsDebuggingEnabled(true)
        }
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
            android.widget.Toast.makeText(this, "No app found to open this file type", android.widget.Toast.LENGTH_LONG).show()
        }
    }
}
