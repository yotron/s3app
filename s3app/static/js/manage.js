let bucketName = "";


$( document ).ready(function() {
    $('#s3accesses').select2({
        data: accessData.data
    }).select2('val', accessData.currentName);
    if ($('#s3accessmanagebuckets')[0]) {
        refreshTableBuckets();
    }
    if ($('#s3buckets')[0]) {
        if (bucketData.currentName != null) {
            $('#s3buckets').select2({
                data: bucketData.data
            }).select2('val', bucketData.currentName);
        } else {
            $('#s3buckets').select2({
                data: []
            })
        }
        setMetrics(bucketData.currentName)
    }
});


function refreshTableBuckets(){
    let content = []
    for (const [key, bucket] of Object.entries(bucketData.data)) {
        let arr = {
            'BucketName': bucket["text"],
            'Region': bucket["region"],
            'CreationDate': bucket["creationdate"],
            'Owner': bucket["owner"],
        }
        content.unshift(arr);
    }
    const tmpJson = {
        recordsTotal: bucketData.entriesAmount, // expected by DataTables to create pagination
        recordsFiltered: bucketData.entriesAmount, // expected by DataTables to create pagination
        data: content, // expected by DataTables to populate the table
        currentPage: bucketData.currentPageNumber // added by me to easily manage correct page displaying
    }
    let dataTableConfig = {
        ajax: function (data, callback, settings) {
            callback(
                tmpJson
            )
        },
        columns: [
            { data: 'BucketName', render: {
                    display: function (data, type, row) {
                        return bucketGetURL(data)
                    }
                } },
            { data: 'Region' },
            { data: 'CreationDate', render: {
                    display: function (data, type, row) {
                        return lastModifiedFormat(data)
                    }
                }
            },
            { data: 'Owner' },
        ],
        language: {
            "emptyTable": bucketData.message
        },
    }
    if (tmpJson.currentPage == null) {
        dataTableConfig.paging = false
    }
    $('#s3accessmanagebuckets').DataTable(dataTableConfig);
}


function bucketGetURL(key, row) {
    return ' <a class="s3File" id="/s3manage/bucket/' + key + '" href="/s3manage/bucket/' + key + '" >' + key + '</a>';
}

function lastModifiedFormat(dateString) {
    let date = new Date(dateString)
    return date.toUTCString()
}

async function setMetrics(bucketName) {
    const result = await getMetrics(bucketName);
}

function getMetrics(bucketName) {
    console.log("Get metrics from Bucket: " + bucketName);
    $.get("/s3manage/metrics/" + bucketName, function (data) {
        console.log(data);
        $("#metrics_amount_content").text(data.bucketAmount);
        $("#metrics_size_content").text(fileSizeFormat(data.bucketSize));
    })
    .done(function () {
        console.log("to be done");
    })
    .fail(function () {
        console.log("to be done");
    })
    .always(function () {
        console.log("to be done");
    });
    console.log("1")
}

function fileSizeFormat(b) {
    var u = 0, s=1024;
    while (b >= s || -b >= s) {
        b /= s;
        u++;
    }
    return (u ? b.toFixed(1) + ' ' : b) + ' KMGTPEZY'[u] + 'B';
}

function blockUi() {
    if ($('.blockOverlay').length === 0) {
        $.blockUI({
            message: $('#throbber'),
            overlayCSS: {
                backgroundColor: '#000',
                opacity: 0.4,
                cursor: 'wait'
            }
        });
    }
}