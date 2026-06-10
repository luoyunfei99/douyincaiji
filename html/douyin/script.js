// var apihost = 'http://192.168.31.164:8000';
var apihost = 'http://127.0.0.1:8000';

// 过滤空参数的函数
function filterEmptyParams(formData) {
    return formData.filter(function (item) {
        return item.value!== '';
    });
}

// 获取所有 Douyin Hao URL 记录
function getDouyinHaoUrls(page) {
    var form = $('#get-all-douyin-hao-urls-form');
    form.find('input[name="page"]').val(page);
    var formData = form.serializeArray();
    formData = filterEmptyParams(formData);
    var queryString = $.param(formData);
    $.ajax({
        url: `${apihost}/douyin_hao_url/?` + queryString,
        type: 'GET',
        success: function (response) {
            var tableBody = $('#douyin-hao-urls-table tbody');
            tableBody.empty();
            totalRecords = response.total_count || 0;
            response.data.forEach(function (item) {
                var row = '<tr data-id="' + item.id + '">' +
                    '<td>' + item.id + '</td>' +
                    '<td>' + item.url + '</td>' +
                    '<td>' + item.keyword + '</td>' +
                    '<td>' + item.level + '</td>' +
                    '<td>' + item.hangye + '</td>' +
                    '<td>' + item.hangye_type + '</td>' +
                    '<td>' + item.last_runtime + '</td>' +
                    '<td>' + item.status + '</td>' +
                    '<td>' + item.touser + '</td>' +
                    '<td>' + item.phone + '</td>' +
                    '<td>' + item.signature + '</td>' +
                    '<td>' + item.nickname + '</td>' +
                    '<td>' + item.unique_id + '</td>' +
                    '<td>' +
                    '<button onclick="deleteDouyinHaoUrl(' + item.id + ')">删除</button>' +
                    '<button onclick="isFans(' + item.id + ')">重新抓取粉丝</button>' +
                    '<button onclick="exportDouyinHaoFans(' + item.id + ')">导出粉丝列表</button>' +
                    '</td>' +
                    '</tr>';
                tableBody.append(row);
            });
            // 生成分页导航
            generatePagination('douyin-hao-urls-pagination', page, totalRecords, formData, 'getDouyinHaoUrls');
        },
        error: function (error) {
            alert('Error: ' + error.responseJSON.message);
        }
    });
}

function generatePagination(paginationId, currentPage, totalRecords, formData, pagefun) {
    var paginationDiv = $('#' + paginationId);
    paginationDiv.empty();
    var pageSize = parseInt($.grep(formData, function (e) { return e.name === 'page_size'; })[0].value);
    var totalPages = Math.ceil(totalRecords / pageSize);
    var showPages = 10; // 中间显示的页码数量

    // 上一页按钮
    if (currentPage > 1) {
        paginationDiv.append('<button onclick="' + pagefun + '(' + (currentPage - 1) + ')">上一页</button>');
    }

    // 第一页按钮
    if (currentPage > showPages / 2 + 1) {
        paginationDiv.append('<button onclick="' + pagefun + '(1)">1</button>');
        if (currentPage > showPages / 2 + 2) {
            paginationDiv.append('<span>...</span>');
        }
    }

    // 中间显示的页码
    var start = Math.max(1, currentPage - Math.floor(showPages / 2));
    var end = Math.min(totalPages, start + showPages - 1);
    for (var i = start; i <= end; i++) {
        if (i === currentPage) {
            paginationDiv.append('<button disabled>' + i + '</button>');
        } else {
            paginationDiv.append('<button onclick="' + pagefun + '(' + i + ')">' + i + '</button>');
        }
    }

    // 最后一页按钮
    if (currentPage < totalPages - Math.floor(showPages / 2)) {
        if (currentPage < totalPages - Math.floor(showPages / 2) - 1) {
            paginationDiv.append('<span>...</span>');
        }
        paginationDiv.append('<button onclick="' + pagefun + '(' + totalPages + ')">' + totalPages + '</button>');
    }

    // 下一页按钮
    if (currentPage < totalPages) {
        paginationDiv.append('<button onclick="' + pagefun + '(' + (currentPage + 1) + ')">下一页</button>');
    }
}

// 获取所有 Douyin Hao URL 记录
function getDouyinUrls(page) {
    var form = $('#get-all-douyin-urls-form');
    form.find('input[name="page"]').val(page);
    var formData = form.serializeArray();
    formData = filterEmptyParams(formData);
    var queryString = $.param(formData);
    $.ajax({
        url: `${apihost}/douyin_url/?` + queryString,
        type: 'GET',
        success: function (response) {
            var tableBody = $('#douyin-urls-table tbody');
            tableBody.empty();
            totalRecords = response.total_count || 0;
            response.data.forEach(function (item) {
                var row = '<tr>' +
                    '<td>' + item.id + '</td>' +
                    '<td>' + item.url + '</td>' +
                    '<td>' + item.keyword + '</td>' +
                    '<td>' + item.level + '</td>' +
                    '<td>' + (item.status?'启用':'暂停') + '</td>' +
                    '<td>' + item.hangye + '</td>' +
                    '<td>' + item.hangye_type + '</td>' +
                    '<td>' + item.type + '</td>' +
                    '<td>' + item.comment_count + '</td>' +
                    '<td>' + item.last_runtime + '</td>' +
                    '<td>' +
                    '<button onclick="updateDouyinUrl(' + item.id + ')">更新</button> ' +
                    '<button onclick="deleteDouyinUrl(' + item.id + ')">删除</button> ' +
                    '<button onclick="setDouyinUrlStatus(' + item.id + ','+(item.status?0:1)+')">'+(item.status?'暂停':'启用')+'</button>' +
                    '</td>' +
                    '</tr>';
                tableBody.append(row);
            });
            // 生成分页导航
            generatePagination('douyin-urls-pagination', page, totalRecords, formData, 'getDouyinUrls');
        },
        error: function (error) {
            alert('Error: ' + error.responseJSON.message);
        }
    });
}

// 获取所有 Douyin Hao URL 记录
function getDouyinHistoryUrls(page) {
    var form = $('#get-all-douyin_history_urls-form');
    form.find('input[name="page"]').val(page);
    var formData = form.serializeArray();
    formData = filterEmptyParams(formData);
    var queryString = $.param(formData);
    $.ajax({
        url: `${apihost}/douyin_history_url/?` + queryString,
        type: 'GET',
        success: function (response) {
            var tableBody = $('#douyin_history_urls-table tbody');
            tableBody.empty();
            totalRecords = response.total_count || 0;
            response.data.forEach(function (item) {
                var row = '<tr>' +
                    '<td>' + item.id + '</td>' +
                    '<td>' + item.url + '</td>' +
                    '<td>' + item.status + '</td>' +
                    '<td>' + item.keyword + '</td>' +
                    '<td>' + item.hangye + '</td>' +
                    '<td>' + item.comment_count + '</td>' +
                    '<td>' +
                    '<button onclick="updateDouyinHistoryUrl(' + item.id + ')">更新</button> ' +
                    '<button onclick="deleteDouyinHistoryUrl(' + item.id + ')">删除</button>' +
                    '</td>' +
                    '</tr>';
                tableBody.append(row);
            });
            // 生成分页导航
            generatePagination('douyin_history_urls-pagination', page, totalRecords, formData, 'getDouyinHistoryUrls');
        },
        error: function (error) {
            alert('Error: ' + error.responseJSON.message);
        }
    });
}

$(document).ready(function () {

    // 创建 Douyin Hao URL 记录
    $('#create-douyin-hao-url-form').on('submit', function (e) {
        e.preventDefault();
        var formData = $(this).serializeJSON();
        $.ajax({
            url: apihost + '/douyin_hao_url/',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function (response) {
                alert(response.message);
            },
            error: function (error) {
                alert('Error: ' + error.responseJSON.message);
            }
        });
    });

    // 获取所有 Douyin Hao URL 记录表单提交事件
    $('#get-all-douyin-hao-urls-form').on('submit', function (e) {
        e.preventDefault();
        var page = parseInt($(this).find('input[name="page"]').val());
        getDouyinHaoUrls(page);
    });

    // 创建 Douyin URL 记录
    $('#create-douyin-url-form').on('submit', function (e) {
        e.preventDefault();
        var formData = $(this).serializeJSON();
        $.ajax({
            url: apihost + '/douyin_url/',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function (response) {
                alert(response.message);
            },
            error: function (error) {
                alert('Error: ' + error.responseJSON.message);
            }
        });
    });

    // 获取所有 Douyin URL 记录
    $('#get-all-douyin-urls-form').on('submit', function (e) {
        e.preventDefault();
        var page = parseInt($(this).find('input[name="page"]').val());
        getDouyinUrls(page);
    });

    // 创建 Douyin History URL 记录
    $('#create-douyin_history_url-form').on('submit', function (e) {
        e.preventDefault();
        var formData = $(this).serializeJSON();
        $.ajax({
            url: apihost + '/douyin_history_url/',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function (response) {
                alert(response.message);
            },
            error: function (error) {
                alert('Error: ' + error.responseJSON.message);
            }
        });
    });

    // 获取所有 Douyin History URL 记录
    $('#get-all-douyin_history_urls-form').on('submit', function (e) {
        e.preventDefault();
        var page = parseInt($(this).find('input[name="page"]').val());
        getDouyinHistoryUrls(page);
    });

     // 创建 Douyin live 记录
     $('#create-douyin-live-form').on('submit', function (e) {
        e.preventDefault();
        var formData = $(this).serializeJSON();
        $.ajax({
            url: apihost + '/douyin_live/',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function (response) {
                alert(response.message);
            },
            error: function (error) {
                alert('Error: ' + error.responseJSON.message);
            }
        });
    });

    // 获取所有 Douyin live 记录表单提交事件
    $('#get-all-douyin-live-form').on('submit', function (e) {
        e.preventDefault();
        var page = parseInt($(this).find('input[name="page"]').val());
        getDouyinLive(page);
    });

    // 获取所有 Douyin live详情记录表单提交事件
    $('#get-douyin-livedetail-form').on('submit', function (e) {
        e.preventDefault();
        var page = parseInt($(this).find('input[name="page"]').val());
        getDouyinLiveDetail(page);
    });

     // 获取所有 Douyin live详情记录表单提交事件
     $('#get-douyin-livedetail-form .export').on('click', function (e) {
        e.preventDefault();
        var form = $('#get-douyin-livedetail-form');
        var formData = form.serializeArray();
        formData = filterEmptyParams(formData);
        var queryString = $.param(formData);
        url = `${apihost}/douyin_livedetail/?` + queryString+'&export=1';
        window.open(url)
    });


    // 添加关键词
    $('#create-douyin-keywords-form').on('submit', function (e) {
        e.preventDefault();
        var formData = $(this).serializeJSON();
        $.ajax({
            url: apihost + '/douyin_keyword/',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function (response) {
                alert(response.message);
            },
            error: function (error) {
                alert('Error: ' + error.responseJSON.message);
            }
        });
    });

    // 获取所有 Douyin live 记录表单提交事件
    $('#get-all-douyin-keywords-form').on('submit', function (e) {
        e.preventDefault();
        var page = parseInt($(this).find('input[name="page"]').val());
        getDouyinKeyword(page);
    });
});

function getDouyinKeyword(page) {
    var form = $('#get-all-douyin-keywords-form');
    form.find('input[name="page"]').val(page);
    var formData = form.serializeArray();
    formData = filterEmptyParams(formData);
    var queryString = $.param(formData);
    $.ajax({
        url: `${apihost}/keywords/?` + queryString,
        type: 'GET',
        success: function (response) {
            var tableBody = $('#douyin-keywords-table tbody');
            tableBody.empty();
            totalRecords = response.total_count || 0;
            response.data.forEach(function (item) {
                var row = '<tr data-id="' + item.id + '">' +
                    '<td>' + item.id + '</td>' +
                    '<td>' + item.keyword + '</td>' +
                    '<td>' + (item.type==1?'非广告视频':'广告视频') + '</td>' +
                    '<td>' + item.status + '</td>' +
                    '<td>' + item.last_runtime + '</td>' +
                    '<td>' + item.last_count + '</td>' +
                    '<td>' +
                    '<button onclick="deleteDouyinKeyword(' + item.id + ')">删除</button>' +
                    '</td>' +
                    '</tr>';
                tableBody.append(row);
            });
            // 生成分页导航
            generatePagination('douyin-keywords-pagination', page, totalRecords, formData, 'getDouyinKeyword');
        },
        error: function (error) {
            alert('Error: ' + error.responseJSON.message);
        }
    });
}

function deleteDouyinKeyword(id) {
    if (confirm('Are you sure you want to delete this kerword?')) {
        $.ajax({
            url: apihost + '/keywords/' + id,
            type: 'DELETE',
            success: function (response) {
                alert(response.message);
                $('#get-all-douyin-keywords-form').submit();
            },
            error: function (error) {
                alert('Error: ' + error.responseJSON.message);
            }
        });
    }
}

// 更新 Douyin Hao URL 记录
function updateDouyinHaoUrl(id) {
    var newData = prompt('输入JSON格式( {"url": "new_url", "status": 1})');
    if (newData) {
        $.ajax({
            url: apihost + '/douyin_hao_url/' + id,
            type: 'PUT',
            contentType: 'application/json',
            data: newData,
            success: function (response) {
                alert(response.message);
                $('#get-all-douyin-hao-urls-form').submit();
            },
            error: function (error) {
                alert('Error: ' + error.responseJSON.message);
            }
        });
    }
}

// 删除 Douyin Hao URL 记录
function deleteDouyinHaoUrl(id) {
    if (confirm('Are you sure you want to delete this record?')) {
        $.ajax({
            url: apihost + '/douyin_hao_url/' + id,
            type: 'DELETE',
            success: function (response) {
                alert(response.message);
                $('#get-all-douyin-hao-urls-form').submit();
            },
            error: function (error) {
                alert('Error: ' + error.responseJSON.message);
            }
        });
    }
}

// 更新 Douyin URL 记录
function updateDouyinUrl(id) {
    var newData = prompt('输入JSON格式( {"url": "new_url", "status": 1})');
    if (newData) {
        $.ajax({
            url: apihost + '/douyin_url/' + id,
            type: 'PUT',
            contentType: 'application/json',
            data: newData,
            success: function (response) {
                alert(response.message);
                $('#get-all-douyin-urls-form').submit();
            },
            error: function (error) {
                alert('Error: ' + error.responseJSON.message);
            }
        });
    }
}

// 删除 Douyin URL 记录
function deleteDouyinUrl(id) {
    if (confirm('Are you sure you want to delete this record?')) {
        $.ajax({
            url: apihost + '/douyin_url/' + id,
            type: 'DELETE',
            success: function (response) {
                alert(response.message);
                $('#get-all-douyin-urls-form').submit();
            },
            error: function (error) {
                alert('Error: ' + error.responseJSON.message);
            }
        });
    }
}

// 更新状态 Douyin URL 记录
function setDouyinUrlStatus(id,status) {
    newData = {'status':status}
    $.ajax({
        url: apihost + '/douyin_url/' + id,
        type: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify(newData),
        success: function (response) {
            alert(response.message);
            $('#get-all-douyin-urls-form').submit();
        },
        error: function (error) {
            alert('Error: ' + error.responseJSON.message);
        }
    });
}

// 更新状态 Douyin live记录
function setDouyinLiveStatus(id,status) {
    newData = {'status':status}
    $.ajax({
        url: apihost + '/douyin_live/' + id,
        type: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify(newData),
        success: function (response) {
            alert(response.message);
            $('#get-all-douyin-live-form').submit();
        },
        error: function (error) {
            alert('Error: ' + error.responseJSON.message);
        }
    });
}

// 更新 Douyin history URL 记录
function updateDouyinHistoryUrl(id) {
    var newData = prompt('输入JSON格式:{"keyword": "品牌"}', '{"keyword": ""}');
    if (newData) {
        $.ajax({
            url: apihost + '/douyin_history_url/' + id,
            type: 'PUT',
            contentType: 'application/json',
            data: newData,
            success: function (response) {
                alert(response.message);
                $('#get-all-douyin-urls-form').submit();
            },
            error: function (error) {
                alert('Error: ' + error.responseJSON.message);
            }
        });
    }
}

// 删除 Douyin history URL 记录
function deleteDouyinHistoryUrl(id) {
    if (confirm('Are you sure you want to delete this record?')) {
        $.ajax({
            url: apihost + '/douyin_history_url/' + id,
            type: 'DELETE',
            success: function (response) {
                alert(response.message);
                $('#get-all-douyin-urls-form').submit();
            },
            error: function (error) {
                alert('Error: ' + error.responseJSON.message);
            }
        });
    }
}



// 更新 Douyin live 记录
function updateDouyinLive(id) {
    var newData = prompt('输入JSON格式( {"liveid": "new_liveid", "status": 1})');
    if (newData) {
        $.ajax({
            url: apihost + '/douyin_live/' + id,
            type: 'PUT',
            contentType: 'application/json',
            data: newData,
            success: function (response) {
                alert(response.message);
                $('#get-all-douyin-live-form').submit();
            },
            error: function (error) {
                alert('Error: ' + error.responseJSON.message);
            }
        });
    }
}

// 删除 Douyin live 记录
function deleteDouyinLive(id) {
    if (confirm('Are you sure you want to delete this record?')) {
        $.ajax({
            url: apihost + '/douyin_live/' + id,
            type: 'DELETE',
            success: function (response) {
                alert(response.message);
                $('#get-all-douyin-live-form').submit();
            },
            error: function (error) {
                alert('Error: ' + error.responseJSON.message);
            }
        });
    }
}
// 获取所有 Douyin live 记录
function getDouyinLive(page) {
    var form = $('#get-all-douyin-live-form');
    form.find('input[name="page"]').val(page);
    var formData = form.serializeArray();
    formData = filterEmptyParams(formData);
    var queryString = $.param(formData);
    $.ajax({
        url: `${apihost}/douyin_live/?` + queryString,
        type: 'GET',
        success: function (response) {
            var tableBody = $('#douyin-live-table tbody');
            tableBody.empty();
            totalRecords = response.total_count || 0;
            response.data.forEach(function (item) {
                var row = '<tr data-id="' + item.id + '">' +
                    '<td>' + item.id + '</td>' +
                    '<td>' + item.liveid + '</td>' +
                    '<td>' + item.name + '</td>' +
                    '<td>' + item.status + '</td>' +
                    '<td>' + item.addtime + '</td>' +
                    '<td>' + item.updatetime + '</td>' +
                    '<td>' + (item.islisten?'是':'否') + '</td>' +
                    '<td>' + (item.lastlistentime || '') + '</td>' +
                    '<td>' + (item.lasttixingtime || '') + '</td>' +
                    '<td>' + item.touser + '</td>' +
                    '<td>' +
                    '<button onclick="deleteDouyinLive(' + item.id + ')">删除</button>  ' +
                    (item.status?'<button onclick="setDouyinLiveStatus(' + item.id + ',0)">重抓</button>':'') +
                    '&nbsp;&nbsp;<a href="douyin-live-detail.html?liveid='+ item.liveid +'" target="_blank">详情</a>'+
                    '</td>' +
                    '</tr>';
                tableBody.append(row);
            });
            // 生成分页导航
            generatePagination('douyin-live-pagination', page, totalRecords, formData, 'getDouyinLive');
        },
        error: function (error) {
            alert('Error: ' + error.responseJSON.message);
        }
    });
}

// 获取所有 Douyin live详情记录
function getDouyinLiveDetail(page) {
    var form = $('#get-douyin-livedetail-form');
    form.find('input[name="page"]').val(page);
    var formData = form.serializeArray();
    formData = filterEmptyParams(formData);
    var queryString = $.param(formData);
    $.ajax({
        url: `${apihost}/douyin_livedetail/?` + queryString,
        type: 'GET',
        success: function (response) {
            var tableBody = $('#douyin-livedetail-table tbody');
            tableBody.empty();
            totalRecords = response.total_count || 0;
            response.data.forEach(function (item) {
                var row = '<tr data-id="' + item.id + '">' +
                    '<td>' + item.id + '</td>' +
                    '<td>' + item.liveid + '</td>' +
                    '<td>' + item.name + '</td>' +
                    '<td>' + item.nickname + '</td>' +
                    '<td>' + item.sec_uid + '</td>' +
                    '<td>' + item.updatetime + '</td>' +
                    '<td>' + item.type + '</td>' +
                    '<td>' + item.text + '</td>' +
                    '<td>' + (item.tunique_id || '') + '</td>' +
                    '<td>' + (item.phone || '') + '</td>' +
                    '<td>' + item.signature + '</td>' +
                    '<td>' + item.address + '</td>' +
                    '<td>' + item.avatar + '</td>' +
                    '<td>' + item.cover + '</td>' +
                    '<td>' + item.status + '</td>' +
                    '</tr>';
                tableBody.append(row);
            });
            // 生成分页导航
            generatePagination('douyin-livedetail-pagination', page, totalRecords, formData, 'getDouyinLiveDetail');
        },
        error: function (error) {
            alert('Error: ' + error.responseJSON.message);
        }
    });
}

// 获取URL中的参数函数
function getUrlParam(name) {
    // 获取当前URL
    var url = window.location.href;
    // 解析URL中的查询字符串
    var queryString = url.split('?')[1];
    
    if (!queryString) {
        return null; // 没有查询字符串
    }
    
    // 将查询字符串拆分为键值对
    var params = queryString.split('&');
    var paramObj = {};
    
    // 遍历参数数组，构建参数对象
    for (var i = 0; i < params.length; i++) {
        var param = params[i].split('=');
        if (param.length === 2) {
            // 解码URI组件
            paramObj[decodeURIComponent(param[0])] = decodeURIComponent(param[1]);
        }
    }
    
    // 返回指定参数的值，如果不存在则返回null
    return paramObj[name] || null;
}

function exportDouyinHaoFans(id){
    var url = `${apihost}/douyin_hao_fans/?` + 'hid=' + id + '&export=1';
    window.open(url)
}

function isFans(id){
    if (confirm('是否要重新抓取该用户的粉丝列表？')) {
        $.ajax({
            url: apihost + '/isfans_douyin_hao/' + id,
            type: 'get',
            success: function (response) {
                alert(response.message);
            },
            error: function (error) {
                alert('Error: ' + error.responseJSON.message);
            }
        });
    }
}

$( function() {
    $.datepicker.regional["zh-CN"] = { closeText: "关闭", prevText: "<上月", nextText: "下月>", currentText: "今天", monthNames: ["一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月"], monthNamesShort: ["一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月"], dayNames: ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"], dayNamesShort: ["周日", "周一", "周二", "周三", "周四", "周五", "周六"], dayNamesMin: ["日", "一", "二", "三", "四", "五", "六"], weekHeader: "周", dateFormat: "yy-mm-dd", firstDay: 1, isRTL: !1, showMonthAfterYear: !0, yearSuffix: "年" }
    $.datepicker.setDefaults($.datepicker.regional["zh-CN"]);
} );