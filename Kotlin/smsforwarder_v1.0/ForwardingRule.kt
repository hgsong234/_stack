package com.example.smsforwarder

data class ForwardingRule(
    val filterNumber: String,
    val filterWord: String,
    val substitutionRule: String,
    val forwardingNumbers: List<String>
)