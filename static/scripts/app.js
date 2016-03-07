"use strict";

function showSuccess(result) {
    alert(result);
}

function sendSms(evt) {
    evt.stopImmediatePropagation();
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

var fetchedExchangeRate = false;

$('.details-link').click(function() {
    var detailsLink = $(this)
    var detailsSection = detailsLink.parent().find('.rate-details')

    detailsSection.toggle('slow', function() {
        if (detailsSection.is(':visible')) {
            detailsLink.text('Hide Details')

             if(!fetchedExchangeRate) {
                $.get('http://apilayer.net/api/live?access_key=b182bc74787f1644a0fded0084ac5c06&currencies=' + currency + '&source=USD')
                .done(function(data) {
                    var quote = data.quotes['USD' + currency]
                    var convertedAmount = quote ?  parseInt(quote * amount) + ' ' + currency : amount + 'USD'

                    detailsLink.parent().find('.spinner-wrapper').text(convertedAmount)
                })
                .fail(function() {
                    detailsLink.parent().find('.spinner-wrapper').text(amount + 'USD')
                })
                .always(function() {
                   fetchedExchangeRate = true; 
                });
            }
        } else {
            detailsLink.text('Show Details')
        }
    })
})

