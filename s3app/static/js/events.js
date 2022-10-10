$( "#s3access" ).change(function() {
    console.log(this.value);
    $(".loader").css("display", "inline-block");
    $.post( "/s3config/access/" + this.value, function( data ) {
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

$( "#s3bucket" ).change(function() {
    console.log(this.value);
    $(".loader").css("display", "inline-block");
    accessnamename = $('#s3access').select2('data');
    bucketname = $('#s3bucket').select2('data');
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

$('#example').on( 'length.dt', function ( e, settings, len ) {
    $(".loader").css("display", "inline-block");
    $.post( "/s3config/maxkeys/" + len, function( data ) {
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
} );

$('#example').on( 'page.dt', function () {
    $(".loader").css("display", "inline-block");
    var table = $('#example').DataTable().page.info();
    newPage = table.page + 1
    $.post( "/s3config/page/" + newPage, function( data ) {
        $(".loader").css("display", "None");
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

$('#exssample').on( 'search.dt', function () {
    console.log(this.value);
    $(".loader").css("display", "inline-block");
    accessnamename = $('#s3access').select2('data');
    bucketname = $('#s3bucket').select2('data');
    $.post( "/s3config/access/" + accessnamename.text + "/bucket/" + bucketname.text + "?searchPrefix=" + this.value, function( data ) {
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

function eventSearchPrefix(searchPrefix) {
    window.location.replace(window.location.pathname + "?searchPrefix=" + searchPrefix);
}