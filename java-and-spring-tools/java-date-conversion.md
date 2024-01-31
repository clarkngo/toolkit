
2023-03-02T03:22:30.794936-0700
```
String timeString = "2023-03-02T03:22:30.794936-0700"
ZonedDateTime z = OffsetDateTime.parse(
        timeString,
        DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss.SSSSSSZ")).atZoneSameInstant(ZoneId.of("America/Phoenix"));
```

// 2020-03-14
```
public static ZonedDateTime convertDateStringToZonedDateTime(String dateString, String pattern, ZoneId zoneId) {
    if (dateString == null || dateString.isEmpty()) {
        return null;
    }
    DateTimeFormatter formatter = DateTimeFormatter.ofPattern(pattern);
    LocalDate localDate = LocalDate.parse(dateString, formatter);
    return localDate.atStartOfDay(zoneId);
}
```

// 2023-02-08T13:51:37.000Z
```
ZonedDateTime z = Util.convertTimeStringToZonedDateTime(
        airtableMerchEp.getCreatedTime().replace(".000Z",""),
        "yyyy-MM-dd'T'HH:mm:ss",
        ZoneId.of("America/Phoenix"));
```


// others
```
    public static ZonedDateTime convertTimeStringToZonedDateTime(String timeString, String pattern, ZoneId zoneId) {
        if (timeString == null || timeString.isEmpty()) {
            return null;
        }
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern(pattern);
        LocalDateTime localDateTime = LocalDateTime.parse(timeString, formatter);
        String offset = localDateTime.atZone(zoneId).getOffset().toString();
        return localDateTime.atOffset(ZoneOffset.of(offset)).toZonedDateTime();
    }
```
