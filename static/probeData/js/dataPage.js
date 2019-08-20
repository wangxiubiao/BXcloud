var sites;               //保存所有的站点信息
var currentSiteId;      //保存用户当前选择的站点
var markers = [];       //保存站点坐标与站点名
var idToName = {};


//登陆成功后获取站点信息
function getSites(){
    $.post("/getSites",{user:"8"},function (data) {
        sites = data.list
        $('#siteDesc').text((sites[0])["desc"])
        currentSiteId = (sites[0])["id"]
        for (i = 0; i < sites.length; i++){
            var opt = document.createElement('option')
            var id = (sites[i])["id"].toString()
            var name = (sites[i])["siteName"]
            opt.text = (sites[i])["siteName"]
            opt.value = (sites[i])["id"]
            $('#siteSelect').append(opt)
            eval("idToName["+id+"]="+"name");
            console.log(idToName["2"])
        }
        siteChange()
        draw_map()
    },"json")
}

//改变用户选择的站点
function siteChange() {
    i = 0;
    var $curSite = $('#siteSelect')
    currentSiteId = $curSite.val()
    curSiteName = $curSite.find("option:selected").text();
    $.post("/selectSite",{'currentSiteId':currentSiteId},function (data) {
        //循环判断当前选择的站点
        for (; i < sites.length; i++){
            if (currentSiteId == (sites[i])["id"]){
                break
            }
        }
        $('#siteDesc').text((sites[i])["desc"])      //更改站点描述信息

        //将当前站点的所有数据加到数据分析模块
        console.log(data.paramType)
        $('#paramSelect > option').remove()
        for (i = 0; i < data.paramType.length; i++){
            opt = document.createElement('option')
            opt.text = data.paramType[i]
            opt.value = data.paramType[i]
            $('#paramSelect').append(opt)
        }
        historyWarning()
        get24HourData()     //默认获取第一个参数数据
        weather(curSiteName.substring(0,curSiteName.length-1))
        urgentPerson()
    },"json")
}

//实时传输通道，用于后台将实时数据传输到前端
function startWebSoc() {
    var s = new WebSocket("ws://127.0.0.1:8000/transport");
    s.onopen = function () {
        console.log('WebSocket open');
    };
    s.onmessage = function (e) {
        console.log('message: ' + e.data);
        jsonData=JSON.parse(e.data)
        if (jsonData["type"] === "pdata") {
            dataShow(jsonData);
        }
        else if (jsonData["type"] === "warning"){
            warningShow(jsonData);
        }
        else if (jsonData["type"] !== "rsSite") {
            console.log(jsonData)
            updateMarker(jsonData);
        }
    };
    s.onclose=function (e) {
        console.log('WebSocket close');
        startWebSoc();
    }
    if(s.readyState==WebSocket.OPEN){
        s.onopen();
    }
}

//将实时数据显示到监测数据模块
function dataShow(jsonData) {
    // jsonData=JSON.parse(data)
    index = 1
    if(jsonData["siteId"] == currentSiteId){
        delete jsonData["siteId"]
        delete jsonData["type"]
        delete jsonData["time"]
        $('.divData > div').css({"display":"none"}) //将所有显示数据的div隐藏
        for (var key in jsonData){
            $('#param'+index).text(key)
            $('#paramData'+index).text(jsonData[key])
            $('#paramUnit'+index).text(paramTounit(key))
            $('.data'+index).css({"display":"block"})
            index++
        }

    }
}

function paramTounit(data) {
    if(data=="PH")
        return "pH";
    if(data=="Cond")
        return "μS/cm";
    if(data=="Turb")
        return "NTU";
    if(data=="LDO")
        return "mg/L";
    if(data=="NH")
        return "mg/L";
    if(data=="COD")
        return "mg/L";
    if(data=="Chla")
        return "μg/L";
    if(data=="TEMP")
        return "℃";
}

function get24HourData() {
    param = $('#paramSelect').val()
    $.ajax({
        url:"/get24HourData",
        type:"POST",
        dataType:"json",
        data:{'currentSiteId':currentSiteId,"param":param}, //当前站点和当前选择查看的参数
        success:function (msg) {
            drawChart(msg.data,msg.time,param)
        },
        error:function (err) {
            console.log(err)
        }
    })
}


function drawChart(data,time,type) {
   var title = {
      text: '24小时数据曲线',
       useHTML: true,
            style: {
                color: '#3497DB',      //字体颜色
                "fontSize": "0.3rem",   //字体大小
                fontWeight: 'bold'
            }
   };
   var subtitle = {
      text: 'Source: runoob.com'
   };

   //背景颜色
   var chart = {
        backgroundColor: "#0F2944",
        type: 'line',
        height:365
    };
   var xAxis = {
       title:{
           text: "时间",
          style: { color: '#2EBBD9' }
       },
      categories: time,
       style: { color: '#2EBBD9' },
       //设置坐标轴文字颜色
       labels:{
          style: { color: '#2EBBD9' }
       }
   };
   var yAxis = {
      title: {
         text: paramTounit(type),
          style: { color: '#2EBBD9' }
      },
       labels:{
          style: { color: '#2EBBD9' }
       },
      plotLines: [{
         value: 0,
         width: 1,
         color: '#2EBBD9'
      }]
   };

   var tooltip = {
      valueSuffix: paramTounit(type),
       style: { color: '#2EBBD9' }
   }

   var legend = {
      layout: 'vertical',
      align: 'right',
      verticalAlign: 'middle',
      borderWidth: 0,
       itemStyle:{ "color": "#fff","font-size":"0.2rem","font-family":"Arial","font-weight":"normal" }
   };

   var series =  [
       {
           name:type ,
           data: data,
       }
   ];
   var credits = [
       {
            enabled: false     //不显示LOGO
        }
   ];


   var json = {};

   json.title = title;
   //json.subtitle = subtitle;
   json.xAxis = xAxis;
   json.yAxis = yAxis;
   json.tooltip = tooltip;
   json.legend = legend;
   json.series = series;
   json.credits = credits;
   json.chart = chart;

   $('#chartContainer').highcharts(json);
}


function warningShow(warningData) {
    if(warningData["siteId"] == currentSiteId || warningData["siteId_id"] == currentSiteId ){
        var time = warningData["time"]
        var param = warningData["warningParam"]
        var type = warningData["warningType"]
        var value = warningData["warningValue"]
        var limit = warningData["limitValue"]
        $('#warnUL').prepend("<li>"+formatTime(new Date(time))+" 报警参数："+param+" 报警类型："+type+" 报警值："+value+" 限定值:"+limit+"</li>")
        $myli = $('#warnUL > li')
        index =  $myli.length
        //如果报警信息显示超过5条，则删除最后一条
        var $num = $('#warningNum')
        $num.text(1+Number($num.text()))
    }
}

// 时间转换，Date的‘toJSON’方法返回格林威治时间的JSON格式字符串，实际是使用‘toISOString’方法的结果。
// 字符串形如‘2018-08-09T10:20:54.396Z’，转化为北京时间需要额外增加八个时区，我们需要取字符串前19位，
// 然后把‘T’替换为空格，即是我们需要的时间格式。
function formatTime(time) {
    time.setHours(time.getHours()+8)
    return time.toJSON().substr(0, 19).replace('T', ' ');
}


function historyWarning() {
    $.ajax({
        url: "/historyWarning",
        dataType: "json",
        type: "POST",
        data:{'currentSiteId':currentSiteId}, //当前站点和当前选择查看的参数
        success:function (msg) {
            console.log("移除li")
            $('#warnUL > li').remove()
            $('#warningNum').text(0)
            for (var i = 0; i < msg.list.length; i++){
                warningShow(msg.list[i])
            }
        },
        error:function (err) {
            console.log(err)
        }
    })
}

function draw_map() {
    map = new AMap.Map('map_container', {
                        resizeEnable: true, //是否监控地图容器尺寸变化
                        zoom:11, //初始化地图层级
                        center: [116.397428, 39.90923] //初始化地图中心点
                    });
    for (var i = 0; i < sites.length; i++){
        markers[i] = {position: [(sites[i])["siteLng"], (sites[i])["siteLat"]],
            title:(sites[i])["siteName"]}
    }

      // 创建一个红色icon
    redIcon = new AMap.Icon({
        size: new AMap.Size(20, 36),
        image: "//a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-red.png",
        imageSize: new AMap.Size(20, 36),
        // imageOffset: new AMap.Pixel(-95, -3)
    });

    //创建一个blue icon
    blueIcon = new AMap.Icon({
        size: new AMap.Size(20, 36),
        image: "//a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-default.png",
        imageSize: new AMap.Size(20, 36),
        // imageOffset: new AMap.Pixel(-95, -3)
    });

    markers.forEach(function(marker) {
        new AMap.Marker({
            map: map,
            icon: marker.icon,
            position: [marker.position[0], marker.position[1]],
            offset: new AMap.Pixel(-13, -30),
            title:marker.title
        });
    });

    var center = map.getCenter();
     console.log('当前中心点坐标：' + center.getLng() + ',' + center.getLat())
     map.setFitView();  //设置当前地图可以显示所有覆盖点标记
}

function updateMarker(msg) {
    var overlays = map.getAllOverlays('marker');
     overlays.forEach(function (overlay) {
         console.log(overlay.getTitle());
         if (overlay.getTitle() === msg["siteName"]){
             overlay.setPosition(new AMap.LngLat(msg["lng"],msg["lat"],false))
             overlay.setAnimation('AMAP_ANIMATION_DROP');
             if (msg["state"] === "normal"){
                //overlay.setIcon('//a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-default.png')
                 overlay.setIcon(blueIcon);
                 overlay.setTop(true)
             }
             else if (msg["state"] === "fault") {
                // overlay.setIcon('//a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-red.png')
                 overlay.setIcon(redIcon)
             }

             //map.remove(overlay)
         }
     })
    map.setFitView();
}

//获取站点所在地区的天气情况
function weather(data) {
    AMap.plugin('AMap.Weather', function() {
        var weather = new AMap.Weather();
        //查询实时天气信息, 查询的城市到行政级别的城市，如朝阳区、杭州市
        weather.getLive(data, function(err, data) {
            if (!err) {
                $("#weather").text("气温："+ data.temperature+"℃，"+data.weather)
            }
        });
    });
}


function urgentPerson() {
    $.ajax({
        url:"/ugPerson",
        type:"POST",
        dataType:"json",
        data:{'currentSiteId':currentSiteId}, //当前站点和当前选择查看的参数
        success:function (msg) {
            console.log(msg)
            var $table = $(".urgent > table")
            $(".urgent > table tr:not(:first)").remove()
            for (var i = 0; i < msg.list.length; i++){
              $table.append("<tr><td>"+(msg.list[0])['name']+"</td><td>"
                  +(msg.list[0])['phone']+"</td><td>"+(msg.list[0])['email']
                  +"</td><td>"+idToName[(msg.list[0])['siteId_id']]+"</td></tr>")
            }
        },
        error:function (err) {
            console.log(err)
        }
    })
}
