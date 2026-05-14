package com.example.licenseadmin

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.os.Bundle
import android.util.Base64
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import org.json.JSONObject
import java.security.KeyFactory
import java.security.PrivateKey
import java.security.PublicKey
import java.security.Signature
import java.security.spec.PKCS8EncodedKeySpec
import java.security.spec.X509EncodedKeySpec

class MainActivity : AppCompatActivity() {
    companion object {
        private const val PRIVATE_KEY_PEM = """
-----BEGIN PRIVATE KEY-----
MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDPdlDp/JH5oj6x
PsFB9f1H1dMIwwd2AHCmlKJie1GwXrr0u/p+bc7yOj0j2J0PEGBJPcbcR5Hp6hd3
O3MhCHc5obdVq+SK8JLnCjBHch5TN2jSqA5W2jAq30NF03rvhxOUomEmop/4A405
BmZ5dZN2Se5XievFFr9zIEZcn8AIxY7D9spJPBL2vPTUbXMPXHtzfQC8+IohThDH
E0qcDVUPQEGZEXfI8SVTUFnpNNc2/fe/i5237zdkR5k7SZIIqkpsCLTu6XzIIiyn
p7SeHpeLQXpQ/USE0r7MugGMB1a6sLAnkAf0+xWkDscSqbeldRMH2x5F2upZOcJj
6wcax1TRAgMBAAECggEATyE8yZK5hvLYYLij8+nEmrK3FJ926A5Q6WjF6zRIOzJW
suRELhbqGUAXc+W6OjWv1B/JCtoNkJ/mJWc6iX32I7hH+lhfCpOqJI+hTI79fBYl
WDwbhAsi1idkPGzmdhgaYtXwolDjHTEVm4uSaH9tKHAYhbEoiXscuOe1jryr/WvU
uHyUIqgG0XXW7lwAWsEIh0AOThT4t4eFcUFP0RJYI+rszUSEQqBVhdN0nxQ1WqAN
hZ8vYXnstSX+brSvw3JVlKuX0cWGvZY4iRS09rl76kfkeKuQf0bfif56+K9z00kf
zZkA2I/edG8Y5P3mSx/1vOgbasttm5O4o1gJNqUOtQKBgQD4KAXyNtOKo97LW7vp
cy9DPRec8UyytuGOBRtbQm2Q07I1fxdzLXccYJLjDuNTjyITNAOf4sadld/1yflI
5rDc9vJkN1YDUhrOwj4utkmoFinl9C+64gWE7HP8Wiv5S61veoQf0bfif56+K9z00kf
zZkA2I/edG8Y5P3mSx/1vOgbasttm5O4o1gJNqUOtQKBgQDWBQNC+kngKwCRinE3
HpWgQq32twBqZIhgoD8kOLzj8nErfSZBNAYiKRSNFL8SDSvYMoxVcyg68OZ9mBiO
74EqHwngn4QQ/9XMSIObZcN6T3UivZUGWvIGUrV0mN57utl6TmOiyxsKJZOT7lav
tPP1//l2T2JfcWuNa8mhNBpq7wKBgFPfAxN4IEstU3Gb0Yj3WzP4g/CRRYDpepZL
d5GChBF82zBlggF1jlpS8ZI4R/DH4ZZn8Amr1cERFJ634r8W6RPlissAQNvidhkH
YYjcJ0zeIM8Nlsws8/yXBiR2PYKGZ1nUKKcVLiuJQDDIzLAMb/+qVOTiUPvh4LD1
MClLvVx1AoGARGo5zrFf6E8W0W+mHW6jeiWWouWBNoGIrwrK5HNWvq+Dydkp33IX
+9eSAD9/jO+08lnGTpKPa7gSlleGkjqx2ZsudyXG/AAsgi80EvsG8BRyZ3afKvbr
o2XRJ8KubHMgjl58r0+qByZX9NQd1fFMg3keb9mUotoI/Z5VSDj1sPUCgYAQ9yAf
zMwwukrXm9eY/P5OlOwk6vazliqjh+KBiwDmmHkRn2+6EYarmRFGi3PH7QY3g3lD
gCcjDWn7ckVOIHPVxxaMDPMcClHeREktNWZQecUDwzoSyt1TAxtxLGd4+YTE0bmh
Flm0PRZb5CsTnNmtqscBoJPvlIYw2b9SsgkFLw==
-----END PRIVATE KEY-----"""

        // Derived public key (RSA modulus from above) – used for verification
        private const val PUBLIC_KEY_PEM = """
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAz3ZQ6fyR+aI+sT7BQfX9
R9XTCMMHdgBwppSiYntRsF669Lv6fu3O8jo9I9idDxBgST3G3EeR6eoXdzt zIQh3
OaG3VavkivCS5wowR3IeUzdo0qgOVtowKt9DRdN674cTlKJhJqKf+AONOQZmeXWT
dknuV4nrxRa/cyBGXJ/ACMWOw/bKSTwS9rz01G1zD1x7c30AvPiKIU4QxxNKnA1V
D0BBmRF3yPElU1BZ6TTXNv33v4udt+83ZEeZO0mSCKpKbAi07ul8yCIsp6e0nh6X
i0F6UP1ElNK+zLoBjAdWurCwJ5AH9PsVpA7HEqm3pXUTB9seRdrqWTnCY+sHGsdU
0QIDAQAB
-----END PUBLIC KEY-----"""
    }

    private lateinit var inputUser: EditText
    private lateinit var inputExpiry: EditText
    private lateinit var inputFeatures: EditText
    private lateinit var outputLicense: TextView
    private lateinit var inputLicenseToken: EditText
    private lateinit var outputVerify: TextView
    private var lastToken: String = ""

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        inputUser         = findViewById(R.id.inputUser)
        inputExpiry       = findViewById(R.id.inputExpiry)
        inputFeatures     = findViewById(R.id.inputFeatures)
        outputLicense     = findViewById(R.id.outputLicense)
        inputLicenseToken = findViewById(R.id.inputLicenseToken)
        outputVerify      = findViewById(R.id.outputVerify)

        findViewById<Button>(R.id.buttonGenerate).setOnClickListener { generateLicense() }
        findViewById<Button>(R.id.buttonCopy).setOnClickListener    { copyToken() }
        findViewById<Button>(R.id.buttonVerify).setOnClickListener  { verifyToken() }
    }

    private fun generateLicense() {
        val user     = inputUser.text.toString().trim()
        val expiry   = inputExpiry.text.toString().trim()
        val features = inputFeatures.text.toString()
            .split(',').map { it.trim() }.filter { it.isNotEmpty() }

        if (user.isEmpty() || expiry.isEmpty()) {
            outputLicense.text = "⚠  Please enter user name and expiry date."
            return
        }

        val payload = JSONObject().apply {
            put("user", user)
            put("expiry", expiry)
            put("features", features.joinToString(","))
            put("license_id", "LIC-${System.currentTimeMillis()}")
            put("issued", System.currentTimeMillis() / 1000)
        }

        lastToken = try {
            signPayload(payload)
        } catch (e: Exception) {
            "ERROR: ${e.message}"
        }
        outputLicense.text = lastToken
    }

    private fun copyToken() {
        if (lastToken.isEmpty()) { Toast.makeText(this, "Generate a token first", Toast.LENGTH_SHORT).show(); return }
        val cm = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        cm.setPrimaryClip(ClipData.newPlainText("license_token", lastToken))
        Toast.makeText(this, "Token copied to clipboard", Toast.LENGTH_SHORT).show()
    }

    private fun verifyToken() {
        val token = inputLicenseToken.text.toString().trim()
        if (token.isEmpty()) { Toast.makeText(this, "Paste a token first", Toast.LENGTH_SHORT).show(); return }
        outputVerify.visibility = View.VISIBLE
        outputVerify.text = try {
            val json = String(Base64.decode(token, Base64.DEFAULT), Charsets.UTF_8)
            val obj  = JSONObject(json)
            val payload   = obj.getJSONObject("payload")
            val sigBytes  = Base64.decode(obj.getString("signature"), Base64.NO_WRAP)
            val payloadBytes = payload.toString().toByteArray(Charsets.UTF_8)

            val pubKey = loadPublicKey()
            val verifier = Signature.getInstance("SHA256withRSA")
            verifier.initVerify(pubKey)
            verifier.update(payloadBytes)
            val valid = verifier.verify(sigBytes)

            if (valid) {
                outputVerify.setBackgroundColor(0xFFF0FDF4.toInt())
                outputVerify.setTextColor(0xFF166534.toInt())
                "✅  VALID\nUser: ${payload.optString("user")}\n" +
                "Expiry: ${payload.optString("expiry")}\n" +
                "Features: ${payload.optString("features")}\n" +
                "ID: ${payload.optString("license_id")}"
            } else {
                outputVerify.setBackgroundColor(0xFFFEF2F2.toInt())
                outputVerify.setTextColor(0xFF991B1B.toInt())
                "❌  INVALID – signature mismatch"
            }
        } catch (e: Exception) {
            outputVerify.setBackgroundColor(0xFFFEF2F2.toInt())
            outputVerify.setTextColor(0xFF991B1B.toInt())
            "❌  ERROR: ${e.message}"
        }
    }

    private fun signPayload(payload: JSONObject): String {
        val privateKey = loadPrivateKey()
        val jsonBytes  = payload.toString().toByteArray(Charsets.UTF_8)
        val signer = Signature.getInstance("SHA256withRSA")
        signer.initSign(privateKey)
        signer.update(jsonBytes)
        val token = JSONObject().apply {
            put("payload", payload)
            put("signature", Base64.encodeToString(signer.sign(), Base64.NO_WRAP))
        }
        return Base64.encodeToString(token.toString().toByteArray(Charsets.UTF_8), Base64.NO_WRAP)
    }

    private fun loadPrivateKey(): PrivateKey {
        val pem = PRIVATE_KEY_PEM
            .replace("-----BEGIN PRIVATE KEY-----", "")
            .replace("-----END PRIVATE KEY-----", "")
            .replace(Regex("\\s"), "")
        return KeyFactory.getInstance("RSA")
            .generatePrivate(PKCS8EncodedKeySpec(Base64.decode(pem, Base64.DEFAULT)))
    }

    private fun loadPublicKey(): PublicKey {
        val pem = PUBLIC_KEY_PEM
            .replace("-----BEGIN PUBLIC KEY-----", "")
            .replace("-----END PUBLIC KEY-----", "")
            .replace(Regex("\\s"), "")
        return KeyFactory.getInstance("RSA")
            .generatePublic(X509EncodedKeySpec(Base64.decode(pem, Base64.DEFAULT)))
    }
}
