/* =============================================================================
#     FileName: hamster.js
#         Desc: javascript for website theme
#       Author: Cother (based on the work of codepiano)
#        Email: ihamsterball
#     HomePage: https://hamsterball.me
#      Version: 0.0.2
#   LastChange: 2016-08-28 19:45:16
#      History: 2013-05-12 01:39:30
============================================================================= */
/* 页面加载后执行 */
!function ($) {
  $(function(){

    var tableReference;
    /* 初始化dataTable */
    if($('#post-data')[0]){
      tableReference = $('#post-data').dataTable(datatablesConfig);
    }

    /* 目录页导航 */
    var url = window.location.href;
    if(url.indexOf('categories.html') > -1){
      $('#categories-nav a').click(function (e){
        $(this).tab('show');
      })

      /* 自动打开链接中的锚点 */
      var matches = url.match(/categories\.html(#.*)/);
      if(matches){
        $('#categories-nav a[href="' + matches[1] + '"]').tab('show');
      }else{
        $('#categories-nav a:first').tab('show');
      }
    } 

    /* 自动根据标签过滤table */
    if(url.indexOf('posts.html') > -1){
      var matches = url.match(/posts\.html#(.*)/);
      if(matches && tableReference){
        tableReference.fnFilter(matches[1],2);
      }

      $('#post-data_filter input').val(matches[1])

      $("#post-data_filter input").keyup( function () {
        tableReference.fnFilter('', 2);
        tableReference.fnFilter( this.value, 2);
      } );
    }
    $('.error-404').tooltip({placement: 'top'});
	$('.featured-ribbon').tooltip({placement: 'top'});
  });
}(window.jQuery);

/* tooltip设置 */
tooltipConfig = {
  "placement": "right",
  "delay": { show: 50, hide: 50 }
}
