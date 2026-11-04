# 中国城市/区县经纬度数据说明

文件：`china_areas.json`

- 格式：`[[省, 市, 区县, 纬度, 经度], ...]`，共 3321 条（省/市/区县级）
- 用途：天气城市搜索（支持中文区县级搜索）与 GPS 反查最近区县
- 来源：[88250/city-geo](https://github.com/88250/city-geo)（整理自
  [modood/Administrative-divisions-of-China](https://github.com/modood/Administrative-divisions-of-China)
  与百度地图 API）
- 许可证：[木兰宽松许可证，第2版 (Mulan PSL v2)](http://license.coscl.org.cn/MulanPSL2)，
  允许自由使用、修改、分发，需保留版权与许可声明。
- 本文件经过格式压缩（去掉 country 字段、坐标保留 5 位小数）以减小 App 体积。
