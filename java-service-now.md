Use offset for storing in database: https://www.baeldung.com/java-zoneddatetime-offsetdatetime

1. 
Output: `javascript:gs.dateGenerate('2022-06-16','15:44:06')`
Use for service now: `sys_created_on>=javascript:gs.dateGenerate('2022-06-16','15:44:06')`

```    
    private String convertToSnowTimeString(ZonedDateTime dateTime) {
        ZonedDateTime dateTimeInSnowTimeZone = dateTime.withZoneSameInstant(Constant.PST_ZONED_ID);
        return String.format("javascript:gs.dateGenerate('%s-%02d-%02d','%02d:%02d:%02d')",
                dateTimeInSnowTimeZone.getYear(),
                dateTimeInSnowTimeZone.getMonthValue(),
                dateTimeInSnowTimeZone.getDayOfMonth(),
                dateTimeInSnowTimeZone.getHour(),
                dateTimeInSnowTimeZone.getMinute(),
                dateTimeInSnowTimeZone.getSecond()
        );
    }
```

2. 
// 2021-06-16 16:10:43
```
private static final String SNOW_DATETIME_PATTERN = "yyyy-MM-dd HH:mm:ss";
private static final ZoneId SNOW_TIMEZONE = Constant.PST_ZONED_ID;
```
Output: (ZonedDateTime) "2022-06-17T13:13:52-07:00[America/Los_Angeles]"
```
    public static ZonedDateTime convertFromSnowTimeString(String snowTimeString) {
        if (snowTimeString == null || snowTimeString.isEmpty()) {
            return null;
        }
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern(SNOW_DATETIME_PATTERN);
        LocalDateTime localDateTime = LocalDateTime.parse(snowTimeString, formatter);
        return localDateTime.atZone(SNOW_TIMEZONE);
    }
```
3.
Output: (ZonedDateTime) "2022-06-17T13:13:52-07:00"
```
    public static ZonedDateTime convertFromSnowTimeString(String snowTimeString) {
        if (snowTimeString == null || snowTimeString.isEmpty()) {
            return null;
        }
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern(SNOW_DATETIME_PATTERN);
        LocalDateTime localDateTime = LocalDateTime.parse(snowTimeString, formatter);
        String offset = localDateTime.atZone(SNOW_TIMEZONE).getOffset().toString();
        return localDateTime.atOffset(ZoneOffset.of(offset)).toZonedDateTime();
    }
```
