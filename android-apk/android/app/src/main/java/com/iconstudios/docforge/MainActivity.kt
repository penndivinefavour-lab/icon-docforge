package com.iconstudios.docforge

import android.annotation.SuppressLint
import android.graphics.Bitmap
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.view.Gravity
import android.view.KeyEvent
import android.view.View
import android.view.ViewGroup
import android.webkit.*
import android.widget.FrameLayout
import android.widget.ProgressBar
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.FileProvider
import java.io.File

class MainActivity : AppCompatActivity() {

    companion object {
        const val TAG = "IconDocForge"
        const val API_PORT = 8765
    }

    private lateinit var webView: WebView
    private lateinit var progressBar: ProgressBar

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Create container
        val container = FrameLayout(this)
        setContentView(container)

        // Create WebView
        webView = WebView(this).apply {
            layoutParams = FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )
        }

        // Create progress bar
        progressBar = ProgressBar(this).apply {
            layoutParams = FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT,
                ViewGroup.LayoutParams.WRAP_CONTENT,
                Gravity.CENTER
            )
            visibility = View.VISIBLE
        }

        container.addView(webView)
        container.addView(progressBar)

        // Configure WebView
        val settings = webView.settings
        settings.javaScriptEnabled = true
        settings.domStorageEnabled = true
        settings.cacheMode = WebSettings.LOAD_DEFAULT
        settings.loadsImagesAutomatically = true
        settings.allowFileAccess = true
        settings.allowContentAccess = true
        settings.useWideViewPort = true
        settings.loadWithOverviewMode = true
        settings.pluginState = WebSettings.PluginState.ON_DEMAND

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            settings.setSafeBrowsingEnabled(false)
        }

        // Set up WebViewClient - intercept HTML to inject config BEFORE execution
        webView.webViewClient = object : WebViewClient() {
            override fun onPageStarted(view: WebView?, url: String?, favicon: Bitmap?) {
                super.onPageStarted(view, url, favicon)
                progressBar.visibility = View.VISIBLE
            }

            override fun onPageFinished(view: WebView?, url: String?) {
                super.onPageFinished(view, url)
                progressBar.visibility = View.GONE
            }

            override fun shouldInterceptRequest(view: WebView?, request: WebResourceRequest?): WebResourceResponse? {
                val url = request?.url.toString()
                if (url.endsWith(".js")) {
                    try {
                        val path = java.net.URL(url).path
                        if (path.contains("/app.js") || path.contains("/main.js")) {
                            val assetName = path.replaceFirst("/", "assets/public/")
                            val inputStream = assets.open(assetName)
                            val content = inputStream.bufferedReader().readText()
                            inputStream.close()

                            // Inject config before the module runs
                            val injectedContent = """
                                window.ICON_DOCFORGE_OFFLINE = true;
                                window.ICON_DOCFORGE_API_BASE = 'http://127.0.0.1:$API_PORT';
                                $content
                            """.trimIndent()

                            return WebResourceResponse(
                                "application/javascript",
                                "UTF-8",
                                injectedContent.byteInputStream()
                            )
                        }
                    } catch (e: Exception) {
                        android.util.Log.e(TAG, "Failed to intercept JS: ${e.message}")
                    }
                }
                return super.shouldInterceptRequest(view, request)
            }

            override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
                val reqUrl = request?.url.toString()
                if (reqUrl.startsWith("file://") || reqUrl.startsWith("http://127.0.0.1") ||
                    reqUrl.startsWith("https://") || reqUrl.startsWith("javascript:")) {
                    return false
                }
                // Handle custom URL schemes
                try {
                    startActivity(android.content.Intent(android.content.Intent.ACTION_VIEW, Uri.parse(reqUrl)))
                    return true
                } catch (e: Exception) {
                    return false
                }
            }

            override fun onReceivedError(view: WebView?, request: WebResourceRequest?, error: WebResourceError?) {
                super.onReceivedError(view, request, error)
                if (request?.isForMainFrame == true) {
                    android.util.Log.e(TAG, "Failed to load page: ${error?.description}")
                }
            }
        }

        // Set up WebChromeClient for progress and dialogs
        webView.webChromeClient = object : WebChromeClient() {
            override fun onProgressChanged(view: WebView?, newProgress: Int) {
                if (newProgress > 70) {
                    progressBar.visibility = View.GONE
                }
                super.onProgressChanged(view, newProgress)
            }

            override fun onJsAlert(view: WebView?, url: String?, message: String?, result: JsResult?): Boolean {
                result?.confirm()
                return true
            }

            override fun onJsConfirm(view: WebView?, url: String?, message: String?, result: JsResult?): Boolean {
                result?.confirm()
                return true
            }

            override fun onJsPrompt(view: WebView?, url: String?, message: String?, defaultValue: String?, result: JsPromptResult?): Boolean {
                result?.confirm(defaultValue ?: "")
                return true
            }
        }

        // Add JavaScript interface for native functionality
        webView.addJavascriptInterface(object : Any() {
            @JavascriptInterface
            fun getFileUri(filePath: String): String? {
                return try {
                    val file = File(filePath)
                    if (file.exists()) {
                        val uri = FileProvider.getUriForFile(
                            this@MainActivity,
                            "${packageName}.fileprovider",
                            file
                        )
                        uri.toString()
                    } else {
                        null
                    }
                } catch (e: Exception) {
                    e.printStackTrace()
                    null
                }
            }
        }, "AndroidBridge")

        // Load the web app
        val url = "file:///android_asset/public/index.html"
        android.util.Log.d(TAG, "Loading: $url")
        webView.loadUrl(url)
    }

    // Handle back button for WebView navigation
    override fun onKeyDown(keyCode: Int, event: KeyEvent?): Boolean {
        if (keyCode == KeyEvent.KEYCODE_BACK) {
            if (webView.canGoBack()) {
                webView.goBack()
                return true
            }
        }
        return super.onKeyDown(keyCode, event)
    }

    // Handle activity recreation
    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        webView.saveState(outState)
    }

    // Restore WebView state
    override fun onRestoreInstanceState(savedInstanceState: Bundle) {
        super.onRestoreInstanceState(savedInstanceState)
        webView.restoreState(savedInstanceState)
    }

    override fun onResume() {
        super.onResume()
        webView.onResume()
        webView.resumeTimers()
    }

    override fun onPause() {
        super.onPause()
        webView.onPause()
        webView.pauseTimers()
    }

    override fun onDestroy() {
        super.onDestroy()
        webView.destroy()
    }
}
