$( "#s3accesses" ).change(function() {
    console.log(this.value);
    blockUi();
    $.post( "/s3config/access/" + this.value, function() {
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
    blockUi();
    accessnamename = $('#s3accesses').select2('data');
    bucketname = $('#s3buckets').select2('data');
    $('.dataTables_filter input').val('')
    $.post( "/s3config/access/" + accessnamename.text + "/bucket/" + bucketname.text, function() {
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
    blockUi();
    $('.dataTables_filter input').val('')
    $.post( "/s3config/maxkeys/" + len, function() {
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
    blockUi();
    var table = $('#s3content').DataTable().page.info();
    newPage = table.page + 1
    $.post( "/s3config/page/" + newPage, function() {
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

$(window).bind('beforeunload', function(){
    blockUi();
});


function clickSearchPrefix(searchprefix) {
    blockUi();
    console.log(searchprefix)
    $.post( "/s3config/searchprefix/" + searchprefix, function() {
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
}