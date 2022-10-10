let bucketName = "";
let tableData = {};

$( document ).ready(function() {
    $('#s3access').select2({
        data: accessList
    }).select2('val', setting.currentAccessName);
    refreshTable();
    paths = window.location.pathname.split('/');
    if (setting.currentBucketName != null) {
        $('#s3bucket').select2({
            data: bucketList
        }).select2('val', setting.currentBucketName);
    } else {
        $('#s3bucket').select2({
            data: []
        })
    }
    $('.dataTables_filter input')
        .not(':input[type=submit]')
        .val(setting.currentSearchPrefix);
});


function refreshTable(){
    for (const [key, prefix] of Object.entries(commonPrefixes)) {
        let arr = {
            'Key': prefix,
            'Size': -1,
            'LastModified': '',
            'Owner': {
                'DisplayName': ''
            }
        }
        contents.unshift(arr);
    }
    const tmpJson = {
        recordsTotal: setting.entriesAmount, // expected by DataTables to create pagination
        recordsFiltered: setting.entriesAmount, // expected by DataTables to create pagination
        data: contents, // expected by DataTables to populate the table
        currentPage: setting.currentPageNumber // added by me to easily manage correct page displaying
    }
    let dataTableConfig = {
        ajax: function (data, callback, settings) {
            callback(
                tmpJson
            )
        },
        initComplete : function() {
            var input = $('.dataTables_filter input').unbind(),
                self = this.api(),
                $searchButton = $('<input>')
                    .attr('id', 'search_prefix')
                    .attr('type', 'submit')
                    .attr('value', String.fromCodePoint(0x1F50D))
                    .click(function() {
                        eventSearchPrefix(input.val());
                    }),
                $clearButton = null
            $('.dataTables_filter').append($searchButton, $clearButton);
        },
        lengthMenu: [10, 20, 50, 100],
        pageLength: setting.maxKeys,
        serverSide: true,
        displayStart: (tmpJson.currentPage - 1) * setting.maxKeys,
        ordering: false,
        searching: true,
        language: {
            "search": "Prefix Search:"
        },
        columns: [
            {
                data: 'Key', render: {
                    display: function (data, type, row) {
                        return linksFormat(data, row);
                    }
                }
            },
            {
                data: 'Size', render: {
                    display: function (data, type, row) {
                        return row.Size >= 0 ? fileSizeFormat(data) : ""
                    }
                }
            },
            {
                data: 'LastModified', render: {
                    display: function (data, type, row) {
                        return row.Size >= 0 ? lastModifiedFormat(data) : ""
                    }
                }
            }
        ],
    }
    if (tmpJson.currentPage == null) {
        dataTableConfig.paging = false
    }
    $('#example').DataTable(dataTableConfig);
}

function fileSizeFormat(b) {
    var u = 0, s=1024;
    while (b >= s || -b >= s) {
        b /= s;
        u++;
    }
    return (u ? b.toFixed(1) + ' ' : b) + ' KMGTPEZY'[u] + 'B';
}

function linksFormat(key, row) {
    let paths = key.split('/');
    replace = key.replace("/", "<->")
    let keyEscaped = encodeURIComponent(key.replaceAll("/", " "));
    if (row.Size < 0) {
        return ' <a class="s3Folder" href="' + keyEscaped + '">' + paths[paths.length - 2] + '/</a>';
    }
    return ' <a class="s3File" id="/s3/' + row.Key + '" href="/s3/' + keyEscaped + '" >' + paths[paths.length - 1] + '</a>';
}

function lastModifiedFormat(dateString) {
    let date = new Date(dateString)
    return date.toUTCString()
}