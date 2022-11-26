$( "#s3accesses" ).change(function() {
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


$(window).bind('beforeunload', function(){
    blockUi();

});

$( "#s3buckets" ).change(function() {
    accessnamename = $('#s3accesses').select2('data');
    bucketname = $('#s3buckets').select2('data');
    blockUi();
    $.post( "/s3config/access/" + accessnamename.text + "/bucket/" + bucketname.text, function( data ) {
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

