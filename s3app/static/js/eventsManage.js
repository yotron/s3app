$( "#s3accesses" ).change(function() {
    console.log(this.value);
    $(".loader").css("display", "inline-block");
    $.post( "/s3config/access/" + this.value, function( data ) {
        window.location.replace("/s3manage");
    })
    .done(function() {
        console.log( "to be done" );
    })
    .fail(function() {
        console.log( "to be done" );
    })
    .always(function() {
        console.log( "to be done" );
    });
});

$( "#s3buckets" ).change(function() {
    console.log(this.value);
    $(".loader").css("display", "inline-block");
    accessnamename = $('#s3accesses').select2('data');
    bucketname = $('#s3buckets').select2('data');
    $.post( "/s3config/access/" + accessnamename.text + "/bucket/" + bucketname.text, function( data ) {
        $(".loader").css("display", "None");
        window.location.replace("/s3manage/bucket/" + bucketname.text);
    })
    .done(function() {
        console.log( "to be done" );
    })
    .fail(function() {
        console.log( "to be done" );
    })
    .always(function() {
        console.log( "to be done" );
    });
});


$('#myTabs a').click(function (e) {
    e.preventDefault()
    $(this).tab('show')
})

function eventSearchPrefix(searchPrefix) {
    window.location.replace(window.location.pathname + "?searchPrefix=" + searchPrefix);
}