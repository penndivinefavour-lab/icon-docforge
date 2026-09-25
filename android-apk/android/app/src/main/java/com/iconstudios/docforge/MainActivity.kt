package com.iconstudios.docforge

import android.annotation.SuppressLint
import android.graphics.Bitmap
import android.os.Build
import android.os.Bundle
import android.view.KeyEvent
import android.webkit.WebChromeClient
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.FileProvider
import java.io.File

class MainActivity : AppCompatActivity() {
    
    private lateinit var webView: WebView
    
    companion object {
        const val TAG = "IconDocForge"
        const val API_PORT = 8765
    }
    
    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        webView = WebView(this)
        setContentView(webView)
        
        val settings = webView.settings
        settings.javaScriptEnabled = true
        settings.domStorageEnabled = true
        settings.cacheMode = WebSettings.LOAD_DEFAULT
        settings.loadsImagesAutomatically = true
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            settings.setSafeBrowsingEnabled(false)
        }
        
        webView.webViewClient = object : WebViewClient() {
            override fun onPageStarted(view: WebView, url: String?, favicon: Bitmap?) {
                super.onPageStarted(view, url, favicon)
            }
            
            override fun onPageFinished(view: WebView, url: String?) {
                super.onPageFinished(view, url)
            }
        }
        
        webView.webChromeClient = WebChromeClient()
        
        val apiBase = "http://127.0.0.1:$API_PORT"
        val html = """
            <!DOCTYPE html>
            <html>
            <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"></head>
            <body><script>
                window.ICON_DOCFORGE_API_BASE = "$apiBase";
                window.ICON_DOCFORGE_OFFLINE = true;
            </script></body>
            </html>
        """.trimIndent()
        
        webView.loadDataWithBaseURL(
            "file:///android_asset/public/",
            html,
            "text/html",
            "UTF-8",
            "file:///android_asset/public/index.html"
        )
    }
    
    override fun onKeyDown(keyCode: Int, event: KeyEvent?): Boolean {
        if (keyCode == KeyEvent.KEYCODE_BACK && webView.canGoBack()) {
            webView.goBack()
            return true
        }
        return super.onKeyDown(keyCode, event)
    }
    
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
}
