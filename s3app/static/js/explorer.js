$( document ).ready(function() {
    $.unblockUI();

    accessSelect2Config = getSelectConfig(accessData);
    accessSelect2Config.placeholder = accessData.message;
    $('#s3accesses').select2(accessSelect2Config);
    if (! accessSelect2Config.disabled) {
        $('#s3accesses').select2('val', accessData.currentName);
    }

    bucketSelect2Config = getSelectConfig(bucketData);
    bucketSelect2Config.placeholder = bucketData.message;
    $('#s3buckets').select2(bucketSelect2Config);
    if (! bucketSelect2Config.disabled) {
        $('#s3buckets').select2('val', bucketData.currentName);
    }
    refreshTable();
    $('.dataTables_filter input')
      .not(':input[type=submit]')
      .val(objectData.currentSearchPrefix);
});

function getSelectConfig(dataConfig){
    if (dataConfig.hasError) {
        return {
            data: [],
            disabled: true,
        }
    } else if (! dataConfig.isAllowed) {
        return {
            data: [],
            disabled: true,
        }
    } else if (! dataConfig.isAvailable) {
        return {
            data: [],
            disabled: true,
        }
    } else {
        return {
            data: dataConfig.data,
            disabled: false,
        }
    }
}

function refreshTable(){
    console.log(objectData.data)
    let content = objectData.data
    if ('commonPrefixesList' in objectData) {
        for (const [key, prefix] of Object.entries(objectData.commonPrefixesList)) {
            let arr = {
                'Key': prefix,
                'Size': -1,
                'LastModified': '',
                'Owner': {
                    'DisplayName': ''
                }
            }
            content.unshift(arr);
        }
    }
    const tmpJson = {
        recordsTotal: objectData.entriesAmount, // expected by DataTables to create pagination
        recordsFiltered: objectData.entriesAmount, // expected by DataTables to create pagination
        data: content, // expected by DataTables to populate the table
        currentPage: objectData.currentPageNumber // added by me to easily manage correct page displaying
    }
    placeholdertext = objectData.message
    let dataTableConfig = {
        ajax: function (data, callback, settings) {
            callback(
                tmpJson
            )
        },
        language: {
            "zeroRecords": placeholdertext,
            "emptyTable":  placeholdertext,
            "search": "Prefix Search:",
        },
        initComplete : function() {
            var input = $('.dataTables_filter input').unbind(),
                self = this.api(),
                $searchButton = $('<input>')
                    .attr('id', 'search_prefix')
                    .attr('type', 'submit')
                    .attr('value', String.fromCodePoint(0x1F50D))
                    .click(function() {
                        clickSearchPrefix(input.val());
                    }),
                $clearButton = null
            $('.dataTables_filter').append($searchButton, $clearButton);
        },
        lengthMenu: [10, 20, 50, 100],
        pageLength: objectData.maxKeys,
        serverSide: true,
        displayStart: (tmpJson.currentPage - 1) * objectData.maxKeys,
        ordering: false,
        searching: true,
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
    $('#s3content').DataTable(dataTableConfig);
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
        return ' <a class="s3Folder s3Entry" href="' + keyEscaped + '">' + paths[paths.length - 2] + '/</a>';
    }
    return ' <a download="/s3/' + keyEscaped + '" class="s3File s3Entry" id="/s3/' + row.Key + '" href="/s3/' + keyEscaped + '" >' + paths[paths.length - 1] + '</a>';
}

function lastModifiedFormat(dateString) {
    let date = new Date(dateString)
    return date.toUTCString()
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
