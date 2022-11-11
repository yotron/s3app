$( "#s3accesses" ).change(function() {
    console.log(this.value);
    $(".loader").css("display", "inline-block");
    $.post( "/s3config/access/" + this.value, function( data ) {
        $('.dataTables_filter input').val('')
        window.location.replace("/s3");
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
    $('.dataTables_filter input').val('')
    $.post( "/s3config/access/" + accessnamename.text + "/bucket/" + bucketname.text, function( data ) {
        $(".loader").css("display", "None");
        window.location.replace("/s3");
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

$('#s3content').on( 'length.dt', function ( e, settings, len ) {
    $(".loader").css("display", "inline-block");
    $('.dataTables_filter input').val('')
    $.post( "/s3config/maxkeys/" + len, function( data ) {
        window.location.replace("/s3" + window.location.search);
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
} );

$('#s3content').on( 'page.dt', function () {
    $(".loader").css("display", "inline-block");
    var table = $('#s3content').DataTable().page.info();
    newPage = table.page + 1
    $.post( "/s3config/page/" + newPage, function( data ) {
       window.location.reload();
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
} );

$('#myTabs a').click(function (e) {
    e.preventDefault()
    $(this).tab('show')
})

function eventSearchPrefix(searchPrefix) {
    window.location.replace(window.location.pathname + "?searchPrefix=" + searchPrefix);
}