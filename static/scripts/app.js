"use strict";

function showSuccess(result) {
    alert(result);
}

function sendSms(evt) {
    evt.preventDefault();

    var formInputs = {
        "input_number": $("#sendtoNo").val(),
        "company": $("#company").val(),
        "time": $("#time").val()
    };

    $.post("/sms", formInputs, showSuccess);
}

$("#send-sms").on("submit", sendSms);


function sendSms2(evt) {
    evt.preventDefault();

    var formInputs = {
        "input_number": $("#sendtoNo2").val(),
        "company": $("#company2").val(),
        "time": $("#time2").val()
    };

    $.post("/sms", formInputs, showSuccess);
}

$("#second-send-sms").on("submit", sendSms2);