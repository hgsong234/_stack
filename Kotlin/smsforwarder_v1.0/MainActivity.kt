package com.example.smsforwarder

import android.Manifest
import android.content.Context
import android.content.SharedPreferences
import android.content.pm.PackageManager
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken

class MainActivity : AppCompatActivity() {

    private val PERMISSIONS_REQUEST_CODE = 100
    private val REQUIRED_PERMISSIONS = arrayOf(
        Manifest.permission.RECEIVE_SMS,
        Manifest.permission.SEND_SMS,
        Manifest.permission.READ_SMS
    )

    private lateinit var etFilterNumber: EditText
    private lateinit var etFilterWord: EditText
    private lateinit var etSubstitutionRule: EditText
    private lateinit var etForwardToNumbers: EditText
    private lateinit var btnAddRule: Button
    private lateinit var btnUpdateRule: Button
    private lateinit var btnDeleteRule: Button
    private lateinit var tvCurrentRules: TextView

    private lateinit var prefs: SharedPreferences
    private val gson = Gson()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        etFilterNumber = findViewById(R.id.et_filter_number)
        etFilterWord = findViewById(R.id.et_filter_word)
        etSubstitutionRule = findViewById(R.id.et_substitution_rule)
        etForwardToNumbers = findViewById(R.id.et_forward_to_numbers)
        btnAddRule = findViewById(R.id.btn_add_rule)
        btnUpdateRule = findViewById(R.id.btn_update_rule)
        btnDeleteRule = findViewById(R.id.btn_delete_rule)
        tvCurrentRules = findViewById(R.id.tv_current_rules)

        prefs = getSharedPreferences("SmsForwarderPrefs", Context.MODE_PRIVATE)

        checkAndRequestPermissions()
        updateRuleListUI()

        btnAddRule.setOnClickListener {
            addRule()
        }

        btnUpdateRule.setOnClickListener {
            updateRule()
        }

        btnDeleteRule.setOnClickListener {
            deleteRule()
        }
    }

    private fun checkAndRequestPermissions() {
        val missingPermissions = REQUIRED_PERMISSIONS.filter {
            ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED
        }

        if (missingPermissions.isNotEmpty()) {
            ActivityCompat.requestPermissions(this, missingPermissions.toTypedArray(), PERMISSIONS_REQUEST_CODE)
        }
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == PERMISSIONS_REQUEST_CODE) {
            if (grantResults.any { it != PackageManager.PERMISSION_GRANTED }) {
                Toast.makeText(this, "모든 권한이 필요합니다.", Toast.LENGTH_LONG).show()
            }
        }
    }

    private fun updateRuleListUI() {
        val rules = getSavedRules()
        if (rules.isEmpty()) {
            tvCurrentRules.text = "현재 등록된 규칙이 없습니다."
        } else {
            val ruleText = rules.joinToString("\n\n") {
                "번호: ${it.filterNumber}\n" +
                        "단어: ${it.filterWord}\n" +
                        "치환: ${it.substitutionRule}\n" +
                        "전달: ${it.forwardingNumbers.joinToString(", ")}"
            }
            tvCurrentRules.text = "현재 규칙 목록:\n$ruleText"
        }
    }

    private fun getSavedRules(): MutableList<ForwardingRule> {
        val json = prefs.getString("forwarding_rules", null)
        return if (json != null) {
            val type = object : TypeToken<MutableList<ForwardingRule>>() {}.type
            gson.fromJson(json, type)
        } else {
            mutableListOf()
        }
    }

    private fun saveRules(rules: List<ForwardingRule>) {
        val json = gson.toJson(rules)
        prefs.edit().putString("forwarding_rules", json).apply()
        updateRuleListUI()
    }

    private fun addRule() {
        val number = etFilterNumber.text.toString().trim()
        val word = etFilterWord.text.toString().trim()
        val substitution = etSubstitutionRule.text.toString().trim()
        val numbersToForward = etForwardToNumbers.text.toString().split(",").map { it.trim() }.filter { it.isNotBlank() }

        if (number.isBlank() && word.isBlank()) {
            Toast.makeText(this, "필터 번호나 단어를 입력해주세요.", Toast.LENGTH_SHORT).show()
            return
        }

        if (numbersToForward.isEmpty()) {
            Toast.makeText(this, "전달받을 번호를 입력해주세요.", Toast.LENGTH_SHORT).show()
            return
        }

        val rules = getSavedRules()
        val newRule = ForwardingRule(number, word, substitution, numbersToForward)
        rules.add(newRule)
        saveRules(rules)
        Toast.makeText(this, "규칙이 추가되었습니다.", Toast.LENGTH_SHORT).show()
        clearInputFields()
    }

    private fun updateRule() {
        val number = etFilterNumber.text.toString().trim()
        val word = etFilterWord.text.toString().trim()

        if (number.isBlank() && word.isBlank()) {
            Toast.makeText(this, "수정할 규칙의 번호나 단어를 입력해주세요.", Toast.LENGTH_SHORT).show()
            return
        }

        val rules = getSavedRules()
        val index = rules.indexOfFirst { it.filterNumber == number && it.filterWord == word }

        if (index != -1) {
            val newSubstitution = etSubstitutionRule.text.toString().trim()
            val newNumbersToForward = etForwardToNumbers.text.toString().split(",").map { it.trim() }.filter { it.isNotBlank() }

            if (newNumbersToForward.isEmpty()) {
                Toast.makeText(this, "전달받을 번호를 입력해주세요.", Toast.LENGTH_SHORT).show()
                return
            }

            val updatedRule = ForwardingRule(number, word, newSubstitution, newNumbersToForward)
            rules[index] = updatedRule
            saveRules(rules)
            Toast.makeText(this, "규칙이 수정되었습니다.", Toast.LENGTH_SHORT).show()
            clearInputFields()
        } else {
            Toast.makeText(this, "일치하는 규칙이 없습니다.", Toast.LENGTH_SHORT).show()
        }
    }

    private fun deleteRule() {
        val number = etFilterNumber.text.toString().trim()
        val word = etFilterWord.text.toString().trim()

        if (number.isBlank() && word.isBlank()) {
            Toast.makeText(this, "삭제할 규칙의 번호나 단어를 입력해주세요.", Toast.LENGTH_SHORT).show()
            return
        }

        val rules = getSavedRules()
        val initialSize = rules.size
        rules.removeAll { it.filterNumber == number && it.filterWord == word }

        if (rules.size < initialSize) {
            saveRules(rules)
            Toast.makeText(this, "규칙이 삭제되었습니다.", Toast.LENGTH_SHORT).show()
            clearInputFields()
        } else {
            Toast.makeText(this, "일치하는 규칙이 없습니다.", Toast.LENGTH_SHORT).show()
        }
    }

    private fun clearInputFields() {
        etFilterNumber.setText("")
        etFilterWord.setText("")
        etSubstitutionRule.setText("")
        etForwardToNumbers.setText("")
    }
}