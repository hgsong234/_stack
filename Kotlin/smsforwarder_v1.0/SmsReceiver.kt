package com.example.smsforwarder

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.provider.Telephony
import android.telephony.SmsManager
import android.util.Log
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken

class SmsReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Telephony.Sms.Intents.SMS_RECEIVED_ACTION) {
            val messages = Telephony.Sms.Intents.getMessagesFromIntent(intent)
            val prefs = context.getSharedPreferences("SmsForwarderPrefs", Context.MODE_PRIVATE)
            val gson = Gson()

            messages?.forEach { smsMessage ->
                val sender = smsMessage.originatingAddress ?: ""
                val messageBody = smsMessage.messageBody

                Log.d("SmsReceiver", "From: $sender, Body: $messageBody")

                // 저장된 규칙 목록 불러오기
                val json = prefs.getString("forwarding_rules", null)
                val rules = if (json != null) {
                    val type = object : TypeToken<List<ForwardingRule>>() {}.type
                    gson.fromJson(json, type)
                } else {
                    listOf<ForwardingRule>()
                }

                // 규칙 목록을 순회하며 일치하는 규칙 찾기
                rules.forEach { rule ->
                    val numberMatch = rule.filterNumber.isBlank() || sender.contains(rule.filterNumber)
                    val wordMatch = rule.filterWord.isBlank() || messageBody.contains(rule.filterWord)

                    if (numberMatch && wordMatch) {
                        // 일치하는 규칙을 찾았으므로 메시지 처리
                        var forwardedMessage = messageBody

                        // 문자치환 적용
                        val parts = rule.substitutionRule.split("->")
                        if (parts.size == 2) {
                            val before = parts[0].trim()
                            val after = parts[1].trim()
                            forwardedMessage = forwardedMessage.replace(before, after)
                        }

                        // 여러 번호로 문자 전달
                        for (forwardToNumber in rule.forwardingNumbers) {
                            try {
                                val smsManager = SmsManager.getDefault()
                                val finalMessage = "[문자 전달]\n발신: $sender\n내용: $forwardedMessage"
                                smsManager.sendTextMessage(forwardToNumber, null, finalMessage, null, null)
                                Log.d("SmsReceiver", "문자 전달 성공: $forwardToNumber")
                            } catch (e: Exception) {
                                Log.e("SmsReceiver", "문자 전달 실패: $forwardToNumber", e)
                            }
                        }
                        // 일치하는 첫 번째 규칙을 찾았으므로 더 이상 순회하지 않고 종료
                        return@forEach
                    }
                }
            }
        }
    }
}