package com.iconstudios.docforge

import android.Manifest
import android.app.Activity
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.DocumentsContract
import android.view.View
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.webkit.WebViewCompat
import capacitor.android.CapacitorActivity
import org.apache.cordova.CallbackContext
import org.apache.cordova.CordovaInterface
import org.apache.cordova.CordovaPlugin
import org.apache.cordova.CordovaWebView
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.io.FileOutputStream

/**
 * MainActivity - ICON DocForge Android Application
 * 
 * This activity hosts the WebView-based document conversion interface
 * and bridges between Android native features and the web UI.
 */
class MainActivity : CapacitorActivity() {
    
    companion object {
        private const val TAG = "IconDocForge"
        private const val REQUEST_STORAGE_PERMISSION = 1001
        private const val REQUEST_OPEN_DOCUMENT = 1002
    }
    
    private lateinit var webView: android.webkit.WebView
    private var currentFileUri: Uri? = null
    
    // File picker result handler
    private val pickFilesLauncher = registerForActivityResult(
        ActivityResultContracts.OpenDocument()
    ) { uri: Uri? ->
        if (uri != null) {
            handleSelectedFile(uri)
        }
    }
    
    // Multiple file picker
    private val pickMultipleFilesLauncher = registerForActivityResult(
        ActivityResultContracts.OpenMultipleDocuments()
    ) { uris: List<Uri>? ->
        if (uris != null && uris.isNotEmpty()) {
            handleSelectedFiles(uris)
        }
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
    
    override fun onStart() {
        super.onStart()
        // Request storage permission if needed (Android 12 and below)
        if (Build.VERSION.SDK_INT <= Build.VERSION_CODES.S_V2) {
            checkStoragePermission()
        }
    }
    
    /**
     * Open file picker for single file selection
     */
    fun openFilePicker(mimeType: String) {
        val intent = Intent(Intent.ACTION_OPEN_DOCUMENT).apply {
            addCategory(Intent.CATEGORY_OPENABLE)
            type = mimeType
        }
        pickFilesLauncher.launch(intent)
    }
    
    /**
     * Open file picker for multiple files
     */
    fun openMultipleFilePicker(mimeType: String) {
        val intent = Intent(Intent.ACTION_OPEN_DOCUMENT).apply {
            addCategory(Intent.CATEGORY_OPENABLE)
            type = mimeType
            putExtra(Intent.EXTRA_ALLOW_MULTIPLE, true)
        }
        pickMultipleFilesLauncher.launch(intent)
    }
    
    /**
     * Handle single file selection
     */
    private fun handleSelectedFile(uri: Uri) {
        currentFileUri = uri
        
        // Copy file to app's temp directory for processing
        val tempFile = copyToTempFile(uri)
        
        if (tempFile != null) {
            // Notify WebView about selected file
            val js = """
                window.App.onFileSelected(${
                    JSONObject().apply {
                        put("name", getFileName(uri))
                        put("path", tempFile.absolutePath)
                        put("size", tempFile.length())
                        put("type", guessMimeType(uri))
                    }.toString()
                })
            """
            webView.evaluateJavascript(js, null)
        } else {
            showError("Failed to copy file for processing")
        }
    }
    
    /**
     * Handle multiple file selection
     */
    private fun handleSelectedFiles(uris: List<Uri>) {
        val files = mutableListOf<JSONObject>()
        
        for (uri in uris) {
            val tempFile = copyToTempFile(uri)
            if (tempFile != null) {
                files.add(JSONObject().apply {
                    put("name", getFileName(uri))
                    put("path", tempFile.absolutePath)
                    put("size", tempFile.length())
                    put("type", guessMimeType(uri))
                })
            }
        }
        
        if (files.isNotEmpty()) {
            val js = """
                window.App.onFilesSelected(${JSONArray(files).toString()})
            """
            webView.evaluateJavascript(js, null)
        }
    }
    
    /**
     * Copy content resolver URI to app's private temp directory
     */
    private fun copyToTempFile(uri: Uri): File? {
        return try {
            val fileName = getFileName(uri)
            val tempDir = File(cacheDir, "temp")
            tempDir.mkdirs()
            
            val outputFile = File(tempDir, sanitizeFilename(fileName))
            
            contentResolver.openInputStream(uri)?.use { inputStream ->
                FileOutputStream(outputFile).use { outputStream ->
                    inputStream.copyTo(outputStream)
                }
            }
            
            outputFile
        } catch (e: Exception) {
            showError("Error copying file: ${e.message}")
            null
        }
    }
    
    /**
     * Get display name from URI
     */
    private fun getFileName(uri: Uri): String {
        var name = ""
        contentResolver.query(uri, arrayOf(DocumentsContract.Document.COLUMN_DISPLAY_NAME), null, null, null)?.use {
            if (it.moveToFirst()) {
                name = it.getString(0)
            }
        }
        return if (name.isNotEmpty()) name else "document_${System.currentTimeMillis()}"
    }
    
    /**
     * Guess MIME type from URI
     */
    private fun guessMimeType(uri: Uri): String {
        return try {
            contentResolver.getType(uri) ?: "application/octet-stream"
        } catch (e: Exception) {
            "application/octet-stream"
        }
    }
    
    /**
     * Sanitize filename for security
     */
    private fun sanitizeFilename(filename: String): String {
        return filename.replace("""[<>:"/\\|?*\x00-\x1f]""".toRegex(), "_")
            .take(200) // Limit length
    }
    
    /**
     * Check storage permission (Android 12 and below)
     */
    private fun checkStoragePermission() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.READ_EXTERNAL_STORAGE)
                != PackageManager.PERMISSION_GRANTED
            ) {
                requestPermissions(
                    arrayOf(Manifest.permission.READ_EXTERNAL_STORAGE),
                    REQUEST_STORAGE_PERMISSION
                )
            }
        }
    }
    
    /**
     * Handle permission result
     */
    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == REQUEST_STORAGE_PERMISSION) {
            if (grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                Toast.makeText(this, "Storage permission granted", Toast.LENGTH_SHORT).show()
            } else {
                Toast.makeText(this, "Storage permission required for file access", Toast.LENGTH_LONG).show()
            }
        }
    }
    
    /**
     * Show error toast to user
     */
    private fun showError(message: String) {
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
    
    /**
     * Navigate to a URL in the WebView
     */
    fun navigateTo(url: String) {
        webView.post {
            webView.loadUrl(url)
        }
    }
    
    /**
     * Clear temporary files
     */
    fun clearTempFiles() {
        val tempDir = File(cacheDir, "temp")
        if (tempDir.exists()) {
            tempDir.deleteRecursively()
            tempDir.mkdirs()
        }
    }
}

/**
 * StarterPlugin - Capacitor plugin registration
 */
class StarterPlugin : CordovaPlugin() {
    override fun execute(action: String, args: JSONArray, callbackContext: CallbackContext): Boolean {
        when (action) {
            "pickFiles" -> {
                val mimeType = if (args.optJSONObject(0)?.optString("mimeType") != null) {
                    args.getJSONObject(0).getString("mimeType")
                } else "*"
                val multiple = args.optJSONObject(0)?.optBoolean("multiple", false) ?: false
                
                (cordova.activity as MainActivity).runOnUiThread {
                    if (multiple) {
                        (cordova.activity as MainActivity).openMultipleFilePicker(mimeType)
                    } else {
                        (cordova.activity as MainActivity).openFilePicker(mimeType)
                    }
                }
                callbackContext.success()
                return true
            }
            "clearTemp" -> {
                (cordova.activity as MainActivity).clearTempFiles()
                callbackContext.success()
                return true
            }
            else -> {
                return false
            }
        }
    }
}
