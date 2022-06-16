epoch
```
    public static ZonedDateTime convertEpochToZonedDateTime(String epoch) {
        long longValue = Long.parseLong(epoch);
        return convertEpochToZonedDateTime(longValue);
    }

    public static ZonedDateTime convertEpochToZonedDateTime(long epoch) {
        return epoch != 0L ? Instant.ofEpochMilli(epoch).atZone(Constant.PST_ZONED_ID) : null;
    }

    public static ZonedDateTime convertEpochToZonedDateTime(String epoch1, String epoch2) {
        Long longValue = Long.parseLong(epoch1) + Long.parseLong(epoch2);
        return longValue != 0L ? Instant.ofEpochMilli(longValue).atZone(Constant.PST_ZONED_ID) : null;
    }
```
